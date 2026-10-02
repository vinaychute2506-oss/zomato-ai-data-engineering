# Zomato AI Data Engineering Pipeline

An end-to-end cloud and AI-driven data engineering pipeline inspired by a high-scale food-delivery platform (Zomato). The project ingests raw platform transactional data into cloud storage, models analytical data marts in Snowflake using dbt, leverages AI for automated intelligence and review insights, and delivers self-service interactive dashboards via Streamlit, orchestrated with containerized Apache Airflow.

## Architecture

```text
CSV dataset
    ↓
Amazon S3
    ↓
Snowflake RAW / Bronze
    ↓
dbt STAGING / Silver
    ↓
dbt MARTS / Gold
    ↓
AI layer
    ↓
Streamlit
    ↑
Apache Airflow orchestration
```

Or visualized linearly:

```text
CSV → S3 → Snowflake → dbt → AI → Streamlit
                         ↑
                      Airflow
```

## Technology Stack

- **Python**: Core programming language and pipeline logic
- **Amazon S3**: Scalable cloud object storage for raw ingestion (Bronze layer landing zone)
- **Snowflake**: Cloud data warehouse for analytical query processing and data storage
- **dbt (data build tool)**: SQL transformations, data lineage, testing, and dimensional modeling (Silver and Gold layers)
- **Apache Airflow**: Workflow orchestration and DAG scheduling
- **Docker**: Containerization for reproducible local services (Airflow, dependencies)
- **OpenAI API**: AI layer for semantic insights, text extraction, and sentiment/review analysis
- **Streamlit**: Interactive user-facing analytical dashboard

## Implementation Status & Roadmap

> [!NOTE]
> All implementation components below are currently placeholders marked as **TODO** as the project is being constructed iteratively across structured development phases.

- [ ] **Phase 1 — Dataset & Project Setup**: Project scaffolding and documentation setup (In Progress)
- [ ] **Phase 2 — Amazon S3**: Ingestion scripts, S3 bucket structure, and cloud storage management (TODO)
- [ ] **Phase 3 — Snowflake**: Database, schemas, stages, file formats, and raw bronze tables (TODO)
- [ ] **Phase 4 — dbt Staging**: Cleaning, deduplication, standardizing staging views/tables (Silver layer) (TODO)
- [ ] **Phase 5 — Dimensional Modeling**: Designing star schema dimensional models and fact tables (Gold layer) (TODO)
- [ ] **Phase 6 — Airflow + Docker**: Containerized Airflow DAGs for automated batch pipelines (TODO)
- [ ] **Phase 7 — AI Layer**: LLM-powered review analysis, cuisine recommendations, and intelligence generation (TODO)
- [ ] **Phase 8 — Streamlit**: Executive and operational food-delivery analytics dashboard (TODO)
- [ ] **Phase 9 — End-to-End Orchestration**: Full pipeline integration, data validation, and end-to-end execution (TODO)
