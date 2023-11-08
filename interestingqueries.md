1. retrieve the names of bus routes, bus stops, and the count of pass-ups for each combination of route and stop where there have been pass-ups. If there haven't been any pass-ups at a particular route-stop combination, it won't be included in the results.

```sql
select bus_routes.route_name, bus_stops.stop_name, COUNT(pass_ups.pass_up_id) as pass_up_count
from buses
join bus_routes on buses.route_id = bus_routes.route_id
join bus_stops on buses.stop_id = bus_stops.stop_id
left join pass_ups on buses.bus_id = pass_ups.bus_id
group by bus_routes.route_name, bus_stops.stop_name
having COUNT(pass_ups.pass_up_id) > 0
```

2. we're selecting information about bus routes, route branches, bus stops, and pass-ups. We're also calculating aggregate statistics such as the pass-up count, average temperature, and maximum wind gust.

The query includes joins across multiple tables, conditional joins, aggregation functions, grouping, a having clause for filtering grouped results, and an order by clause to sort the results based on pass-up count.

```sql
select 
    br.route_num, 
    br.name as route_name,
    rb.destination, 
    bs.stop_name,
    COUNT(pu.pu_id) as pass_up_count,
    AVG(dw.averageTemp) as avg_temperature,
    MAX(dw.maxWindGust) as max_wind_gust
from 
    BusRoute br
join 
    RouteBranch rb on br.route_num = rb.route_num
join 
    Contains c on br.route_num = c.routeNum and rb.destination = c.Destination
join 
    BusStop bs on c.BusStopID = bs.bs_id
left join 
    Pass_up pu on br.route_num = pu.routeNum and rb.destination = pu.destination
left join 
    DailyWeather dw on pu.date = dw.date
group by 
    br.route_num, 
    br.name, 
    rb.destination, 
    bs.stop_name
having 
    COUNT(pu.pu_id) > 10
order by 
    pass_up_count desc
```

3. we're using three CTEs:

PassUpCounts: This CTE calculates the pass-up counts for each route and destination combination.
MaxPassUp: This CTE calculates the maximum pass-up count across all routes and destinations.
RoutesWithMaxPassUp: This CTE identifies the routes and destinations with the maximum pass-up count.
The final select statement combines information from the BusRoute, RouteBranch, Contains, and BusStop tables, and also includes the pass-up count. It uses left joins and COALESCE to handle cases where there may be no pass-up counts available.

```sql
WITH PassUpCounts as (
    select
        br.route_num,
        rb.destination,
        COUNT(pu.pu_id) as pass_up_count
    from
        BusRoute br
    join
        RouteBranch rb on br.route_num = rb.route_num
    left join
        Pass_up pu on br.route_num = pu.routeNum and rb.destination = pu.destination
    group by
        br.route_num,
        rb.destination
),

MaxPassUp as (
    select
        MAX(pass_up_count) as max_pass_up_count
    from
        PassUpCounts
),

RoutesWithMaxPassUp as (
    select
        pc.route_num,
        pc.destination,
        pc.pass_up_count
    from
        PassUpCounts pc
    join
        MaxPassUp mp on pc.pass_up_count = mp.max_pass_up_count
)

select
    r.route_num,
    rb.destination,
    bs.stop_name,
    COALESCE(pc.pass_up_count, 0) as pass_up_count
from
    BusRoute r
join
    RouteBranch rb on r.route_num = rb.route_num
join
    Contains c on r.route_num = c.routeNum and rb.destination = c.Destination
join
    BusStop bs on c.BusStopID = bs.bs_id
left join
    RoutesWithMaxPassUp pc on r.route_num = pc.route_num and rb.destination = pc.destination
order by
    pass_up_count desc;
```

3. we're using several CTEs:

