# Dataset Profile

> **Generated**: 2026-10-02 | **Method**: Streaming row-by-row scan (no full-file RAM load)
> No data was modified, generated, or uploaded during profiling.

---

## Dataset Overview

This dataset represents a synthetic food-delivery platform modelled after Zomato.
It covers orders, customers, restaurants, menus, food items, and customer reviews
across Indian cities. All monetary values are in **INR**.

---

## File Inventory

| Filename | File Size | File Size (MB) | Rows | Columns |
|---|---|---|---|---|
| `users.csv` | 11,239,820 bytes | 10.72 MB | 100,000 | 12 |
| `restaurant.csv` | 46,731,352 bytes | 44.58 MB | 148,541 | 12 |
| `food.csv` | 17,208,649 bytes | 16.41 MB | 371,561 | 4 |
| `menu.csv` | 65,833,035 bytes | 62.78 MB | 1,179,936 | 6 |
| `reviews.csv` | 25,406,720 bytes | 24.22 MB | 300,000 | 7 |
| `order_items.csv` | 955,117,276 bytes | 910.81 MB | 22,998,179 | 7 |
| `orders.csv` | 1,332,004,808 bytes | 1,270.18 MB | 10,000,000 | 19 |

> [!NOTE]
> `order_items.csv` and `orders.csv` were scanned using streaming I/O; they were **not** loaded into RAM.

---

## Schema of Each CSV

### `users.csv` (100,000 rows)

| Column | Inferred Type | Null Count | Null % | Distinct Values |
|---|---|---|---|---|
| `` (unnamed index) | integer | 0 | 0.00% | 100,000 |
| `user_id` | integer | 0 | 0.00% | 100,000 |
| `name` | string | 0 | 0.00% | 71,251 |
| `email` | string | 0 | 0.00% | 85,662 |
| `password` | string | 0 | 0.00% | 100,000 |
| `Age` | integer | 0 | 0.00% | 16 |
| `Gender` | string | 0 | 0.00% | 2 |
| `Marital Status` | string | 0 | 0.00% | 3 |
| `Occupation` | string | 0 | 0.00% | 4 |
| `Monthly Income` | string | 0 | 0.00% | 5 |
| `Educational Qualifications` | string | 0 | 0.00% | 5 |
| `Family size` | integer | 0 | 0.00% | 6 |

**Sample rows (first 3):**
```
[0, 1, 'Claire Ferguson', 'fordanthony@example.net', 'NKz0fWDh!5', 20, 'Female', 'Single', 'Student', 'No Income', 'Post Graduate', 4]
[1, 2, 'Jennifer Young', 'ann96@example.com', '+i5Q91jt!s', 24, 'Female', 'Single', 'Student', 'Below Rs.10000', 'Graduate', 3]
[2, 3, 'Jermaine Roberson', 'uwalker@example.org', 'eO4GqGusF(', 22, 'Male', 'Single', 'Student', 'Below Rs.10000', 'Post Graduate', 3]
```

---

### `restaurant.csv` (148,541 rows)

| Column | Inferred Type | Null Count | Null % | Distinct Values |
|---|---|---|---|---|
| `` (unnamed index) | integer | 0 | 0.00% | 148,541 |
| `id` | integer | 0 | 0.00% | 148,541 |
| `name` | string | 86 | 0.06% | 112,819 |
| `city` | string | 0 | 0.00% | 821 |
| `rating` | string | 86 | 0.06% | 43 |
| `rating_count` | string | 86 | 0.06% | 9 |
| `cost` | string | 131 | 0.09% | 364 |
| `cuisine` | string | 99 | 0.07% | 2,132 |
| `lic_no` | string | 229 | 0.15% | 108,764 |
| `link` | string | 0 | 0.00% | 148,541 |
| `address` | string | 86 | 0.06% | 148,402 |
| `menu` | string | 0 | 0.00% | 148,541 |

**Notable:** `rating` is stored as a string (e.g., `"3.5"`, `"--"`), `cost` contains the Rupee symbol (e.g., `"Rs. 200"`), and `rating_count` is a categorical band (e.g., `"1K+ ratings"`).

---

### `food.csv` (371,561 rows)

| Column | Inferred Type | Null Count | Null % | Distinct Values |
|---|---|---|---|---|
| `` (unnamed index) | integer | 0 | 0.00% | 371,561 |
| `f_id` | string | 0 | 0.00% | 371,561 |
| `item` | string | 1 | ~0.00% | 369,356 |
| `veg_or_non_veg` | string | 1 | ~0.00% | 3 |

**`veg_or_non_veg` values observed:** `Veg`, `Non-veg`, `` (1 null)

---

### `menu.csv` (1,179,936 rows)

