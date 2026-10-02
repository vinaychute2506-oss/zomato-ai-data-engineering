import os

import numpy as np
import ollama
import snowflake.connector
from dotenv import load_dotenv
from cryptography.hazmat.primitives import serialization


load_dotenv("ai/.env")


def get_snowflake_connection():
    with open(
        os.environ["SNOWFLAKE_PRIVATE_KEY_PATH"],
        "rb",
    ) as key_file:

        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=os.environ[
                "SNOWFLAKE_PRIVATE_KEY_PASSPHRASE"
            ].encode(),
        )

    private_key_der = private_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    return snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        private_key=private_key_der,
        database=os.environ["SNOWFLAKE_DATABASE"],
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
        schema=os.environ["SNOWFLAKE_SCHEMA"],
    )


def get_embedding(text):
    response = ollama.embed(
        model="nomic-embed-text",
        input=text,
    )

    return np.array(
        response["embeddings"][0]
    )


def cosine_similarity(a, b):
    return np.dot(a, b) / (
        np.linalg.norm(a)
        * np.linalg.norm(b)
    )


def retrieve_reviews(query, top_k=3):

    conn = get_snowflake_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            REVIEW_ID,
            REVIEW_TEXT,
            SENTIMENT_LABEL,
            TOPIC,
            KEY_ISSUE
        FROM ZOMATO_DB.AI.REVIEW_ENRICHED
        WHERE REVIEW_TEXT IS NOT NULL
        ORDER BY TRY_TO_NUMBER(REVIEW_ID)
        """
    )

    reviews = cursor.fetchall()

    cursor.close()
    conn.close()

    query_embedding = get_embedding(query)

    results = []

    for (
        review_id,
        review_text,
        sentiment,
        topic,
        key_issue,
    ) in reviews:

        review_embedding = get_embedding(
            review_text
        )

        score = cosine_similarity(
            query_embedding,
            review_embedding,
        )

        results.append(
            {
                "score": score,
                "review_id": review_id,
                "review_text": review_text,
                "sentiment": sentiment,
                "topic": topic,
                "key_issue": key_issue,
            }
        )

    results.sort(
        key=lambda x: x["score"],
        reverse=True,
    )

    return results[:top_k]


def generate_answer(query, retrieved_reviews):

    context_parts = []

    for review in retrieved_reviews:

        context_parts.append(
            f"""
Review ID: {review["review_id"]}
Review: {review["review_text"]}
Sentiment: {review["sentiment"]}
Topic: {review["topic"]}
Key issue: {review["key_issue"]}
"""
        )

    context = "\n".join(context_parts)

    prompt = f"""
You are a data assistant analyzing Zomato customer reviews.

Answer the user's question using ONLY the retrieved review context below.

If the context does not contain enough information to answer,
say that the available reviews do not provide enough information.

Do not invent facts.

Retrieved review context:
{context}

User question:
{query}

Give a concise answer and mention the relevant review IDs when useful.
"""

    response = ollama.chat(
        model="llama3.2",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    return response["message"]["content"]


def main():

    query = input(
        "\nAsk about the reviews: "
    )

    print("\nSearching reviews...\n")

    retrieved_reviews = retrieve_reviews(
        query,
        top_k=3,
    )

    print("Retrieved reviews:")

    for review in retrieved_reviews:

        print(
            f'{review["score"]:.4f} '
            f'→ Review {review["review_id"]}: '
            f'{review["review_text"]}'
        )

    print("\nGenerating answer...\n")

    answer = generate_answer(
        query,
        retrieved_reviews,
    )

    print("ANSWER:")
    print(answer)


if __name__ == "__main__":
    main()