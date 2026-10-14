# US Airline Pricing Strategy: Data Analysis for Aviation Pricing Analysts ✈️📊

### 1. Executive Summary
This end-to-end data analytics project analyzes over 85,000 US flight records (DB1B dataset) to explore the relationship between market concentration and ticket pricing. Designed from the perspective of an Aviation Pricing Analyst, the project utilizes SQL for robust data modeling, Python for data processing, and Power BI for building an interactive strategic dashboard.

### 2. Business Problem
**The Context:** In the highly competitive airline industry, Revenue Management and Route Planning teams must constantly adjust pricing strategies and seek new profitable routes. 

**The Problem:** Without a clear visualization of how market concentration (HHI - Herfindahl-Hirschman Index) impacts the Price-per-Mile (PPM) across different airline business models (Legacy, LCC, Regional), airlines struggle to spot uncompetitive routes or optimize their own pricing power.

**The Objective:** This project provides an interactive dashboard tailored for Pricing Analysts and Aviation Strategists to solve two main challenges:
1. **Identify Market Entry Opportunities:** Enable Low-Cost Carriers (LCCs) to spot highly concentrated, overpriced routes ripe for disruption.
2. **Optimize Yield Management:** Allow Legacy and Regional carriers to benchmark their pricing power and adjust dynamic pricing based on local competition levels.

### 3. Methodology
* **Data Engineering (SQL Server):** Built a robust 5-step ETL pipeline to clean, aggregate, and calculate key economics metrics (HHI, total route passengers, average PPM) from raw DOT flight data.
* **Data Processing (Python):** Utilized `pandas` for data validation, sampling, and generating representative datasets.
* **Data Visualization (Power BI):** Developed an interactive dashboard using DAX to classify business models dynamically and visualize pricing distributions and correlation trends.

### 4. Skills & Tools
* **Languages:** SQL, Python (Pandas)
* **Tools:** SQL Server, Power BI, GitHub
* **Analytical Skills:** Pricing Strategy, Yield Management, Market Concentration (HHI), ETL Pipelines, Data Visualization, DAX (Data Analysis Expressions).

### 5. Results & Business Recommendations
* **LCC Market Disruption:** The data reveals that Low-Cost Carriers maintain consistently low prices regardless of market concentration. **Recommendation:** LCCs should target highly concentrated routes currently dominated by Regional carriers, where the "monopoly premium" is highest, to capture market share.
* **Regional Carrier Yield Optimization:** Regional carriers demonstrate the highest price elasticity relative to market concentration, capitalizing heavily on monopolistic routes. **Recommendation:** Network planners and Legacy carriers partnering with Regionals should closely monitor these routes and optimize price discrimination strategies before LCC competitors enter the market.

### 6. Dashboard Preview
<img width="1443" height="808" alt="image" src="https://github.com/user-attachments/assets/96202b7d-ec71-496b-8e74-7fa937f63561" />


