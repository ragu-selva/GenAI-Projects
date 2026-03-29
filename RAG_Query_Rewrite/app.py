# ════════════════════════════════════════════════════════════════
# Query Rewrite RAG  ·  Streamlit App
# ════════════════════════════════════════════════════════════════
#
# HOW TO RUN:
#   pip install streamlit openai chromadb sentence-transformers
#   streamlit run app.py
#
# WHAT IS QUERY REWRITING?
#   Users often ask vague, short, or poorly-phrased questions.
#   Before searching, we use an LLM to rewrite the query into
#   a clearer, more specific version — then search with THAT.
#
#   User types:  "tell me bout that python thing"
#   Rewritten:   "What is the Python programming language and
#                 what are its main features?"
#   Result:      Much better retrieval!
#
# ════════════════════════════════════════════════════════════════

import json
import streamlit as st
import chromadb
import openai
from sentence_transformers import SentenceTransformer

# ── Page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="Query Rewrite RAG",
    page_icon="✏️",
    layout="wide",
)

# ── CSS ───────────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #F8F9FF; }

    /* Original query box */
    .query-original {
        background: #FEF3C7;
        border: 2px solid #F59E0B;
        border-radius: 10px;
        padding: 12px 16px;
        font-size: 14px;
        color: #92400E;
    }

    /* Rewritten query box */
    .query-rewritten {
        background: #ECFDF5;
        border: 2px solid #10B981;
        border-radius: 10px;
        padding: 12px 16px;
        font-size: 14px;
        color: #065F46;
    }

    /* Strategy badge */
    .strategy-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 700;
        font-family: monospace;
        margin: 2px;
    }

    /* Chunk result card */
    .chunk-card {
        background: white;
        border: 1px solid #E5E7EB;
        border-left: 4px solid #6366F1;
        border-radius: 8px;
        padding: 12px 14px;
        margin: 8px 0;
        font-size: 13px;
        color: #374151;
        line-height: 1.6;
    }

    /* Final answer box */
    .answer-box {
        background: #EFF6FF;
        border: 2px solid #3B82F6;
        border-radius: 12px;
        padding: 20px;
        font-size: 15px;
        line-height: 1.8;
        color: #1E3A5F;
    }

    /* Step header */
    .step-header {
        background: white;
        border: 1px solid #E5E7EB;
        border-radius: 10px;
        padding: 10px 16px;
        margin: 10px 0 6px 0;
        font-weight: 700;
        font-size: 13px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    #MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════
# CACHED RESOURCES  (load once, reuse forever)
# ════════════════════════════════════════════════════════════════

@st.cache_resource
def load_embedder():
    return SentenceTransformer("all-MiniLM-L6-v2")

@st.cache_resource
def load_vector_store():
    client = chromadb.Client()
    return client.get_or_create_collection(
        name="qr_rag",
        metadata={"hnsw:space": "cosine"},
    )

embedder = load_embedder()
col      = load_vector_store()


# ════════════════════════════════════════════════════════════════
# SAMPLE KNOWLEDGE BASE
# ════════════════════════════════════════════════════════════════

SAMPLE_DOCS = [
    {
        "id": "py1",
        "text": "Python is a high-level programming language created by Guido van Rossum in 1991. "
                "It emphasizes code readability and uses indentation to define code blocks. "
                "Python supports multiple programming paradigms including procedural, "
                "object-oriented, and functional programming.",
        "source": "python_basics.txt",
    },
    {
        "id": "py2",
        "text": "Python is widely used in web development, data science, artificial intelligence, "
                "machine learning, automation, and scientific computing. Popular frameworks include "
                "Django and Flask for web, NumPy and Pandas for data, and PyTorch and TensorFlow "
                "for machine learning.",
        "source": "python_uses.txt",
    },
    {
        "id": "rag1",
        "text": "RAG stands for Retrieval-Augmented Generation. It was introduced by Facebook AI "
                "Research in 2020. RAG works by first retrieving relevant documents from a knowledge "
                "base using vector similarity search, then passing those documents as context to a "
                "large language model to generate an accurate answer.",
        "source": "rag_overview.txt",
    },
    {
        "id": "rag2",
        "text": "The main benefit of RAG is reducing hallucinations in large language models. "
                "Instead of the model relying solely on its training data, it can access "
                "up-to-date or private information from a knowledge base. RAG systems typically "
                "use vector databases like ChromaDB, Pinecone, or Weaviate.",
        "source": "rag_benefits.txt",
    },
    {
        "id": "llm1",
        "text": "Large Language Models (LLMs) are neural networks trained on massive text datasets. "
                "Examples include GPT-4 by OpenAI, Claude by Anthropic, and Gemini by Google. "
                "LLMs can perform tasks like text generation, summarization, translation, "
                "question answering, and code generation.",
        "source": "llm_basics.txt",
    },
    {
        "id": "embed1",
        "text": "Text embeddings convert words and sentences into numerical vectors that capture "
                "semantic meaning. Similar texts produce similar vectors. Embedding models like "
                "all-MiniLM-L6-v2 from SentenceTransformers produce 384-dimensional vectors. "
                "OpenAI's text-embedding-3-small produces 1536-dimensional vectors.",
        "source": "embeddings.txt",
    },
    {
        "id": "vec1",
        "text": "Vector databases store embeddings and support fast similarity search using "
                "Approximate Nearest Neighbour algorithms like HNSW. ChromaDB is a free open-source "
                "vector database. Pinecone is a managed cloud vector database. "
                "Cosine similarity measures the angle between two vectors — score of 1.0 means identical.",
        "source": "vector_db.txt",
    },
    {
        "id": "qr1",
        "text": "Query rewriting improves RAG retrieval by transforming vague or poorly-worded "
                "questions into clearer, more specific search queries before searching. "
                "A user might ask 'tell me about the python thing' which gets rewritten to "
                "'What is the Python programming language and what are its main features and uses?'",
        "source": "query_rewriting.txt",
    },
]


# ════════════════════════════════════════════════════════════════
# LOAD DOCS INTO VECTOR STORE
# ════════════════════════════════════════════════════════════════

def load_sample_docs():
    if col.count() == 0:
        texts = [d["text"] for d in SAMPLE_DOCS]
        ids   = [d["id"]   for d in SAMPLE_DOCS]
        metas = [{"source": d["source"]} for d in SAMPLE_DOCS]
        embs  = embedder.encode(texts).tolist()
        col.upsert(documents=texts, embeddings=embs, ids=ids, metadatas=metas)

load_sample_docs()


# ════════════════════════════════════════════════════════════════
# QUERY REWRITING STRATEGIES
# ════════════════════════════════════════════════════════════════

def get_openai_client():
    key = st.session_state.get("api_key", "")
    if not key:
        st.error("⚠ Add your OpenAI API key in the sidebar.")
        st.stop()
    return openai.OpenAI(api_key=key)


# ── STRATEGY 1: Simple Rewrite ───────────────────────────────
def rewrite_simple(client, query: str) -> str:
    """
    Most basic rewrite — expand and clarify the query.

    "tell me about python" 
    → "What is Python programming language, what are its
       main features, and what is it commonly used for?"
    """
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": (
                    "Rewrite the user's question to be clearer and more specific "
                    "for a document search system. Expand abbreviations, fix grammar, "
                    "and make implicit intent explicit. "
                    "Return ONLY the rewritten question, nothing else."
                ),
            },
            {"role": "user", "content": query},
        ],
    )
    return resp.choices[0].message.content.strip()


