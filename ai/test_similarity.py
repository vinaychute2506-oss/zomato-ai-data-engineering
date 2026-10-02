import ollama
import numpy as np


texts = [
    "Great eco-friendly packaging. Delivered right on time.",
    "The delivery partner was polite and helpful.",
    "Far too expensive for what you get.",
]

query = "Which review talks about delivery?"


def get_embedding(text):
    response = ollama.embed(
        model="nomic-embed-text",
        input=text,
    )
    return np.array(response["embeddings"][0])


def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


query_embedding = get_embedding(query)

results = []

for text in texts:
    text_embedding = get_embedding(text)

    score = cosine_similarity(
        query_embedding,
        text_embedding,
    )

    results.append((score, text))


results.sort(reverse=True)


print("\nQUERY:")
print(query)

print("\nSIMILARITY RESULTS:")

for score, text in results:
    print(f"{score:.4f} -> {text}")