| Column | Inferred Type | Null Count | Null % | Distinct Values |
|---|---|---|---|---|
| `` (unnamed index) | integer | 0 | 0.00% | 1,179,936 |
| `menu_id` | string | 0 | 0.00% | 1,048,575 |
| `r_id` | integer | 0 | 0.00% | 12,286 |
| `f_id` | string | 0 | 0.00% | 371,561 |
| `cuisine` | string | 0 | 0.00% | 1,442 |
| `price` | float | 0 | 0.00% | 4,959 |

**Notable:** `menu_id` has 1,179,936 rows but only 1,048,575 unique values — **131,361 duplicate menu_id values** detected.  
Price range: 0 – 9,999 INR. Zero-price entries: 79.

---

### `reviews.csv` (300,000 rows)

| Column | Inferred Type | Null Count | Null % | Distinct Values |
|---|---|---|---|---|
| `review_id` | integer | 0 | 0.00% | 300,000 |
| `order_id` | integer | 0 | 0.00% | 295,541 |
| `user_id` | integer | 0 | 0.00% | 95,093 |
| `restaurant_id` | integer | 0 | 0.00% | 128,994 |
| `rating` | integer | 0 | 0.00% | 5 |
| `comment` | string | 0 | 0.00% | 294 |
| `review_date` | datetime | 0 | 0.00% | 912 |

**Notable:** Only 294 distinct comment strings across 300,000 reviews — comments appear to be template-generated.  
Rating range: 1 – 5 (valid).  
`order_id` has 295,541 unique values (4,459 orders have multiple reviews — or duplicates exist).

---

### `order_items.csv` (22,998,179 rows)

| Column | Inferred Type | Null Count | Null % | Distinct Values |
|---|---|---|---|---|
| `order_item_id` | integer | 0 | 0.00% | N/A (large file) |
| `order_id` | integer | 0 | 0.00% | N/A (large file) |
| `r_id` | integer | 0 | 0.00% | N/A (large file) |
| `f_id` | string | 0 | 0.00% | N/A (large file) |
| `price` | integer | 0 | 0.00% | N/A (large file) |
| `quantity` | integer | 0 | 0.00% | N/A (large file) |
| `line_amount` | integer | 0 | 0.00% | N/A (large file) |

> Distinct value counts skipped for large files; spot-check of first 500,000 rows used for quality checks.

**Spot-check (first 500k rows):** zero_qty=0, neg_qty=0, zero_price=3, neg_price=0.

**Sample rows (first 3):**
```
[1, 1, 366828, 'fd538029', 223, 1, 223]
[2, 2, 100236, 'fd1042651', 87, 1, 87]
[3, 2, 100236, 'fd499871', 197, 1, 197]
```

---

### `orders.csv` (10,000,000 rows)

| Column | Inferred Type | Null Count | Null % |
|---|---|---|---|
| `order_id` | integer | 0 | 0.00% |
| `order_timestamp` | datetime | 0 | 0.00% |
| `order_date` | datetime | 0 | 0.00% |
| `user_id` | integer | 0 | 0.00% |
| `r_id` | integer | 0 | 0.00% |
| `restaurant_city` | string | 0 | 0.00% |
| `cuisine` | string | 0 | 0.00% |
| `items_count` | integer | 0 | 0.00% |
| `sales_qty` | integer | 0 | 0.00% |
| `subtotal` | integer | 0 | 0.00% |
| `discount` | integer | 0 | 0.00% |
| `delivery_fee` | integer | 0 | 0.00% |
| `gst` | integer | 0 | 0.00% |
| `sales_amount` | integer | 0 | 0.00% |
| `currency` | string | 0 | 0.00% |
| `payment_method` | string | 0 | 0.00% |
| `order_status` | string | 0 | 0.00% |
| `customer_rating` | float | 3,592,803 | **35.93%** |
| `delivery_time_min` | float | 849,878 | **8.50%** |

**Spot-check (first 200k rows):** neg_subtotal=0, neg_discount=0.  
`order_status` values: `Delivered`, `Cancelled`, `Refunded`  
`payment_method` values: `UPI`, `Card`, `COD`, `NetBanking`, `Wallet`  
`currency`: `INR` only  
Date range observed: 2024-07-13 to 2026-03-06

---

## Data Types

### Columns Requiring Type Conversion at Load Time

| File | Column | Raw Type | Recommended Type | Reason |
|---|---|---|---|---|
| `restaurant.csv` | `rating` | string | float (nullable) | Contains `"--"` sentinel for unrated |
| `restaurant.csv` | `rating_count` | string | categorical/ordinal | Band values like `"1K+ ratings"` |
| `restaurant.csv` | `cost` | string | integer (nullable) | Contains `"Rs. 200"` currency prefix |
| `users.csv` | `Monthly Income` | string | categorical/ordinal | Band values like `"Below Rs.10000"` |
| `food.csv` | `f_id` | string | string | Format: `fd<integer>` — not a plain int |
| `menu.csv` | `f_id` | string | string | Same `fd<integer>` format |
| `orders.csv` | `customer_rating` | float | float (nullable) | 35.93% null — only present for delivered orders |
| `orders.csv` | `delivery_time_min` | float | float (nullable) | 8.50% null — likely missing for cancelled orders |

