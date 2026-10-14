-- Classify airlines into business models based on the academic research methodology
SELECT 
    [Route],
    Carrier,
    Total_Carrier_Pax,
    Route_Distance,
    avg_ppm,
    HHI,
    Airline_Num,
    -- Creating a categorical column mapping each carrier to its exact business model
    CASE 
        -- Legacy / Network Carriers
        WHEN Carrier IN ('DL', 'AA', 'UA', 'AS', 'HA') THEN 'Legacy'
        
        -- Low-Cost / Ultra Low-Cost Carriers
        WHEN Carrier IN ('MX', 'XP', 'SY', 'WN', 'B6', 'NK', 'F9', 'G4') THEN 'LCC'
        
        -- Regional Carriers / Feeders
        WHEN Carrier IN ('OH', '9E', 'YX', 'YV', 'MQ', 'OO', 'PT', 'G7', 'QX', 'C5', 'ZW', '3M') THEN 'Regional'
        
        ELSE 'Other' 
    END AS Business_Model
FROM Final_Analysis_Table
ORDER BY HHI DESC, avg_ppm DESC;