# ── STRATEGY 2: HyDE (Hypothetical Document Embedding) ───────
def rewrite_hyde(client, query: str) -> str:
    """
    HyDE = generate a HYPOTHETICAL ANSWER, then search with that.

    Instead of searching with the question, we search with
    what a good answer would look like. This often finds
    better matches because answers are more similar to
    document text than questions are.

    "What is RAG?"
    → "RAG (Retrieval-Augmented Generation) is a technique
       that combines information retrieval with language model
       generation. It works by first retrieving relevant
       documents from a knowledge base..."
    """
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.3,
        messages=[
            {
                "role": "system",
                "content": (
                    "Write a short 2-3 sentence hypothetical answer to the question "
                    "as if you were an expert. This will be used to search a document "
                    "database — write it as a factual passage, not as 'I think...'. "
                    "Return ONLY the hypothetical answer passage."
                ),
            },
            {"role": "user", "content": query},
        ],
    )
    return resp.choices[0].message.content.strip()


# ── STRATEGY 3: Step-Back Prompting ──────────────────────────
def rewrite_stepback(client, query: str) -> str:
    """
    Step-back = ask a more GENERAL version of the question.

    If the specific question doesn't find good results,
    stepping back to the broader topic often helps.

    "What year did Python 3.11 release?" 
    → "What is the history and version timeline of Python?"

    "How do I fix ChromaDB connection error?"
    → "How does ChromaDB work and what are common setup issues?"
    """
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": (
                    "Rewrite the question as a broader, more general version "
                    "that covers the underlying concept or topic. "
                    "This helps find relevant background information. "
                    "Return ONLY the rewritten question, nothing else."
                ),
            },
            {"role": "user", "content": query},
        ],
    )
    return resp.choices[0].message.content.strip()


