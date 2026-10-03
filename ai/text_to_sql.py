import json
import os
import re

import ollama
import snowflake.connector
from cryptography.hazmat.primitives import serialization
from dotenv import load_dotenv


# =========================================================
# ENVIRONMENT
# =========================================================

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
# GET MART SCHEMA
# =========================================================

def get_mart_schema():

    conn = get_snowflake_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            TABLE_NAME,
            COLUMN_NAME,
            DATA_TYPE
        FROM ZOMATO_DB.INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = 'MARTS'
          AND TABLE_NAME IN (
              'FCT_ORDERS',
              'DIM_USERS',
              'DIM_RESTAURANTS'
          )
        ORDER BY
            TABLE_NAME,
            ORDINAL_POSITION
        """
    )

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    schema = {}

    for table_name, column_name, data_type in rows:

        if table_name not in schema:
            schema[table_name] = []

        schema[table_name].append(
            f"{column_name} ({data_type})"
        )

    return schema


# =========================================================
# FORMAT SCHEMA
# =========================================================

def format_schema(schema):

    parts = []

    for table_name, columns in schema.items():

        parts.append(
            f"TABLE: ZOMATO_DB.MARTS.{table_name}\n"
            + "\n".join(
                f"  - {column}"
                for column in columns
            )
        )

    return "\n\n".join(parts)


# =========================================================
# GENERATE SQL
# =========================================================

def generate_sql(question, schema):

    schema_text = format_schema(schema)

    system_prompt = f"""
You are a Text-to-SQL assistant for a Zomato data warehouse.

Your job is to convert the user's natural-language question
into ONE correct, read-only Snowflake SQL query.

DATABASE SCHEMA:

{schema_text}

AVAILABLE TABLES:

1. ZOMATO_DB.MARTS.FCT_ORDERS

Important columns include:
- ORDER_ID
- USER_ID
- RESTAURANT_ID
- ORDER_TIMESTAMP
- ORDER_DATE
- RESTAURANT_CITY
- CUISINE
- ITEMS_COUNT
- SALES_QTY
- SUBTOTAL
- DISCOUNT
- DELIVERY_FEE
- GST
- SALES_AMOUNT
- CURRENCY
- PAYMENT_METHOD
- ORDER_STATUS
- CUSTOMER_RATING
- DELIVERY_TIME_MIN

2. ZOMATO_DB.MARTS.DIM_USERS

3. ZOMATO_DB.MARTS.DIM_RESTAURANTS

CRITICAL RULES:

1. Generate exactly ONE SQL query.

2. The query must start with SELECT or WITH.

3. The query must be READ-ONLY.

4. NEVER generate:
   INSERT
   UPDATE
   DELETE
   DROP
   ALTER
   TRUNCATE
   CREATE
   REPLACE
   GRANT
   REVOKE

5. NEVER invent a table.

6. NEVER invent a column.

7. Use the exact column names from the schema.

8. Do NOT create unnecessary CTEs.

9. Do NOT calculate information that the user did not request.

10. Do NOT use CROSS JOIN unless the user explicitly asks
    for a Cartesian combination.

11. For city-level analysis in FCT_ORDERS, use:
    RESTAURANT_CITY

12. For delivery time analysis, use:
    DELIVERY_TIME_MIN

13. For sales/revenue analysis, use:
    SALES_AMOUNT

14. For order counts, use:
    ORDER_ID

15. For cuisine analysis, use:
    CUISINE

16. When calculating averages, exclude NULL values when
    appropriate.

17. Use fully qualified table names.

18. Return JSON in exactly this format:

{{
    "sql": "SELECT ..."
}}

EXAMPLES:

Question:
How many orders are there?

Correct SQL:

SELECT COUNT(*) AS ORDER_COUNT
FROM ZOMATO_DB.MARTS.FCT_ORDERS;


Question:
What is the average delivery time by city?

Correct SQL:

SELECT
    RESTAURANT_CITY,
    AVG(DELIVERY_TIME_MIN) AS AVERAGE_DELIVERY_TIME
FROM ZOMATO_DB.MARTS.FCT_ORDERS
WHERE DELIVERY_TIME_MIN IS NOT NULL
GROUP BY RESTAURANT_CITY
ORDER BY AVERAGE_DELIVERY_TIME DESC;


Question:
What are the top 10 cities by sales?

Correct SQL:

SELECT
    RESTAURANT_CITY,
    SUM(SALES_AMOUNT) AS TOTAL_SALES
