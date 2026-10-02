import json
import os
from datetime import datetime, timezone

import ollama
import snowflake.connector
from cryptography.hazmat.primitives import serialization
from dotenv import load_dotenv


# =========================================================
# CONFIGURATION
# =========================================================

load_dotenv("ai/.env")

MODEL = "llama3.2"

ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")
USER = os.getenv("SNOWFLAKE_USER")
DATABASE = os.getenv("SNOWFLAKE_DATABASE")
WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE")
SCHEMA = os.getenv("SNOWFLAKE_SCHEMA")
PRIVATE_KEY_PATH = os.getenv("SNOWFLAKE_PRIVATE_KEY_PATH")
PRIVATE_KEY_PASSPHRASE = os.getenv("SNOWFLAKE_PRIVATE_KEY_PASSPHRASE")


# =========================================================
# VALIDATE CONFIGURATION
# =========================================================

required_variables = {
    "SNOWFLAKE_ACCOUNT": ACCOUNT,
    "SNOWFLAKE_USER": USER,
    "SNOWFLAKE_DATABASE": DATABASE,
    "SNOWFLAKE_WAREHOUSE": WAREHOUSE,
    "SNOWFLAKE_SCHEMA": SCHEMA,
    "SNOWFLAKE_PRIVATE_KEY_PATH": PRIVATE_KEY_PATH,
    "SNOWFLAKE_PRIVATE_KEY_PASSPHRASE": PRIVATE_KEY_PASSPHRASE,
}

missing_variables = [
    name
    for name, value in required_variables.items()
    if not value
]

if missing_variables:
    raise ValueError(
        "Missing environment variables: "
        + ", ".join(missing_variables)
    )


# =========================================================
# LOAD SNOWFLAKE PRIVATE KEY
# =========================================================

print("Loading Snowflake private key...")

with open(PRIVATE_KEY_PATH, "rb") as key_file:
    private_key = serialization.load_pem_private_key(
        key_file.read(),
        password=PRIVATE_KEY_PASSPHRASE.encode(),
    )

private_key_bytes = private_key.private_bytes(
    encoding=serialization.Encoding.DER,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption(),
)

print("Private key loaded successfully.")


# =========================================================
# CONNECT TO SNOWFLAKE
# =========================================================

print("Connecting to Snowflake...")

conn = snowflake.connector.connect(
    account=ACCOUNT,
    user=USER,
    private_key=private_key_bytes,
    warehouse=WAREHOUSE,
    database=DATABASE,
    schema=SCHEMA,
)

cursor = conn.cursor()

print("Connected to Snowflake.")


# =========================================================
# CREATE AI SCHEMA
# =========================================================

cursor.execute("""
    CREATE SCHEMA IF NOT EXISTS ZOMATO_DB.AI
""")

print("AI schema ready.")


# =========================================================
# CREATE AI ENRICHMENT TABLE
# =========================================================

cursor.execute("""
    CREATE TABLE IF NOT EXISTS ZOMATO_DB.AI.REVIEW_ENRICHED (
        REVIEW_ID VARCHAR,
        SENTIMENT_LABEL VARCHAR,
        SENTIMENT_SCORE FLOAT,
        TOPIC VARCHAR,
        KEY_ISSUE VARCHAR,
        MODEL VARCHAR,
        ENRICHED_AT TIMESTAMP_NTZ
    )
""")

print("REVIEW_ENRICHED table ready.")


# =========================================================
# CLEAR PREVIOUS TEST RESULTS
# =========================================================
# We are currently working with the tutorial's 5-review
# experiment, so clear the previous partial test results.

cursor.execute("""
    TRUNCATE TABLE ZOMATO_DB.AI.REVIEW_ENRICHED
""")

conn.commit()

print("Previous test results cleared.")


# =========================================================
# FETCH 5 REAL REVIEWS FROM SNOWFLAKE
# =========================================================

print("Fetching 5 reviews from Snowflake...")

cursor.execute("""
    SELECT
        REVIEW_ID,
        RATING,
        COMMENT,
        REVIEW_DATE
    FROM ZOMATO_DB.RAW.REVIEWS_RAW
    WHERE COMMENT IS NOT NULL
    ORDER BY TRY_TO_NUMBER(REVIEW_ID)
    LIMIT 5
""")

reviews = cursor.fetchall()

print(f"Fetched {len(reviews)} reviews.")


if len(reviews) == 0:
    raise RuntimeError("No reviews were returned from Snowflake.")


# =========================================================
# AI ENRICHMENT FUNCTION
# =========================================================

