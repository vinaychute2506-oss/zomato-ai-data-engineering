with source as (

    select *
    from {{ source('zomato_raw', 'REVIEWS_RAW') }}

),

renamed as (

    select
        trim(review_id) as review_id,
        trim(order_id) as order_id,
        trim(user_id) as user_id,
        trim(restaurant_id) as restaurant_id,

        try_to_decimal(rating, 3, 1) as rating,

        trim(comment) as comment,

        try_to_date(review_date) as review_date

    from source

)

select *
from renamed