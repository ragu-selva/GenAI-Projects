import os
import sys

# Force UTF-8 globally — prevents charmap errors on Windows
os.environ.setdefault("PYTHONUTF8", "1")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

import streamlit as st
import os
import time
from pathlib import Path
from rag_engine import Basel3RAGEngine
from ui_components import render_sidebar, render_chat_message, render_sources_panel

# ── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Basel III RAG Advisor",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Load CSS ─────────────────────────────────────────────────────────────────
css_path = Path(__file__).parent / "style.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "rag_engine" not in st.session_state:
    st.session_state.rag_engine = None
if "vectorstore_ready" not in st.session_state:
    st.session_state.vectorstore_ready = False
if "last_sources" not in st.session_state:
    st.session_state.last_sources = []
if "retrieval_mode" not in st.session_state:
    st.session_state.retrieval_mode = "hybrid"
if "top_k" not in st.session_state:
    st.session_state.top_k = 5
if "last_context_data" not in st.session_state:
    st.session_state.last_context_data = None


# ── Sidebar ───────────────────────────────────────────────────────────────────
render_sidebar()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-container">
  <div class="header-badge">Basel III · Regulatory Intelligence</div>
  <h1 class="main-title">Basel III RAG Advisor</h1>
  <p class="subtitle">Advanced Retrieval-Augmented Generation for Capital Adequacy & Risk Reporting</p>
