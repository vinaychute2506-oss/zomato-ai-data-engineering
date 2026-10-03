{{ config(
    materialized='table',
    tags=['ai']
) }}

SELECT
    rest.city,
    e.topic,
    e.sentiment_label,
    COUNT(*) AS review_count,
    ROUND(AVG(r.rating), 2) AS avg_rating,
    ROUND(AVG(e.sentiment_score), 3) AS avg_sentiment_score,
    MAX(e.key_issue) AS key_issue
FROM {{ source('ai', 'review_enriched') }} AS e
INNER JOIN {{ ref('stg_reviews') }} AS r
    ON e.review_id = r.review_id
INNER JOIN {{ ref('stg_restaurants') }} AS rest
    ON r.restaurant_id = rest.restaurant_id
GROUP BY
    rest.city,
    e.topic,
    e.sentiment_label