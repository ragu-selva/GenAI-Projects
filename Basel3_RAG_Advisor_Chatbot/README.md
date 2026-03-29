# 🏦 Basel III RAG Advisor

An **Advanced Retrieval-Augmented Generation (RAG) chatbot** for Basel III regulatory reporting, built with LangChain and Streamlit.

---

## ✨ Features

| Feature | Details |
|---|---|
| **Hybrid Search** | Dense (FAISS + OpenAI embeddings) + Sparse (BM25) retrieval |
| **Multi-Query Expansion** | Generates query variants to improve recall |
| **MMR Re-ranking** | Maximal Marginal Relevance for diverse, non-redundant results |
| **Keyword Re-ranking** | Post-retrieval overlap scoring for precision |
| **Demo Corpus** | Built-in Basel III regulatory knowledge base (no upload needed) |
| **Document Upload** | Supports PDF, TXT, DOCX, HTML |
| **Source Attribution** | Every answer shows evidence sources with snippets |
| **Dark Financial UI** | Production-grade Streamlit interface |

---

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the app
```bash
streamlit run app.py
```

### 3. Configure
1. Paste your **OpenAI API key** in the sidebar
2. Click **🏛️ Load Demo** to use the built-in Basel III corpus  
   — OR upload your own regulatory PDFs
3. Start asking questions!

---

## 🔍 Retrieval Modes

| Mode | Description | Best For |
|---|---|---|
| **Hybrid** | FAISS (60%) + BM25 (40%) | General regulatory queries |
| **Dense** | Semantic embedding search | Conceptual / context questions |
| **Sparse** | BM25 keyword matching | Exact terms, ratios, thresholds |
| **Multi-Query** | Generates 3 query variants | Complex or ambiguous questions |

---

## 📚 Demo Corpus Topics

The built-in corpus covers all major Basel III pillars:

- **Capital Adequacy** — CET1, AT1, Tier 2, conservation & countercyclical buffers, G-SIB surcharges
- **Liquidity** — LCR (HQLA, cash flow stress), NSFR (ASF/RSF factors)
- **Leverage Ratio** — Tier 1 / Exposure Measure, G-SIB leverage buffer
- **Credit Risk** — Standardised Approach (SA) risk weights by asset class
- **Market Risk** — FRTB (IMA: Expected Shortfall, SA: SBM, DRC, RRAO)
- **Operational Risk** — SA-OR (Business Indicator, ILM, ORC)
- **Pillar 2 & 3** — ICAAP, SREP, Pillar 3 disclosure templates

---

## 🏗️ Architecture

```
User Query
    │
    ▼
Query Processing
    │
    ├── Multi-Query Expansion (optional)
    │
    ▼
Parallel Retrieval
    ├── FAISS Dense Search (text-embedding-3-small)
    └── BM25 Sparse Search
    │
    ▼
EnsembleRetriever (hybrid fusion)
    │
    ▼
Keyword Re-ranking
    │
    ▼
Context Assembly (top-K chunks)
    │
    ▼
GPT-4o-mini Generation
(Basel III system prompt)
    │
    ▼
Answer + Source Attribution
```

---

## 🛠️ Tech Stack

- **LangChain** — RAG orchestration, retrievers, chains
- **OpenAI** — `text-embedding-3-small` + `gpt-4o-mini`
- **FAISS** — Vector similarity search
- **BM25** — Keyword retrieval (rank-bm25)
- **Streamlit** — Web interface
- **PyPDF / Docx2txt** — Document loaders

---

## 📝 Example Questions

- *"What is the minimum CET1 ratio under Basel III?"*
- *"Explain HQLA Level 1 and Level 2 assets for the LCR"*
- *"How is the NSFR calculated? What are the ASF and RSF factors?"*
- *"What does FRTB change about market risk capital?"*
- *"What is a G-SIB surcharge and how is it applied?"*
- *"Explain Pillar 2 ICAAP requirements"*
- *"What risk weights apply to residential mortgages under SA?"*
- *"How is operational risk capital calculated under SA-OR?"*
