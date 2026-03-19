"""
VECTOR STORE 1: ChromaDB
=========================
ChromaDB = A local database that stores embeddings on disk.
Think of it like SQLite but for vectors.

HOW IT DIFFERS FROM 3_search.py:
  Before: embeddings lived in RAM → lost when script ends
  Now:    embeddings saved to disk → available forever

FLOW:
  Documents → Embed → Store in ChromaDB → Query anytime
"""

import chromadb
from sentence_transformers import SentenceTransformer

# -------------------------------------------------------
# Our knowledge base (same as 3_search.py)
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
]

# Metadata for each document (extra info stored alongside vectors)
metadatas = [
    {"category": "technology", "language": "english"},
    {"category": "AI",         "language": "english"},
    {"category": "travel",     "language": "english"},
    {"category": "AI",         "language": "english"},
    {"category": "food",       "language": "english"},
    {"category": "AI",         "language": "english"},
    {"category": "travel",     "language": "english"},
    {"category": "AI",         "language": "english"},
    {"category": "travel",     "language": "english"},
    {"category": "AI",         "language": "english"},
]

# -------------------------------------------------------
# STEP 1: Load embedding model
# -------------------------------------------------------
print("Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

# -------------------------------------------------------
# STEP 2: Create ChromaDB client
#   PersistentClient = saves to disk at given folder path
#   Next time you run this script, data is already there!
# -------------------------------------------------------
print("Connecting to ChromaDB...")
client = chromadb.PersistentClient(path="./chroma_db")  # saved to local folder

# -------------------------------------------------------
# STEP 3: Create a Collection
#   Collection = like a "table" in SQL, or a "folder" for vectors
#   delete_collection first so we start fresh on each run
# -------------------------------------------------------
try:
    client.delete_collection("knowledge_base")  # fresh start
except:
    pass

collection = client.create_collection(
    name="knowledge_base",
    metadata={"hnsw:space": "cosine"}  # use cosine similarity for search
)
print(f"Created collection: 'knowledge_base'\n")

# -------------------------------------------------------
# STEP 4: Embed and Store documents
#   Each document needs:
#     - id         : unique string identifier
#     - embedding  : the vector (list of numbers)
#     - document   : the original text
#     - metadata   : any extra info you want to store
# -------------------------------------------------------
print("Embedding and storing documents...")
embeddings = model.encode(documents).tolist()  # ChromaDB needs plain lists

collection.add(
    ids        = [f"doc_{i}" for i in range(len(documents))],  # ["doc_0", "doc_1", ...]
    embeddings = embeddings,
    documents  = documents,
    metadatas  = metadatas
)
print(f"Stored {collection.count()} documents in ChromaDB\n")

# -------------------------------------------------------
# STEP 5: Query the collection
#   ChromaDB embeds your query and finds closest vectors
# -------------------------------------------------------
def search_chroma(query: str, top_k: int = 3, filter_category: str = None):
    query_embedding = model.encode([query]).tolist()

    # Optional: filter by metadata category
    where_filter = {"category": filter_category} if filter_category else None

    results = collection.query(
        query_embeddings = query_embedding,
        n_results        = top_k,
        where            = where_filter,  # metadata filter!
        include          = ["documents", "distances", "metadatas"]
    )
    return results

# -------------------------------------------------------
# STEP 6: Run searches
# -------------------------------------------------------
print("=" * 60)
print("SEARCH 1: General query")
print("=" * 60)
results = search_chroma("How does AI understand language?", top_k=3)
for i, (doc, dist) in enumerate(zip(results["documents"][0], results["distances"][0])):
    score = 1 - dist   # ChromaDB returns distance, not similarity (lower=closer)
    print(f"  #{i+1} Score: {score:.3f} | {doc}")

print()
print("=" * 60)
print("SEARCH 2: Filter by category='travel' only")
print("=" * 60)
results = search_chroma("Famous landmarks", top_k=3, filter_category="travel")
for i, (doc, dist, meta) in enumerate(zip(
    results["documents"][0],
    results["distances"][0],
    results["metadatas"][0]
)):
    score = 1 - dist
    print(f"  #{i+1} Score: {score:.3f} | Category: {meta['category']} | {doc}")

print()
print("=" * 60)
print(f"ChromaDB saved to: ./chroma_db/")
print("Run this script again — documents load instantly from disk!")
print("=" * 60)