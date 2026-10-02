select
    user_id,
    name,
    email,
    age,

    case
        when age is null then 'Unknown'
        when age < 25 then 'Gen Z'
        when age < 40 then 'Millennials'
        when age > 55 then 'Gen X'
        else 'Boomer'
    end as age_segment,

    gender,
    marital_status,
    occupation,
    monthly_income,
    educational_qualifications,
    family_size
from {{ ref('stg_users') }}