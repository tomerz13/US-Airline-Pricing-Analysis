-- Aggregating pricing data by business model to compare pricing strategies
WITH Classified_Data AS (
    SELECT 
        [Route],
        Total_Carrier_Pax,
        avg_ppm,
        CASE 
            WHEN Carrier IN ('DL', 'AA', 'UA', 'AS', 'HA') THEN 'Legacy'
            WHEN Carrier IN ('MX', 'XP', 'SY', 'WN', 'B6', 'NK', 'F9', 'G4') THEN 'LCC'
            WHEN Carrier IN ('OH', '9E', 'YX', 'YV', 'MQ', 'OO', 'PT', 'G7', 'QX', 'C5', 'ZW', '3M') THEN 'Regional'
            ELSE 'Other' 
        END AS Business_Model
    FROM Final_Analysis_Table
)
SELECT 
    Business_Model,
    COUNT([Route]) AS Total_Routes_Flown,
    SUM(Total_Carrier_Pax) AS Total_Passengers,
    -- Calculating the true weighted average price per mile for the entire business model
    SUM(avg_ppm * Total_Carrier_Pax) / SUM(Total_Carrier_Pax) AS True_Weighted_Avg_PPM
FROM Classified_Data
GROUP BY Business_Model
ORDER BY True_Weighted_Avg_PPM DESC;