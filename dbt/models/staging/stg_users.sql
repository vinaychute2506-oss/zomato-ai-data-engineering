WITH source AS (

    SELECT *
    FROM {{ source('zomato_raw', 'USERS_RAW') }}

),

cleaned AS (

    SELECT
        TRIM(user_id) AS user_id,
        TRIM(name) AS name,
        LOWER(TRIM(email)) AS email,

        TRY_TO_NUMBER(age) AS age,

        TRIM(gender) AS gender,
        TRIM(marital_status) AS marital_status,
        TRIM(occupation) AS occupation,

        TRY_TO_NUMBER(monthly_income) AS monthly_income,

        TRIM(educational_qualifications) AS educational_qualifications,

        TRY_TO_NUMBER(family_size) AS family_size

    FROM source

)

SELECT *
FROM cleaned