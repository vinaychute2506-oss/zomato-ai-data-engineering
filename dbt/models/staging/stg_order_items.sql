with source as (

    select *
    from {{ source('zomato_raw', 'ORDER_ITEMS_RAW') }}

),

renamed as (

    select
        trim(order_item_id) as order_item_id,
        trim(order_id) as order_id,
        trim(r_id) as restaurant_id,
        trim(f_id) as food_id,

        try_to_decimal(price, 10, 2) as price,
        try_to_number(quantity) as quantity,
        try_to_decimal(line_amount, 12, 2) as line_amount

    from source

)

select *
from renamed