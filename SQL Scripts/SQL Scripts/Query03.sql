-- Step 1: Calculate Price Per Mile (PPM) and weight it by passenger count for each ticket
WITH Price_Weighting AS (
    SELECT 
        [Route],
        Carrier,
        Distance,
        Passengers,
        (Fare / Distance) AS Price_Per_Mile,
        (Fare / Distance) * Passengers AS Weighted_PPM
    FROM Cleaned_Flights_Table
    WHERE Distance > 0 
),

-- Step 2: Group by route and carrier to calculate the weighted average PPM
Avg_Price_Per_Carrier AS (
    SELECT 
        [Route],
        Carrier,
        MAX(Distance) AS Route_Distance,
        SUM(Weighted_PPM) / SUM(Passengers) AS avg_ppm,
        SUM(Passengers) AS Total_Carrier_Pax
    FROM Price_Weighting
    GROUP BY [Route], Carrier
)

-- Step 3: Merge pricing data with HHI concentration metrics to create the final analytical datasetSELECT 
SELECT
    p.[Route],
    p.Carrier,
    p.Total_Carrier_Pax,
    p.Route_Distance,
    p.avg_ppm,
    h.HHI,
    h.Airline_Num
INTO Final_Analysis_Table
FROM Avg_Price_Per_Carrier p
INNER JOIN Route_HHI_Table h ON p.[Route] = h.[Route]