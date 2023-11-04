1. This query will retrieve the names of bus routes, bus stops, and the count of pass-ups for each combination of route and stop where there have been pass-ups. If there haven't been any pass-ups at a particular route-stop combination, it won't be included in the results.

```sql
SELECT bus_routes.route_name, bus_stops.stop_name, COUNT(pass_ups.pass_up_id) AS pass_up_count
FROM buses
JOIN bus_routes ON buses.route_id = bus_routes.route_id
JOIN bus_stops ON buses.stop_id = bus_stops.stop_id
LEFT JOIN pass_ups ON buses.bus_id = pass_ups.bus_id
GROUP BY bus_routes.route_name, bus_stops.stop_name
HAVING COUNT(pass_ups.pass_up_id) > 0
```

2. we're selecting information about bus routes, route branches, bus stops, and pass-ups. We're also calculating aggregate statistics such as the pass-up count, average temperature, and maximum wind gust.

The query includes joins across multiple tables, conditional joins, aggregation functions, grouping, a HAVING clause for filtering grouped results, and an ORDER BY clause to sort the results based on pass-up count.

```sql
SELECT 
    br.route_num, 
    br.name AS route_name,
    rb.destination, 
    bs.stop_name,
    COUNT(pu.pu_id) AS pass_up_count,
    AVG(dw.averageTemp) AS avg_temperature,
    MAX(dw.maxWindGust) AS max_wind_gust
FROM 
    BusRoute br
JOIN 
    RouteBranch rb ON br.route_num = rb.route_num
JOIN 
    Contains c ON br.route_num = c.routeNum AND rb.destination = c.Destination
JOIN 
    BusStop bs ON c.BusStopID = bs.bs_id
LEFT JOIN 
    Pass_up pu ON br.route_num = pu.routeNum AND rb.destination = pu.destination
LEFT JOIN 
    DailyWeather dw ON pu.date = dw.date
GROUP BY 
    br.route_num, 
    br.name, 
    rb.destination, 
    bs.stop_name
HAVING 
    COUNT(pu.pu_id) > 10
ORDER BY 
    pass_up_count DESC
```

3. we're using three CTEs:

PassUpCounts: This CTE calculates the pass-up counts for each route and destination combination.
MaxPassUp: This CTE calculates the maximum pass-up count across all routes and destinations.
RoutesWithMaxPassUp: This CTE identifies the routes and destinations with the maximum pass-up count.
The final SELECT statement combines information from the BusRoute, RouteBranch, Contains, and BusStop tables, and also includes the pass-up count. It uses LEFT JOINs and COALESCE to handle cases where there may be no pass-up counts available.

```sql
WITH PassUpCounts AS (
    SELECT
        br.route_num,
        rb.destination,
        COUNT(pu.pu_id) AS pass_up_count
    FROM
        BusRoute br
    JOIN
        RouteBranch rb ON br.route_num = rb.route_num
    LEFT JOIN
        Pass_up pu ON br.route_num = pu.routeNum AND rb.destination = pu.destination
    GROUP BY
        br.route_num,
        rb.destination
),

MaxPassUp AS (
    SELECT
        MAX(pass_up_count) AS max_pass_up_count
    FROM
        PassUpCounts
),

RoutesWithMaxPassUp AS (
    SELECT
        pc.route_num,
        pc.destination,
        pc.pass_up_count
    FROM
        PassUpCounts pc
    JOIN
        MaxPassUp mp ON pc.pass_up_count = mp.max_pass_up_count
)

SELECT
    r.route_num,
    r.name AS route_name,
    rb.destination,
    bs.stop_name,
    COALESCE(pc.pass_up_count, 0) AS pass_up_count
FROM
    BusRoute r
JOIN
    RouteBranch rb ON r.route_num = rb.route_num
JOIN
    Contains c ON r.route_num = c.routeNum AND rb.destination = c.Destination
JOIN
    BusStop bs ON c.BusStopID = bs.bs_id
LEFT JOIN
    RoutesWithMaxPassUp pc ON r.route_num = pc.route_num AND rb.destination = pc.destination
ORDER BY
    pass_up_count DESC;
```

3. we're using several CTEs:

