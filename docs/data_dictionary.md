# Data Dictionary

> Based on actual column headers and values observed in the downloaded CSV files.
> Column meanings marked **"Meaning requires confirmation"** where inference is uncertain.
> No column names or meanings have been invented.

---

## `users.csv`

| Column | Observed Type | Description |
|---|---|---|
| `` (unnamed) | integer | Pandas row index exported as a column. Not a business field. Exclude at load. |
| `user_id` | integer | Unique identifier for each registered user. Likely primary key (100% unique). |
| `name` | string | Full name of the user. |
| `email` | string | Email address of the user. Not fully unique (85,662/100,000 distinct). |
| `password` | string | User password string. **Note:** plain-text passwords — not for production use. |
| `Age` | integer | Age of the user in years. Observed range: 18–33. |
| `Gender` | string | Gender of the user. Observed values: `Female`, `Male`. |
| `Marital Status` | string | Marital status. Observed values: `Single`, `Married`, `Prefer not to say`. |
| `Occupation` | string | Occupation category. Observed values: `Student`, `Employee`, `Self Employed`, `House Wife`. |
| `Monthly Income` | string | Monthly income band. Observed values: `No Income`, `Below Rs.10000`, `10001 to 25000`, `25001 to 50000`, `More than 50000`. |
| `Educational Qualifications` | string | Highest education level. Observed values: `Post Graduate`, `Graduate`, `Under Graduate`, `School`, `Uneducated`. |
| `Family size` | integer | Number of people in the user's household. Observed range: 1–6. |

---

## `restaurant.csv`

| Column | Observed Type | Description |
|---|---|---|
| `` (unnamed) | integer | Pandas row index. Not a business field. Exclude at load. |
| `id` | integer | Unique identifier for each restaurant. Likely primary key. Referenced as `r_id` in other tables. |
| `name` | string | Restaurant name. 86 nulls present. |
| `city` | string | City where the restaurant is located. 821 distinct cities. |
| `rating` | string | Average customer rating displayed on the platform. Stored as string; `"--"` indicates too few ratings. Range: `"1.0"` to `"5.0"`. Requires CAST to float. |
| `rating_count` | string | Categorical band indicating number of ratings received. Values: `Too Few Ratings`, `20+ ratings`, `50+ ratings`, `100+ ratings`, `500+ ratings`, `1K+ ratings`, `5K+ ratings`, `10K+ ratings`. |
| `cost` | string | Approximate cost for two people including currency symbol (e.g., `"Rs. 200"`). Requires string stripping to extract numeric value. |
| `cuisine` | string | Comma-separated list of cuisine types offered by the restaurant. |
| `lic_no` | string | FSSAI or similar food license number. 229 nulls. |
| `link` | string | URL to the restaurant's page on Swiggy. |
| `address` | string | Full street address of the restaurant. 86 nulls. |
| `menu` | string | Relative path to a JSON file containing the restaurant's menu (e.g., `Menu/567335.json`). Meaning requires confirmation for pipeline use. |

---

## `food.csv`

| Column | Observed Type | Description |
|---|---|---|
| `` (unnamed) | integer | Pandas row index. Not a business field. Exclude at load. |
| `f_id` | string | Unique identifier for each food/dish item. Format: `fd<integer>` (e.g., `fd0`, `fd1048555`). Likely primary key. |
| `item` | string | Name of the food dish or item. 1 null present. |
| `veg_or_non_veg` | string | Dietary classification. Observed values: `Veg`, `Non-veg`. 1 null present. |

---

## `menu.csv`

| Column | Observed Type | Description |
|---|---|---|
| `` (unnamed) | integer | Pandas row index. Not a business field. Exclude at load. |
| `menu_id` | string | Identifier for a menu entry. Format: `mn<integer>`. **Not a clean primary key** — 131,361 duplicates observed. |
| `r_id` | integer | Candidate foreign key referencing `restaurant.id`. 273 values have no matching restaurant. |
| `f_id` | string | Candidate foreign key referencing `food.f_id`. All values matched (0 orphans). |
| `cuisine` | string | Cuisine classification for this menu item at this restaurant. |
| `price` | float | Price of the food item at this restaurant in INR. Range: 0–9,999. 79 zero-price entries observed. |

---

## `reviews.csv`

| Column | Observed Type | Description |
|---|---|---|
| `review_id` | integer | Unique identifier for each review. Likely primary key (100% unique). |
| `order_id` | integer | Candidate foreign key referencing `orders.order_id`. 295,541 distinct values out of 300,000 reviews. |
| `user_id` | integer | Candidate foreign key referencing `users.user_id`. 0 orphans confirmed. |
| `restaurant_id` | integer | Candidate foreign key referencing `restaurant.id`. 0 orphans confirmed. |
| `rating` | integer | Numeric rating given by the user. Range: 1–5. |
| `comment` | string | Text comment of the review. Only 294 distinct strings observed — template-generated. |
| `review_date` | date | Date the review was submitted. Format: `YYYY-MM-DD`. 912 distinct dates. |

---

## `order_items.csv`

| Column | Observed Type | Description |
|---|---|---|
| `order_item_id` | integer | Unique identifier for each order line item. Likely primary key. |
| `order_id` | integer | Candidate foreign key referencing `orders.order_id`. |
| `r_id` | integer | Candidate foreign key referencing `restaurant.id`. Restaurant that fulfilled this item. |
| `f_id` | string | Candidate foreign key referencing `food.f_id`. Food item ordered. |
| `price` | integer | Unit price of the food item at time of order, in INR. |
| `quantity` | integer | Number of units of this item ordered. No zero or negative quantities observed in spot-check. |
| `line_amount` | integer | Total line amount = price * quantity. Computed field; verify consistency during staging. |

---

## `orders.csv`

| Column | Observed Type | Description |
|---|---|---|
| `order_id` | integer | Unique identifier for each order. Likely primary key. Range: 1–10,000,000. |
| `order_timestamp` | datetime | Full timestamp of when the order was placed. Format: `YYYY-MM-DD HH:MM:SS`. |
| `order_date` | date | Date portion of the order. Format: `YYYY-MM-DD`. Appears derived from `order_timestamp`. |
| `user_id` | integer | Candidate foreign key referencing `users.user_id`. |
| `r_id` | integer | Candidate foreign key referencing `restaurant.id`. |
| `restaurant_city` | string | City/locality of the restaurant. May contain compound values like `"Ameerpet,Hyderabad"`. |
| `cuisine` | string | Comma-separated cuisine type(s) of the order. |
| `items_count` | integer | Number of distinct menu items in the order. |
| `sales_qty` | integer | Total quantity of items ordered (sum of quantities). |
| `subtotal` | integer | Order subtotal before discount, delivery fee, and tax, in INR. |
| `discount` | integer | Discount amount applied to the order, in INR. |
| `delivery_fee` | integer | Delivery fee charged, in INR. |
| `gst` | integer | GST (Goods and Services Tax) amount applied, in INR. |
| `sales_amount` | integer | Final amount paid by customer: subtotal - discount + delivery_fee + gst, in INR. |
| `currency` | string | Currency of all monetary values. Observed value: `INR` only. |
| `payment_method` | string | Payment method used. Observed values: `UPI`, `Card`, `COD`, `NetBanking`, `Wallet`. |
| `order_status` | string | Status of the order. Observed values: `Delivered`, `Cancelled`, `Refunded`. |
| `customer_rating` | float | Rating given by customer for this order (nullable). 35.93% null. Likely only present for Delivered orders. |
| `delivery_time_min` | float | Delivery time in minutes (nullable). 8.50% null. Likely missing for Cancelled/Refunded orders. |
