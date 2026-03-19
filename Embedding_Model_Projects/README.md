# 🧠 HuggingFace Embeddings — Sample Project

A beginner-friendly project to understand text embeddings step by step.

---

## What Are Embeddings?

Embeddings are a way to convert **text into numbers** so computers can understand *meaning*.

```
"I love pizza"     →  [0.23, -0.81, 0.44, 0.19, ...]  (384 numbers)
"I enjoy pizza"    →  [0.21, -0.79, 0.46, 0.18, ...]  (very similar!)
"The stock market" →  [0.91,  0.32, -0.7, 0.55, ...]  (very different!)
```

Similar meanings → similar numbers → close together in "vector space"

---

## Setup & Run

### 1. Create a virtual environment (recommended)
```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```
> First run downloads the model (~80MB) from HuggingFace automatically.

### 3. Run the scripts in order

```bash
# Script 1: See what embeddings look like
python 1_basics.py

# Script 2: Measure similarity between sentences
python 2_similarity.py

# Script 3: Build a semantic search engine
python 3_search.py
```

---

## What Each Script Teaches

| Script | Concept | Key Takeaway |
|--------|---------|-------------|
| `1_basics.py` | What embeddings are | Each sentence → 384 numbers |
| `2_similarity.py` | Cosine similarity | Score 0.0–1.0 measures meaning closeness |
| `3_search.py` | Semantic search | Find relevant docs without keyword matching |

---

## The Model: `all-MiniLM-L6-v2`

- 📦 Size: ~80MB
- ⚡ Speed: Fast (CPU-friendly)
- 📐 Output: 384-dimensional vectors
- 🎯 Good for: Similarity, search, clustering
- 🔗 HuggingFace: https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2

---

## Real-World Applications

- **ChatGPT file search** — embeds your docs, finds relevant chunks
- **Recommendation systems** — find similar products/articles
- **Duplicate detection** — find near-identical support tickets
- **RAG (Retrieval Augmented Generation)** — feed relevant context to LLMs
- **Multilingual search** — search across languages!

---

## Key Concepts Glossary

| Term | Simple Definition |
|------|------------------|
| **Embedding** | A list of numbers representing meaning |
| **Vector** | Another word for "list of numbers" |
| **Cosine Similarity** | How close two vectors point (0=opposite, 1=same) |
| **Vector Space** | Imaginary multi-dimensional space where vectors live |
| **Semantic Search** | Search by meaning, not keywords |
| **RAG** | Giving an AI model relevant context before asking questions |
