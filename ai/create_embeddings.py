import json
import os

import ollama
import snowflake.connector
from cryptography.hazmat.primitives import serialization
from dotenv import load_dotenv


# ---------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------

load_dotenv("ai/.env")


# ---------------------------------------------------------
# Snowflake connection
# ---------------------------------------------------------

def get_snowflake_connection():
    """Create a Snowflake connection using the encrypted
    Snowflake private key."""

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

    connection = snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        private_key=private_key_der,
        database=os.environ["SNOWFLAKE_DATABASE"],
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
        schema=os.environ["SNOWFLAKE_SCHEMA"],
    )

    return connection


# ---------------------------------------------------------
# Generate embedding
# ---------------------------------------------------------

def get_embedding(text):
    """Generate a 768-dimensional embedding using
    the local Ollama embedding model."""

    response = ollama.embed(
        model="nomic-embed-text",
        input=text,
    )

    return response["embeddings"][0]


# ---------------------------------------------------------
# Main embedding pipeline
# ---------------------------------------------------------

def main():

    print("\n========================================")
    print(" ZOMATO REVIEW EMBEDDING PIPELINE")
    print("========================================\n")

    # Connect to Snowflake
    print("Connecting to Snowflake...")

    conn = get_snowflake_connection()
    cursor = conn.cursor()

    print("Snowflake connection successful.\n")

    # -----------------------------------------------------
    # Clear previous embeddings
    # -----------------------------------------------------

    print("Clearing existing embeddings...")

    cursor.execute(
        """
        TRUNCATE TABLE ZOMATO_DB.AI.REVIEW_EMBEDDINGS
        """
    )

    conn.commit()

    print("Embedding table cleared.\n")

    # -----------------------------------------------------
    # Fetch reviews
    # -----------------------------------------------------

    cursor.execute(
        """
        SELECT
            REVIEW_ID,
            REVIEW_TEXT
        FROM ZOMATO_DB.AI.REVIEW_ENRICHED
        WHERE REVIEW_TEXT IS NOT NULL
        ORDER BY TRY_TO_NUMBER(REVIEW_ID)
        """
    )

    reviews = cursor.fetchall()

    print(f"Found {len(reviews)} reviews.\n")

    # -----------------------------------------------------
    # Generate and store embeddings
    # -----------------------------------------------------

    successful = 0
    failed = 0

    for review_id, review_text in reviews:

        print(f"Embedding review {review_id}...")

        try:

            # Generate embedding using Ollama
            embedding = get_embedding(review_text)

            # Validate vector size
            if len(embedding) != 768:
                raise ValueError(
                    f"Expected 768 dimensions, "
                    f"received {len(embedding)}"
                )

            # Convert Python list to JSON
            embedding_json = json.dumps(
                [float(value) for value in embedding]
            )

            # Insert embedding into Snowflake.
            #
            # PARSE_JSON converts the JSON string into
            # a Snowflake value which can then be converted
            # to VECTOR(FLOAT, 768).
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
                f"  ✓ Review {review_id} stored "
                f"(768 dimensions)"
            )

        except Exception as error:

            failed += 1

            print(
                f"  ✗ Review {review_id} failed:"
            )

            print(
                f"    {error}"
            )

    # -----------------------------------------------------
    # Close connection
    # -----------------------------------------------------

    cursor.close()
    conn.close()

    # -----------------------------------------------------
    # Final status
    # -----------------------------------------------------

    print("\n========================================")
    print(" EMBEDDING PIPELINE COMPLETE")
    print("========================================")

    print(f"Successful: {successful}")
    print(f"Failed:     {failed}")
    print(f"Total:      {len(reviews)}")

    print("\n")


# ---------------------------------------------------------
# Entry point
# ---------------------------------------------------------

if __name__ == "__main__":
    main()