</div>
""", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_chat, tab_explorer, tab_context = st.tabs(["💬 Chat", "🗄️ Chunk Explorer", "🔍 Context Analyzer"])

# ── Layout: chat + sources ─────────────────────────────────────────────────────
with tab_chat:
 col_chat, col_sources = st.columns([2, 1])

 with col_chat:
     # Status banner
     if not st.session_state.vectorstore_ready:
         st.markdown("""
         <div class="status-banner warning">
           <span class="status-icon">⚠️</span>
           <span>Upload Basel III documents or load the demo corpus from the sidebar to begin.</span>
         </div>
         """, unsafe_allow_html=True)
     else:
         st.markdown("""
         <div class="status-banner success">
           <span class="status-icon">✅</span>
           <span>Knowledge base ready — ask any Basel III regulatory question.</span>
         </div>
         """, unsafe_allow_html=True)

     # Chat history
     chat_container = st.container()
     with chat_container:
         if not st.session_state.messages:
             st.markdown("""
             <div class="empty-state">
               <div class="empty-icon">🏛️</div>
               <div class="empty-title">Basel III Intelligence Ready</div>
               <div class="empty-body">
                 Ask about Capital Adequacy Ratios, Liquidity Coverage Ratios,
                 NSFR, Leverage Ratios, Credit Risk, Market Risk, or Operational Risk.
               </div>
             </div>
             """, unsafe_allow_html=True)
         else:
             for msg in st.session_state.messages:
                 render_chat_message(msg)

     # Input
     if prompt := st.chat_input(
         "Ask about Basel III — e.g. 'What is the minimum CET1 ratio?'",
         disabled=not st.session_state.vectorstore_ready
     ):
         st.session_state.messages.append({"role": "user", "content": prompt})
         with st.spinner("Retrieving regulatory context..."):
             try:
                 result = st.session_state.rag_engine.query(
                     question=prompt,
                     retrieval_mode=st.session_state.retrieval_mode,
                     top_k=st.session_state.top_k,
                 )
                 answer = result["answer"]
                 sources = result.get("sources", [])
                 metadata = result.get("metadata", {})
                 st.session_state.messages.append({
                     "role": "assistant",
                     "content": answer,
                     "sources": sources,
                     "metadata": metadata,
                 })
                 st.session_state.last_sources = sources
                 st.session_state.last_context_data = result.get('context_data')
             except Exception as e:
                 st.session_state.messages.append({
                     "role": "assistant",
                     "content": f"❌ Error: {str(e)}",
                     "sources": [],
                 })
         st.rerun()

 with col_sources:
     render_sources_panel(st.session_state.last_sources)

# ── Chunk Explorer Tab ─────────────────────────────────────────────────────────
with tab_explorer:
    if not st.session_state.vectorstore_ready:
        st.info("Load documents first to explore chunks.")
    else:
        engine = st.session_state.rag_engine
        docs = engine.docs
        total = len(docs)

        # ── Stats row ──
        sources_list = list({d.metadata.get("source", "Unknown") for d in docs})
        sections_list = list({d.metadata.get("section", "") for d in docs if d.metadata.get("section")})
        avg_len = int(sum(len(d.page_content) for d in docs) / max(total, 1))

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total chunks", f"{total:,}")
        c2.metric("Unique sources", len(sources_list))
        c3.metric("Sections", len(sections_list))
        c4.metric("Avg chunk length", f"{avg_len} chars")

        st.divider()

        # ── Filters ──
        fc1, fc2, fc3 = st.columns([2, 2, 1])
        with fc1:
            search_term = st.text_input("Search inside chunks", placeholder="e.g. CET1, 4.5%, LCR...")
        with fc2:
            source_options = ["All sources"] + sorted(sources_list)
            selected_source = st.selectbox("Filter by source", source_options)
        with fc3:
            page_size = st.selectbox("Per page", [10, 25, 50], index=0)

        # ── Filter logic ──
        filtered = docs
        if selected_source != "All sources":
            filtered = [d for d in filtered if d.metadata.get("source") == selected_source]
        if search_term.strip():
            term = search_term.strip().lower()
            filtered = [d for d in filtered if term in d.page_content.lower()]

        st.caption(f"Showing **{len(filtered):,}** of **{total:,}** chunks")

        # ── Pagination ──
        total_pages = max(1, (len(filtered) + page_size - 1) // page_size)
        if "explorer_page" not in st.session_state:
            st.session_state.explorer_page = 0
        # Reset page on filter change
        if st.session_state.get("last_search") != search_term or st.session_state.get("last_source") != selected_source:
            st.session_state.explorer_page = 0
            st.session_state.last_search = search_term
            st.session_state.last_source = selected_source

        page = st.session_state.explorer_page
        start = page * page_size
        page_docs = filtered[start: start + page_size]

        # ── Chunk cards ──
        for i, doc in enumerate(page_docs, start + 1):
            src  = doc.metadata.get("source", "Unknown")
            sec  = doc.metadata.get("section", "")
            pg   = doc.metadata.get("page", "")
            chars = len(doc.page_content)
            label = f"Chunk #{i}  ·  {src}"
            if sec: label += f"  ·  {sec}"
            if pg:  label += f"  ·  p.{pg}"
            label += f"  ·  {chars} chars"
            with st.expander(label):
                st.code(doc.page_content, language=None)
                st.caption(f"Metadata: {doc.metadata}")

        # ── Page controls ──
        if total_pages > 1:
            st.divider()
            p1, p2, p3 = st.columns([1, 3, 1])
            with p1:
                if st.button("← Prev", disabled=page == 0):
                    st.session_state.explorer_page -= 1
                    st.rerun()
            with p2:
                st.caption(f"Page {page + 1} of {total_pages}")
            with p3:
                if st.button("Next →", disabled=page >= total_pages - 1):
                    st.session_state.explorer_page += 1
                    st.rerun()


# ── Context Analyzer Tab ───────────────────────────────────────────────────────
with tab_context:
    cd = st.session_state.last_context_data

    if cd is None:
        st.info("Ask a question in the Chat tab first — the context sent to GPT will appear here.")
    else:
        n_chunks  = len(cd["chunk_breakdown"])
        est_tok   = cd["estimated_tokens"]
        avg_score = cd["avg_score"]
        confidence = cd["confidence"]

        # ── Header metrics ──────────────────────────────────────────────────
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Chunks sent to GPT",  n_chunks)
        m2.metric("Estimated tokens",    f"{est_tok:,}")
        m3.metric("Avg relevance score", avg_score)
        m4.metric("Confidence",          confidence)

        st.divider()

        # ── Question ────────────────────────────────────────────────────────
        st.markdown("#### Question sent to GPT")
        st.info(cd["question"])

        st.divider()

        # ── Per-chunk breakdown ─────────────────────────────────────────────
        st.markdown("#### Retrieved chunks — context window contents")
        st.caption("These are the exact chunks assembled into the {context} placeholder of the prompt.")

        for chunk in cd["chunk_breakdown"]:
            score = chunk["score"]
            if score >= 0.35:
                badge = "HIGH"
            elif score >= 0.15:
                badge = "MEDIUM"
            else:
                badge = "LOW"

            src     = chunk["source"]
            sec     = ("  ·  " + chunk["section"]) if chunk["section"] else ""
            pg      = ("  ·  p." + str(chunk["page"])) if chunk["page"] else ""
            chars   = chunk["chars"]
            idx     = chunk["index"]
            label   = f"[{idx}]  {src}{sec}{pg}  ·  {chars} chars  ·  score {score}  ·  {badge}"

            with st.expander(label, expanded=(idx == 1)):
                st.code(chunk["text"], language=None)

        st.divider()

        # ── Assembled context string ────────────────────────────────────────
        st.markdown("#### Assembled context string")
        st.caption("Exactly what fills the {context} placeholder — including source headers and --- separators.")
        st.text_area(
            label="context_str",
            value=cd["context_str"],
            height=300,
            label_visibility="collapsed",
        )

        st.divider()

        # ── Full prompt ─────────────────────────────────────────────────────
        st.markdown("#### Full prompt sent to GPT-4o-mini")

        used_k  = round(est_tok / 1000, 1)
        pct     = min(round((est_tok / 128000) * 100, 1), 100)
        st.caption(f"System persona + context + question — ~{est_tok:,} tokens  (GPT-4o-mini limit: 128,000 tokens)")

        token_bar = (
            '<div style="border:1px solid #2d4070;border-radius:4px;padding:6px 10px;margin-bottom:8px;">'
            f'<div style="font-size:11px;color:#8899b4;margin-bottom:4px;">Token budget: {used_k}k / 128k used</div>'
            '<div style="background:#1e2538;border-radius:2px;height:8px;">'
            f'<div style="background:#c9a84c;width:{pct}%;height:8px;border-radius:2px;"></div>'
            '</div></div>'
        )
        st.markdown(token_bar, unsafe_allow_html=True)

        st.text_area(
            label="full_prompt",
            value=cd["full_prompt"],
            height=420,
            label_visibility="collapsed",
        )
