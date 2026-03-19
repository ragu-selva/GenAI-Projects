"""
STEP 1: UNDERSTANDING BASIC EMBEDDINGS
=======================================
What this does:
- Loads a pretrained model from HuggingFace
- Converts sentences into number arrays (vectors)
- Shows you what those numbers look like
"""

from sentence_transformers import SentenceTransformer

# -------------------------------------------------------
# 1. Load a pretrained model from HuggingFace
#    'all-MiniLM-L6-v2' is small (80MB) but very capable
#    It downloads automatically on first run!
# -------------------------------------------------------
print("Loading model from HuggingFace...")
model = SentenceTransformer("all-MiniLM-L6-v2")
print("Model loaded!\n")

# -------------------------------------------------------
# 2. Define some sentences to embed
# -------------------------------------------------------
sentences = [
    "I love eating pizza",
    "Pizza is my favorite food",
    "The stock market crashed today",
    "Dogs are loyal animals",
    "Cats are independent pets",
]

# -------------------------------------------------------
# 3. Generate embeddings
#    Each sentence → a list of 384 numbers (a vector)
# -------------------------------------------------------
embeddings = model.encode(sentences)

# -------------------------------------------------------
# 4. Inspect the results
# -------------------------------------------------------
print(f"Number of sentences: {len(sentences)}")
print(f"Embedding shape: {embeddings.shape}")
print(f"  → {embeddings.shape[0]} sentences, each with {embeddings.shape[1]} numbers\n")

for i, (sentence, embedding) in enumerate(zip(sentences, embeddings)):
    print(f"Sentence {i+1}: '{sentence}'")
    print(f"  First 5 numbers: {embedding[:5].round(4)}")
    print(f"  Last  5 numbers: {embedding[-5:].round(4)}\n")

print("KEY INSIGHT: Similar sentences will have similar numbers!")
print("Run 2_similarity.py to prove it.")
