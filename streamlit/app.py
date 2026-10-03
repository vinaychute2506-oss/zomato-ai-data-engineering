import json
import os
import re

import ollama
import pandas as pd
import snowflake.connector
import streamlit as st

from cryptography.hazmat.primitives import serialization
from dotenv import load_dotenv


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv("ai/.env")

EMBED_MODEL = "nomic-embed-text"
CHAT_MODEL = "llama3.2"

DATABASE = "ZOMATO_DB"
WAREHOUSE = os.environ["SNOWFLAKE_WAREHOUSE"]


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Zomato AI Data Assistant",
    page_icon="🍽️",
    layout="wide",
)


# ============================================================
# CUSTOM HEADER
# ============================================================

st.title("🍽️ Zomato AI Data Assistant")

st.caption(
    "Local LLM + RAG + Text-to-SQL + Snowflake"
)

st.divider()


# ============================================================
# SNOWFLAKE CONNECTION
# ============================================================

@st.cache_resource
def get_snowflake_connection():

    private_key_path = os.environ[
        "SNOWFLAKE_PRIVATE_KEY_PATH"
    ]

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
        database=DATABASE,
        warehouse=WAREHOUSE,
    )


# ============================================================
# GENERIC SNOWFLAKE QUERY
# ============================================================

def run_query(sql):

    conn = get_snowflake_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(sql)

        rows = cursor.fetchall()

        if cursor.description:

            columns = [
                column[0]
                for column in cursor.description
            ]

        else:

            columns = []

        return columns, rows

    finally:

        cursor.close()


# ============================================================
# EMBEDDING
# ============================================================

def create_embedding(text):

    response = ollama.embed(
        model=EMBED_MODEL,
        input=text,
    )

    return response["embeddings"][0]


# ============================================================
# COSINE SIMILARITY
# ============================================================

def cosine_similarity(vector_a, vector_b):

    dot_product = sum(
        a * b
        for a, b in zip(vector_a, vector_b)
    )

    magnitude_a = sum(
        a * a
        for a in vector_a
    ) ** 0.5

    magnitude_b = sum(
        b * b
        for b in vector_b
    ) ** 0.5

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (
        magnitude_a * magnitude_b
    )


# ============================================================
# LOAD REVIEW EMBEDDINGS
# ============================================================

@st.cache_data
def load_review_embeddings():

    sql = """
    SELECT
        REVIEW_ID,
        REVIEW_TEXT,
        EMBEDDING
    FROM ZOMATO_DB.AI.REVIEW_EMBEDDINGS
    ORDER BY TRY_TO_NUMBER(REVIEW_ID)
    """

    columns, rows = run_query(sql)

    reviews = []

    for row in rows:

        review_id = row[0]
        review_text = row[1]
        embedding = row[2]

        if isinstance(embedding, str):

            embedding = embedding.strip()

            if embedding.startswith("["):
                embedding = json.loads(embedding)

        embedding = list(embedding)

        reviews.append(
            {
                "review_id": review_id,
                "review_text": review_text,
                "embedding": embedding,
            }
        )

    return reviews


# ============================================================
# RAG RETRIEVAL
# ============================================================

def retrieve_reviews(question, top_k=3):

    query_embedding = create_embedding(question)

    reviews = load_review_embeddings()

    results = []

    for review in reviews:

        score = cosine_similarity(
            query_embedding,
            review["embedding"],
        )

        results.append(
            {
                "review_id": review["review_id"],
                "review_text": review["review_text"],
                "score": score,
            }
        )

    results.sort(
        key=lambda x: x["score"],
        reverse=True,
    )

    return results[:top_k]


# ============================================================
# RAG ANSWER
# ============================================================

