with source as (

    select *
    from {{ source('zomato_raw', 'FOOD_RAW') }}

),

renamed as (

    select
        trim(f_id) as food_id,
        trim(item) as item,
        trim(veg_or_non_veg) as veg_or_non_veg
    from source

)

select *
from renamed