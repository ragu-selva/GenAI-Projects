"""
UI Components for Basel III RAG Chatbot
"""
import streamlit as st
import tempfile
import os
from pathlib import Path


def render_sidebar():
    """Render the full sidebar with config and document upload."""
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-logo">
          <span class="sidebar-logo-icon">🏦</span>
          <span class="sidebar-logo-text">Basel III Advisor</span>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        # ── API Key ─────────────────────────────────────────────────────────
        st.markdown("### 🔑 OpenAI API Key")
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            value=st.session_state.get("openai_api_key", ""),
            placeholder="sk-...",
            label_visibility="collapsed",
        )
        if api_key:
            st.session_state.openai_api_key = api_key

        st.divider()

        # ── Knowledge Base ───────────────────────────────────────────────────
        st.markdown("### 📚 Knowledge Base")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🏛️ Load Demo", use_container_width=True, type="primary"):
                if not st.session_state.get("openai_api_key"):
                    st.error("Please enter your OpenAI API key first.")
                else:
                    with st.spinner("Building knowledge base..."):
                        try:
                            from rag_engine import Basel3RAGEngine
                            engine = Basel3RAGEngine(st.session_state.openai_api_key)
                            n = engine.load_demo_corpus()
                            st.session_state.rag_engine = engine
                            st.session_state.vectorstore_ready = True
                            st.success(f"✅ {n} chunks indexed!")
                        except Exception as e:
                            st.error(f"Error: {e}")

        with col2:
            if st.button("🗑️ Reset", use_container_width=True):
                st.session_state.rag_engine = None
                st.session_state.vectorstore_ready = False
                st.session_state.messages = []
                st.session_state.last_sources = []
                st.rerun()

        # File uploader
        uploaded_files = st.file_uploader(
            "Upload Basel III Documents",
            type=["pdf", "txt", "docx", "html"],
            accept_multiple_files=True,
            help="Upload PDF, TXT, DOCX or HTML regulatory documents",
        )

        merge_demo = st.checkbox(
            "Merge with demo corpus",
            value=False,
            help="OFF = only your uploaded files are searched (recommended). "
                 "ON = uploaded files + built-in Basel III demo corpus combined.",
        )

        if uploaded_files and st.button("⬆️ Index Uploaded Files", use_container_width=True):
            if not st.session_state.get("openai_api_key"):
                st.error("Please enter your OpenAI API key first.")
            else:
                with st.spinner(f"Processing {len(uploaded_files)} file(s)..."):
                    try:
                        from rag_engine import Basel3RAGEngine
                        # Always create a fresh engine so no stale demo corpus leaks in
                        engine = Basel3RAGEngine(st.session_state.openai_api_key)
                        if merge_demo:
                            # Pre-load demo corpus first, then merge uploaded files
                            engine.load_demo_corpus()

                        tmp_paths = []
                        for uf in uploaded_files:
                            suffix = Path(uf.name).suffix
                            with tempfile.NamedTemporaryFile(
                                delete=False, suffix=suffix, mode="wb"
                            ) as tmp:
                                tmp.write(uf.read())
                                tmp_paths.append(tmp.name)

                        n = engine.load_documents(tmp_paths, merge_with_existing=merge_demo)
                        for p in tmp_paths:
                            os.unlink(p)

                        st.session_state.rag_engine = engine
                        st.session_state.vectorstore_ready = True
                        mode_label = "merged with demo corpus" if merge_demo else "isolated (PDF only)"
                        st.success(f"✅ {n} chunks indexed — {mode_label}")
                    except Exception as e:
                        st.error(f"Error: {e}")

        st.divider()

        # ── Retrieval Settings ───────────────────────────────────────────────
        st.markdown("### ⚙️ Retrieval Settings")

        st.session_state.retrieval_mode = st.selectbox(
            "Retrieval Mode",
            options=["hybrid", "dense", "sparse", "multi_query"],
            index=0,
            format_func=lambda x: {
                "hybrid": "🔀 Hybrid (Dense + BM25)",
                "dense": "🧠 Dense (Semantic)",
                "sparse": "📝 Sparse (BM25 Keyword)",
                "multi_query": "🔍 Multi-Query Expansion",
            }[x],
        )

        st.session_state.top_k = st.slider(
            "Top-K Chunks",
            min_value=2,
            max_value=10,
            value=5,
            help="Number of context chunks to retrieve",
        )

        # Mode description
        mode_info = {
            "hybrid": "Combines semantic and keyword search for best coverage.",
            "dense": "Pure embedding-based semantic similarity search.",
            "sparse": "BM25 keyword matching — good for exact regulatory terms.",
            "multi_query": "Generates multiple query variants for broader recall.",
        }
        st.info(mode_info[st.session_state.retrieval_mode])

        st.divider()

        # ── Quick Questions ──────────────────────────────────────────────────
        st.markdown("### 💡 Quick Questions")
        quick_qs = [
            "What is the minimum CET1 ratio?",
            "Explain the LCR formula and HQLA",
            "What is the NSFR and its minimum?",
            "How is the leverage ratio calculated?",
            "What are FRTB risk charges?",
            "Explain Pillar 2 ICAAP requirements",
            "What is the G-SIB surcharge?",
            "Describe operational risk SA-OR",
        ]
        for q in quick_qs:
            if st.button(q, use_container_width=True, key=f"qq_{q[:20]}"):
                if st.session_state.vectorstore_ready:
                    st.session_state.messages.append({"role": "user", "content": q})
                    with st.spinner("Retrieving..."):
                        try:
                            result = st.session_state.rag_engine.query(
                                question=q,
                                retrieval_mode=st.session_state.retrieval_mode,
                                top_k=st.session_state.top_k,
                            )
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": result["answer"],
                                "sources": result.get("sources", []),
                                "metadata": result.get("metadata", {}),
                            })
                            st.session_state.last_sources = result.get("sources", [])
                        except Exception as e:
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": f"Error: {e}",
                                "sources": [],
                            })
                    st.rerun()
                else:
                    st.warning("Load the knowledge base first.")

        st.divider()

        # ── Conversation controls ────────────────────────────────────────────
        st.markdown("### 💬 Conversation")
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.last_sources = []
            st.rerun()

        # Stats
        if st.session_state.vectorstore_ready and st.session_state.rag_engine:
            n_docs = len(st.session_state.rag_engine.docs)
            st.markdown(f"""
            <div class="stats-box">
              <div class="stat-item">
                <span class="stat-label">Chunks indexed</span>
                <span class="stat-value">{n_docs}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">Messages</span>
                <span class="stat-value">{len(st.session_state.messages)}</span>
              </div>
            </div>
            """, unsafe_allow_html=True)


