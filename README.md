# Zomato AI Data Engineering Pipeline

An end-to-end **AI-powered Data Engineering platform** built around a large-scale Zomato-style food delivery dataset.

The project demonstrates cloud data ingestion, Snowflake data warehousing, dbt transformations, dimensional modeling, Apache Airflow orchestration, local LLM-powered review enrichment, RAG-based review search, Text-to-SQL, and a Streamlit data assistant.

---

## Architecture

```text
                         ┌──────────────────────┐
                         │      CSV Dataset     │
                         │      ~35M rows       │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │      Amazon S3       │
                         │     Raw Storage      │
                         └──────────┬───────────┘
                                    │
                                    ▼
                    ┌──────────────────────────────┐
                    │         Snowflake            │
                    │                              │
                    │  RAW → STAGING → MARTS       │
                    └──────────────┬───────────────┘
                                   │
                         ┌─────────┴─────────┐
                         │                   │
                         ▼                   ▼
                    dbt Core            AI Layer
                         │                   │
                         │             Ollama / Llama 3.2
                         │             nomic-embed-text
                         │                   │
                         │                   ▼
                         │          AI.REVIEW_ENRICHED
                         │                   │
                         │                   ▼
                         │          AI Review Mart
                         │
                         ▼
                    Analytics
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
        Streamlit Data        Review RAG
           Assistant
              │
              ▼
         Text-to-SQL

                    ▲
                    │
              Apache Airflow
              Orchestration

CSV
 ↓
Amazon S3
 ↓
Snowflake RAW
 ↓
dbt STAGING
 ↓
dbt MARTS
 ↓
AI Enrichment
 ↓
AI dbt Mart
 ↓
Streamlit

Apache Airflow orchestrates the core dbt transformation, AI enrichment, and final AI mart build.

Project Highlights
~35 million rows across 7 source datasets
~2.3 GB of raw CSV data
Amazon S3 raw data lake
Snowflake cloud data warehouse
dbt-based ELT transformation pipeline
RAW / STAGING / MARTS architecture
Dimensional modeling
Incremental fact table processing
dbt data-quality tests
Apache Airflow orchestration
Dockerized Airflow environment
Local LLM inference using Ollama
Llama 3.2 for review enrichment
nomic-embed-text embeddings
RAG-based review retrieval
Natural-language Text-to-SQL
SQL safety guardrails
Streamlit interactive AI data assistant
Snowflake key-pair authentication
Git-based project versioning
Technology Stack
Technology	Purpose
Python	Pipeline logic and AI integration
Amazon S3	Raw data storage
Snowflake	Cloud data warehouse
SQL	Data transformation and analytics
dbt	ELT transformations, testing and modeling
Apache Airflow	Workflow orchestration
Docker	Airflow containerization
Ollama	Local LLM inference
Llama 3.2	Review enrichment and Text-to-SQL
nomic-embed-text	Text embeddings
Streamlit	Interactive data application
Git	Version control
Dataset

The project uses seven datasets representing a food-delivery platform:

users.csv
restaurant.csv
food.csv
menu.csv
reviews.csv
order_items.csv
orders.csv

Approximate scale:

Dataset	Rows
users	100,000
restaurant	148,541
food	371,561
menu	1,179,936
reviews	300,000
order_items	22,998,179
orders	10,000,000
Total	~35.1M

Total raw data size is approximately 2.3 GB.

Data Engineering Architecture
1. Amazon S3

Raw CSV datasets are organized in S3 by entity:

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

S3 acts as the raw landing zone before warehouse ingestion.

2. Snowflake

Snowflake is organized into three primary layers:

ZOMATO_DB
│
├── RAW
│
├── STAGING
│
└── MARTS
RAW

Contains the source data loaded from Amazon S3.

USERS_RAW
RESTAURANT_RAW
FOOD_RAW
MENU_RAW
REVIEWS_RAW
ORDER_ITEMS_RAW
ORDERS_RAW
STAGING

dbt models standardize and clean the RAW layer.

stg_users
stg_restaurants
stg_food
stg_menu
stg_reviews
stg_order_items
stg_orders
MARTS

Business-ready analytical models include:

dim_users
dim_restaurants
fct_orders
mart_review_insights
3. dbt

dbt is used for:

SQL transformations
Data cleaning
Source definitions
Model dependencies
Data-quality testing
Dimensional modeling
Incremental processing
AI mart construction

The project follows a layered transformation approach:

RAW
 ↓
STAGING / Silver
 ↓
MARTS / Gold
dbt Tests

The staging layer includes uniqueness and not-null tests for key entities.

The implemented test suite completed successfully with:

12 / 12 tests passing
4. Dimensional Modeling

The MARTS layer contains analytical dimensions and facts.

Dimensions
dim_users
dim_restaurants
Fact
fct_orders

fct_orders is implemented as an incremental dbt model.

The resulting warehouse structure supports analytical queries without repeatedly processing the full raw dataset.

5. Data Quality Findings

During dataset profiling, several real data-quality issues were identified rather than assuming the source data was perfectly clean.

Menu IDs

menu_id contains duplicates and therefore is not treated as a reliable primary key.

Restaurant Ratings

Restaurant ratings contain sentinel values such as:

--

which require transformation before analytical use.

Restaurant Cost

Restaurant cost values are stored in string formats such as:

Rs. 200

and require parsing.

Order Customer Ratings

Customer ratings are nullable because not every order has a customer rating.

Delivery Time

Delivery time also contains null values for some orders.

Menu Relationships

273 menu restaurant references were identified as orphaned relationships during profiling.

These findings were incorporated into the transformation and modeling approach.

6. AI Layer

The project uses local AI inference instead of a paid external LLM API.

Ollama
Ollama
├── llama3.2
└── nomic-embed-text

This keeps the AI layer local and avoids API usage costs.

AI Review Enrichment

Restaurant reviews are enriched using Llama 3.2.

The model produces structured information including:

sentiment_label
sentiment_score
topic
key_issue

The results are stored in:

ZOMATO_DB.AI.REVIEW_ENRICHED

Example conceptual output:

Review
  ↓
Llama 3.2
  ↓
Sentiment
Topic
Key Issue
  ↓
Snowflake AI table
7. AI dbt Mart

The AI enrichment table is registered as a dbt source.

The final model:

MARTS.MART_REVIEW_INSIGHTS

combines:

AI.REVIEW_ENRICHED
        +
STG_REVIEWS
        +
STG_RESTAURANTS

and produces analytical review insights such as:

CITY
TOPIC
SENTIMENT_LABEL
REVIEW_COUNT
AVG_RATING
AVG_SENTIMENT_SCORE
KEY_ISSUE

The model is tagged:

ai

and can be built using:

dbt build --select tag:ai
8. RAG Review Assistant

The project also implements Retrieval-Augmented Generation.

The pipeline is:

Review Text
    ↓
nomic-embed-text
    ↓
768-dimensional embedding
    ↓
Snowflake AI.REVIEW_EMBEDDINGS
    ↓
Cosine Similarity Retrieval
    ↓
Relevant Reviews
    ↓
Llama 3.2
    ↓
Natural Language Answer

This allows questions such as:

Which reviews talk about delivery?

The system retrieves semantically relevant reviews before generating the response.

9. Text-to-SQL

The project implements a natural-language data assistant.

Example:

User:
How many orders are there?

The AI generates:

SELECT COUNT(*)
FROM ZOMATO_DB.MARTS.FCT_ORDERS;

The SQL is then validated and executed against Snowflake.

SQL Safety

The Text-to-SQL layer contains guardrails against destructive SQL operations.

Blocked operations include:

DROP
DELETE
TRUNCATE
ALTER
UPDATE
INSERT
CREATE
REPLACE
GRANT
REVOKE

Only read-oriented queries are permitted.

This prevents the LLM from directly generating destructive warehouse operations.

10. Streamlit Application

The Streamlit application provides two primary interfaces:

Zomato AI Data Assistant
│
├── Review RAG
│
└── Data Chat
Review RAG

Users can ask natural-language questions about restaurant reviews.

Data Chat

Users can ask analytical questions such as:

How many orders are there?

Which cuisine has the most orders?

What is the average delivery time by city?

The system:

Natural Language
      ↓
Llama 3.2
      ↓
SQL
      ↓
Safety Validation
      ↓
Snowflake
      ↓
Result
11. Apache Airflow

Airflow orchestrates the end-to-end workflow.

The final DAG is:

dbt_run
   ↓
enrich_reviews
   ↓
dbt_build_ai
Task 1 — dbt Core

Runs the main dbt transformation pipeline.

Task 2 — AI Review Enrichment

Runs:

/opt/airflow/ai/enrich_reviews.py

and uses the local Ollama service.

Task 3 — AI dbt Build

Runs:

dbt build --select tag:ai

to rebuild the AI mart.

The complete DAG has been successfully executed end-to-end.

12. Docker Integration

Airflow runs inside Docker while Ollama runs locally on the Windows host.

Docker communicates with the host Ollama service through:

http://host.docker.internal:11434

The Airflow container mounts:

/opt/airflow/dbt
/opt/airflow/ai
/opt/airflow/secrets
/opt/airflow/dbt_profiles

This allows the containerized orchestration layer to access the dbt project, AI scripts, Snowflake authentication material, and dbt configuration.

Project Structure
zomato-ai-data-engineering/
│
├── ai/
│   ├── create_embeddings.py
│   ├── enrich_reviews.py
│   ├── rag_chat.py
│   ├── rag_retrieval.py
│   ├── test_embeddings.py
│   ├── test_local_llm.py
│   ├── test_similarity.py
│   └── text_to_sql.py
│
├── airflow/
│   ├── dags/
│   │   └── zomato_pipeline.py
│   ├── dbt_profiles/
│   ├── logs/
│   ├── plugins/
│   ├── Dockerfile
│   └── docker-compose.yaml
│
├── data/
│   ├── raw/
│   └── sample/
│
├── dbt/
│   ├── models/
│   │   ├── staging/
│   │   └── marts/
│   ├── macros/
│   ├── analyses/
│   ├── seeds/
│   ├── snapshots/
│   ├── tests/
│   └── dbt_project.yml
│
├── docs/
├── scripts/
├── sql/
├── streamlit/
│   └── app.py
├── tests/
│
├── .env.example
├── .gitignore
├── project_status.md
└── README.md
Running the Project
Prerequisites

Install:

Python 3.12+
Git
Docker Desktop
AWS CLI
Snowflake account
Ollama
Start Ollama

Make sure the required local models are available:

ollama list

Required:

llama3.2
nomic-embed-text
Start Airflow

From the Airflow directory:

cd airflow
docker compose up -d

Airflow UI:

http://localhost:8080
Run dbt locally

Activate the Python environment:

.venv\Scripts\Activate.ps1

Then:

cd dbt
dbt debug
dbt run
dbt test
Run the complete Airflow pipeline
docker exec zomato_airflow airflow dags trigger zomato_dbt_pipeline

Check runs:

docker exec zomato_airflow airflow dags list-runs zomato_dbt_pipeline
Start Streamlit

From the project root:

streamlit run streamlit/app.py

Application:

http://localhost:8501
Security

Credentials and private authentication material are intentionally excluded from Git.

Ignored files include:

ai/.env
airflow/.env
secrets/

Snowflake authentication uses an encrypted private key stored outside version control.

No API keys or private keys should be committed to the repository.

Engineering Decisions
Why S3?

S3 provides a durable raw landing zone and separates ingestion storage from warehouse transformations.

Why Snowflake?

Snowflake provides scalable cloud data warehousing and separates compute from storage.

Why dbt?

dbt provides SQL-based transformation, dependency management, testing, documentation, and incremental modeling.

Why Airflow?

Airflow manages task dependencies and orchestrates the end-to-end workflow.

Why Docker?

Docker provides a reproducible environment for Airflow and its dependencies.

Why Ollama?

Ollama enables local LLM inference without requiring paid external API usage.

Why RAG?

RAG allows the system to retrieve relevant review context before generating an answer.

Why Text-to-SQL?

Text-to-SQL provides a natural-language interface to analytical warehouse data while safety validation limits destructive operations.

Validation Results

The completed implementation has been validated across the major pipeline components.

S3 ingestion                         PASS
Snowflake RAW loading                PASS
dbt staging                          PASS
dbt tests                            12/12 PASS
dbt marts                            PASS
Incremental orders model             PASS
Ollama LLM                           PASS
Embeddings                           PASS
RAG retrieval                        PASS
Text-to-SQL                          PASS
Streamlit                            PASS
Airflow                              PASS
AI review enrichment                 5/5 PASS
AI dbt mart                          PASS
End-to-end Airflow DAG               PASS

The final Airflow DAG successfully executed:

dbt_run
   ↓
enrich_reviews
   ↓
dbt_build_ai

and produced:

ZOMATO_DB.MARTS.MART_REVIEW_INSIGHTS
Key Learning Outcomes

This project demonstrates practical experience with:

Cloud object storage
Data warehouse architecture
ELT pipelines
Medallion-style data layers
Dimensional modeling
SQL transformation
dbt
Data-quality testing
Incremental models
Workflow orchestration
Docker
Local LLM deployment
Embeddings
RAG
Text-to-SQL
AI safety guardrails
Streamlit application development
End-to-end data pipeline design
Project Status

Status: Completed

The core data engineering, AI, orchestration, and application components have been implemented and validated end-to-end.

Author

Vinay Chute

B.Tech Computer Science Engineering

Disclaimer

This project is an engineering/portfolio implementation inspired by a food-delivery data platform. The dataset contains synthetic or generated elements and is used for educational and demonstration purposes.


### Step 2 — save it

Press:

**Ctrl + S**

Then run:

```powershell
git status