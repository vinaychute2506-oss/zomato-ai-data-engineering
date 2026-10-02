select
    restaurant_id,
    restaurant_name,
    city,
    rating,
    rating_count,
    cost,
    cuisine,
    license_number,
    restaurant_link,
    address,
    menu_link
from {{ ref('stg_restaurants') }}