def enrich_review(review_id, rating, comment):
    """
    Send one review to the local Llama model and return
    structured enrichment data.
    """

    prompt = f"""
You are analyzing a customer restaurant review.

Review ID:
{review_id}

Review:
{comment}

Customer Rating:
{rating}/5

Return ONLY valid JSON with exactly these fields:

{{
    "sentiment_label": "positive, negative, or neutral",
    "sentiment_score": 0.0,
    "topic": "food quality, delivery, pricing, service, packaging, or others",
    "key_issue": "short description of the main issue or positive point"
}}

Rules:
1. sentiment_label must be exactly one of:
   positive, negative, neutral

2. sentiment_score must be a number between -1 and 1.

3. topic must be one of:
   food quality, delivery, pricing, service, packaging, others

4. key_issue must be short.

5. Return JSON only.

6. Do not use markdown code fences.

7. Do not include explanations outside the JSON.
"""

    response = ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        format="json",
    )

    content = response["message"]["content"].strip()

    # -----------------------------------------------------
    # Parse JSON
    # -----------------------------------------------------

    try:
        result = json.loads(content)

    except json.JSONDecodeError:
        print("\nERROR: Model returned invalid JSON.")
        print("Raw model response:")
        print(content)
        raise

    # -----------------------------------------------------
    # Validate required fields
    # -----------------------------------------------------

    required_fields = [
        "sentiment_label",
        "sentiment_score",
        "topic",
        "key_issue",
    ]

    for field in required_fields:
        if field not in result:
            raise ValueError(
                f"Missing field '{field}' in model response."
            )

    # -----------------------------------------------------
    # Validate sentiment
    # -----------------------------------------------------

    valid_sentiments = {
        "positive",
        "negative",
        "neutral",
    }

    result["sentiment_label"] = (
        str(result["sentiment_label"])
        .strip()
        .lower()
    )

    if result["sentiment_label"] not in valid_sentiments:
        raise ValueError(
            f"Invalid sentiment: {result['sentiment_label']}"
        )

    # -----------------------------------------------------
    # Validate score
    # -----------------------------------------------------

    result["sentiment_score"] = float(
        result["sentiment_score"]
    )

    if not -1 <= result["sentiment_score"] <= 1:
        raise ValueError(
            f"Invalid sentiment score: "
            f"{result['sentiment_score']}"
        )

    # -----------------------------------------------------
    # Normalize text fields
    # -----------------------------------------------------

    result["topic"] = str(
        result["topic"]
    ).strip().lower()

    result["key_issue"] = str(
        result["key_issue"]
    ).strip()

    return result


# =========================================================
# PROCESS REVIEWS
# =========================================================

successful_count = 0

for review_id, rating, comment, review_date in reviews:

    print()
    print("=" * 60)
    print(f"Processing review {review_id}...")
    print("=" * 60)

    try:

        result = enrich_review(
            review_id=review_id,
            rating=rating,
            comment=comment,
        )

        print("AI result:")
        print(json.dumps(result, indent=2))

        # -------------------------------------------------
        # INSERT INTO SNOWFLAKE
        # -------------------------------------------------

        cursor.execute(
            """
            INSERT INTO ZOMATO_DB.AI.REVIEW_ENRICHED
            (
                REVIEW_ID,
                SENTIMENT_LABEL,
                SENTIMENT_SCORE,
                TOPIC,
                KEY_ISSUE,
                MODEL,
                ENRICHED_AT
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                str(review_id),
                result["sentiment_label"],
                result["sentiment_score"],
                result["topic"],
                result["key_issue"],
                MODEL,
                datetime.now(timezone.utc).replace(
                    tzinfo=None
                ),
            ),
        )

        conn.commit()

        successful_count += 1

        print(f"Review {review_id} inserted into Snowflake.")

    except Exception as error:

        print(
            f"ERROR processing review {review_id}: "
            f"{error}"
        )

        # Roll back only the failed database operation.
        conn.rollback()

        # Continue with the next review.
        continue


# =========================================================
# FINAL RESULT
# =========================================================

print()
print("=" * 60)
print("AI ENRICHMENT COMPLETE")
print("=" * 60)

print(
    f"Successfully processed: "
    f"{successful_count}/{len(reviews)} reviews"
)


# =========================================================
# VERIFY RESULTS FROM SNOWFLAKE
# =========================================================

cursor.execute("""
    SELECT
        REVIEW_ID,
        SENTIMENT_LABEL,
        SENTIMENT_SCORE,
        TOPIC,
        KEY_ISSUE,
        MODEL,
        ENRICHED_AT
    FROM ZOMATO_DB.AI.REVIEW_ENRICHED
    ORDER BY REVIEW_ID
""")

results = cursor.fetchall()


print()
print("--- SNOWFLAKE AI RESULTS ---")

for row in results:
    print(row)


# =========================================================
# CLOSE CONNECTION
# =========================================================

cursor.close()
conn.close()

print()
print("Snowflake connection closed.")
print("Pipeline finished.")