---

## Missing Values

| File | Column | Null Count | Null % | Likely Reason |
|---|---|---|---|---|
| `restaurant.csv` | `lic_no` | 229 | 0.15% | Some restaurants may not have a license on record |
| `restaurant.csv` | `cost`, `name`, `rating`, etc. | 86–131 | 0.06–0.09% | Incomplete restaurant records |
| `food.csv` | `item`, `veg_or_non_veg` | 1 each | ~0.00% | Single malformed row |
| `orders.csv` | `customer_rating` | 3,592,803 | **35.93%** | Rating only present for delivered orders |
| `orders.csv` | `delivery_time_min` | 849,878 | **8.50%** | Missing for cancelled/refunded orders |

---

## Candidate Primary Keys

| File | Column | Unique Values | Total Rows | Assessment |
|---|---|---|---|---|
| `users.csv` | `user_id` | 100,000 | 100,000 | **Likely primary key** — 100% unique, no nulls |
| `restaurant.csv` | `id` | 148,541 | 148,541 | **Likely primary key** — 100% unique, no nulls |
| `food.csv` | `f_id` | 371,561 | 371,561 | **Likely primary key** — 100% unique, no nulls |
| `menu.csv` | `menu_id` | 1,048,575 | 1,179,936 | **Not a clean PK** — 131,361 duplicates detected |
| `reviews.csv` | `review_id` | 300,000 | 300,000 | **Likely primary key** — 100% unique, no nulls |
| `order_items.csv` | `order_item_id` | N/A (large) | 22,998,179 | **Likely primary key** — sequential integers observed |
| `orders.csv` | `order_id` | N/A (large) | 10,000,000 | **Likely primary key** — sequential 1–10,000,000 observed |

> [!NOTE]
> The unnamed first column (`""`) in `users.csv`, `restaurant.csv`, `food.csv`, and `menu.csv` appears to be a DataFrame row index exported from Python/pandas. It is **not** a business key.

---

## Candidate Foreign Keys

| Child Table | Child Column | Parent Table | Parent Column | Assessment |
|---|---|---|---|---|
| `orders.csv` | `user_id` | `users.csv` | `user_id` | **Candidate FK** — spot-check shows all 66,435 unique user_ids (first 200k orders) exist in users |
| `orders.csv` | `r_id` | `restaurant.csv` | `id` | **Candidate FK** — observed relationship; `r_id` values match restaurant `id` format |
| `order_items.csv` | `order_id` | `orders.csv` | `order_id` | **Candidate FK** — `order_id` values in order_items reference orders |
| `order_items.csv` | `r_id` | `restaurant.csv` | `id` | **Candidate FK** — r_id present in both order_items and restaurant |
| `order_items.csv` | `f_id` | `food.csv` | `f_id` | **Candidate FK** — `fd<int>` format matches food.f_id |
| `menu.csv` | `r_id` | `restaurant.csv` | `id` | **Candidate FK** — 273 orphan r_id values observed (r_ids in menu not present in restaurant) |
| `menu.csv` | `f_id` | `food.csv` | `f_id` | **Candidate FK** — all 371,561 menu f_ids matched food f_ids (0 orphans) |
| `reviews.csv` | `user_id` | `users.csv` | `user_id` | **Candidate FK** — 0 orphans; all review user_ids found in users |
| `reviews.csv` | `restaurant_id` | `restaurant.csv` | `id` | **Candidate FK** — 0 orphans; all review restaurant_ids found in restaurant |
| `reviews.csv` | `order_id` | `orders.csv` | `order_id` | **Candidate FK** — observed relationship; verification requires full scan |

---

## Observed Relationships

```
users (100K)
  └─[user_id]──→ orders (10M) [candidate FK: 0 orphans in spot-check]
  └─[user_id]──→ reviews (300K) [candidate FK: 0 orphans confirmed]

restaurant (148K)
  └─[id]──→ orders (10M).r_id [candidate FK]
  └─[id]──→ menu (1.18M).r_id [candidate FK: 273 orphan r_ids in menu]
  └─[id]──→ reviews (300K).restaurant_id [candidate FK: 0 orphans confirmed]

food (371K)
  └─[f_id]──→ menu (1.18M).f_id [candidate FK: 0 orphans confirmed]
  └─[f_id]──→ order_items (23M).f_id [candidate FK]

orders (10M)
  └─[order_id]──→ order_items (23M).order_id [candidate FK]
  └─[order_id]──→ reviews (300K).order_id [candidate FK: 295,541/300,000 distinct]

menu (1.18M)
  links restaurant ↔ food with price and cuisine
  r_id → restaurant.id (273 orphan r_ids)
  f_id → food.f_id (0 orphans)
```

