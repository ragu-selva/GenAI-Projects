# ============================================================
# ADVANCED RAG - With Re-ranking
# ============================================================

# Install: pip install openai chromadb sentence-transformers python-dotenv
from openai import OpenAI
from dotenv import load_dotenv
from sentence_transformers import CrossEncoder

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
    "Embeddings are dense numerical representations of data such as words, sentences, images or audio mapped into a continuous high dimensional space where similar items are positioned closer together.",
    "Machine learning models that capture semantic meaning, context and relationships within the data generates them.",
    "Instead of comparing raw text or media directly embeddings allow systems to measure similarity through mathematical distance metrics like cosine similarity or Euclidean distance for faster search and extraction.",
    "This makes them important for tasks such as semantic search, recommendation systems, clustering, classification and cross lingual matching.",
    "Pinecone: Fully managed, cloud native vector database with high scalability and low latency search.",
    "Weaviate: Open source, supports hybrid (keyword + vector) search and offers built in machine learning modules.",
    "Milvus: Highly scalable, open source database optimized for large scale similarity search.",
    "Qdrant: Open source, focuses on high recall, performance and ease of integration with AI applications.",
    "Chromadb: Lightweight, developer friendly vector database often used in LLM powered applications."
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


# Re-ranker model (scores query-document pairs)
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

def retrieve_and_rerank(query, top_k_retrieve=5, top_k_final=2):
    """
    Step 1: Retrieve more docs than needed (cast wide net)
    Step 2: Re-rank them by true relevance
    Step 3: Keep only the best
    """
    # Retrieve more candidates first
    query_embedding = embedder.encode([query]).tolist()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k_retrieve  # Get 5 instead of 2
    )
    candidates = results["documents"][0]
    
    # Re-rank: Score each candidate against the query
    pairs = [[query, doc] for doc in candidates]
    scores = reranker.predict(pairs)
    
    # Sort by score, keep top_k_final
    ranked = sorted(zip(scores, candidates), reverse=True)
    top_docs = [doc for _, doc in ranked[:top_k_final]]
    
    print(f"Before re-rank: {candidates}")
    print(f"After re-rank (top {top_k_final}): {top_docs}")
    
    return top_docs

def advanced_rag_pipeline(user_question):
    chunks = retrieve_and_rerank(user_question)
    answer = generate_answer(user_question, chunks)
    return answer

answer = advanced_rag_pipeline("Tell me about vector databases")
print(f"Answer: {answer}")