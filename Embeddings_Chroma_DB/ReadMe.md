# 📦 ChromaDB Vector Store Example

This project demonstrates how to use **ChromaDB** as a persistent vector database for storing and searching text embeddings.

---

## 🚀 Overview

This script builds a simple **vector search system** using:

* **ChromaDB** → Stores embeddings on disk
* **Sentence Transformers** → Converts text into embeddings

### 💡 Key Idea

| Approach          | Storage Type | Persistence            |
| ----------------- | ------------ | ---------------------- |
| In-memory vectors | RAM          | ❌ Lost after execution |
| ChromaDB          | Disk         | ✅ Persistent           |

---

## 🔄 Workflow

```
Documents → Embeddings → Store in ChromaDB → Query anytime
```

---

## 📚 Dataset

The script uses a small set of sample documents across categories:

* Technology
* AI
* Travel
* Food

Each document also includes **metadata** like:

```json
{
  "category": "AI",
  "language": "english"
}
```

---

## ⚙️ Installation

Install required dependencies:

```bash
pip install chromadb sentence-transformers
```

---

## 🧠 How It Works

### 1. Load Embedding Model

```python
model = SentenceTransformer("all-MiniLM-L6-v2")
```

* Converts text into numerical vectors (embeddings)

---

### 2. Create Persistent Database

```python
client = chromadb.PersistentClient(path="./chroma_db")
```

* Stores data locally in `./chroma_db`
* Data persists across runs

---

### 3. Create Collection

```python
collection = client.create_collection(
    name="knowledge_base",
    metadata={"hnsw:space": "cosine"}
)
```

* Similar to a table in SQL
* Uses **cosine similarity** for search

---

### 4. Store Documents

```python
collection.add(
    ids=[...],
    embeddings=embeddings,
    documents=documents,
    metadatas=metadatas
)
```

Each entry includes:

* `id` → unique identifier
* `embedding` → vector representation
* `document` → original text
* `metadata` → additional info

---

### 5. Search Function

```python
def search_chroma(query, top_k=3, filter_category=None):
```

Supports:

* 🔍 Semantic search
* 🎯 Top-K results
* 🏷️ Metadata filtering

---

## 🔎 Example Queries

### 1. General Search

```python
search_chroma("How does AI understand language?")
```

✔ Returns most relevant documents based on meaning (not keywords)

---

### 2. Filtered Search

```python
search_chroma("Famous landmarks", filter_category="travel")
```

✔ Only returns results from the **travel** category

---

## 📊 Understanding Results

ChromaDB returns **distance**, not similarity.

```python
score = 1 - distance
```

* Lower distance → More similar
* Higher score → Better match

---

## 💾 Persistence

All data is saved locally:

```
./chroma_db/
```

✅ Run the script again → No re-embedding needed
✅ Instant loading from disk

---

## 🧪 Example Output

```
SEARCH 1: General query
#1 Score: 0.892 | Natural language processing helps computers understand human text.
#2 Score: 0.865 | Machine learning uses algorithms to learn patterns from data.

SEARCH 2: Filter by category='travel'
#1 Score: 0.910 | The Eiffel Tower is located in Paris, France.
```

---

## 🎯 Use Cases

* 🔎 Semantic search engines
* 🤖 RAG (Retrieval-Augmented Generation) systems
* 📄 Document search
* 💬 Chatbots with memory
* 🧠 Knowledge bases

---

## 🆚 Comparison with Previous Approach

| Feature     | In-Memory Search | ChromaDB |
| ----------- | ---------------- | -------- |
| Speed       | Fast             | Fast     |
| Persistence | ❌ No             | ✅ Yes    |
| Scalability | Limited          | High     |
| Filtering   | ❌ No             | ✅ Yes    |

---

## 📌 Key Takeaways

* Embeddings turn text into vectors for AI understanding
* ChromaDB enables **persistent vector storage**
* You can perform **semantic + filtered search** efficiently
* Ideal foundation for **AI applications like RAG systems**

---

## 🏁 Next Steps

You can extend this project by:

* Adding real-world datasets
* Building a REST API (Flask/FastAPI)
* Integrating with LLMs (OpenAI, etc.)
* Creating a frontend search UI

---

## 📂 Project Structure

```
.
├── app.py
├── chroma_db/        # Auto-created database folder
└── README.md
```

---

## 🙌 Conclusion

This project shows how to move from **temporary vector search** to a **production-ready persistent system** using ChromaDB.

Run it once, store forever, query anytime 🚀
