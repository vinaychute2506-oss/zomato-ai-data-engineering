WITH source AS (

    SELECT *
    FROM {{ source('zomato_raw', 'RESTAURANT_RAW') }}

),

cleaned AS (

    SELECT
        TRIM(id) AS restaurant_id,
        TRIM(name) AS restaurant_name,
        TRIM(city) AS city,

        TRY_TO_DECIMAL(
            NULLIF(TRIM(rating), '--'),
            3,
            2
        ) AS rating,

        TRY_TO_NUMBER(rating_count) AS rating_count,

        TRY_TO_NUMBER(
            REGEXP_REPLACE(TRIM(cost), '[^0-9.]', '')
        ) AS cost,

        TRIM(cuisine) AS cuisine,
        TRIM(lic_no) AS license_number,
        TRIM(link) AS restaurant_link,
        TRIM(address) AS address,
        TRIM(menu) AS menu_link

    FROM source

)

SELECT *
FROM cleaned