# Dataset Overview & Specifications

This document outlines the dataset domain, expected platform entities, and estimated scale for the Zomato-inspired food delivery data engineering pipeline.

> [!IMPORTANT]
> **Source-of-Truth Note**
> The entity descriptions and scale metrics documented below are based **strictly on the project specification and tutorial outline**.
> Specific schema column names, data types, and file layouts will only be documented once the actual raw CSV source files are acquired and inspected. No speculative column definitions are included at this stage.

---

## Expected Core Entities

The food-delivery business model operates around seven primary entities:

### 1. `users`
Represents registered customers and platform users who browse menus, place food delivery orders, and write reviews. This entity serves as the foundation for customer demographics, behavioral segmentation, and lifetime value analysis.

### 2. `restaurants`
Represents restaurant merchant partners registered on the food delivery platform. It contains establishment-level entity information such as restaurant location, regional operating zone, and profile attributes.

### 3. `food`
Represents the culinary food catalog items, categories, dish classifications, and cuisine groupings available across the food delivery ecosystem.

### 4. `menu`
Represents the menu listings and item offerings that associate specific food catalog items with particular restaurant partners, including restaurant-specific pricing and availability.

### 5. `orders`
Represents transaction headers for completed customer purchases. Each order record captures a discrete order event linking a purchasing customer to a fulfilling restaurant partner at a specific point in time, with associated total order monetary metrics.

### 6. `order_items`
Represents individual line items within each order transaction. It captures the specific dish items selected from a restaurant menu, unit quantities ordered, and line-item prices.

### 7. `reviews`
Represents customer-generated qualitative and quantitative feedback. It includes numerical ratings and text review commentary evaluating restaurants, specific meals, and order fulfillment experiences. This entity provides the primary input for the AI and NLP sentiment enrichment layer.

---

## Target Project Scale (Tutorial Reference)

The target architectural scale defined in the tutorial benchmark encompasses:

- **Target Orders**: ~10,000,000 (10 Million) records
- **Target Order Line Items**: ~23,000,000 (23 Million) records
- **Target Customer Reviews**: ~300,000 (300 Thousand) records

> [!NOTE]
> **Current Data Status**:
> The metrics listed above represent the **target benchmark / tutorial scale** for which the data warehouse and pipeline architecture are being engineered.
> We do **not** currently possess or claim to have these raw files locally. The raw data ingestion will occur in later phases once the appropriate storage stages and data sources are connected. No fake or placeholder datasets have been generated.
