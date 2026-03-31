# 🕸️ KG-RAG — Knowledge Graph RAG

A simple, runnable Knowledge Graph + RAG system that turns any PDF into a
queryable knowledge graph using **Neo4j** (or in-memory NetworkX), **Claude Haiku**
for entity extraction and answer generation, and **sentence-transformers** for
local embeddings — all wrapped in a **Streamlit** UI.

---

## Architecture

```
PDF
 └─► PyPDF (text extraction)
      └─► Chunker (400-word overlapping windows)
           ├─► Claude Haiku (entity + relation extraction) ──► NetworkX graph
           │                                                └──► Neo4j (optional)
           └─► sentence-transformers (all-MiniLM-L6-v2)  ──► in-memory embeddings

Query
 └─► sentence-transformers (embed query)
      ├─► Cosine similarity → top-k chunks
      ├─► Graph context (nodes linked to top-k chunk ids)
      └─► Claude Haiku (generate answer with citations)
```

---

## Quick Start

### 1. Clone / copy files

```
kg-rag/
├── app.py             # Streamlit UI
├── kg_rag.py          # Core engine
├── requirements.txt
└── README.md
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

> **Note:** `sentence-transformers` downloads ~90 MB of model weights on first run.
> Subsequent runs use the cached model.

### 3. (Optional) Start Neo4j

**Docker (easiest):**
```bash
docker run -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  --name neo4j-kg \
  neo4j:5
```
Then open http://localhost:7474 to verify.

**Neo4j Desktop:** Download from https://neo4j.com/download/ and create a local DB.

If you skip Neo4j, the app uses **NetworkX in-memory graph** — everything still works.

### 4. Run the app

```bash
streamlit run app.py
```

Opens at http://localhost:8501

---

## Usage

1. **Enter your Anthropic API key** in the sidebar
   - Get one at https://console.anthropic.com
   - Uses Claude Haiku (cheap — ~$0.25/M input tokens)

2. **(Optional) Configure Neo4j** — check "Enable Neo4j" and fill URI/user/pass

3. **Upload a PDF** — any PDF: Basel 3 NPR, research paper, contract, policy doc

4. **Click "Process PDF"** — ingestion takes ~30 sec for a 20-page doc
   - Larger PDFs scale linearly; reduce chunk size to speed up

5. **Ask questions** in the Chat tab

6. **Explore the graph** in the Graph Explorer tab

7. **Run Cypher queries** in the Neo4j tab (if connected)

---

## What Claude Haiku extracts

For each ~400-word chunk, Claude extracts:

**Entities** with types:
- `Person` — named individuals
- `Organization` — companies, agencies, institutions
- `Concept` — abstract ideas, frameworks, methods
- `Rule` — regulations, requirements, provisions
- `Location` — geographic references
- `Event` — dates, milestones, occurrences

**Relationships** as directed edges:
- `DEFINES`, `APPLIES_TO`, `REQUIRES`, `GOVERNS`, `REFERENCES`, `PART_OF`, `CREATED_BY`, etc.

---

## File Reference

| File | Purpose |
|------|---------|
| `app.py` | Streamlit UI: Chat, Graph Explorer, Entity browser, Neo4j Cypher |
| `kg_rag.py` | Core engine: ingestion, entity extraction, graph building, RAG query |
| `requirements.txt` | Python dependencies |

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `ImportError: sentence_transformers` | `pip install sentence-transformers` |
| `ImportError: pyvis` | `pip install pyvis` |
| Neo4j connection refused | Make sure Docker is running; check port 7687 |
| Claude API error | Verify API key; check console.anthropic.com for quota |
| Graph shows nothing | Ingestion may have failed silently; re-process the PDF |
| Slow on large PDFs | Reduce chunk_size slider; fewer API calls = faster |

---

## Estimated API Cost

Using Claude Haiku (claude-haiku-4-5-20251001):
- Input: ~$0.25 / 1M tokens
- Output: ~$1.25 / 1M tokens

A 50-page PDF ≈ ~100 chunks × ~600 tokens each = ~60K tokens input ≈ **~$0.015**
Each query ≈ ~2K tokens = **~$0.0005**

Total for typical usage: **< $0.10**

---

## Extending this project

- **Better embeddings:** Swap `all-MiniLM-L6-v2` for `text-embedding-3-large` (OpenAI) or `nomic-embed-text` (local)
- **BM25 retrieval:** Add `rank_bm25` for keyword matching alongside dense vectors
- **LangChain GraphCypherQAChain:** Auto-generate Cypher from natural language questions
- **Multiple PDFs:** Extend `ingest()` to accept a list; add `source_doc` node property
- **ChromaDB:** Replace in-memory numpy with ChromaDB for persistence across restarts
