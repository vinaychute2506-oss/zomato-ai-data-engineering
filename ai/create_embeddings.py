import json
import os

import ollama
import snowflake.connector
from cryptography.hazmat.primitives import serialization
from dotenv import load_dotenv


load_dotenv("ai/.env")


# =========================================================
# SNOWFLAKE CONNECTION
# =========================================================

def get_snowflake_connection():

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
# EMBEDDING
# =========================================================

def get_embedding(text):

    response = ollama.embed(
        model="nomic-embed-text",
        input=text,
    )

    embedding = response["embeddings"][0]

    if len(embedding) != 768:
        raise ValueError(
            f"Expected 768 dimensions, got {len(embedding)}"
        )

    return embedding


# =========================================================
# MAIN
# =========================================================

def main():

    print("\n========================================")
    print(" INCREMENTAL REVIEW EMBEDDING PIPELINE")
    print("========================================\n")

    conn = get_snowflake_connection()
    cursor = conn.cursor()

    print("Connected to Snowflake.\n")

    # -----------------------------------------------------
    # Find new OR changed reviews
    # -----------------------------------------------------

    cursor.execute(
        """
        SELECT
            r.REVIEW_ID,
            r.REVIEW_TEXT
        FROM ZOMATO_DB.AI.REVIEW_ENRICHED AS r
        LEFT JOIN ZOMATO_DB.AI.REVIEW_EMBEDDINGS AS e
            ON r.REVIEW_ID = e.REVIEW_ID
           AND r.REVIEW_TEXT = e.REVIEW_TEXT
        WHERE r.REVIEW_TEXT IS NOT NULL
          AND e.REVIEW_ID IS NULL
        ORDER BY TRY_TO_NUMBER(r.REVIEW_ID)
        """
    )

    reviews = cursor.fetchall()

    print(
        f"Reviews requiring embeddings: {len(reviews)}\n"
    )

    if not reviews:

        print(
            "No new or changed reviews require embeddings."
        )

        cursor.close()
        conn.close()

        return

    successful = 0
    failed = 0

    # -----------------------------------------------------
    # Generate embeddings
    # -----------------------------------------------------

    for review_id, review_text in reviews:

        print(
            f"Processing review {review_id}..."
        )

        try:

            embedding = get_embedding(
                review_text
            )

            embedding_json = json.dumps(
                [
                    float(value)
                    for value in embedding
                ]
            )

            # Remove any previous embedding for this ID.
            cursor.execute(
                """
                DELETE FROM ZOMATO_DB.AI.REVIEW_EMBEDDINGS
                WHERE REVIEW_ID = %s
                """,
                (review_id,),
            )

            # Insert the current embedding.
            cursor.execute(
                """
                INSERT INTO ZOMATO_DB.AI.REVIEW_EMBEDDINGS
                (
                    REVIEW_ID,
                    REVIEW_TEXT,
                    EMBEDDING,
                    MODEL,
                    EMBEDDED_AT
                )
                SELECT
                    %s,
                    %s,
                    PARSE_JSON(%s)::VECTOR(FLOAT, 768),
                    %s,
                    CURRENT_TIMESTAMP()
                """,
                (
                    review_id,
                    review_text,
                    embedding_json,
                    "nomic-embed-text",
                ),
            )

            conn.commit()

            successful += 1

            print(
                f"  ✓ Review {review_id} embedded"
            )

        except Exception as error:

            conn.rollback()

            failed += 1

            print(
                f"  ✗ Review {review_id} failed"
            )

            print(
                f"    {error}"
            )

    cursor.close()
    conn.close()

    print("\n========================================")
    print(" PIPELINE COMPLETE")
    print("========================================")

    print(f"Processed:  {len(reviews)}")
    print(f"Successful: {successful}")
    print(f"Failed:     {failed}")

    print()


if __name__ == "__main__":
    main()