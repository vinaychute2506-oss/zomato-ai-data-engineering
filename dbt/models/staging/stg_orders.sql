with source as (

    select *
    from {{ source('zomato_raw', 'ORDERS_RAW') }}

),

renamed as (

    select
        -- Keys
        trim(order_id) as order_id,
        trim(user_id) as user_id,
        trim(r_id) as restaurant_id,

        -- Dates
        try_to_timestamp_ntz(order_timestamp) as order_timestamp,
        try_to_date(order_date) as order_date,

        -- Restaurant/order attributes
        trim(restaurant_city) as restaurant_city,
        trim(cuisine) as cuisine,

        -- Quantities
        try_to_number(items_count) as items_count,
        try_to_number(sales_qty) as sales_qty,

        -- Financial measures
        try_to_number(subtotal) as subtotal,
        try_to_number(discount) as discount,
        try_to_number(delivery_fee) as delivery_fee,
        try_to_number(gst) as gst,
        try_to_number(sales_amount) as sales_amount,

        -- Other attributes
        trim(currency) as currency,
        trim(payment_method) as payment_method,
        trim(order_status) as order_status,

        -- Nullable customer/delivery metrics
        try_to_decimal(customer_rating, 3, 1) as customer_rating,
        try_to_decimal(delivery_time_min, 10, 2) as delivery_time_min

    from source

)

select *
from renamed