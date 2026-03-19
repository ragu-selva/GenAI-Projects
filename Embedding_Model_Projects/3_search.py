"""
STEP 3: BUILD A MINI SEMANTIC SEARCH ENGINE
=============================================
What this does:
- Creates a small "knowledge base" of documents
- Embeds all documents ONCE and stores them
- Takes a user query, embeds it, finds closest matches
- This is exactly how RAG (Retrieval Augmented Generation) works!
"""

from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Load model
model = SentenceTransformer("all-MiniLM-L6-v2")

# -------------------------------------------------------
# 1. Our "knowledge base" - documents to search through
# -------------------------------------------------------
documents = [
    "Python is a popular programming language known for its simplicity.",
    "Machine learning uses algorithms to learn patterns from data.",
    "The Eiffel Tower is located in Paris, France.",
    "Neural networks are inspired by the human brain structure.",
    "Pizza was invented in Naples, Italy in the 18th century.",
    "Deep learning is a subset of machine learning using neural networks.",
    "The Great Wall of China stretches over 13,000 miles.",
    "Natural language processing helps computers understand human text.",
    "Rome has more fountains than any other city in the world.",
    "Embeddings convert text into numerical vectors for AI models.",
    "The Amazon rainforest produces 20% of the world's oxygen.",
    "Transformers are a type of neural network architecture for NLP.",
]

# -------------------------------------------------------
# 2. Pre-compute embeddings for all documents
#    (In a real app, you'd store these in a vector database)
# -------------------------------------------------------
print("Embedding knowledge base...")
doc_embeddings = model.encode(documents)
print(f"Stored {len(documents)} document embeddings.\n")

# -------------------------------------------------------
# 3. Search function
# -------------------------------------------------------
def search(query: str, top_k: int = 3) -> list:
    """Find the most relevant documents for a query."""
    # Embed the query
    query_embedding = model.encode([query])

    # Compare query against all documents
    scores = cosine_similarity(query_embedding, doc_embeddings)[0]

    # Get top-k results sorted by score
    top_indices = np.argsort(scores)[::-1][:top_k]

    results = []
    for idx in top_indices:
        results.append({
            "document": documents[idx],
            "score": scores[idx],
            "rank": len(results) + 1,
        })
    return results

# -------------------------------------------------------
# 4. Run test queries
# -------------------------------------------------------
queries = [
    "How do AI models understand language?",   # Should match NLP/embeddings docs
    "Tell me about Italian culture and food",   # Should match pizza/Rome docs
    "What is deep learning?",                   # Should match ML/neural network docs
    "Landmarks in Europe",                      # Should match Eiffel Tower/Great Wall
]

for query in queries:
    print("=" * 65)
    print(f"QUERY: '{query}'")
    print("=" * 65)

    results = search(query, top_k=3)
    for result in results:
        bar = "█" * int(result["score"] * 20)
        print(f"  #{result['rank']} [{result['score']:.3f}] {bar}")
        print(f"      {result['document']}\n")

print("=" * 65)
print("SUCCESS! You just built a semantic search engine!")
print("Notice: It finds RELATED content even with different words.")
print("This is the foundation of tools like ChatGPT's file search.")
