IF OBJECT_ID('Route_HHI_Table', 'U') IS NOT NULL
    DROP TABLE Route_HHI_Table;
GO
-- Step 1: Calculate total passengers per route and filter out low-traffic routes
WITH Route_Totals AS (
    SELECT 
        [Route],
        SUM(Passengers) AS Total_Route_Pax
    FROM Cleaned_Flights_Table
    GROUP BY [Route]
    HAVING SUM(Passengers) >= 90
),

-- Step 2: Calculate total passengers for each carrier on each route
Carrier_Totals AS (
    SELECT 
        [Route],
        Carrier,
        SUM(Passengers) AS Total_Carrier_Pax
    FROM Cleaned_Flights_Table
    GROUP BY [Route], Carrier
),

-- Step 3: Merge data to calculate market share and square it for the HHI formula
Market_Shares AS (
    SELECT 
        c.[Route],
        c.Carrier,
        c.Total_Carrier_Pax,
        r.Total_Route_Pax,        
        (CAST(c.Total_Carrier_Pax AS FLOAT) / r.Total_Route_Pax) * 100 AS Market_Share,
        POWER((CAST(c.Total_Carrier_Pax AS FLOAT) / r.Total_Route_Pax) * 100, 2) AS Share_Squared
    FROM Carrier_Totals c
    INNER JOIN Route_Totals r ON c.[Route] = r.[Route]
)

-- Step 4: Aggregate the squared shares to calculate the final HHI and count competitors
SELECT 
    [Route],
    SUM(Share_Squared) AS HHI,
    COUNT(Carrier) AS Airline_Num
INTO Route_HHI_Table
FROM Market_Shares
GROUP BY [Route]