def render_chat_message(msg: dict):
    """Render a single chat message."""
    role = msg["role"]
    content = msg["content"]

    if role == "user":
        st.markdown(f"""
        <div class="chat-message user-message">
          <div class="message-avatar user-avatar">You</div>
          <div class="message-bubble user-bubble">{content}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        sources = msg.get("sources", [])
        meta = msg.get("metadata", {})
        mode_badge = ""
        if meta.get("retrieval_mode"):
            mode_labels = {
                "hybrid": "Hybrid", "dense": "Dense",
                "sparse": "BM25", "multi_query": "Multi-Query"
            }
            label = mode_labels.get(meta["retrieval_mode"], meta["retrieval_mode"])
            chunks = meta.get("chunks_retrieved", "")

            confidence = meta.get("confidence", "")
            conf_colours = {"HIGH": "#22c55e", "MEDIUM": "#f59e0b", "LOW": "#ef4444"}
            conf_html = ""
            if confidence:
                colour = conf_colours.get(confidence, "#888")
                avg = meta.get("avg_score", "")
                conf_html = (
                    f'<span class="meta-badge" style="border-color:{colour};color:{colour};">'
                    f'{confidence} confidence · score {avg}</span>'
                )

            mode_badge = (
                f'<span class="meta-badge">{label} · {chunks} chunks</span>'
                + conf_html
            )

        # Format content with basic markdown-like rendering
        formatted = content.replace("\n\n", "</p><p>").replace("\n", "<br>")
        formatted = f"<p>{formatted}</p>"

        src_html = ""
        if sources:
            src_items = "".join([
                f'<span class="src-tag">📄 {s["source"]}</span>'
                for s in sources[:3]
            ])
            src_html = f'<div class="source-tags">{src_items}</div>'

        st.markdown(f"""
        <div class="chat-message assistant-message">
          <div class="message-avatar assistant-avatar">AI</div>
          <div class="message-bubble assistant-bubble">
            {mode_badge}
            <div class="message-content">{formatted}</div>
            {src_html}
          </div>
        </div>
        """, unsafe_allow_html=True)


def render_sources_panel(sources: list[dict]):
    """Render the sources / evidence panel."""
    st.markdown("""
    <div class="sources-panel-header">
      <span class="sources-icon">📋</span>
      <span class="sources-title">Evidence Sources</span>
    </div>
    """, unsafe_allow_html=True)

    if not sources:
        st.markdown("""
        <div class="sources-empty">
          <div style="font-size:2rem; margin-bottom:.5rem;">📑</div>
          <div>Sources will appear here after your first query.</div>
        </div>
        """, unsafe_allow_html=True)
        return

    for i, src in enumerate(sources, 1):
        section = f" · {src['section']}" if src.get("section") else ""
        page = f" · p.{src['page']}" if src.get("page") else ""
        with st.expander(f"[{i}] {src['source']}{section}{page}"):
            st.markdown(f"""
            <div class="source-snippet">
              <div class="source-label">📌 Excerpt</div>
              <div class="source-text">{src.get('snippet', '')}</div>
            </div>
            """, unsafe_allow_html=True)