# ── STRATEGY 4: Multi-Query ───────────────────────────────────
def rewrite_multiquery(client, query: str) -> list[str]:
    """
    Multi-query = generate MULTIPLE different phrasings,
    retrieve for each, then merge results.

    "What is RAG?"
    → ["How does Retrieval-Augmented Generation work?",
       "What are the components of a RAG system?",
       "Why is RAG better than using LLMs alone?"]

    Casting a wider net catches documents that a single
    query might miss.
    """
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.4,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": (
                    "Generate 3 different versions of the question that "
                    "approach the topic from different angles. "
                    "Return ONLY JSON: {\"queries\": [\"q1\", \"q2\", \"q3\"]}"
                ),
            },
            {"role": "user", "content": query},
        ],
    )
    result = json.loads(resp.choices[0].message.content)
    return result.get("queries", [query])


# ════════════════════════════════════════════════════════════════
# RETRIEVAL
# ════════════════════════════════════════════════════════════════

def retrieve(query_text: str, top_k: int = 3) -> list[dict]:
    """Search the vector store with a query string."""
    emb     = embedder.encode([query_text]).tolist()
    results = col.query(
        query_embeddings=emb,
        n_results=min(top_k, col.count()),
        include=["documents", "metadatas", "distances"],
    )
    return [
        {
            "text":   text,
            "source": meta.get("source", "?"),
            "score":  round(1 - dist, 3),
        }
        for text, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        )
    ]


def retrieve_and_deduplicate(queries: list[str], top_k: int = 3) -> list[dict]:
    """
    Retrieve for multiple queries, deduplicate by text.
    Used by multi-query strategy.
    """
    seen   = set()
    merged = []
    for q in queries:
        for chunk in retrieve(q, top_k=top_k):
            if chunk["text"] not in seen:
                seen.add(chunk["text"])
                merged.append(chunk)
    # Sort by score descending
    return sorted(merged, key=lambda x: x["score"], reverse=True)[:top_k * 2]


# ════════════════════════════════════════════════════════════════
# GENERATION
# ════════════════════════════════════════════════════════════════

def generate_answer(client, original_query: str, context_chunks: list[dict]) -> str:
    """Generate final answer from original question + retrieved context."""
    context = "\n\n".join(
        f"[Source: {c['source']}]\n{c['text']}"
        for c in context_chunks
    )
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.1,
        messages=[
            {
                "role": "system",
                "content": (
                    "Answer the question using the provided context. "
                    "Be clear and concise. Cite sources where relevant."
                ),
            },
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {original_query}",
            },
        ],
    )
    return resp.choices[0].message.content.strip()


# ════════════════════════════════════════════════════════════════
# SESSION STATE
# ════════════════════════════════════════════════════════════════

if "api_key"  not in st.session_state: st.session_state.api_key  = ""
if "strategy" not in st.session_state: st.session_state.strategy = "Simple Rewrite"
if "top_k"    not in st.session_state: st.session_state.top_k    = 3
if "history"  not in st.session_state: st.session_state.history  = []


