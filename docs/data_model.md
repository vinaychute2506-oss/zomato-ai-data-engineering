# Conceptual Data Model

This document outlines the high-level business entity relationships for the food delivery pipeline.

> [!IMPORTANT]
> **Conceptual Modeling Constraint**
> In accordance with data governance and engineering best practices, this model defines **conceptual relationships only**.
> Specific primary keys (PK), foreign keys (FK), column naming conventions (e.g., `user_id` vs `customer_id`), surrogate keys, and data types are intentionally **not** assumed here and will be formally defined only after inspecting the raw source CSV files.

---

## Conceptual Entity Relationships

The core interactions between the platform entities are structured as follows:

```text
users ------------+
                  |
                  v
             [ orders ] --------> [ order_items ]
                  ^                      ^
                  |                      |
restaurants ------+                      |
      |                                  |
      +----------> [ menu ] -------------+
                     ^
                     |
                 [ food ]

users ------------+
                  |
                  v
             [ reviews ]
                  ^
                  |
restaurants ------+
```

### Detailed Relationship Descriptions

1. **`users` → `orders`**
   - **Relationship**: One-to-Many
   - **Business Meaning**: A single registered user can place multiple food delivery orders over time. Each individual order transaction is initiated and owned by exactly one customer profile.

2. **`restaurants` → `orders`**
   - **Relationship**: One-to-Many
   - **Business Meaning**: A restaurant partner receives, prepares, and fulfills multiple customer orders. Every order transaction is fulfilled by a specific restaurant partner.

3. **`orders` → `order_items`**
   - **Relationship**: One-to-Many
   - **Business Meaning**: An order contains one or more line items (e.g., a customer ordering two burgers and one soda in a single checkout event). Each line item belongs strictly to its parent order.

4. **`food` / `menu` → `order_items`**
   - **Relationship**: One-to-Many
   - **Business Meaning**: Menu listings (which associate specific food items with restaurant offerings and prices) are referenced by order line items to specify what food product was purchased, at what unit price, and in what quantity.

5. **`users` / `restaurants` → `reviews`**
   - **Relationship**: One-to-Many (from both Users and Restaurants)
   - **Business Meaning**: Customers write qualitative evaluations and assign numeric ratings. A review evaluates a restaurant partner and/or a specific fulfillment experience, linking back to the user who authored the review and the restaurant being reviewed.

---

## Downstream Data Modeling Roadmap (dbt)

During subsequent project phases:
- **Bronze Layer (RAW)**: Exact source schemas loaded into Snowflake as append/staging tables.
- **Silver Layer (STAGING)**: Standardized naming, casting, deduplication, surrogate key generation, and cleansing via dbt.
- **Gold Layer (MARTS)**: Dimensional star schema models (e.g., `fct_orders`, `fct_order_items`, `fct_reviews`, `dim_users`, `dim_restaurants`, `dim_food`) optimized for fast analytical queries and BI consumption.
