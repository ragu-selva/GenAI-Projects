"""
STEP 2: MEASURING SIMILARITY BETWEEN SENTENCES
================================================
What this does:
- Embeds multiple sentences
- Uses "cosine similarity" to measure how close they are
- Score range: 0.0 (opposite) → 1.0 (identical meaning)
"""

from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Load model
model = SentenceTransformer("all-MiniLM-L6-v2")

# -------------------------------------------------------
# Test pairs: (sentence_a, sentence_b, expected_result)
# -------------------------------------------------------
test_pairs = [
    # Pair 1: Very similar
    ("I love pizza",
     "Pizza is my favorite food",
     "HIGH similarity expected"),

    # Pair 2: Same topic, different phrasing
    ("The dog ran quickly",
     "The puppy sprinted fast",
     "HIGH similarity expected"),

    # Pair 3: Completely unrelated
    ("I love pizza",
     "The stock market crashed today",
     "LOW similarity expected"),

    # Pair 4: Tricky - same words, opposite meaning
    ("I love this movie",
     "I hate this movie",
     "MEDIUM similarity (same topic, opposite sentiment)"),

    # Pair 5: Synonyms
    ("The car is fast",
     "The automobile is speedy",
     "HIGH similarity expected"),
]

print("=" * 60)
print("COSINE SIMILARITY RESULTS")
print("=" * 60)
print("Score: 0.0 = completely different | 1.0 = identical\n")

for sentence_a, sentence_b, note in test_pairs:
    # Embed both sentences
    emb_a = model.encode([sentence_a])
    emb_b = model.encode([sentence_b])

    # Calculate cosine similarity
    score = cosine_similarity(emb_a, emb_b)[0][0]

    print(f"Sentence A: '{sentence_a}'")
    print(f"Sentence B: '{sentence_b}'")
    print(f"Similarity Score: {score:.4f}  ← {note}")
    print("-" * 60)

print("\nKEY INSIGHT:")
print("The model understands MEANING, not just matching words!")
print("'automobile' and 'car' score high even though they share no letters.")
print("\nRun 3_search.py to build a semantic search engine!")