PassUpCounts: Calculates the pass-up counts for each route and destination combination.
MaxPassUp: Finds the maximum pass-up count across all routes and destinations.
RoutesWithMaxPassUp: Identifies routes and destinations with the maximum pass-up count.
AverageTemperature: Calculates the average temperature for each date with at least 5 recorded temperatures.
BusRoutesWithGoodWeather: Joins bus route information with pass-up counts and average temperatures.
Finally, we select the results from BusRoutesWithGoodWeather and add a calculated column called situation that categorizes routes based on pass-up counts and average temperatures. The results are then ordered by pass-up count and average temperature in descending order.
```sql
WITH PassUpCounts AS (
    SELECT
        br.route_num,
        rb.destination,
        COUNT(pu.pu_id) AS pass_up_count
    FROM
        BusRoute br
    JOIN
        RouteBranch rb ON br.route_num = rb.route_num
    LEFT JOIN
        Pass_up pu ON br.route_num = pu.routeNum AND rb.destination = pu.destination
    GROUP BY
        br.route_num,
        rb.destination
),

MaxPassUp AS (
    SELECT
        MAX(pass_up_count) AS max_pass_up_count
    FROM
        PassUpCounts
),

RoutesWithMaxPassUp AS (
    SELECT
        pc.route_num,
        pc.destination,
        pc.pass_up_count
    FROM
        PassUpCounts pc
    JOIN
        MaxPassUp mp ON pc.pass_up_count = mp.max_pass_up_count
),

AverageTemperature AS (
    SELECT
        date,
        AVG(averageTemp) AS avg_temperature
    FROM
        DailyWeather
    GROUP BY
        date
    HAVING
        COUNT(*) >= 5
),

BusRoutesWithGoodWeather AS (
    SELECT
        br.route_num,
        br.name AS route_name,
        rb.destination,
        bs.stop_name,
        COALESCE(pc.pass_up_count, 0) AS pass_up_count,
        at.avg_temperature
    FROM
        BusRoute br
    JOIN
        RouteBranch rb ON br.route_num = rb.route_num
    JOIN
        Contains c ON br.route_num = c.routeNum AND rb.destination = c.Destination
    JOIN
        BusStop bs ON c.BusStopID = bs.bs_id
    LEFT JOIN
        RoutesWithMaxPassUp pc ON br.route_num = pc.route_num AND rb.destination = pc.destination
    JOIN
        AverageTemperature at ON pu.date = at.date
)

SELECT
    *,
    CASE
        WHEN pass_up_count > 5 AND avg_temperature > 25 THEN 'High Pass-Up and Hot Weather'
        WHEN pass_up_count > 5 THEN 'High Pass-Up'
        WHEN avg_temperature > 25 THEN 'Hot Weather'
        ELSE 'Normal'
    END AS situation
FROM
    BusRoutesWithGoodWeather
ORDER BY
    pass_up_count DESC, avg_temperature DESC;
```

4. In this query, we're joining the Arrival table with the BusRoute and RouteBranch tables based on the route number and destination. We've added a condition to filter for a specific route and destination.

The query categorizes arrivals into 'late', 'early', and 'on time' based on the deviation value, and then groups the results by deviation category, route number, route name, and destination. We've also included a HAVING clause to filter for cases where the deviation count is greater than 5.
```sql
SELECT
    CASE
        WHEN a.deviation > 0 THEN 'late'
        WHEN a.deviation < 0 THEN 'early'
        ELSE 'on time'
    END AS deviation_category,
    br.route_num,
    br.name AS route_name,
    rb.destination,
    COUNT(*) AS deviation_count
FROM
    Arrival a
JOIN
    BusRoute br ON a.route_num = br.route_num
JOIN
    RouteBranch rb ON a.route_num = rb.route_num AND a.destination = rb.destination
WHERE
    br.route_num = 'YourRouteNumber' -- Replace with your specific route number
    AND rb.destination = 'YourDestination' -- Replace with your specific destination
GROUP BY
    deviation_category,
    br.route_num,
    br.name,
    rb.destination
HAVING
    COUNT(*) > 5
```

5. we're retrieving information about deviations (deviation) and expected arrival times (expectedTime) from the Arrival table. We're also including the corresponding average temperature (averageTemp) from the DailyWeather table.

The JOIN clause connects the Arrival and DailyWeather tables based on the date column. We're also using a WHERE clause to filter for cases where there is a deviation (deviation IS NOT NULL) and where the average temperature is less than or equal to 20 degrees Celsius (dw.averageTemp <= 20).

```sql
SELECT
    a.deviation,
    a.expectedTime,
    dw.averageTemp
FROM
    Arrival a
JOIN
    DailyWeather dw ON a.date = dw.date
WHERE
    a.deviation IS NOT NULL
    AND dw.averageTemp <= 20
```

6. we're using the YEAR function to extract the year from the date column. We then use a CASE statement to categorize the average deviation into 'good', 'bad', and 'ok'. If the average deviation is greater than 5, it's categorized as 'bad'. If it's less than 2, it's categorized as 'good'. Otherwise, it's categorized as 'ok'.

The query groups the results by year and deviation category, and counts the number of occurrences for each combination.
```sql
SELECT
    YEAR(a.date) AS year,
    CASE
        WHEN AVG(a.deviation) > 5 THEN 'bad'
        WHEN AVG(a.deviation) < 2 THEN 'good'
        ELSE 'ok'
    END AS deviation_category,
    COUNT(*) AS year_count
FROM
    Arrival a
GROUP BY
    YEAR(a.date),
    deviation_category
```