FROM ZOMATO_DB.MARTS.FCT_ORDERS
GROUP BY RESTAURANT_CITY
ORDER BY TOTAL_SALES DESC
LIMIT 10;


Question:
Which cuisine has the most orders?

Correct SQL:

SELECT
    CUISINE,
    COUNT(*) AS ORDER_COUNT
FROM ZOMATO_DB.MARTS.FCT_ORDERS
GROUP BY CUISINE
ORDER BY ORDER_COUNT DESC
LIMIT 1;

Return ONLY the JSON object.
"""

    response = ollama.chat(
        model="llama3.2",
        format="json",
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": question,
            },
        ],
    )

    raw_response = response["message"]["content"]

    data = json.loads(raw_response)

    sql = data.get("sql", "").strip()

    if not sql:
        raise ValueError(
            "The LLM did not return SQL."
        )

    sql = re.sub(
        r"^```(?:sql)?\s*",
        "",
        sql,
        flags=re.IGNORECASE,
    )

    sql = re.sub(
        r"\s*```$",
        "",
        sql,
    )

    return sql.strip()


# =========================================================
# SQL SAFETY CHECK
# =========================================================

FORBIDDEN_WORDS = [
    "DROP",
    "DELETE",
    "TRUNCATE",
    "ALTER",
    "UPDATE",
    "INSERT",
    "CREATE",
    "REPLACE",
    "GRANT",
    "REVOKE",
]


def is_safe_sql(sql):

    cleaned = sql.strip()

    if not cleaned:
        return False, "SQL is empty."

    lowered = cleaned.lower()

    if not (
        lowered.startswith("select")
        or lowered.startswith("with")
    ):
        return False, (
            "Only SELECT or WITH queries are allowed."
        )

    statements = [
        statement.strip()
        for statement in cleaned.split(";")
        if statement.strip()
    ]

    if len(statements) > 1:
        return False, (
            "Multiple SQL statements are not allowed."
        )

    for word in FORBIDDEN_WORDS:

        pattern = rf"\b{word.lower()}\b"

        if re.search(pattern, lowered):

            return False, (
                f"Forbidden SQL operation detected: {word}"
            )

    return True, "SQL passed safety checks."


# =========================================================
# EXECUTE SQL
# =========================================================

def run_query(sql):

    conn = get_snowflake_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(sql)

        rows = cursor.fetchall()

        columns = [
            column[0]
            for column in cursor.description
        ]

        return columns, rows

    finally:

        cursor.close()
        conn.close()


# =========================================================
# DISPLAY RESULTS
# =========================================================

def print_results(columns, rows):

    print("\nQUERY RESULT:")
    print("-" * 70)

    if not rows:

        print("No rows returned.")
        return

    print(
        " | ".join(
            str(column)
            for column in columns
        )
    )

    print("-" * 70)

    for row in rows[:20]:

        print(
            " | ".join(
                str(value)
                for value in row
            )
        )

    if len(rows) > 20:

        print(
            f"\nShowing first 20 of {len(rows)} rows."
        )


# =========================================================
# MAIN
# =========================================================

def main():

    print("\n========================================")
    print("       ZOMATO TEXT-TO-SQL")
    print("========================================")

    print("\nLoading warehouse schema...")

    schema = get_mart_schema()

    print(
        f"Loaded {len(schema)} MARTS tables."
    )

    print("\nAvailable tables:")

    for table_name in schema:

        print(
            f"  - ZOMATO_DB.MARTS.{table_name}"
        )

    question = input(
        "\nAsk a question about your Zomato data: "
    ).strip()

    if not question:

        print("No question entered.")
        return

    print("\nGenerating SQL with llama3.2...")

    sql = generate_sql(
        question,
        schema,
    )

    print("\nGENERATED SQL:")
    print("-" * 70)
    print(sql)
    print("-" * 70)

    safe, reason = is_safe_sql(sql)

    print(
        f"\nSAFETY CHECK: {reason}"
    )

    if not safe:

        print("\nQuery was blocked.")
        return

    print(
        "\nExecuting query in Snowflake..."
    )

    try:

        columns, rows = run_query(sql)

        print(
            f"Returned {len(rows)} row(s)."
        )

        print_results(
            columns,
            rows,
        )

    except Exception as error:

        print("\nERROR EXECUTING SQL:")
        print(error)

    print(
        "\n========================================"
    )

    print("              COMPLETE")

    print(
        "========================================\n"
    )


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":
    main()