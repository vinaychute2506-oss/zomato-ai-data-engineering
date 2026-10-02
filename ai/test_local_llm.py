import ollama

response = ollama.chat(
    model="llama3.2",
    messages=[
        {
            "role": "user",
            "content": "Explain what a data warehouse is in 2 sentences."
        }
    ],
)

print("\n--- LLM RESPONSE ---\n")
print(response["message"]["content"])