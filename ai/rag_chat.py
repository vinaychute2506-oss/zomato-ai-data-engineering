import json
import os

import ollama
import snowflake.connector
from cryptography.hazmat.primitives import serialization
from dotenv import load_dotenv


# =========================================================
# LOAD ENVIRONMENT
# =========================================================

load_dotenv("ai/.env")


# =========================================================
# SNOWFLAKE CONNECTION
# =========================================================

def get_snowflake_connection():
    """Connect to Snowflake using the RSA private key."""

    private_key_path = os.environ["SNOWFLAKE_PRIVATE_KEY_PATH"]
    private_key_passphrase = os.environ[
        "SNOWFLAKE_PRIVATE_KEY_PASSPHRASE"
    ]

    with open(private_key_path, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=private_key_passphrase.encode(),
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


# =========================================================
# QUERY EMBEDDING
# =========================================================

def get_query_embedding(query):
    """Generate a 768-dimensional embedding for the query."""

    response = ollama.embed(
        model="nomic-embed-text",
        input=query,
    )

    embedding = response["embeddings"][0]

    if len(embedding) != 768:
        raise ValueError(
            f"Expected 768 dimensions, got {len(embedding)}"
        )

    return embedding


# =========================================================
# RETRIEVE REVIEWS
# =========================================================

def retrieve_reviews(query, top_k=3):

    print("\nGenerating query embedding...")

    query_embedding = get_query_embedding(query)

    # Convert Python list into JSON.
    embedding_json = json.dumps(
        [float(value) for value in query_embedding]
    )

    print("Searching stored review embeddings...")

    conn = get_snowflake_connection()
    cursor = conn.cursor()

    sql = """
        SELECT
            e.REVIEW_ID AS REVIEW_ID,
            e.REVIEW_TEXT AS REVIEW_TEXT,
            r.SENTIMENT_LABEL AS SENTIMENT_LABEL,
            r.TOPIC AS TOPIC,
            r.KEY_ISSUE AS KEY_ISSUE,
            VECTOR_COSINE_SIMILARITY(
                e.EMBEDDING,
                PARSE_JSON(%s)::VECTOR(FLOAT, 768)
            ) AS SIMILARITY_SCORE
        FROM ZOMATO_DB.AI.REVIEW_EMBEDDINGS AS e
        INNER JOIN ZOMATO_DB.AI.REVIEW_ENRICHED AS r
            ON e.REVIEW_ID = r.REVIEW_ID
        WHERE e.EMBEDDING IS NOT NULL
        ORDER BY SIMILARITY_SCORE DESC
        LIMIT %s
    """

    cursor.execute(
        sql,
        (
            embedding_json,
            top_k,
        ),
    )

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    results = []

    for row in rows:

        (
            review_id,
            review_text,
            sentiment,
            topic,
            key_issue,
            similarity_score,
        ) = row

        results.append(
            {
                "review_id": review_id,
                "review_text": review_text,
                "sentiment": sentiment,
                "topic": topic,
                "key_issue": key_issue,
                "score": float(similarity_score),
            }
        )

    return results


# =========================================================
# GENERATE LLM ANSWER
# =========================================================

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
Similarity score: {review["score"]:.4f}
"""
        )

    context = "\n".join(context_parts)

    prompt = f"""
You are a data assistant analyzing Zomato customer reviews.

Answer the user's question using ONLY the retrieved review context.

Do not invent facts.

If the retrieved context does not contain enough information,
say that the available reviews do not provide enough information.

Mention relevant review IDs when useful.

Retrieved review context:

{context}

User question:

{query}

Give a concise and factual answer.
"""

    print("\nGenerating answer with llama3.2...\n")

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


# =========================================================
# MAIN
# =========================================================

def main():

    print("\n========================================")
    print("          ZOMATO RAG CHAT")
    print("========================================")

    query = input(
        "\nAsk about the reviews: "
    ).strip()

    if not query:
        print("Please enter a question.")
        return

    # Retrieve relevant reviews
    retrieved_reviews = retrieve_reviews(
        query,
        top_k=3,
    )

    if not retrieved_reviews:
        print("\nNo reviews were found.")
        return

    # Display retrieved reviews
    print("\nTOP MATCHING REVIEWS:")
    print("-" * 60)

    for review in retrieved_reviews:

        print(
            f"Score: {review['score']:.4f}"
        )

        print(
            f"Review ID: {review['review_id']}"
        )

        print(
            f"Review: {review['review_text']}"
        )

        print(
            f"Sentiment: {review['sentiment']}"
        )

        print(
            f"Topic: {review['topic']}"
        )

        print(
            f"Key issue: {review['key_issue']}"
        )

        print("-" * 60)

    # Generate final answer
    answer = generate_answer(
        query,
        retrieved_reviews,
    )

    print("\nANSWER:")
    print(answer)

    print("\n========================================")
    print("              COMPLETE")
    print("========================================\n")


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":
    main()