# ════════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("## ✏️ Query Rewrite RAG")
    st.divider()

    st.markdown("### 🔑 OpenAI API Key")
    st.session_state.api_key = st.text_input(
        "key", type="password",
        placeholder="sk-...",
        value=st.session_state.api_key,
        label_visibility="collapsed",
    )

    st.divider()
    st.markdown("### 🔀 Rewriting Strategy")

    strategy = st.radio(
        "strategy",
        ["Simple Rewrite", "HyDE", "Step-Back", "Multi-Query"],
        label_visibility="collapsed",
        captions=[
            "Expand & clarify the query",
            "Search with a hypothetical answer",
            "Ask the broader topic question",
            "Generate 3 query variants",
        ],
    )
    st.session_state.strategy = strategy

    st.divider()
    st.markdown("### ⚙ Settings")
    st.session_state.top_k = st.slider("Chunks to retrieve", 1, 5, 3)

    st.divider()
    st.markdown("### 📚 Knowledge Base")
    st.info(f"**{col.count()} chunks** loaded")
    topics = ["Python", "RAG", "LLMs", "Embeddings", "Vector DBs", "Query Rewriting"]
    for t in topics:
        st.markdown(f"• {t}")

    st.divider()

    # ── Strategy guide ────────────────────────────────────────
    st.markdown("### 📖 When to use each?")
    guides = {
        "Simple Rewrite": "User asks vague or short questions",
        "HyDE":           "Questions with no good keyword matches",
        "Step-Back":      "Very specific questions about niche topics",
        "Multi-Query":    "Complex questions needing broad coverage",
    }
    for name, guide in guides.items():
        active = "→ " if name == strategy else "   "
        color  = "#10B981" if name == strategy else "#9CA3AF"
        st.markdown(
            f'<span style="color:{color}; font-size:12px;">'
            f'{active}<b>{name}</b>: {guide}</span>',
            unsafe_allow_html=True,
        )


# ════════════════════════════════════════════════════════════════
# MAIN UI
# ════════════════════════════════════════════════════════════════

st.markdown("# ✏️ Query Rewrite RAG")
st.markdown(
    "Normal RAG searches with the user's raw query. "
    "**Query Rewrite RAG rewrites the query first** — making it clearer, "
    "broader, or even turning it into a hypothetical answer — "
    "then searches with the improved version."
)

# ── Strategy explanation banner ───────────────────────────────
strategy_info = {
    "Simple Rewrite": {
        "color": "#F59E0B", "icon": "✏️",
        "flow": "Raw Query → LLM Rewrite → Better Query → Retrieve → Answer",
        "desc": "The LLM expands abbreviations, fixes grammar, and makes implicit intent explicit.",
    },
    "HyDE": {
        "color": "#8B5CF6", "icon": "🔮",
        "flow": "Raw Query → Generate Hypothetical Answer → Use as Search Query → Retrieve → Answer",
        "desc": "Instead of searching with the question, search with what a good answer would look like.",
    },
    "Step-Back": {
        "color": "#06B6D4", "icon": "↩️",
        "flow": "Raw Query → Ask Broader Version → Retrieve Background → Answer Specific Q",
        "desc": "Zooms out to the general topic — finds background context for specific questions.",
    },
    "Multi-Query": {
        "color": "#10B981", "icon": "🔀",
        "flow": "Raw Query → 3 Variants → Retrieve for Each → Merge & Deduplicate → Answer",
        "desc": "Casts a wider net — different phrasings catch different relevant documents.",
    },
}

info  = strategy_info[strategy]
color = info["color"]

st.markdown(
    f'<div style="background:{color}11; border:2px solid {color}44; '
    f'border-radius:12px; padding:14px 18px; margin-bottom:16px;">'
    f'<div style="font-weight:800; color:{color}; font-size:14px; margin-bottom:6px;">'
    f'{info["icon"]} {strategy}</div>'
    f'<div style="font-family:monospace; font-size:12px; color:{color}; margin-bottom:6px;">'
    f'📍 {info["flow"]}</div>'
    f'<div style="font-size:13px; color:#374151;">{info["desc"]}</div>'
    f'</div>',
    unsafe_allow_html=True,
)

st.divider()

# ── Example queries ───────────────────────────────────────────
st.markdown("#### 💡 Try these examples")