PassUpCounts: Calculates the pass-up counts for each route and destination combination.
MaxPassUp: Finds the maximum pass-up count across all routes and destinations.
RoutesWithMaxPassUp: Identifies routes and destinations with the maximum pass-up count.
AverageTemperature: Calculates the average temperature for each date with at least 5 recorded temperatures.
BusRoutesWithGoodWeather: Joins bus route information with pass-up counts and average temperatures.
Finally, we select the results from BusRoutesWithGoodWeather and add a calculated column called situation that categorizes routes based on pass-up counts and average temperatures. The results are then ordered by pass-up count and average temperature in descending order.
```sql
with PassUpCounts as (
    select
        br.route_num,
        rb.destination,
        COUNT(pu.pu_id) as pass_up_count from BusRoute br
    join RouteBranch rb on br.route_num = rb.route_num
    left join Pass_up pu on br.route_num = pu.routeNum and rb.destination = pu.destination
    group by
        br.route_num,
        rb.destination
),
MaxPassUp as (
    select MAX(pass_up_count) as max_pass_up_count
    from PassUpCounts
),
RoutesWithMaxPassUp as (
    select
        pc.route_num,
        pc.destination,
        pc.pass_up_count from PassUpCounts pc
    join MaxPassUp mp on pc.pass_up_count = mp.max_pass_up_count
),
AverageTemperature as (
    select
        date,
        AVG(averageTemp) as avg_temperature from DailyWeather
    group by date
    having COUNT(*) >= 5
),
BusRoutesWithGoodWeather as (
    select
        br.route_num,
        br.name as route_name,
        rb.destination,
        bs.stop_name,
        COALESCE(pc.pass_up_count, 0) as pass_up_count,
        at.avg_temperature from BusRoute br
    natural join RouteBranch rb 
    join Contains c on br.route_num = c.routeNum and rb.destination = c.Destination
    natural join BusStop bs on c.BusStopID = bs.bs_id
    left join RoutesWithMaxPassUp pc on br.route_num = pc.route_num and rb.destination = pc.destination
    natural join AverageTemperature 
)
select
    *,
    case
        when pass_up_count > 5 and avg_temperature > 25 then 'High Pass-Up and Hot Weather'
        when pass_up_count > 5 then 'High Pass-Up'
        when avg_temperature > 25 then 'Hot Weather'
        else 'Normal'
    end as situation from BusRoutesWithGoodWeather
order by pass_up_count desc, avg_temperature desc;
```

4. In this query, we're joining the Arrival table with the BusRoute and RouteBranch tables based on the route number and destination. We've added a condition to filter for a specific route and destination.

The query categorizes arrivals into 'late', 'early', and 'on time' based on the deviation value, and then groups the results by deviation category, route number, route name, and destination. We've also included a having clause to filter for cases where the deviation count is greater than 5.
```sql
select
    case
        when a.deviation > 0 then 'late'
        when a.deviation < 0 then 'early'
        else 'on time'
    end as deviation_category,
    br.route_num,
    br.name as route_name,
    rb.destination
from
    Arrival a
join
    BusRoute br on a.route_num = br.route_num
join
    RouteBranch rb on a.route_num = rb.route_num and a.destination = rb.destination
where
    br.route_num = 'YourRouteNumber' -- Replace with your specific route number
    and rb.destination = 'YourDestination' -- Replace with your specific destination
group by
    deviation_category,
    br.route_num,
    br.name,
    rb.destination
having
    COUNT(*) > 5
```

5. we're retrieving information about deviations (deviation) and expected arrival times (expectedTime) from the Arrival table. We're also including the corresponding average temperature (averageTemp) from the DailyWeather table.

The join clause connects the Arrival and DailyWeather tables based on the date column. We're also using a where clause to filter for cases where there is a deviation (deviation is not null) and where the average temperature is less than or equal to 20 degrees Celsius (dw.averageTemp <= 20).

```sql
select
    a.deviation,
    a.expectedTime,
    dw.averageTemp
from
    Arrival a
join
    DailyWeather dw on a.date = dw.date
where
    a.deviation is not null
    and dw.averageTemp <= 20
```

6. we're using the YEAR function to extract the year from the date column. We then use a case statement to categorize the average deviation into 'good', 'bad', and 'ok'. If the average deviation is greater than 5, it's categorized as 'bad'. If it's less than 2, it's categorized as 'good'. Otherwise, it's categorized as 'ok'.

The query groups the results by year and deviation category, and counts the number of occurrences for each combination.

