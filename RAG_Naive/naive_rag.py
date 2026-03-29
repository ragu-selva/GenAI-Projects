# Install: pip install openai chromadb sentence-transformers python-dotenv
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  # loads variables from .env file

openai_client = OpenAI()  # reads OPENAI_API_KEY from environment

# ============================================================
# NAIVE RAG - The Foundation
# ============================================================

# STEP 1: Your Documents (Knowledge Base)
documents = [
    "Python is a high-level programming language known for simplicity.",
    "Machine learning is a subset of AI that learns from data.",
    "RAG stands for Retrieval-Augmented Generation.",
    "Vector databases store embeddings for fast similarity search.",
    "LLMs like GPT-4 are trained on large amounts of text data.",
]

# STEP 2: Chunk the documents
# (For bigger docs, split them into smaller pieces)
def chunk_text(text, chunk_size=100):
    words = text.split()
    return [" ".join(words[i:i+chunk_size]) 
            for i in range(0, len(words), chunk_size)]

# STEP 3: Create Embeddings & Store in Vector DB
import chromadb
from sentence_transformers import SentenceTransformer

# Load embedding model
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# Create vector store
client = chromadb.Client()
collection = client.create_collection("my_docs")

# Embed and store documents
embeddings = embedder.encode(documents).tolist()
collection.add(
    documents=documents,
    embeddings=embeddings,
    ids=[f"doc_{i}" for i in range(len(documents))]
)

# STEP 4: Retrieve relevant docs for a query
def retrieve(query, top_k=2):
    query_embedding = embedder.encode([query]).tolist()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k
    )
    return results["documents"][0]  # Return top matching chunks

# STEP 5: Generate answer using retrieved context
def generate_answer(query, context_chunks):
    context = "\n".join(context_chunks)
    prompt = f"""Answer the question using ONLY the context below.
    
Context:
{context}

Question: {query}
Answer:"""
    
    print(f"PROMPT SENT TO LLM:\n{prompt}\n")
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    return response.choices[0].message.content

# STEP 6: Full Pipeline
def naive_rag_pipeline(user_question):
    print(f"Question: {user_question}\n")
    
    # 1. Retrieve
    relevant_chunks = retrieve(user_question)
    print(f"Retrieved chunks: {relevant_chunks}\n")
    
    # 2. Generate
    answer = generate_answer(user_question, relevant_chunks)
    return answer

# Run it!
answer = naive_rag_pipeline("What is RAG?")
print(f"Answer: {answer}")