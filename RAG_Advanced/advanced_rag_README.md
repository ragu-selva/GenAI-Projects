# 🚀 Advanced RAG (Retrieval-Augmented Generation) with Re-Ranking

An intermediate-to-advanced implementation of a **RAG pipeline with Re-ranking** using:

- OpenAI (LLM for answer generation)
- ChromaDB (vector database)
- Sentence Transformers (embeddings)
- Cross-Encoder (re-ranking model)

---

## 🧠 What Makes This "Advanced"?

Unlike Naive RAG, this implementation introduces:

✅ **Re-ranking step** for better accuracy  
✅ Retrieves more candidates and filters best ones  
✅ Uses Cross-Encoder for semantic relevance scoring  

---

## 🏗️ Architecture

```
User Query
    ↓
Embedding (SentenceTransformer)
    ↓
Vector Search (ChromaDB) → Top-K candidates
    ↓
Re-ranking (CrossEncoder)
    ↓
Top relevant documents
    ↓
LLM (OpenAI)
    ↓
Final Answer
```

---

## 🚀 Features

- Semantic search using embeddings
- Vector storage with ChromaDB
- Re-ranking using Cross-Encoder (`ms-marco-MiniLM`)
- Improved answer quality over naive RAG
- Clean modular pipeline

---

## ⚙️ Installation

```bash
pip install openai chromadb sentence-transformers python-dotenv
```

---

## 🔑 Setup

Create a `.env` file:

```
OPENAI_API_KEY=your_api_key_here
```

---

## 🔄 How It Works

### 1. Documents (Knowledge Base)

A collection of sample documents including:
- AI concepts
- Embeddings explanation
- Vector databases (Pinecone, Weaviate, Milvus, Qdrant, ChromaDB)

---

### 2. Embeddings + Storage

```python
embedder = SentenceTransformer("all-MiniLM-L6-v2")
collection.add(...)
```

---

### 3. Retrieval (Initial Search)

- Retrieves top **K = 5** similar documents

```python
def retrieve(query, top_k=2):
```

---

### 4. Re-ranking (Key Improvement ⭐)

- Uses CrossEncoder to score each (query, document) pair
- Sorts documents by relevance
- Selects best **Top 2**

```python
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
```

```python
def retrieve_and_rerank(query, top_k_retrieve=5, top_k_final=2):
```

---

### 5. Generation (LLM)

- Uses only re-ranked context
- Generates grounded answer

```python
def generate_answer(query, context_chunks):
```

---

### 6. Full Pipeline

```python
def advanced_rag_pipeline(user_question):
```

---

## ▶️ Run the Project

```bash
python main.py
```

---

## 🧪 Example Query

```
Tell me about vector databases
```

---

## 🧪 Sample Output

```
Before re-rank: [doc1, doc2, doc3, doc4, doc5]
After re-rank: [best_doc1, best_doc2]

Answer:
Vector databases are systems designed to store embeddings...
```

---

## ⚖️ Naive vs Advanced RAG

| Feature              | Naive RAG | Advanced RAG |
|---------------------|----------|--------------|
| Retrieval           | Top-K    | Top-K (wider) |
| Re-ranking          | ❌ No     | ✅ Yes         |
| Accuracy            | Medium   | High         |
| Complexity          | Low      | Medium       |

---

## 🚀 Future Improvements

- Hybrid search (BM25 + Vector)
- Metadata filtering
- Streaming responses
- UI (Streamlit / React)
- Multi-query retrieval
- Agentic RAG pipelines

---

## 📌 Key Learnings

- Why retrieval alone is not enough
- Importance of re-ranking
- Cross-encoder vs bi-encoder
- Improving RAG accuracy in production

---

## 📄 License

Educational use only.
