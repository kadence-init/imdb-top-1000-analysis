/*
SQL-запрос для выявления актуальных топ-режиссеров десятилетия.
Проект: IMDb Explorer

Задача этого запроса — не просто найти режиссеров с самыми высокими оценками,
а идентифицировать тех, кто демонстрирует СТАБИЛЬНО ВЫСОКОЕ КАЧЕСТВО прямо сейчас,
выпустив несколько высокооцененных фильмов за последнее десятилетие.
Это — ключевой аналитический инсайт для дашборда.
*/

SELECT
    Director,
    COUNT(Series_Title) AS HighRated_Films_Count,
    AVG(IMDB_Rating)    AS Average_Rating_Of_Top_Films
FROM
    imdb_data
WHERE
    Released_Year >= 2014 
    AND 
    IMDB_Rating >= 8.0
GROUP BY
    Director
HAVING
    COUNT(Series_Title) >= 2
ORDER BY
    Average_Rating_Of_Top_Films DESC;