Average deviation of each year, then categorize into 'good', 'bad', 'ok'. If it's less than 2, it's categorized as 'good'. Otherwise, it's categorized as 'ok'.
```sql
select year(t.date)
    case 
        when AVG(deviation) > 5 then 'bad'
        when AVG(deviation) < 2 then 'good'
        else 'ok'
    end as dev
    count(*) from Arrival as a
left join time_table as t on t.id = a.id 
group by
    year(t.date), dev
```
find the most popular bus stop for the route with the highest traffic count
```sql
WITH RouteTrafficCount as (
    select
        R.route_num,
        R.name as route_name,
        COUNT(*) as total_traffic_count from BusRoute R
    natural join RouteBranch RB on 
    natural join Drives D 
    natural join Traffic T 
    group by R.route_num, R.name
    order by total_traffic_count desc
    LIMIT 1
)
select
    RTC.route_num,
    RTC.route_name,
    RTC.total_traffic_count,
    BS.str_name as most_popular_bus_stop from RouteTrafficCount RTC
natural join RouteBranch RB 
natural join Contains C 
natural join BusStop BS 
where C.routeNum = RTC.route_num
group by RTC.route_num, RTC.route_name, RTC.total_traffic_count, BS.str_name
```

PassUpCounts - calculates the pass-up counts for each route and destination
MaxPassUp - calculates the maximum pass-up count across all routes and destinations
RoutesWithMaxPassUp - identifies the routes and destinations with the maximum pass-up count
Then combines information from the BusRoute, RouteBranch, Contains, and BusStop tables, and also includes the pass-up count
```sql
with PassUpCounts as (
    select
        br.route_num,
        rb.destination,
        COUNT(pu.pu_id) as pass_up_count from BusRoute br
    natural join RouteBranch rb 
    left join Pass_up pu on br.route_num = pu.routeNum and rb.destination = pu.destination
    group by
        br.route_num,
        rb.destination
),
MaxPassUp as (
    select MAX(pass_up_count) as max_pass_up_count from PassUpCounts
),
RoutesWithMaxPassUp as (
    select
        pc.route_num,
        pc.destination,
        pc.pass_up_count from PassUpCounts pc
    natural join MaxPassUp mp 
)
select
    r.route_num,
    rb.destination,
    bs.stop_name,
    --coalesce: replace null with 0
    coalesce(pc.pass_up_count, 0) as pass_up_count from BusRoute r
natural join RouteBranch rb 
join Contains c on r.route_num = c.routeNum and rb.destination = c.Destination
natural join BusStop bs 
left join RoutesWithMaxPassUp pc on r.route_num = pc.route_num and rb.destination = pc.destination
order by
    pass_up_count desc;
```

similar to the one above but with temperature
```sql
with PassUpCounts as (
    select
        br.route_num,
        rb.destination,
        COUNT(pu.pu_id) as pass_up_count from BusRoute br
    natural join RouteBranch rb 
    left join Pass_up pu on br.route_num = pu.routeNum and rb.destination = pu.destination
    group by
        br.route_num,
        rb.destination
),
MaxPassUp as (
    select MAX(pass_up_count) as max_pass_up_count
    from PassUpCounts
),
RoutesWithMaxPassUp as (
    select
        pc.route_num,
        pc.destination,
        pc.pass_up_count from PassUpCounts pc
    natural join MaxPassUp mp 
),
AverageTemperature as (
    select
        date,
        AVG(averageTemp) as avg_temperature from DailyWeather
    group by date
    having COUNT(*) >= 5
),
BusRoutesWithBadWeather as (
    select
        br.route_num,
        br.name as route_name,
        rb.destination,
        bs.stop_name,
        COALESCE(pc.pass_up_count, 0) as pass_up_count,
        at.avg_temperature from BusRoute br
    natural join RouteBranch rb 
    join Contains c on br.route_num = c.routeNum and rb.destination = c.Destination
    natural join BusStop bs on c.BusStopID = bs.bs_id
    left join RoutesWithMaxPassUp pc on br.route_num = pc.route_num and rb.destination = pc.destination
    natural join AverageTemperature 
)
select
    *,
    case
        when pass_up_count > 5 and avg_temperature < 0 then 'High Pass-Up and Cold Weather'
        when pass_up_count > 5 then 'High Pass-Up'
        when avg_temperature < 0 then 'Cold Weather'
        else 'Normal'
    end as situation from BusRoutesWithBadWeather
order by pass_up_count desc, avg_temperature desc;
```

search by busroute and a destination, see whether it comes late, early or on time
```sql
select
    case
        when a.deviation > 0 then 'late'
        when a.deviation < 0 then 'early'
        else 'on time'
    end as deviation_category,
    br.route_num,
    rb.destination from Arrival a
natural join BusRoute br 
join RouteBranch rb on a.route_num = rb.route_num and a.destination = rb.destination
where br.route_num = ? and rb.destination = ?
group by
    deviation_category,
    br.route_num,
    rb.destination
```