def generate_rag_answer(question, retrieved_reviews):

    context = "\n\n".join(
        [
            (
                f"Review ID: {review['review_id']}\n"
                f"Review: {review['review_text']}"
            )
            for review in retrieved_reviews
        ]
    )

    prompt = f"""
You are a Zomato review assistant.

Answer the user's question using ONLY the review
context provided below.

Do not invent reviews or information.

If the context does not contain enough information,
say that the available reviews do not provide enough
information.

REVIEW CONTEXT:

{context}

USER QUESTION:

{question}

Give a concise answer and mention relevant review IDs.
"""

    response = ollama.chat(
        model=CHAT_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    return response["message"]["content"]


# ============================================================
# TEXT-TO-SQL SCHEMA
# ============================================================

def get_mart_schema():

    sql = """
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

    columns, rows = run_query(sql)

    schema = {}

    for table_name, column_name, data_type in rows:

        if table_name not in schema:
            schema[table_name] = []

        schema[table_name].append(
            f"{column_name} ({data_type})"
        )

    return schema


# ============================================================
# TEXT-TO-SQL GENERATION
# ============================================================

def generate_sql(question, schema):

    schema_text = ""

    for table_name, columns in schema.items():

        schema_text += (
            f"\nTABLE: ZOMATO_DB.MARTS.{table_name}\n"
        )

        for column in columns:

            schema_text += f"  - {column}\n"

    prompt = f"""
You are a Snowflake Text-to-SQL assistant.

Convert the user's question into ONE read-only SQL query.

DATABASE SCHEMA:

{schema_text}

RULES:

1. Only SELECT or WITH queries are allowed.
2. Never use INSERT.
3. Never use UPDATE.
4. Never use DELETE.
5. Never use DROP.
6. Never use ALTER.
7. Never use TRUNCATE.
8. Never use CREATE.
9. Never use REPLACE.
10. Never use GRANT.
11. Never use REVOKE.
12. Never invent tables.
13. Never invent columns.
14. Use exact column names from the schema.
15. Use fully qualified table names.
16. Return JSON only.

The JSON must be:

{{
    "sql": "SELECT ..."
}}

USER QUESTION:

{question}
"""

    response = ollama.chat(
        model=CHAT_MODEL,
        format="json",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    data = json.loads(
        response["message"]["content"]
    )

    sql = data.get("sql", "").strip()

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


# ============================================================
# SQL SAFETY
# ============================================================

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


def validate_sql(sql):

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

        if re.search(
            rf"\b{word.lower()}\b",
            lowered,
        ):

            return False, (
                f"Forbidden SQL operation: {word}"
            )

    return True, "SQL passed safety checks."


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("AI Features")

    st.markdown(
        """
        **Available**

        🧠 Review RAG  
        Search reviews using semantic similarity.

        📊 Text-to-SQL  
        Ask questions about the warehouse
        using natural language.
        """
    )

    st.divider()

    st.subheader("Example questions")

    st.markdown(
        """
        **RAG**

        • Which reviews talk about delivery?

        • What do customers say about packaging?

        • Are there reviews about expensive food?

        **Text-to-SQL**

        • How many orders are there?

        • What is the average delivery time by city?

        • Which cuisine has the most orders?

        • What are the top 10 cities by sales?
        """
    )


# ============================================================
# TABS
# ============================================================

rag_tab, sql_tab = st.tabs(
    [
        "🧠 Review RAG",
        "📊 Data Chat",
    ]
)


# ============================================================
# RAG TAB
# ============================================================

with rag_tab:

    st.header("Chat with Zomato Reviews")

    st.caption(
        "Semantic search powered by "
        "nomic-embed-text + Llama 3.2"
    )

    rag_question = st.text_input(
        "Ask something about the reviews",
        placeholder=(
            "Which reviews talk about delivery?"
        ),
        key="rag_question",
    )

    if st.button(
        "Search Reviews",
        key="rag_button",
        type="primary",
    ):

        if not rag_question.strip():

            st.warning(
                "Please enter a question."
            )

        else:

            with st.spinner(
                "Searching review embeddings..."
            ):

                try:

                    retrieved = retrieve_reviews(
                        rag_question,
                        top_k=3,
                    )

                    st.subheader(
                        "Retrieved Reviews"
                    )

                    for review in retrieved:

                        st.write(
                            f"**Review {review['review_id']}** "
                            f"— similarity "
                            f"{review['score']:.4f}"
                        )

                        st.write(
                            review["review_text"]
                        )

                        st.divider()

                    with st.spinner(
                        "Generating answer..."
                    ):

                        answer = generate_rag_answer(
                            rag_question,
                            retrieved,
                        )

                    st.subheader("Answer")

                    st.write(answer)

                except Exception as error:

                    st.error(
                        f"RAG error: {error}"
                    )


# ============================================================
# TEXT-TO-SQL TAB
# ============================================================

with sql_tab:

    st.header("Chat with Zomato Data")

    st.caption(
        "Natural language → SQL → Snowflake"
    )

    sql_question = st.text_input(
        "Ask a question about your Zomato data",
        placeholder=(
            "What is the average delivery time by city?"
        ),
        key="sql_question",
    )

    if st.button(
        "Ask Data",
        key="sql_button",
        type="primary",
    ):

        if not sql_question.strip():

            st.warning(
                "Please enter a question."
            )

        else:

            try:

                with st.spinner(
                    "Loading warehouse schema..."
                ):

                    schema = get_mart_schema()

                with st.spinner(
                    "Generating SQL with Llama 3.2..."
                ):

                    generated_sql = generate_sql(
                        sql_question,
                        schema,
                    )

                st.subheader("Generated SQL")

                st.code(
                    generated_sql,
                    language="sql",
                )

                safe, reason = validate_sql(
                    generated_sql
                )

                if not safe:

                    st.error(
                        f"Query blocked: {reason}"
                    )

                else:

                    st.success(
                        "SQL passed safety checks."
                    )

                    with st.spinner(
                        "Executing query in Snowflake..."
                    ):

                        columns, rows = run_query(
                            generated_sql
                        )

                    st.subheader("Query Result")

                    if rows:

                        dataframe = pd.DataFrame(
                            rows,
                            columns=columns,
                        )

                        st.dataframe(
                            dataframe,
                            use_container_width=True,
                        )

                        st.caption(
                            f"{len(rows)} row(s) returned."
                        )

                    else:

                        st.info(
                            "The query returned no rows."
                        )

            except Exception as error:

                st.error(
                    f"Text-to-SQL error: {error}"
                )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Zomato AI Data Engineering Project • "
    "Snowflake + dbt + Airflow + Docker + Ollama + Streamlit"
)