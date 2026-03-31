"""
app.py — Knowledge Graph RAG · Streamlit Application
Run: streamlit run app.py
"""

import streamlit as st
import json
import networkx as nx

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title   = "KG-RAG · Basel 3 NPR",
    page_icon    = "🕸️",
    layout       = "wide",
    initial_sidebar_state = "expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Syne:wght@700;800&display=swap');

  html, body, [class*="css"] { font-family: 'IBM Plex Mono', monospace; }
  .main { background: #05080f; }

  /* Chat bubbles */
  .user-msg   { background:#0d1b2a; border:1px solid #1e3a5f; border-radius:8px; padding:12px 16px; margin:8px 0; }
  .assist-msg { background:#0a1a0a; border:1px solid #1e3f1e; border-radius:8px; padding:12px 16px; margin:8px 0; }

  /* Metric cards */
  div[data-testid="metric-container"] {
    background:#0d1b2a; border:1px solid #1e3a5f;
    border-radius:8px; padding:12px;
  }

  /* Source chips */
  .source-chip {
    display:inline-block; font-size:11px;
    background:#0d1b2a; border:1px solid #1e3a5f;
    border-radius:4px; padding:4px 8px; margin:3px;
    color:#6a9abb;
  }

  /* Entity badges */
  .badge-Person       { background:#f43f5e20; color:#f43f5e; border:1px solid #f43f5e40; }
  .badge-Organization { background:#4a9eff20; color:#4a9eff; border:1px solid #4a9eff40; }
  .badge-Concept      { background:#10b98120; color:#10b981; border:1px solid #10b98140; }
  .badge-Rule         { background:#f5a62320; color:#f5a623; border:1px solid #f5a62340; }
  .badge-Location     { background:#7c3aed20; color:#a78bfa; border:1px solid #7c3aed40; }
  .badge-Event        { background:#fb923c20; color:#fb923c; border:1px solid #fb923c40; }
  .badge-Other        { background:#64748b20; color:#94a3b8; border:1px solid #64748b40; }
  .badge { font-size:10px; padding:2px 7px; border-radius:3px; margin:2px; display:inline-block; }
</style>
""", unsafe_allow_html=True)


# ── Session state bootstrap ───────────────────────────────────────────────────
for key, default in {
    "rag":          None,
    "stats":        None,
    "chat_history": [],
    "ingested":     False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


# ── Helper: build pyvis HTML ──────────────────────────────────────────────────
def build_graph_html(G, highlight_ids: list = None) -> str:
    """Render NetworkX graph as interactive pyvis HTML string."""
    try:
        from pyvis.network import Network
    except ImportError:
        return "<p style='color:#f43f5e'>Install pyvis: pip install pyvis</p>"

    highlight_ids = set(highlight_ids or [])
    net = Network(
        height="520px", width="100%",
        bgcolor="#05080f", font_color="#c8ddf0",
        directed=True,
    )
    net.barnes_hut(gravity=-5000, central_gravity=0.3, spring_length=120)

    COLOR_MAP = {
        "Person":       "#f43f5e", "Organization": "#4a9eff",
        "Concept":      "#10b981", "Rule":         "#f5a623",
        "Location":     "#7c3aed", "Event":        "#fb923c",
        "Other":        "#64748b",
    }

    for nid, data in G.nodes(data=True):
        color = COLOR_MAP.get(data.get("type", "Other"), "#64748b")
        size  = 20 + G.degree(nid) * 4
        border = "#ffffff" if nid in highlight_ids else color
        net.add_node(
            nid,
            label   = data.get("label", nid)[:24],
            title   = f"<b>{data.get('label',nid)}</b><br>{data.get('type','?')}<br>{data.get('description','')}",
            color   = {"background": color, "border": border},
            size    = min(size, 50),
            font    = {"size": 11, "color": "#e0f0ff"},
        )

    for src, dst, edata in G.edges(data=True):
        net.add_edge(
            src, dst,
            title  = edata.get("description", ""),
            label  = edata.get("type", ""),
            color  = "#2a4060",
            font   = {"size": 9, "color": "#5a7a9a"},
            arrows = "to",
        )

    # Inject custom CSS into the generated HTML
    html = net.generate_html()
    html = html.replace(
        "<body>",
        "<body style='background:#05080f;margin:0;padding:0;'>"
    )
    return html


# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### 🕸️ KG-RAG Setup")
    st.markdown("---")

    # API key
    api_key = st.text_input(
        "Anthropic API Key",
        type="password",
        placeholder="sk-ant-…",
        help="Get yours at console.anthropic.com",
    )

    # Neo4j config
    with st.expander("🔷 Neo4j Config (optional)", expanded=False):
        neo4j_uri  = st.text_input("URI",      value="bolt://localhost:7687")
        neo4j_user = st.text_input("Username", value="neo4j")
        neo4j_pass = st.text_input("Password", type="password")
        neo4j_enabled = st.checkbox("Enable Neo4j", value=False)

    st.markdown("---")

    # PDF upload
    st.markdown("### 📄 Upload PDF")
    uploaded = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"],
        help="Upload any PDF — Basel 3 NPR, research paper, policy document…",
    )

    chunk_size = st.slider("Chunk size (words)", 200, 800, 400, step=50,
                           help="Larger = more context per chunk; smaller = more precise retrieval")

    # Ingest button
    if st.button("⚡ Process PDF", type="primary", use_container_width=True,
                 disabled=not (uploaded and api_key)):
        from kg_rag import KnowledgeGraphRAG

        neo4j_cfg = None
        if neo4j_enabled and neo4j_uri:
            neo4j_cfg = {"uri": neo4j_uri, "username": neo4j_user, "password": neo4j_pass}

        rag = KnowledgeGraphRAG(api_key=api_key, neo4j_cfg=neo4j_cfg)

        progress_bar = st.progress(0)
        status_text  = st.empty()

        def update_progress(pct, msg):
            progress_bar.progress(pct)
            status_text.text(msg)

        try:
            stats = rag.ingest(
                uploaded.getvalue(),
                chunk_size  = chunk_size,
                progress_cb = update_progress,
                source_doc  = uploaded.name,   # ← pass filename
            )
            st.session_state.rag       = rag
            st.session_state.stats     = stats
            st.session_state.ingested  = True
            st.session_state.chat_history = []
            st.success("✅ PDF processed!")
        except Exception as exc:
            st.error(f"Error: {exc}")

    # Stats panel
    if st.session_state.ingested and st.session_state.stats:
        s = st.session_state.stats
        st.markdown("---")
        st.markdown("### 📊 Corpus Stats")
        col1, col2 = st.columns(2)
        col1.metric("Pages",  s["pages"])
        col2.metric("Chunks", s["chunks"])
        col1.metric("Nodes",  s["nodes"])
        col2.metric("Edges",  s["edges"])
        if s["neo4j"]:
            st.success("Neo4j: connected ✓")
        else:
            st.info("Neo4j: using in-memory graph")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN AREA
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown(
    "<h2 style='font-family:Syne,sans-serif;font-weight:800;color:#e0f0ff;margin-bottom:4px'>"
    "🕸️ Knowledge Graph RAG</h2>"
    "<p style='color:#5a7a9a;font-size:12px;margin-bottom:16px'>"
    "PDF → Entity Extraction → Knowledge Graph + Vector Retrieval → Cited Answers"
    "</p>",
    unsafe_allow_html=True,
)

if not st.session_state.ingested:
    st.info("👈 Upload a PDF and click **Process PDF** to get started.")
    st.markdown("""
    **What this does:**
    1. Extracts text from your PDF and splits it into overlapping chunks
    2. Uses **Claude Haiku** to extract entities and relationships from each chunk
    3. Builds a **NetworkX in-memory knowledge graph** (and optionally syncs to **Neo4j**)
    4. Embeds chunks with **sentence-transformers** (all-MiniLM-L6-v2, runs locally)
    5. On each question: hybrid graph + vector retrieval → **Claude Haiku** generates a cited answer
    """)
    st.stop()


# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_chat, tab_graph, tab_entities, tab_neo4j = st.tabs([
    "💬 Chat", "🕸️ Graph Explorer", "🔍 Entities & Chunks", "🔷 Neo4j Cypher"
])


# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — CHAT
# ─────────────────────────────────────────────────────────────────────────────
with tab_chat:
    rag = st.session_state.rag

    # Display history
    for turn in st.session_state.chat_history:
        with st.container():
            st.markdown(
                f"<div class='user-msg'>🧑 <b>You:</b> {turn['question']}</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div class='assist-msg'>🤖 <b>Assistant:</b><br>{turn['answer']}</div>",
                unsafe_allow_html=True,
            )
            # Sources
            if turn.get("sources"):
                chips = "".join(
                    f"<span class='source-chip'>📄 Page {s['page']} · score {s['score']:.2f}</span>"
                    for s in turn["sources"]
                )
                st.markdown(f"<div style='margin:4px 0 12px'>{chips}</div>", unsafe_allow_html=True)
            # Graph nodes used
            if turn.get("graph_nodes", 0) > 0:
                st.caption(f"🕸️ {turn['graph_nodes']} graph node(s) contributed to this answer")

    # Input
    col_q, col_btn = st.columns([5, 1])
    with col_q:
        question = st.text_input(
            "Ask a question about your document…",
            key="question_input",
            placeholder="e.g. What are the main risk weights defined in this document?",
            label_visibility="collapsed",
        )
    with col_btn:
        ask = st.button("Ask →", type="primary", use_container_width=True)

    if ask and question.strip():
        with st.spinner("Retrieving and generating…"):
            result = rag.query(question.strip())

        st.session_state.chat_history.append({
            "question":    question.strip(),
            "answer":      result["answer"],
            "sources":     result["sources"],
            "graph_nodes": result["graph_nodes"],
        })
        st.rerun()

    if st.session_state.chat_history:
        if st.button("🗑️ Clear chat", use_container_width=False):
            st.session_state.chat_history = []
            st.rerun()

    # Example questions
    with st.expander("💡 Example questions"):
        examples = [
            "What are the main topics covered in this document?",
            "Who are the key entities mentioned?",
            "What are the most important rules or requirements?",
            "Summarise the key thresholds or numeric values.",
            "What relationships exist between the main concepts?",
        ]
        for q in examples:
            if st.button(q, key=f"ex_{q[:20]}", use_container_width=True):
                with st.spinner("Generating…"):
                    result = rag.query(q)
                st.session_state.chat_history.append({
                    "question":    q,
                    "answer":      result["answer"],
                    "sources":     result["sources"],
                    "graph_nodes": result["graph_nodes"],
                })
                st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — GRAPH EXPLORER
# ─────────────────────────────────────────────────────────────────────────────
with tab_graph:
    rag  = st.session_state.rag
    G    = rag.graph
    summ = rag.graph_summary()

    # Summary metrics
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Nodes", summ["nodes"])
    c2.metric("Total Edges", summ["edges"])
    c3.metric("Entity Types", len(summ["node_types"]))
    c4.metric("Connected?", "Yes" if nx.is_weakly_connected(G) else "No" if G.number_of_nodes() else "—")

    # Node type breakdown
    st.markdown("**Entity type distribution**")
    type_cols = st.columns(len(summ["node_types"]) or 1)
    colors = {"Person":"#f43f5e","Organization":"#4a9eff","Concept":"#10b981",
               "Rule":"#f5a623","Location":"#7c3aed","Event":"#fb923c","Other":"#64748b"}
    for i, (etype, count) in enumerate(summ["node_types"].items()):
        clr = colors.get(etype, "#888")
        type_cols[i % len(type_cols)].markdown(
            f"<span class='badge badge-{etype}'>{etype}</span> **{count}**",
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # Search + filter
    col_search, col_filter = st.columns([3, 1])
    with col_search:
        search_term = st.text_input("🔍 Search nodes", placeholder="Type an entity name…", label_visibility="collapsed")
    with col_filter:
        filter_type = st.selectbox("Filter type", ["All"] + list(summ["node_types"].keys()),
                                   label_visibility="collapsed")

    # Build subgraph for display
    if search_term:
        matched = rag.search_graph(search_term)
        highlight_ids = [m["id"] for m in matched]
        if highlight_ids:
            # Show 2-hop neighbourhood around matches
            neighbours = set(highlight_ids)
            for nid in highlight_ids:
                neighbours |= set(G.predecessors(nid)) | set(G.successors(nid))
            sub = G.subgraph(neighbours)
            st.info(f"Showing {len(sub)} nodes around '{search_term}'")
        else:
            sub = G
            highlight_ids = []
            st.warning(f"No nodes matched '{search_term}'")
    elif filter_type != "All":
        sub_nodes = [n for n, d in G.nodes(data=True) if d.get("type") == filter_type]
        sub = G.subgraph(sub_nodes)
        highlight_ids = sub_nodes
    else:
        # Limit to top 80 nodes by degree for readability
        top_nodes = sorted(G.nodes(), key=lambda n: G.degree(n), reverse=True)[:80]
        sub = G.subgraph(top_nodes)
        highlight_ids = []

    # Render graph
    if sub.number_of_nodes() == 0:
        st.warning("No nodes to display with current filter.")
    else:
        graph_html = build_graph_html(sub, highlight_ids)
        import streamlit.components.v1 as components
        components.html(graph_html, height=540, scrolling=False)

    # Top hubs table
    st.markdown("**Top hub nodes (by degree)**")
    hub_rows = []
    for nid, deg in summ["top_hubs"]:
        d = G.nodes.get(nid, {})
        hub_rows.append({
            "Node": d.get("label", nid),
            "Type": d.get("type", "?"),
            "Degree": deg,
            "Description": (d.get("description", "") or "")[:80],
        })
    if hub_rows:
        import pandas as pd
        st.dataframe(pd.DataFrame(hub_rows), hide_index=True, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — ENTITIES & CHUNKS
# ─────────────────────────────────────────────────────────────────────────────
with tab_entities:
    rag = st.session_state.rag
    G   = rag.graph

    left, right = st.columns([1, 1])

    # Left: all entities
    with left:
        st.markdown("**All extracted entities**")
        rows = []
        for nid, data in G.nodes(data=True):
            rows.append({
                "Label":       data.get("label", nid),
                "Type":        data.get("type", "Other"),
                "Description": (data.get("description") or "")[:70],
                "Connections": G.degree(nid),
            })
        if rows:
            import pandas as pd
            rows.sort(key=lambda r: r["Connections"], reverse=True)
            st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True, height=350)

    # Right: all relationships
    with right:
        st.markdown("**All extracted relationships**")
        rel_rows = []
        for src, dst, edata in G.edges(data=True):
            src_d = G.nodes.get(src, {})
            dst_d = G.nodes.get(dst, {})
            rel_rows.append({
                "From":         src_d.get("label", src)[:25],
                "Relationship": edata.get("type", "RELATES"),
                "To":           dst_d.get("label", dst)[:25],
            })
        if rel_rows:
            st.dataframe(pd.DataFrame(rel_rows), hide_index=True, use_container_width=True, height=350)

    st.markdown("---")

    # Chunk browser
    st.markdown("**Chunk browser**")
    chunk_page = st.number_input(
        "Jump to chunk #",
        min_value=1, max_value=max(len(rag.chunk_meta), 1), value=1, step=1,
    )
    if rag.chunk_meta:
        cm = rag.chunk_meta[chunk_page - 1]
        st.markdown(
            f"**Chunk {cm['id']+1} / {len(rag.chunk_meta)}** — Page {cm['page']}",
        )
        st.text_area("Text", cm["text"], height=200, label_visibility="collapsed")

        # Entities in this chunk
        chunk_ents = [
            (nid, d) for nid, d in G.nodes(data=True)
            if cm["id"] in d.get("chunk_ids", [])
        ]
        if chunk_ents:
            badge_parts = []
            for nid, d in chunk_ents:
                etype = d.get("type", "Other")
                elabel = d.get("label", nid)
                badge_parts.append(
                    f"<span class='badge badge-{etype}'>{elabel}</span>"
                )
            badges = " ".join(badge_parts)
            st.markdown(f"Entities in this chunk: {badges}", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 4 — NEO4J CYPHER
# ─────────────────────────────────────────────────────────────────────────────
with tab_neo4j:
    rag = st.session_state.rag

    if not rag.neo4j:
        st.warning(
            "Neo4j is not connected. Enable it in the sidebar with your bolt:// URI, "
            "username, and password, then re-process the PDF."
        )
        st.markdown("**Quick start with Neo4j Desktop / Docker:**")
        st.code(
            "# Docker\n"
            "docker run -p 7474:7474 -p 7687:7687 \\\n"
            "  -e NEO4J_AUTH=neo4j/password \\\n"
            "  neo4j:5\n\n"
            "# Then set URI=bolt://localhost:7687, user=neo4j, pass=password",
            language="bash",
        )
    else:
        st.success("✅ Neo4j connected")

        # Preset queries
        preset = st.selectbox("Preset queries", [
            "MATCH (n:Entity) RETURN n.label, n.type, n.description LIMIT 20",
            "MATCH (a)-[r:RELATES]->(b) RETURN a.label, r.type, b.label LIMIT 20",
            "MATCH (n:Entity) RETURN n.type, count(*) AS count ORDER BY count DESC",
            "MATCH (n:Entity {type: 'Concept'}) RETURN n.label, n.description LIMIT 15",
            "MATCH (n:Entity)-[r]->(m:Entity) WHERE n.label CONTAINS $term RETURN n,r,m LIMIT 10",
        ])

        cypher = st.text_area("Cypher query", value=preset, height=100)

        if st.button("▶️ Run Cypher", type="primary"):
            with st.spinner("Querying Neo4j…"):
                try:
                    results = rag.neo4j_cypher(cypher)
                    if results:
                        import pandas as pd
                        st.dataframe(pd.DataFrame(results), use_container_width=True)
                        st.caption(f"{len(results)} rows returned")
                    else:
                        st.info("Query returned no results.")
                except Exception as exc:
                    st.error(f"Cypher error: {exc}")

        st.markdown("---")
        st.markdown("**Sample Cypher patterns**")
        st.code("""
// All entities and their types
MATCH (n:Entity) RETURN n.label, n.type ORDER BY n.type

// Find connected concepts
MATCH (a:Entity)-[r:RELATES]->(b:Entity)
WHERE a.type = 'Concept'
RETURN a.label, r.type, b.label LIMIT 20

// Hub nodes (most connections)
MATCH (n:Entity)-[r]-()
RETURN n.label, count(r) AS degree
ORDER BY degree DESC LIMIT 10

// Entities from a specific page
MATCH (n:Entity) WHERE n.chunk_id IN [0,1,2]
RETURN n.label, n.type, n.description

// Path between two entities
MATCH p = shortestPath(
  (a:Entity {label:'EntityA'})-[*]-(b:Entity {label:'EntityB'})
)
RETURN p
        """, language="cypher")
