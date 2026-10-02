with source as (

    select *
    from {{ source('zomato_raw', 'MENU_RAW') }}

),

renamed as (

    select
        trim(menu_id) as menu_id,
        trim(r_id) as restaurant_id,
        trim(f_id) as food_id,
        trim(cuisine) as cuisine,

        try_to_decimal(
            regexp_replace(price, '[^0-9.]', ''),
            10,
            2
        ) as price

    from source

)

select *
from renamed