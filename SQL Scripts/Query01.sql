-- Aviation Project Q1 2025 - American Flight Market
USE Aviation_Project;
GO
IF OBJECT_ID('Cleaned_Flights_Table', 'U') IS NOT NULL
    DROP TABLE Cleaned_Flights_Table;
GO
-- Step 1: Extract, clean, and format raw flight data
SELECT 
    ORIGIN AS Origin,
    DEST AS Destination,

    -- Create a unique route identifier by joining Origin and Destination
    CONCAT(ORIGIN, '-', DEST) AS [Route],
    REPORTING_CARRIER AS Carrier,
    
    -- Safely convert text to number: handle potential decimals first (FLOAT), then convert to whole numbers (INT)
    CAST(TRY_CAST(PASSENGERS AS FLOAT) AS INT) AS Passengers,
    TRY_CAST(MARKET_FARE AS FLOAT) AS Fare,
    TRY_CAST(MARKET_DISTANCE AS FLOAT) AS Distance

-- Store the processed results into a new physical table for downstream analysis
INTO Cleaned_Flights_Table
FROM T_DB1B_MARKET
WHERE 
    -- Filter out invalid fares and drop missing data (NULLs)
    TRY_CAST(MARKET_FARE AS FLOAT) IS NOT NULL
    AND TRY_CAST(MARKET_FARE AS FLOAT) >= 10 
    AND ORIGIN IS NOT NULL 
    AND DEST IS NOT NULL