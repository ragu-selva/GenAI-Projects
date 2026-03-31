"""
kg_rag.py — Knowledge Graph RAG Core Engine
Supports: NetworkX (in-memory, always) + Neo4j (optional, if configured)
"""

import json
import re
import io
import numpy as np
import networkx as nx
from typing import Optional
import anthropic


# ── Colour palette for entity types ──────────────────────────────────────────
NODE_COLORS = {
    "Person":       "#f43f5e",
    "Organization": "#4a9eff",
    "Concept":      "#10b981",
    "Rule":         "#f5a623",
    "Location":     "#7c3aed",
    "Event":        "#fb923c",
    "Other":        "#64748b",
}


class KnowledgeGraphRAG:
    """
    End-to-end KG-RAG pipeline:
      PDF → chunks → entity/relation extraction (Claude)
           → NetworkX graph (+ optional Neo4j)
           → sentence-transformer embeddings
           → hybrid graph + vector retrieval
           → Claude answer generation
    """

    ENTITY_PROMPT = """Extract entities and relationships from the text below.

Return ONLY valid JSON — no markdown, no explanation, just the JSON object:
{{
  "entities": [
    {{"id": "snake_case_id", "label": "Display Name", "type": "Person|Organization|Concept|Rule|Location|Event|Other", "description": "one sentence"}}
  ],
  "relationships": [
    {{"from": "entity_id_1", "to": "entity_id_2", "type": "VERB_PHRASE_IN_CAPS", "description": "one sentence"}}
  ]
}}

Guidelines:
- Entity ids: unique snake_case, ≤ 30 chars
- Extract 3-8 entities per chunk
- Extract 2-6 meaningful relationships
- Skip trivial words; focus on domain concepts
- Relationship type examples: DEFINES, APPLIES_TO, REQUIRES, GOVERNS, REFERENCES, PART_OF

TEXT:
{chunk}"""

    def __init__(self, api_key: str, neo4j_cfg: Optional[dict] = None):
        self.client   = anthropic.Anthropic(api_key=api_key)
        self.graph    = nx.DiGraph()          # in-memory graph (always available)
        self.chunks   = []                    # raw text chunks
        self.embeddings: list[np.ndarray] = [] # one per chunk
        self.chunk_meta: list[dict] = []      # page / source info per chunk
        self.neo4j    = None
        self._st_model = None                 # lazy-loaded sentence transformer

        if neo4j_cfg and neo4j_cfg.get("uri"):
            self._init_neo4j(neo4j_cfg)

    # ── Neo4j ────────────────────────────────────────────────────────────────

    def _init_neo4j(self, cfg: dict):
        try:
            from neo4j import GraphDatabase
            self.neo4j = GraphDatabase.driver(
                cfg["uri"], auth=(cfg["username"], cfg["password"])
            )
            # Verify connectivity
            self.neo4j.verify_connectivity()
        except Exception as exc:
            self.neo4j = None
            raise ConnectionError(f"Neo4j connection failed: {exc}") from exc

    def _neo4j_clear(self):
        """Wipe ALL nodes and relationships before ingesting a new PDF."""
        if not self.neo4j:
            return
        with self.neo4j.session() as s:
            s.run("MATCH (n) DETACH DELETE n")

    def _neo4j_push(self, entities: list, rels: list, chunk_id: int, source_doc: str = ""):
        if not self.neo4j:
            return
        with self.neo4j.session() as s:
            for e in entities:
                s.run(
                    "MERGE (n:Entity {id: $id}) "
                    "SET n.label=$label, n.type=$type, "
                    "    n.description=$desc, n.chunk_id=$cid, "
                    "    n.source_doc=$src",
                    id=e["id"], label=e["label"],
                    type=e["type"], desc=e.get("description", ""),
                    cid=chunk_id, src=source_doc,
                )
            for r in rels:
                s.run(
                    "MATCH (a:Entity {id:$f}), (b:Entity {id:$t}) "
                    "MERGE (a)-[rel:RELATES {type:$rtype}]->(b) "
                    "SET rel.description=$desc, rel.source_doc=$src",
                    f=r["from"], t=r["to"],
                    rtype=r["type"], desc=r.get("description", ""),
                    src=source_doc,
                )

    def neo4j_cypher(self, cypher: str) -> list[dict]:
        """Run arbitrary read Cypher, return list of record dicts."""
        if not self.neo4j:
            return []
        with self.neo4j.session() as s:
            result = s.run(cypher)
            return [dict(record) for record in result]

    # ── PDF ingestion ─────────────────────────────────────────────────────────

    def load_pdf(self, pdf_bytes: bytes) -> str:
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(pdf_bytes))
        pages  = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            pages.append((i + 1, text))
        return pages                          # list of (page_num, text)

    def chunk_pages(
        self,
        pages: list[tuple[int, str]],
        chunk_size: int = 400,
        overlap: int   = 60,
    ) -> list[dict]:
        """Split pages into word-windowed chunks with metadata."""
        chunks = []
        for page_num, text in pages:
            words = text.split()
            for i in range(0, len(words), chunk_size - overlap):
                window = " ".join(words[i : i + chunk_size])
                if len(window.strip()) < 30:
                    continue
                chunks.append({
                    "id":      len(chunks),
                    "page":    page_num,
                    "text":    window,
                    "preview": window[:120] + ("…" if len(window) > 120 else ""),
                })
        return chunks

    # ── Entity / Relation extraction ─────────────────────────────────────────

    def extract_entities(self, chunk_text: str) -> dict:
        """Call Claude Haiku to extract entities + relationships from one chunk."""
        prompt = self.ENTITY_PROMPT.format(chunk=chunk_text[:1800])
        resp = self.client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1200,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = resp.content[0].text
        # Be tolerant: grab first JSON object in the response
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        if not m:
            return {"entities": [], "relationships": []}
        try:
            return json.loads(m.group())
        except json.JSONDecodeError:
            return {"entities": [], "relationships": []}

    # ── Graph building ────────────────────────────────────────────────────────

    def add_to_graph(self, entities: list, rels: list, chunk_id: int):
        """Upsert extracted entities/relations into the NetworkX graph."""
        for e in entities:
            eid = e["id"]
            if self.graph.has_node(eid):
                # Merge: append chunk_ids already seen
                existing = self.graph.nodes[eid].get("chunk_ids", [])
                self.graph.nodes[eid]["chunk_ids"] = list(set(existing + [chunk_id]))
            else:
                self.graph.add_node(
                    eid,
                    label       = e["label"],
                    type        = e.get("type", "Other"),
                    description = e.get("description", ""),
                    chunk_ids   = [chunk_id],
                    color       = NODE_COLORS.get(e.get("type", "Other"), "#64748b"),
                )

        for r in rels:
            fid, tid = r.get("from"), r.get("to")
            if fid in self.graph and tid in self.graph:
                self.graph.add_edge(
                    fid, tid,
                    type        = r.get("type", "RELATES_TO"),
                    description = r.get("description", ""),
                )

    # ── Full ingestion pipeline ───────────────────────────────────────────────

    def ingest(
        self,
        pdf_bytes: bytes,
        chunk_size: int = 400,
        progress_cb=None,   # optional callable(pct, msg)
        source_doc: str = "document",
    ) -> dict:
        """
        Master ingestion: PDF → chunks → entities → graph → embeddings.
        Returns stats dict.
        """
        # Reset in-memory state
        self.graph      = nx.DiGraph()
        self.chunks     = []
        self.embeddings = []
        self.chunk_meta = []

        _prog = progress_cb or (lambda p, m: None)

        # Clear Neo4j so new PDF replaces old data
        _prog(3, "Clearing previous data from Neo4j…")
        self._neo4j_clear()

        # 1 — Extract text
        _prog(5, "Extracting text from PDF…")
        pages = self.load_pdf(pdf_bytes)

        # 2 — Chunk
        _prog(10, "Chunking text…")
        chunk_dicts = self.chunk_pages(pages, chunk_size=chunk_size)
        self.chunks     = [c["text"] for c in chunk_dicts]
        self.chunk_meta = chunk_dicts

        # 3 — Entity extraction + graph building
        total = len(chunk_dicts)
        for i, cd in enumerate(chunk_dicts):
            pct = int(10 + 60 * (i / max(total, 1)))
            _prog(pct, f"Extracting entities — chunk {i+1}/{total}…")
            result   = self.extract_entities(cd["text"])
            entities = result.get("entities", [])
            rels     = result.get("relationships", [])
            self.add_to_graph(entities, rels, cd["id"])
            self._neo4j_push(entities, rels, cd["id"], source_doc=source_doc)

        # 4 — Embeddings
        _prog(75, "Computing embeddings…")
        self._embed_all()

        _prog(100, "Done!")
        return {
            "pages":    len(pages),
            "chunks":   len(self.chunks),
            "nodes":    self.graph.number_of_nodes(),
            "edges":    self.graph.number_of_edges(),
            "neo4j":    self.neo4j is not None,
        }

    # ── Embeddings ────────────────────────────────────────────────────────────

    def _get_st_model(self):
        if self._st_model is None:
            from sentence_transformers import SentenceTransformer
            self._st_model = SentenceTransformer("all-MiniLM-L6-v2")
        return self._st_model

    def _embed_all(self):
        model = self._get_st_model()
        arr   = model.encode(self.chunks, batch_size=32, show_progress_bar=False)
        self.embeddings = list(arr)

    def _cosine(self, a: np.ndarray, b: np.ndarray) -> float:
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))

    # ── Retrieval ─────────────────────────────────────────────────────────────

    def retrieve_chunks(self, query: str, top_k: int = 3) -> list[dict]:
        """Dense vector retrieval: return top-k chunks with similarity scores."""
        if not self.embeddings:
            return []
        model    = self._get_st_model()
        q_emb    = model.encode([query])[0]
        scores   = [self._cosine(q_emb, e) for e in self.embeddings]
        top_idxs = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        return [
            {**self.chunk_meta[i], "score": scores[i]}
            for i in top_idxs
        ]

    def get_graph_context(self, chunk_ids: list[int], max_nodes: int = 12) -> str:
        """Build a textual graph context from nodes linked to retrieved chunks."""
        relevant = [
            (nid, data)
            for nid, data in self.graph.nodes(data=True)
            if any(c in data.get("chunk_ids", []) for c in chunk_ids)
        ][:max_nodes]

        if not relevant:
            return ""

        lines = ["── Knowledge Graph Context ──"]
        for nid, data in relevant:
            lines.append(f"• [{data['type']}] {data['label']}: {data.get('description','')}")
            # Out-edges
            for _, target, edata in self.graph.out_edges(nid, data=True):
                tdata = self.graph.nodes.get(target, {})
                lines.append(f"    → {edata.get('type','RELATES')} → {tdata.get('label', target)}")
        return "\n".join(lines)

    # ── Generation ────────────────────────────────────────────────────────────

    def query(self, question: str, top_k: int = 3) -> dict:
        """Full RAG pipeline: retrieve → assemble context → generate → return."""
        if not self.chunks:
            return {
                "answer": "Please upload and process a PDF first.",
                "sources": [], "graph_nodes": 0,
            }

        # 1 — Vector retrieval
        top_chunks = self.retrieve_chunks(question, top_k=top_k)
        chunk_ids  = [c["id"] for c in top_chunks]

        # 2 — Graph context
        graph_ctx = self.get_graph_context(chunk_ids)

        # 3 — Assemble prompt context
        text_ctx = "\n\n---\n\n".join(
            f"[Page {c['page']}, score={c['score']:.2f}]\n{c['text']}"
            for c in top_chunks
        )

        system = (
            "You are a helpful assistant answering questions based on a provided document. "
            "Always ground your answer in the supplied context. "
            "If the answer is not in the context, say so clearly."
        )

        user_prompt = f"""{graph_ctx}

Document Excerpts:
{text_ctx}

Question: {question}

Answer concisely, citing page numbers where relevant."""

        resp = self.client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1200,
            system=system,
            messages=[{"role": "user", "content": user_prompt}],
        )

        return {
            "answer":      resp.content[0].text,
            "sources":     top_chunks,
            "graph_nodes": sum(
                1 for _, d in self.graph.nodes(data=True)
                if any(c in d.get("chunk_ids", []) for c in chunk_ids)
            ),
            "graph_ctx":   graph_ctx,
        }

    # ── Graph helpers for UI ──────────────────────────────────────────────────

    def graph_summary(self) -> dict:
        types = {}
        for _, d in self.graph.nodes(data=True):
            t = d.get("type", "Other")
            types[t] = types.get(t, 0) + 1
        return {
            "nodes":       self.graph.number_of_nodes(),
            "edges":       self.graph.number_of_edges(),
            "node_types":  types,
            "top_hubs":    sorted(
                [(n, self.graph.degree(n)) for n in self.graph.nodes()],
                key=lambda x: x[1], reverse=True
            )[:8],
        }

    def search_graph(self, term: str) -> list[dict]:
        """Return nodes whose label or description contains term."""
        term_lower = term.lower()
        return [
            {
                "id": nid,
                "label": d.get("label", nid),
                "type":  d.get("type", "Other"),
                "description": d.get("description", ""),
                "degree": self.graph.degree(nid),
            }
            for nid, d in self.graph.nodes(data=True)
            if term_lower in d.get("label", "").lower()
            or term_lower in d.get("description", "").lower()
        ]