EXAMPLES = {
    "Simple Rewrite": [
        "tell me bout that python thing",
        "how does rag work",
        "whats an llm",
        "vector db stuff",
    ],
    "HyDE": [
        "What is RAG?",
        "How do embeddings work?",
        "What is query rewriting?",
        "Explain vector similarity",
    ],
    "Step-Back": [
        "What year was Python 3.0 released?",
        "What is ChromaDB written in?",
        "How many dimensions does MiniLM produce?",
        "Who made GPT-4?",
    ],
    "Multi-Query": [
        "How does RAG reduce hallucinations?",
        "What makes Python good for AI?",
        "Why use vector databases?",
        "How do LLMs generate text?",
    ],
}

example_cols = st.columns(4)
for i, ex in enumerate(EXAMPLES[strategy]):
    with example_cols[i]:
        if st.button(ex, key=f"ex_{strategy}_{i}", use_container_width=True):
            st.session_state.query_input = ex

# ── Main query input ──────────────────────────────────────────
query = st.text_input(
    "Your question",
    placeholder="Ask anything about Python, RAG, LLMs, embeddings...",
    value=st.session_state.get("query_input", ""),
    key="query_input",
)

run_btn = st.button(
    f"▶ Run with {strategy}",
    type="primary",
    use_container_width=True,
)

# ════════════════════════════════════════════════════════════════
# RUN THE PIPELINE
# ════════════════════════════════════════════════════════════════

