import ollama

texts = [
    "Great eco-friendly packaging. Delivered right on time.",
    "The delivery partner was polite and helpful.",
    "Far too expensive for what you get.",
]

for text in texts:
    response = ollama.embed(
        model="nomic-embed-text",
        input=text,
    )

    embedding = response["embeddings"][0]

    print("\nTEXT:")
    print(text)

    print("\nVECTOR LENGTH:")
    print(len(embedding))

    print("\nFIRST 10 VALUES:")
    print(embedding[:10])