# US Airline Market Concentration & Pricing Dynamics ✈️📊

## Project Overview
This project analyzes the impact of market concentration (measured by the Herfindahl-Hirschman Index - HHI) on domestic flight prices in the US. By processing raw DB1B ticketing data from the US Department of Transportation, this project explores how different airline business models (Legacy, Low-Cost, and Regional) leverage local monopolies and market power to implement price discrimination.

## Tech Stack
* **SQL (SQL Server / T-SQL):** End-to-end Data Pipeline (ETL), window functions, table joins, data type casting, and business logic implementation (`CASE WHEN`).
* **Python:** Data visualization, quantile regression, and statistical analysis (Pandas, Statsmodels, Matplotlib, Seaborn).

## Data Pipeline (SQL)
The data processing was entirely handled in SQL Server through a 5-step pipeline:
1. **`01_ETL_and_Cleaning.sql`:** Extracted raw ticket data, filtered invalid fares, and cast data types for numerical analysis.
2. **`02_Market_Share_and_HHI.sql`:** Used Common Table Expressions (CTEs) to calculate route-level passenger volumes and compute the HHI market concentration index.
3. **`03_Pricing_and_Integration.sql`:** Calculated the true passenger-weighted average Price Per Mile (PPM) and merged it with the HHI metrics.
4. **`04_Airline_Classification.sql`:** Implemented business logic using `CASE WHEN` to classify carriers into Legacy, LCC, and Regional models based on academic methodologies.
5. **`05_Business_Model_Insights.sql`:** Aggregated the final dataset to generate macro-level business insights regarding pricing strategies across different carrier types.

## Key Business Insights
* **The Monopoly Markup:** A strong positive correlation exists between route concentration (HHI) and the average price per mile. Monopolistic routes are significantly more expensive than competitive ones.
* **Business Model Heterogeneity:** 
  * **Legacy Carriers** (e.g., Delta, United) aggressively leverage monopoly power to maximize the "monopoly premium," heavily targeting price-inelastic business travelers.
  * **Low-Cost Carriers (LCCs)** (e.g., Southwest, Spirit) are significantly restricted in their ability to exploit market power due to the high price elasticity of their leisure-focused customer base.
* **Indirect Competition:** Flight distance acts as a mitigating factor. On long-haul routes, the availability of connecting flights via rival hubs suppresses the direct route's monopoly pricing power.

## How to View the Project
* The complete data engineering pipeline can be found in the `sql_scripts/` folder.
* The visual and statistical analysis can be viewed in the `notebooks/` folder.
