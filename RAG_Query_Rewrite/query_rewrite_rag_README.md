# ✏️ Query Rewrite RAG (Streamlit App)

An interactive **RAG (Retrieval-Augmented Generation)** application that improves search quality using **Query Rewriting techniques** before retrieving documents.

Built with:
- 🧠 OpenAI (LLM)
- 🗂️ ChromaDB (Vector Database)
- 🔎 Sentence Transformers (Embeddings)
- 🎨 Streamlit (UI)

---

## 🚀 Overview

Traditional RAG systems directly use the user query for retrieval.

👉 This project improves results by **rewriting the query first** using different strategies:
- Make it clearer
- Make it broader
- Generate hypothetical answers
- Create multiple variations

---

## 🧠 Why Query Rewriting?

Users often ask:
"tell me bout python"

Rewritten to:
"What is the Python programming language and what are its main features?"

✅ Result: Better document retrieval → Better answers

---

## 🏗️ Architecture

User Query
    ↓
Query Rewriting (LLM)
    ↓
Embedding (SentenceTransformer)
    ↓
Vector Search (ChromaDB)
    ↓
Top-K Documents
    ↓
LLM Answer Generation
    ↓
Final Answer

---

## 🔀 Query Rewriting Strategies

### 1. ✏️ Simple Rewrite
- Expands and clarifies the query  
- Fixes grammar and intent  
**Use when:** Query is vague or short  

### 2. 🔮 HyDE (Hypothetical Document Embedding)
- Generates a fake answer  
- Uses it as the search query  
**Use when:** No strong keyword match  

### 3. ↩️ Step-Back Prompting
- Converts query into a broader question  
**Use when:** Query is too specific  

### 4. 🔀 Multi-Query
- Generates multiple variations  
- Merges and deduplicates results  
**Use when:** Complex questions  

---

## ✨ Features

- Interactive UI with Streamlit
- Multiple query rewriting strategies
- Real-time query transformation visualization
- Side-by-side comparison
- Semantic search using embeddings
- Query history tracking

---

## ⚙️ Installation

pip install streamlit openai chromadb sentence-transformers

---

## ▶️ Run the App

streamlit run app.py

---

## 🔑 Setup

Enter your OpenAI API key in the sidebar when running the app.

---

## 📚 Knowledge Base

Includes sample documents on:
- Python
- RAG
- LLMs
- Embeddings
- Vector Databases
- Query Rewriting

---

## 🔄 Pipeline Steps

1. User Query Input  
2. Query Rewriting  
3. Vector Search  
4. Retrieve Documents  
5. Generate Answer  
6. Display Results  

---

## 📈 Key Learnings

- Query quality impacts retrieval quality  
- Rewriting improves RAG performance  
- Different strategies suit different queries  

---

## 🚀 Future Improvements

- Add re-ranking  
- Hybrid search  
- File uploads  
- Deployment  

---

## 📄 License

Educational use only.
