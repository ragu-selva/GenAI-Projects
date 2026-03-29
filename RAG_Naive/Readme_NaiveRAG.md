# 📚 Naive RAG (Retrieval-Augmented Generation) Demo

A beginner-friendly implementation of a **Naive RAG pipeline** using:
- OpenAI (LLM for generation)
- ChromaDB (vector database)
- Sentence Transformers (embeddings)

This project demonstrates the **core concept of RAG**:  
➡️ Retrieve relevant information → ➡️ Generate answer using LLM

---

## 🚀 Features

- Simple and easy-to-understand RAG pipeline
- Uses local embeddings (`all-MiniLM-L6-v2`)
- Stores vectors in ChromaDB
- Retrieves relevant documents based on similarity
- Generates answers using OpenAI LLM (`gpt-4o-mini`)

---

## 🧠 What is RAG?

**Retrieval-Augmented Generation (RAG)** is a technique where:
1. Relevant documents are retrieved from a knowledge base
2. These documents are passed as context to an LLM
3. The LLM generates a more accurate and grounded answer

---

## 🏗️ Project Structure

```
.
├── main.py        # Main RAG pipeline script
├── .env           # Environment variables (API key)
└── README.md
```

---

## ⚙️ Installation

Install required dependencies:

```bash
pip install openai chromadb sentence-transformers python-dotenv
```

---

## 🔑 Setup

Create a `.env` file in the root directory:

```
OPENAI_API_KEY=your_api_key_here
```

---

## 🔄 How It Works

### 1. Define Documents

```python
documents = [
    "Python is a high-level programming language...",
]
```

---

### 2. Chunking

```python
def chunk_text(text, chunk_size=100):
```

---

### 3. Embeddings + Storage

```python
embedder = SentenceTransformer("all-MiniLM-L6-v2")
collection.add(...)
```

---

### 4. Retrieval

```python
def retrieve(query, top_k=2):
```

---

### 5. Generation

```python
def generate_answer(query, context_chunks):
```

---

### 6. Full Pipeline

```python
def naive_rag_pipeline(user_question):
```

---

## ▶️ Run the Project

```bash
python main.py
```

---

## 🧪 Sample Output

```
Question: What is RAG?

Retrieved chunks:
['RAG stands for Retrieval-Augmented Generation.']

Answer:
RAG stands for Retrieval-Augmented Generation.
```

---

## ⚠️ Limitations

- No re-ranking
- No advanced chunking
- Small dataset

---

## 🚀 Future Improvements

- Hybrid search
- Better chunking
- UI integration

---

## 📌 Key Learnings

- Embeddings
- Vector search
- RAG pipeline basics

---

## 📄 License

Educational use only.