---

## Data Quality Findings

| # | File | Issue | Severity | Detail |
|---|---|---|---|---|
| 1 | `users.csv` | Unnamed index column | Low | Column `""` is a pandas row index, not a business field |
| 2 | `users.csv` | Duplicate emails | Low | 85,662 unique emails vs 100,000 rows — ~14,338 non-unique emails |
| 3 | `users.csv` | Narrow age range | Note | Ages 18–33 only — may reflect dataset generation constraints |
| 4 | `restaurant.csv` | `rating` stored as string | Medium | Value `"--"` used as sentinel for unrated; needs cast to float (nullable) |
| 5 | `restaurant.csv` | `cost` contains currency symbol | Medium | Values like `"Rs. 200"` — requires string stripping before numeric use |
| 6 | `restaurant.csv` | `rating_count` is categorical band | Medium | Values like `"1K+ ratings"` — not directly aggregatable |
| 7 | `restaurant.csv` | Unnamed index column | Low | Same as users — pandas artifact |
| 8 | `restaurant.csv` | 86 rows with null name/rating/address | Low | Small subset (~0.06%) of incomplete restaurant records |
| 9 | `food.csv` | 1 null `item` and `veg_or_non_veg` | Low | Single malformed record |
| 10 | `food.csv` | Unnamed index column | Low | Pandas artifact |
| 11 | `menu.csv` | **131,361 duplicate `menu_id` values** | **High** | Out of 1,179,936 rows, 1,048,575 unique — `menu_id` is **not a clean PK** |
| 12 | `menu.csv` | 79 zero-price entries | Medium | Menu items with price=0; may be intentional (free items) or data errors |
| 13 | `menu.csv` | 273 orphan `r_id` values | Medium | r_ids in menu have no matching restaurant in restaurant.csv |
| 14 | `menu.csv` | Unnamed index column | Low | Pandas artifact |
| 15 | `reviews.csv` | Only 294 distinct comment strings | Note | Highly templated comments — synthetic dataset characteristic |
| 16 | `orders.csv` | `customer_rating` null 35.93% | Medium | Expected: cancelled/refunded orders have no rating — handle with nullable type |
| 17 | `orders.csv` | `delivery_time_min` null 8.50% | Medium | Expected: missing for non-delivered orders |
| 18 | `orders.csv` | `restaurant_city` contains compound values | Note | Values like `"Ameerpet,Hyderabad"`, `"HSR,Bangalore"` — area + city pattern |
| 19 | `order_items.csv` | 3 zero-price line items (spot-check) | Low | In first 500k rows; likely needs investigation |
| 20 | `order_items.csv` | Duplicate line in last 5 rows | Note | `order_item_id` 22998178 and 22998179 both: `[..., 'fd50037', 79, 1, 79]` |

---

## Dataset Scale

| Entity | File | Actual Row Count |
|---|---|---|
| Users | `users.csv` | **100,000** |
| Restaurants | `restaurant.csv` | **148,541** |
| Food items | `food.csv` | **371,561** |
| Menu entries | `menu.csv` | **1,179,936** |
| Reviews | `reviews.csv` | **300,000** |
| Order line items | `order_items.csv` | **22,998,179** |
| Orders | `orders.csv` | **10,000,000** |
| **Total records** | — | **~35,098,217** |

---

## Important Differences From Tutorial

| # | Difference | Detail |
|---|---|---|
| 1 | **File named `restaurant.csv` not `restaurants.csv`** | The tutorial refers to `restaurants.csv` (plural). The downloaded dataset contains `restaurant.csv` (singular). All joins and dbt models must reference the actual filename. |
| 2 | **`menu_id` is not a clean primary key** | 131,361 duplicate `menu_id` values exist. The tutorial may assume `menu_id` is unique. A surrogate key will be needed for staging. |
| 3 | **`rating` in restaurant is a string, not numeric** | Contains `"--"` as a sentinel value. Requires a NULLIF/CAST transformation in staging. |
| 4 | **`customer_rating` is 35.93% null** | Not all orders have a customer rating — only delivered orders typically receive one. |
| 5 | **273 orphan r_ids in menu.csv** | Some menu entries reference restaurant IDs not present in restaurant.csv — may cause FK violations if enforced in Snowflake. |
| 6 | **`restaurant_city` contains compound locality strings** | Values like `"Ameerpet,Hyderabad"` combine locality and city — splitting may be needed for city-level analysis. |
| 7 | **Unnamed index column in 4 files** | `users.csv`, `restaurant.csv`, `food.csv`, `menu.csv` all have an unnamed first column (pandas `df.to_csv()` artifact). This column should be excluded during loading. |