if run_btn and query.strip():
    client = get_openai_client()
    top_k  = st.session_state.get("top_k", 3)

    st.divider()
    st.markdown("## 🔬 Pipeline Steps")

    # ════════════════════════════
    # STEP 1  ·  Show original query
    # ════════════════════════════
    st.markdown(
        '<div class="step-header">📥 Step 1 · Original Query</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="query-original">💬 <b>You asked:</b> {query}</div>',
        unsafe_allow_html=True,
    )

    # ════════════════════════════
    # STEP 2  ·  Rewrite
    # ════════════════════════════
    st.markdown(
        f'<div class="step-header">✏️ Step 2 · Query Rewriting — <span style="color:{color}">{strategy}</span></div>',
        unsafe_allow_html=True,
    )

    rewritten_queries = []   # will hold 1 string or a list of strings

    with st.spinner(f"Rewriting with {strategy}..."):

        if strategy == "Simple Rewrite":
            rewritten = rewrite_simple(client, query)
            rewritten_queries = [rewritten]
            st.markdown(
                f'<div class="query-rewritten">'
                f'✅ <b>Rewritten:</b> {rewritten}'
                f'</div>',
                unsafe_allow_html=True,
            )

        elif strategy == "HyDE":
            rewritten = rewrite_hyde(client, query)
            rewritten_queries = [rewritten]
            st.markdown(
                f'<div class="query-rewritten">'
                f'🔮 <b>Hypothetical answer (used as search query):</b><br><br>'
                f'<i>{rewritten}</i>'
                f'</div>',
                unsafe_allow_html=True,
            )
            st.caption("↑ This hypothetical answer is embedded and searched — not shown to the user as the final answer")

        elif strategy == "Step-Back":
            rewritten = rewrite_stepback(client, query)
            rewritten_queries = [rewritten]

            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(
                    f'<div class="query-original">🎯 <b>Specific (original):</b><br>{query}</div>',
                    unsafe_allow_html=True,
                )
            with col_b:
                st.markdown(
                    f'<div class="query-rewritten">↩️ <b>General (step-back):</b><br>{rewritten}</div>',
                    unsafe_allow_html=True,
                )

        elif strategy == "Multi-Query":
            variants = rewrite_multiquery(client, query)
            rewritten_queries = variants

            st.markdown(
                f'<div class="query-rewritten">'
                f'🔀 <b>Generated {len(variants)} query variants:</b><br><br>'
                + "<br>".join(f"&nbsp;&nbsp;<b>{i+1}.</b> {v}" for i, v in enumerate(variants))
                + "</div>",
                unsafe_allow_html=True,
            )

    # ════════════════════════════
    # STEP 3  ·  Retrieval
    # ════════════════════════════
    st.markdown(
        '<div class="step-header">🔍 Step 3 · Vector Search</div>',
        unsafe_allow_html=True,
    )

    with st.spinner("Searching knowledge base..."):
        if strategy == "Multi-Query":
            chunks = retrieve_and_deduplicate(rewritten_queries, top_k=top_k)
            st.caption(f"Searched with {len(rewritten_queries)} queries → merged & deduplicated → {len(chunks)} unique chunks")
        else:
            # Search with the rewritten query (not the original)
            chunks = retrieve(rewritten_queries[0], top_k=top_k)
            st.caption(f"Searched with rewritten query → {len(chunks)} chunks retrieved")

    # Show retrieved chunks
    for i, chunk in enumerate(chunks):
        score_color = "#10B981" if chunk["score"] > 0.7 else "#F59E0B" if chunk["score"] > 0.5 else "#EF4444"
        st.markdown(
            f'<div class="chunk-card">'
            f'<span style="font-size:11px; color:#6B7280;">📄 {chunk["source"]} &nbsp;|&nbsp; '
            f'<span style="color:{score_color}; font-weight:700;">similarity: {chunk["score"]}</span></span>'
            f'<br><br>{chunk["text"]}'
            f'</div>',
            unsafe_allow_html=True,
        )

    # ── Side-by-side comparison (original vs rewritten retrieval) ──
    with st.expander("👀 Compare: original query vs rewritten query retrieval"):
        cmp1, cmp2 = st.columns(2)

        with cmp1:
            st.markdown(f"**Original query:** `{query[:60]}...`")
            orig_chunks = retrieve(query, top_k=top_k)
            for c in orig_chunks:
                score_color = "#10B981" if c["score"] > 0.7 else "#F59E0B"
                st.markdown(
                    f'<div class="chunk-card" style="border-left-color: #F59E0B;">'
                    f'<span style="font-size:11px; color:{score_color};">score: {c["score"]}</span><br>'
                    f'{c["text"][:120]}...</div>',
                    unsafe_allow_html=True,
                )

        with cmp2:
            rq = rewritten_queries[0] if rewritten_queries else query
            st.markdown(f"**Rewritten query:** `{rq[:60]}...`")
            new_chunks = retrieve(rq, top_k=top_k)
            for c in new_chunks:
                score_color = "#10B981" if c["score"] > 0.7 else "#F59E0B"
                st.markdown(
                    f'<div class="chunk-card" style="border-left-color: #10B981;">'
                    f'<span style="font-size:11px; color:{score_color};">score: {c["score"]}</span><br>'
                    f'{c["text"][:120]}...</div>',
                    unsafe_allow_html=True,
                )

    # ════════════════════════════
    # STEP 4  ·  Generate Answer
    # ════════════════════════════
    st.markdown(
        '<div class="step-header">💬 Step 4 · Generate Answer</div>',
        unsafe_allow_html=True,
    )

    with st.spinner("Generating answer..."):
        # Always answer the ORIGINAL question — not the rewritten one
        answer = generate_answer(client, query, chunks)

    st.markdown(
        f'<div class="answer-box">{answer}</div>',
        unsafe_allow_html=True,
    )

    # ── Summary metrics ───────────────────────────────────────
    st.markdown("")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Strategy",       strategy)
    m2.metric("Chunks used",    len(chunks))
    m3.metric("Query variants", len(rewritten_queries))
    m4.metric("Avg similarity", f"{sum(c['score'] for c in chunks)/len(chunks):.2f}" if chunks else "N/A")

    # ── Save to history ───────────────────────────────────────
    st.session_state.history.append({
        "query":    query,
        "strategy": strategy,
        "rewritten": rewritten_queries,
        "answer":   answer,
        "chunks":   len(chunks),
    })


# ── Query history ─────────────────────────────────────────────
if st.session_state.history:
    st.divider()
    st.markdown("### 📜 History")
    for h in reversed(st.session_state.history[-4:]):
        with st.expander(f"[{h['strategy']}]  {h['query'][:60]}..."):
            st.markdown(f"**Strategy:** `{h['strategy']}`")
            st.markdown(f"**Rewritten to:** {h['rewritten']}")
            st.markdown(f"**Answer:** {h['answer']}")
