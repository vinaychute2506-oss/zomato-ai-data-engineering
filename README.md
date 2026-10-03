# Zomato AI Data Engineering Pipeline

An end-to-end cloud and AI-driven data engineering pipeline inspired by a large-scale food-delivery platform.

The project demonstrates how raw transactional data can be ingested into cloud storage, loaded into Snowflake, transformed with dbt, orchestrated with Apache Airflow, enriched with a local LLM, exposed through RAG and Text-to-SQL capabilities, and presented through Streamlit.

---

## Architecture

```text
CSV Dataset
    |
    v
Amazon S3
    |
    v
Snowflake RAW / Bronze
    |
    v
dbt STAGING / Silver
    |
    v
dbt MARTS / Gold
    |
    +----------------------+
    |                      |
    v                      v
AI Layer              Analytics
    |                      |
    +----------+-----------+
               |
               v
          Streamlit
               
        ^
        |
Apache Airflow
(Docker orchestration)

The architecture follows an ELT and medallion-style approach:

RAW / Bronze — raw data landing layer
STAGING / Silver — cleaned and standardized data
MARTS / Gold — analytical and dimensional models
AI Layer — LLM enrichment, embeddings, RAG and Text-to-SQL
Streamlit — interactive user-facing application
Airflow — workflow orchestration
Project Goals

The project was built to demonstrate practical data engineering skills across:

Cloud data ingestion
Data warehousing
SQL transformation
Dimensional modeling
Data quality testing
Incremental processing
Workflow orchestration
Containerization
Local LLM integration
Vector embeddings
Retrieval-Augmented Generation (RAG)
Natural-language-to-SQL
Interactive analytics
Technology Stack
Technology	Purpose
Python	Pipeline and AI application logic
Amazon S3	Raw cloud data storage
Snowflake	Cloud data warehouse
dbt	SQL transformation, testing and modeling
Apache Airflow	Pipeline orchestration
Docker	Containerized Airflow environment
Ollama	Local LLM inference
Llama 3.2	Local language model
nomic-embed-text	Text embeddings
Streamlit	Interactive application
Git/GitHub	Version control and portfolio
Dataset

The project uses a synthetic Zomato-style dataset containing approximately 35 million records across seven entities.

Dataset	Approx. Rows
Users	100,000
Restaurants	148,541
Food	371,561
Menu	1,179,936
Reviews	300,000
Order Items	22,998,179
Orders	10,000,000

The largest tables are orders and order_items, providing a realistic large-volume workload for the pipeline.

Data Engineering Pipeline
1. Amazon S3

Raw CSV files are organized in S3 by entity:

raw/
├── food/
│   └── food.csv
├── users/
│   └── users.csv
├── restaurant/
│   └── restaurant.csv
├── menu/
│   └── menu.csv
├── reviews/
│   └── reviews.csv
├── order_items/
│   └── order_items.csv
└── orders/
    └── orders.csv

Snowflake accesses the S3 data through an external stage and storage integration.

2. Snowflake RAW Layer

The raw data is loaded into:

ZOMATO_DB.RAW

Tables include:

USERS_RAW
RESTAURANT_RAW
FOOD_RAW
MENU_RAW
REVIEWS_RAW
ORDER_ITEMS_RAW
ORDERS_RAW

Final verified row counts:

USERS_RAW          100,000
RESTAURANT_RAW     148,541
FOOD_RAW           371,561
MENU_RAW           1,179,936
REVIEWS_RAW        300,000
ORDER_ITEMS_RAW    22,998,179
ORDERS_RAW         10,000,000
dbt Transformation

dbt is used to transform the RAW layer into analytical datasets.

STAGING / Silver

Staging models standardize and clean the raw data:

stg_users
stg_restaurants
stg_food
stg_menu
stg_reviews
stg_order_items
stg_orders

The project uses dbt tests for key fields including:

not_null
unique

The complete dbt build currently passes:

23 total
23 success

including:

12 tests
12 passed
MARTS / Gold

The analytical layer contains dimensional and fact models:

dim_users
dim_restaurants
fct_orders

The order fact table uses incremental materialization.

Current verified row counts:

DIM_USERS          100,000
DIM_RESTAURANTS    148,541
FCT_ORDERS         10,000,000
AI Layer

The project uses local Ollama models, avoiding a paid external LLM API dependency.

Review Enrichment

Customer reviews are processed by the local Llama model to extract:

Sentiment label
Sentiment score
Topic
Key issue

Results are stored in:

ZOMATO_DB.AI.REVIEW_ENRICHED

Example:

Review:
"The delivery partner was polite and helpful."

Topic:
delivery

Sentiment:
positive
Vector Embeddings

Review text is converted into vector embeddings using:

nomic-embed-text

The embeddings are stored in Snowflake:

ZOMATO_DB.AI.REVIEW_EMBEDDINGS

The embedding dimension is:

768
Retrieval-Augmented Generation

The project implements a local RAG workflow.

User Question
      |
      v
Embedding Model
      |
      v
Snowflake Review Embeddings
      |
      v
Similarity Search
      |
      v
Relevant Reviews
      |
      v
Llama 3.2
      |
      v
Generated Answer

Example question:

Which reviews talk about delivery?

The system retrieves semantically relevant reviews before generating the answer.

Text-to-SQL

The project also includes a schema-aware natural-language-to-SQL system.

Natural Language Question
          |
          v
Retrieve MARTS Schema
          |
          v
Llama 3.2
          |
          v
Generated SQL
          |
          v
Safety Validation
          |
          v
Snowflake
          |
          v
Query Result

Example:

Question:
How many orders are there?

Generated SQL:
SELECT COUNT(*)
FROM ZOMATO_DB.MARTS.FCT_ORDERS;

The implementation includes safety checks that restrict generated statements to read-oriented queries and reject destructive SQL operations.

AI Analytics Mart

AI-enriched review data is transformed into:

ZOMATO_DB.MARTS.MART_REVIEW_INSIGHTS

The model contains analytical fields such as:

CITY
TOPIC
SENTIMENT_LABEL
REVIEW_COUNT
AVG_RATING
AVG_SENTIMENT_SCORE
KEY_ISSUE
Apache Airflow

Airflow runs inside Docker and orchestrates the data and AI workflow.

Current pipeline:

                 +----------------+
                 |    dbt run     |
                 +-------+--------+
                         |
                         v
              +----------+----------+
              |                     |
              v                     v
        dbt transformations    AI enrichment
              |                     |
              |                     v
              |               +-----+------+
              |               | dbt AI mart|
              |               +------------+
              |                     |
              +----------+----------+
                         |
                         v
                  Snowflake MARTS

The Airflow DAG:

zomato_db_pipeline

contains the main tasks:

dbt_run
enrich_reviews
dbt_build_ai

The DAG has been manually executed successfully multiple times.

Docker

Airflow is containerized using Docker.

The custom Airflow image includes:

Apache Airflow Snowflake provider
dbt Snowflake adapter
Ollama Python client
python-dotenv

Ollama itself runs locally on the host machine, while the Airflow container communicates with it through:

http://host.docker.internal:11434
Streamlit Application

The Streamlit application provides two main interfaces.

Review RAG

Users can ask questions about customer reviews using semantic retrieval.

Example:

Which reviews talk about delivery?
Data Chat

Users can ask analytical questions in natural language.

Examples:

How many orders are there?

Which cuisine has the most orders?

What is the average delivery time by city?

The system generates SQL, validates it, executes it against Snowflake, and displays the result.

Project Structure
zomato-ai-data-engineering/
│
├── ai/
│   ├── create_embeddings.py
│   ├── enrich_reviews.py
│   ├── rag_chat.py
│   ├── rag_retrieval.py
│   ├── text_to_sql.py
│   └── test_local_llm.py
│
├── airflow/
│   ├── dags/
│   │   └── zomato_pipeline.py
│   ├── dbt_profiles/
│   ├── Dockerfile
│   └── docker-compose.yaml
│
├── dbt/
│   ├── models/
│   │   ├── staging/
│   │   └── marts/
│   └── dbt_project.yml
│
├── data/
│   ├── raw/
│   └── sample/
│
├── streamlit/
│   └── app.py
│
├── sql/
├── scripts/
├── tests/
├── docs/
│
├── .env.example
├── .gitignore
├── README.md
└── project_status.md
Data Quality Findings

During dataset profiling, several data quality issues were identified and handled appropriately.

Examples include:

menu_id contains duplicate values and is therefore not treated as a clean primary key.
Restaurant ratings contain string/sentinel values requiring normalization.
Restaurant cost values require parsing.
Customer ratings are nullable for some orders.
Delivery time is nullable for some orders.
Some menu records contain orphan restaurant IDs.
Several CSV files contain unnamed index columns that should not become business columns.

These findings were identified through profiling rather than assuming the source data was perfectly clean.

Validation

The project has been validated at multiple levels.

dbt
23 models/tests
23 successful
12 tests passed
Snowflake
DIM_USERS          100,000
DIM_RESTAURANTS    148,541
FCT_ORDERS         10,000,000
MART_REVIEW_INSIGHTS 5
Airflow

The main DAG has completed successfully through manual runs.

AI

Verified:

Local LLM inference
Review enrichment
768-dimensional embeddings
Vector similarity retrieval
RAG responses
Text-to-SQL generation
SQL safety validation
Streamlit

Verified:

Review RAG interface
Natural-language data queries
Snowflake result display
Security

Secrets are intentionally excluded from version control.

Ignored files include:

ai/.env
airflow/.env
secrets/

Snowflake authentication uses an encrypted private key locally.

No Snowflake private key, passphrase, or API credential is stored in the Git repository.

Local Setup
Prerequisites

Install:

Python 3.12
Docker Desktop
Git
dbt
Ollama

Pull the local models:

ollama pull llama3.2
ollama pull nomic-embed-text

Create local environment files from:

.env.example

Configure Snowflake credentials locally.

Then start the Airflow environment:

cd airflow
docker compose up -d --build

Run dbt locally:

cd ..\dbt
dbt debug
dbt build

Start Streamlit:

cd ..
streamlit run .\streamlit\app.py
Key Engineering Concepts Demonstrated

This project demonstrates practical experience with:

ELT architecture
Medallion architecture
Cloud object storage
Snowflake data warehousing
External stages and storage integrations
SQL transformation
dbt sources
dbt models
dbt testing
Dimensional modeling
Fact and dimension tables
Incremental models
Data quality profiling
Docker
Apache Airflow
DAG orchestration
Local LLM inference
Embeddings
Vector similarity search
Retrieval-Augmented Generation
Text-to-SQL
SQL safety validation
Streamlit applications
Git/GitHub
Project Status

The core end-to-end implementation is complete.

Dataset Profiling       ✅
Amazon S3               ✅
Snowflake RAW           ✅
dbt STAGING             ✅
dbt MARTS               ✅
dbt Testing             ✅
AI Enrichment           ✅
Embeddings              ✅
RAG                     ✅
Text-to-SQL             ✅
Airflow                 ✅
Docker                  ✅
Streamlit               ✅
Git/GitHub              ✅
Author

Vinay Chute

B.Tech Computer Science Engineering

GitHub:

https://github.com/vinaychute2506-oss