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
            password=os.environ["SNOWFLAKE_PRIVATE_KEY_PASSPHRASE"].encode(),
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

    return np.array(response["embeddings"][0])


def cosine_similarity(a, b):
    return np.dot(a, b) / (
        np.linalg.norm(a) * np.linalg.norm(b)
    )


def main():

    query = input("\nAsk about the reviews: ")

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

    for review_id, review_text, sentiment, topic, key_issue in reviews:

        review_embedding = get_embedding(review_text)

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

    print("\nTOP MATCHING REVIEWS:\n")

    for result in results[:3]:

        print(
            f"Score: {result['score']:.4f}"
        )

        print(
            f"Review ID: {result['review_id']}"
        )

        print(
            f"Review: {result['review_text']}"
        )

        print(
            f"Sentiment: {result['sentiment']}"
        )

        print(
            f"Topic: {result['topic']}"
        )

        print(
            f"Key issue: {result['key_issue']}"
        )

        print("-" * 60)


if __name__ == "__main__":
    main()