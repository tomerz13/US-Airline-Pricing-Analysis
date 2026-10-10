# -*- coding: utf-8 -*-
"""
Created on Mon Jun  8 21:53:28 2026

@author: tomer
"""

########################## Seminar in Economics - Bar Illan University ######################################
#Student's ID: Tomer Zilberman 
#Facilitator: Prof. Yuval Heller
#Date: 20/08/2026

#############################################################################################################
#                                     Imports & Packages                                                    #
#############################################################################################################
#1.1)
import pandas as pd
from statsmodels.formula.api import ols
import matplotlib.pyplot as plt
import numpy as np
#from patsy import Treatment
from statsmodels.iolib.summary2 import summary_col
from statsmodels.formula.api import quantreg
import seaborn as sns
#################################### DB1B DATASET (BIG DATA) ############################################
#1.2)
df=pd.read_csv(r'ADD ADRESS HERE') 
#if you want to insert the file by yourself you may do so (copy the empty excel link between those :'' and remove the: #):
#df=pd.read_csv(r'')

#Variables:
#YEAR
#QUARTER
#ORIGIN = DEPARTURE
#DEST = LANDING
#REPORTING_CARRIER = The operator company
#PASSENGERS = How many people have paid the same fare.
#MARKET_FARE = Ticket Fare.
#MARKET_DISTANCE = Miles 

###################################################### PART 1: DATA ##########################################################
# 1.3) - Initial Cleaning (All Market)
# Remove tickets (less than $10):
df_clean_all = df[df['MARKET_FARE'] >= 10].copy()

# 1.4) - Defining "Route"
# Create a unique identifier for each route by combining Origin and Destination airports:
df_clean_all['Route'] = df_clean_all['ORIGIN'] + "-" + df_clean_all['DEST']

# 1.5) - Route Data (Calculated on ALL airlines to get true market size)
# Calculate the total number of passengers for each route across all airlines:
route_total_pax = df_clean_all.groupby('Route')['PASSENGERS'].sum().reset_index()
route_total_pax.rename(columns={'PASSENGERS': 'Total_Pax'}, inplace=True)
# Filter out small, insignificant routes (less than 90 passengers in the quarter):
route_total_pax = route_total_pax[route_total_pax['Total_Pax'] >= 90]

#Comparison - Track data retention:
total_pax_before = df_clean_all['PASSENGERS'].sum()
total_pax_after = route_total_pax['Total_Pax'].sum()
percentage_kept = (total_pax_after / total_pax_before) * 100
#The report:
print("\n=== Data Filtering Report ===")
print(f"Total passengers before filter: {total_pax_before:,.0f}")
print(f"Total passengers after filter:  {total_pax_after:,.0f}")
print(f"Percentage of passengers kept:  {percentage_kept:.2f}%")
print("=============================\n")

# 1.6) - Airline Market Share & HHI Index:
# Calculate total passengers per carrier on each route:
carrier_pax = df_clean_all.groupby(['Route', 'REPORTING_CARRIER'])['PASSENGERS'].sum().reset_index()
# Merge with total route passengers to calculate market shares:
hhi_df = pd.merge(carrier_pax, route_total_pax, on='Route')
# Calculate market share (%) and square it for the HHI formula:
hhi_df['Market_Share'] = (hhi_df['PASSENGERS'] / hhi_df['Total_Pax']) * 100
hhi_df['Share_Squared'] = hhi_df['Market_Share'] ** 2
# Sum the squared market shares per route to get the final HHI index:
route_hhi = hhi_df.groupby('Route')['Share_Squared'].sum().reset_index()
route_hhi.rename(columns={'Share_Squared': 'HHI'}, inplace=True)


#1.7) - Number of Airline Companies:
num_airlines = df_clean_all['REPORTING_CARRIER'].nunique()
print('Number of Airlines is:', num_airlines)
print(df_clean_all['REPORTING_CARRIER'].unique())

#1.8) - ALL MARKET (Weighted Average Calculation)
# Merge the cleaned dataset with the HHI index data for each route
df_all_carriers = pd.merge(df_clean_all, route_hhi[['Route']], on='Route').copy()
# Calculate the base Price per Mile (PPM) for each ticket/fare row
df_all_carriers['Price_Per_Mile'] = df_all_carriers['MARKET_FARE'] / df_all_carriers['MARKET_DISTANCE']
# Create a weighted value by multiplying the PPM by the actual number of passengers who paid that fare
df_all_carriers['Weighted_PPM'] = df_all_carriers['Price_Per_Mile'] * df_all_carriers['PASSENGERS']
# Group the data by Route and Airline Carrier, aggregating the sum of weighted PPM, total passengers, and keeping the distance
avg_ppm_all = df_all_carriers.groupby(['Route', 'REPORTING_CARRIER']).agg(
    Total_Weighted_PPM=('Weighted_PPM', 'sum'),
    Total_Carrier_Pax=('PASSENGERS', 'sum'),
    MARKET_DISTANCE=('MARKET_DISTANCE', 'first')
).reset_index()
# Calculate the final Weighted Average Price per Mile by dividing the total weighted sum by the total number of passengers
avg_ppm_all['avg_ppm'] = avg_ppm_all['Total_Weighted_PPM'] / avg_ppm_all['Total_Carrier_Pax']
# Drop the intermediate helper columns to clean up the dataframe
avg_ppm_all.drop(columns=['Total_Weighted_PPM', 'Total_Carrier_Pax'], inplace=True)
# Merge the finalized weighted average data with the route's HHI index to create the final dataframe for the regressions
final_all_df = pd.merge(avg_ppm_all, route_hhi, on='Route')

################################################################################################################################
#
#
#
#
#
###################################################### PART 2: REGRESSIONS ##########################################################
# 2.1) Model 1 

# Step 1: Normalizing variables
# Dividing concentration (HHI) and flight distance by 1,000. This is done to prevent near-zero coefficients,
# facilitate economic interpretation (the effect of a 1,000-point/mile increase),
# and improve the numerical stability of the model (reducing the Condition Number).
final_all_df['HHI_k'] = final_all_df['HHI'] / 1000.0
final_all_df['DIST_k'] = final_all_df['MARKET_DISTANCE'] / 1000.0

# Step 2: Running the regression models (stepwise building)
# Model 1: Baseline regression - effect of concentration only
m1 = ols("avg_ppm ~ HHI_k", data=final_all_df).fit()

# Model 2: Adding flight distance as a control variable (to control for spatial economies of scale)
m2 = ols("avg_ppm ~ HHI_k + DIST_k", data=final_all_df).fit()

# Model 3: Adding an interaction between concentration and distance (to test the "indirect competition" hypothesis via connecting flights)
m3 = ols("avg_ppm ~ HHI_k + DIST_k + HHI_k:DIST_k", data=final_all_df).fit()

# Model 4: Adding Carrier Fixed Effects to control for firm heterogeneity.
# Using 'Treatment' explicitly designates Delta Airlines (DL) as the reference category.
m4 = ols("avg_ppm ~ HHI_k + DIST_k + C(REPORTING_CARRIER, Treatment(reference='DL'))", data=final_all_df).fit()

# Model 5: The main structural model of the study - includes both the interaction and fixed effects
m5 = ols("avg_ppm ~ HHI_k + DIST_k + HHI_k:DIST_k + C(REPORTING_CARRIER, Treatment(reference='DL'))", data=final_all_df).fit()

# Model 6: Saturated model for robustness check - assumes the effect of distance varies across different airlines
m6 = ols("avg_ppm ~ HHI_k + DIST_k + HHI_k:DIST_k + C(REPORTING_CARRIER, Treatment(reference='DL')) + DIST_k:C(REPORTING_CARRIER, Treatment(reference='DL'))", data=final_all_df).fit()

# Step 3: Compiling and formatting the results table (in a professional academic format)
reg_table = summary_col(
    [m1, m2, m3, m4, m5, m6],
    stars=True,                                       # Adding statistical significance stars (*, **, ***)
    float_format='%.4f',                              # Rounding results to 4 decimal places
    model_names=['(1)', '(2)', '(3)', '(4)', '(5)', '(6)'], # Numbering the model columns
    regressor_order=['Intercept', 'HHI_k', 'DIST_k', 'HHI_k:DIST_k'], # Fixing the order of the regressors displayed in the table
    drop_omitted=True,                                # Hiding the rest of the coefficients (omitting the Fixed Effects rows to prevent visual clutter)
    info_dict={                                       # Adding statistical information rows at the bottom of the table
        'R-squared': lambda x: f"{x.rsquared:.3f}",
        'Adj. R-squared': lambda x: f"{x.rsquared_adj:.3f}",
        # Lambda function that checks if the model includes fixed effects and returns Yes/No accordingly
        'Carrier Fixed Effects': lambda x: 'Yes' if 'C(REPORTING_CARRIER' in str(x.model.formula) else 'No',
        'N Observations': lambda x: f"{int(x.nobs):,}" # Formatting the number of observations with commas
    }
)

# Step 4: Printing and exporting the data
print(reg_table)
# Exporting the table to a CSV file. The 'utf-8-sig' encoding ensures special characters open correctly in Excel
reg_table.tables[0].to_csv('regression_summary_normalized.csv', encoding='utf-8-sig')





# 2.2) Model 2 

# Step 1: Define the formula
# The '*' operator in statsmodels automatically includes both the main effects 
# (HHI_k and DIST_k) and their interaction term (HHI_k:DIST_k).
formula_quant = "avg_ppm ~ HHI_k * DIST_k"

# Step 2: Fit the Quantile Regression models
# Fitting the model for the 25th percentile (q=0.25). 
# This serves as a proxy for the leisure/budget passenger segment (high price elasticity, early booking).
model_q25 = quantreg(formula_quant, data=final_all_df).fit(q=0.25)

# Fitting the model for the 75th percentile (q=0.75). 
# This serves as a proxy for the business/premium passenger segment (inelastic demand, last-minute booking).
model_q75 = quantreg(formula_quant, data=final_all_df).fit(q=0.75)

# Grouping the models for the summary table
quant_models = [model_q25, model_q75]

# Step 3: Compiling and formatting the results table
quant_table = summary_col(
    quant_models, 
    stars=True,                                       # Adding statistical significance stars (*, **, ***)
    float_format='%.4f',                              # Rounding results to 4 decimal places
    model_names=['Quantile 0.25\n(Leisure/Budget)', 'Quantile 0.75\n(Business/Premium)'], # Assigning descriptive names to columns
    regressor_order=['Intercept', 'HHI_k', 'DIST_k', 'HHI_k:DIST_k'], # Fixing the order of the regressors
    info_dict={                                       # Adding statistical information rows at the bottom
        # Quantile regression uses Pseudo R-squared (based on absolute deviations) instead of standard R-squared
        'Pseudo R-squared': lambda x: f"{x.prsquared:.4f}",
        'N Observations': lambda x: f"{int(x.nobs):,}"
    }
)

# Step 4: Printing and exporting the data
print(quant_table)
# Exporting the quantile regression table to a CSV file. 
# The 'utf-8-sig' encoding ensures special characters (like the \n in names) open correctly in Excel
quant_table.tables[0].to_csv('quantile_regression_summary.csv', encoding='utf-8-sig')





# 2.3) Model 3 

# Step 1: Create a mapping dictionary to classify airlines into three business models
# This classification captures the structural and operational differences between airlines 
# (e.g., Hub-and-Spoke networks vs. Point-to-Point, cost structures).
carrier_mapping = {
    # Legacy Carriers (Network carriers with Hub-and-Spoke models and complex Revenue Management)
    'DL': 'Legacy', 'AA': 'Legacy', 'UA': 'Legacy', 'AS': 'Legacy', 'HA': 'Legacy',
    # Low-Cost Carriers (LCCs with point-to-point routes, flat pricing, and high price elasticity)
    'WN': 'LCC', 'B6': 'LCC', 'NK': 'LCC', 'F9': 'LCC', 'G4': 'LCC', 'SY': 'LCC', 'XP': 'LCC', 'MX': 'LCC',
    # Regional Carriers (Feeder airlines operating short, sparse routes under contract)
    'OO': 'Regional', 'MQ': 'Regional', 'YV': 'Regional', 'YX': 'Regional', 
    '9E': 'Regional', 'OH': 'Regional', 'ZW': 'Regional', 'PT': 'Regional', 
    'G7': 'Regional', 'QX': 'Regional', 'C5': 'Regional', '3M': 'Regional'
}

# Apply the mapping to create a new 'Business_Model' column and drop any unmapped observations
final_all_df['Business_Model'] = final_all_df['REPORTING_CARRIER'].map(carrier_mapping)
df_model_c = final_all_df.dropna(subset=['Business_Model']).copy()

# Step 2: Create binary (dummy) variables for the business models
# We explicitly create dummies for LCC and Regional. 
df_model_c['LCC'] = (df_model_c['Business_Model'] == 'LCC').astype(int)
df_model_c['Regional'] = (df_model_c['Business_Model'] == 'Regional').astype(int)

# NOTE ON ECONOMETRICS: To avoid perfect multicollinearity (the "dummy variable trap"), 
# one category must be omitted. Here, Legacy Carriers serve as the baseline/reference category.
# When LCC=0 and Regional=0, the model is evaluating a Legacy Carrier.

# Step 3: Run the regressions evaluating business model heterogeneity
# m_bus1: Tests baseline price differences (LCC, Regional) and how each model 
# exploits concentration differently (HHI_k:LCC, HHI_k:Regional).
m_bus1 = ols("avg_ppm ~ HHI_k + LCC + Regional + HHI_k:LCC + HHI_k:Regional", data=df_model_c).fit()

# m_bus2: Adds flight distance as a control variable for spatial economies of scale.
m_bus2 = ols("avg_ppm ~ HHI_k + LCC + Regional + HHI_k:LCC + HHI_k:Regional + DIST_k", data=df_model_c).fit()

# m_bus3: The full interaction model. Adds the HHI_k:DIST_k interaction to control 
# for indirect competition (connecting flights) on longer routes.
m_bus3 = ols("avg_ppm ~ HHI_k + LCC + Regional + HHI_k:LCC + HHI_k:Regional + DIST_k + HHI_k:DIST_k", data=df_model_c).fit()

# Step 4: Compile the results into a formatted summary table for Chapter 4.3
table_c = summary_col(
    [m_bus1, m_bus2, m_bus3],
    stars=True,
    float_format='%.4f',
    model_names=['(1) Base Model', '(2) Distance Control', '(3) Full Interaction'],
    regressor_order=['Intercept', 'HHI_k', 'LCC', 'Regional', 'HHI_k:LCC', 'HHI_k:Regional', 'DIST_k', 'HHI_k:DIST_k'],
    info_dict={
        'R-squared': lambda x: f"{x.rsquared:.3f}",
        'N Observations': lambda x: f"{int(x.nobs):,}"
    }
)

# Print the table to the console
print("\n=== PART C: Pricing Premium by Business Model ===")
print(table_c)

# Export the table to a CSV file for inclusion in the seminar paper
table_c.tables[0].to_csv('business_model_regression_clean.csv', encoding='utf-8-sig')

# Print the sample distribution across the three business models 
# (useful for validating that the sample is balanced and robust)
print(df_model_c['Business_Model'].value_counts())
###################################################################################################################





###################################################################################################################
################################################# Graphs ##########################################################
###################################################################################################################

################# FIGURE 1 ###################
# Step 1: Define HHI bins and labels
# Creating uniform bins of 500 points for the HHI index (from 1,000 to 10,000).
# This allows us to observe the non-linear trend of prices across different concentration levels.
bins = range(1000, 10500, 500)
labels = [f"{b}-{b+500}" for b in bins[:-1]]

# Step 2: Assign observations to bins and calculate the mean
df_plot = final_all_df.copy()
# pd.cut segments the continuous HHI variable into the discrete intervals defined above
df_plot['HHI_Bin'] = pd.cut(df_plot['HHI'], bins=bins, labels=labels, right=False)

# Grouping by the newly created HHI bins and calculating the expected average price per mile (mean)
grouped_df = df_plot.groupby('HHI_Bin', observed=False)['avg_ppm'].mean().reset_index()
grouped_df = grouped_df.dropna() # Removing any empty bins to ensure a continuous line plot

# Step 3: Initialize the plot
fig, ax = plt.subplots(figsize=(16, 8))

# Extracting X and Y values for plotting
x_labels = grouped_df['HHI_Bin'].astype(str)
x_idx = np.arange(len(grouped_df)) # Using numerical indices for X to allow smooth shading and plotting
y = grouped_df['avg_ppm'].values

# Step 4: Plot the main trend line and markers
line_color = '#1f77b4'
# Plotting the thick main line representing the pricing trend
ax.plot(x_idx, y, color=line_color, linewidth=3.5, zorder=3)

# Adding distinct markers (white circles with colored edges) for each specific bin's average
ax.plot(x_idx, y, 'o', color=line_color, markersize=9, 
        markerfacecolor='white', markeredgewidth=2.5, markeredgecolor=line_color, zorder=4)

# Step 5: Create the dynamic gradient fill under the curve
# This visually emphasizes the "markup" as concentration increases
cmap = plt.cm.Blues
norm = plt.Normalize(vmin=y.min() - 0.05, vmax=y.max()) # Normalizing Y values to map them to the color scale

for i in range(len(x_idx) - 1):
    current_y_avg = (y[i] + y[i+1]) / 2 # Calculating the midpoint height for the current segment
    relative_height = (current_y_avg - y.min()) / (y.max() - y.min())
    
    # Dynamically increasing the opacity (alpha) as the price increases
    alpha_val = 0.06 + 0.32 * relative_height
    segment_color = cmap(norm(current_y_avg)) # Assigning a darker blue shade for higher prices
    
    # Filling the area under the specific line segment
    ax.fill_between(
        x_idx[i:i+2], 
        y[i:i+2], 
        0, 
        color=segment_color, 
        alpha=alpha_val, 
        zorder=1
    )

# Step 6: Add data value annotations (price labels) above each marker
for i, txt in enumerate(y):
    ax.text(i, txt + 0.007, f"${txt:.3f}", ha='center', va='bottom', 
            color='#0a3d6e', fontweight='bold', fontsize=11, zorder=5)

# Step 7: Aesthetic formatting (Academic/Professional Style)
# Setting a bold, descriptive title and axis labels
ax.set_title("The Monopoly Markup: Route Concentration vs. Average Fare per Mile", 
             fontsize=22, fontweight='bold', pad=22, color='#222222')
ax.set_xlabel("Market Concentration (HHI Bins)", fontsize=15, fontweight='bold', labelpad=15, color='#333333')
ax.set_ylabel("Average Price Per Mile ($)", fontsize=15, fontweight='bold', labelpad=15, color='#333333')

# Formatting the X-axis ticks to show the HHI ranges diagonally for readability
ax.set_xticks(x_idx)
ax.set_xticklabels(x_labels, rotation=45, ha='right', fontsize=12)
plt.yticks(fontsize=12)

# Adding a subtle background grid for easier value reading
ax.grid(True, linestyle='--', alpha=0.5, color='#e0e0e0', zorder=0)

# Removing the top and right chart borders (spines) for a cleaner, modern look
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color('#cccccc')
ax.spines['bottom'].set_color('#cccccc')

# Setting chart limits to ensure proper spacing and visibility of all elements
ax.set_xlim(-0.5, len(x_idx) - 0.5)
ax.set_ylim(0, y.max() + 0.035)

# Automatically adjusting subplot parameters to give specified padding
plt.tight_layout()
plt.show()
##############################################


################# FIGURE 2 ###################
# Visualizing the Interaction Effect: Market Concentration across Flight Distances (Model 5)

# Step 1: Generate a continuous range of HHI values for the X-axis
# np.linspace creates 100 evenly spaced points between the minimum and maximum observed HHI_k values
hhi_range = np.linspace(final_all_df['HHI_k'].min(), final_all_df['HHI_k'].max(), 100)

# Step 2: Extract the estimated coefficients from the main structural model (Model 5)
b0 = m5.params['Intercept']       # Baseline price intercept
b_hhi = m5.params['HHI_k']        # Main effect of market concentration
b_dist = m5.params['DIST_k']      # Main effect of flight distance (economies of scale)
b_int = m5.params['HHI_k:DIST_k'] # Interaction effect (how distance mitigates the monopoly markup)

# Step 3: Initialize the plot and define the simulation scenarios
plt.figure(figsize=(10, 6))

# We simulate three distinct flight distance scenarios to illustrate the interaction.
# Note: Values are in thousands (e.g., 0.5 represents 500 miles).
distances = [0.5, 1.5, 2.5]
labels = ['Short-Haul (500 miles)', 'Medium-Haul (1,500 miles)', 'Long-Haul (2,500 miles)']
colors = ['#d95f02', '#7570b3', '#1b9e77'] # Distinct, colorblind-friendly colors

# Step 4: Calculate and plot the predicted pricing trends for each scenario
for dist, label, color in zip(distances, labels, colors):
    # ECONOMETRIC NOTE: The original regression equation is:
    # Price = b0 + b_hhi*HHI + b_dist*DIST + b_int*(HHI*DIST)
    # 
    # To plot this as a 2D line (y = intercept + slope * x) where X is HHI, 
    # we algebraically rearrange the equation by factoring out HHI:
    # y_pred = (b0 + b_dist*DIST) + (b_hhi + b_int*DIST) * HHI
    y_pred = (b0 + b_dist * dist) + (b_hhi + b_int * dist) * hhi_range
    
    # Plot the predicted line for the current distance scenario
    plt.plot(hhi_range, y_pred, label=label, color=color, linewidth=3)

# Step 5: Aesthetic formatting (Academic/Professional Style)
plt.title('Predicted Price per Mile by Concentration across Flight Distances (Model 5)', 
          fontsize=14, fontweight='bold')
plt.xlabel('Market Concentration (HHI / 1000)', fontsize=12)
plt.ylabel('Predicted Average Price Per Mile ($)', fontsize=12)

# Adding a legend with a clear frame
plt.legend(frameon=True, fontsize=11)

# Adding a subtle grid to help with reading specific values
plt.grid(True, linestyle='--', alpha=0.5)

# Adjust layout to prevent clipping of labels
plt.tight_layout()
plt.show()#################################


################# FIGURE 3 ###################
# Visualizing Price Discrimination: Interquartile Range (IQR) across Market Concentration

# Step 1: Define HHI bins and labels
# Creating uniform bins of 500 points for the HHI index (from 1,000 to 10,000).
bins = list(range(1000, 10500, 500))
labels = [f"{b}-{b+500}" for b in bins[:-1]]

df_plot = final_all_df.copy()
# Segment the continuous HHI variable into the defined discrete intervals
df_plot['HHI_Bin'] = pd.cut(df_plot['HHI'], bins=bins, labels=labels, right=False)

# Step 2: Calculate the specific quantiles for each bin
# Calculating the 25th percentile (Proxy for Leisure/Budget travelers: high elasticity, early booking)
q25_df = df_plot.groupby('HHI_Bin', observed=False)['avg_ppm'].quantile(0.25).reset_index().dropna()

# Calculating the 75th percentile (Proxy for Business/Premium travelers: inelastic demand, late booking)
q75_df = df_plot.groupby('HHI_Bin', observed=False)['avg_ppm'].quantile(0.75).reset_index().dropna()

# Extracting data arrays for plotting
actual_labels = q25_df['HHI_Bin'].astype(str)
y_q25 = q25_df['avg_ppm'].values
y_q75 = q75_df['avg_ppm'].values

# Step 3: Initialize the plot
fig, ax = plt.subplots(figsize=(16, 8))
x_positions = np.arange(len(actual_labels))

# Step 4: Calculate the Interquartile Range (IQR) representing the Price Discrimination Zone
gap = y_q75 - y_q25
min_gap, max_gap = gap.min(), gap.max()

# Step 5: Create a dynamic fill between the 25th and 75th percentiles
# The shading becomes darker (higher alpha) as the gap widens, visually emphasizing 
# how monopoly power facilitates aggressive price discrimination.
for i in range(len(x_positions) - 1):
    current_gap = (gap[i] + gap[i+1]) / 2 # Average gap for the current segment
    
    # Normalize the gap to scale the opacity (alpha) proportionally
    relative_gap = (current_gap - min_gap) / (max_gap - min_gap)
    alpha_val = 0.08 + 0.30 * relative_gap # Base opacity of 0.08, up to 0.38 at maximum gap
    
    # Shade the area between the two quantile curves
    ax.fill_between(
        x_positions[i:i+2], 
        y_q25[i:i+2], 
        y_q75[i:i+2], 
        color='#4A4A4A', 
        alpha=alpha_val, 
        zorder=1
    )

# Step 6: Plot the main quantile lines
# Plotting the 75th Percentile (Premium) curve - Purple line with square markers
ax.plot(x_positions, y_q75, color='#8E44AD', linewidth=4, marker='s', markersize=10, 
        markerfacecolor='white', markeredgewidth=2.5, label='75th Percentile (Business / Last-Minute)', zorder=3)

# Plotting the 25th Percentile (Leisure) curve - Green line with circle markers
ax.plot(x_positions, y_q25, color='#27AE60', linewidth=4, marker='o', markersize=10, 
        markerfacecolor='white', markeredgewidth=2.5, label='25th Percentile (Leisure / Budget)', zorder=3)

# Step 7: Aesthetic formatting (Academic/Professional Style)
ax.set_title("The Widening Gap: Price Discrimination Escalates in Monopoly Markets", 
             fontsize=22, fontweight='bold', pad=20, color='#333333')
ax.set_xlabel("Market Concentration (HHI Bins)", fontsize=16, fontweight='bold', labelpad=15)
ax.set_ylabel("Average Price Per Mile ($)", fontsize=16, fontweight='bold', labelpad=15)

# Formatting axes and grid
plt.xticks(x_positions, actual_labels, rotation=45, ha='right', fontsize=12)
plt.yticks(fontsize=12)
ax.grid(True, linestyle='--', alpha=0.5, zorder=0)

# Removing top and right chart borders for a cleaner look
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Step 8: Add an explanatory text box directly inside the shaded region
# Placing the text near the right side of the graph where the gap is most prominent
ax.text(len(actual_labels)-2, (y_q25[-1] + y_q75[-1])/2, 
        "Zone of Price\nDiscrimination", ha='center', va='center', 
        fontsize=12, fontweight='bold', color='#333333', 
        bbox=dict(facecolor='white', alpha=0.85, edgecolor='none', pad=4), zorder=4)

# Adding a legend with a drop shadow
ax.legend(fontsize=14, loc='upper left', frameon=True, shadow=True)

plt.tight_layout()
plt.show()
########################################


################# FIGURE 4 ###################
# Visualizing Fare Density Distributions across Airline Business Models

# Step 1: Initialize dictionaries for labels and colors
# We assign distinct, easily distinguishable colors to each business model.
model_labels = {}
colors_with_stats = {}
base_colors = {'Legacy': 'blue', 'LCC': 'green', 'Regional': 'orange'}

# Step 2: Calculate summary statistics for each group
# Iterating through each business model to calculate the empirical mean and standard deviation.
# This provides a statistical summary directly in the legend, supporting the visual interpretation
# of pricing strategies (e.g., flat pricing of LCCs vs. aggressive price discrimination of Legacy carriers).
for model in ['Legacy', 'LCC', 'Regional']:
    # Extract the price per mile data for the specific business model
    subset = df_model_c[df_model_c['Business_Model'] == model]['avg_ppm']
    mean_val = subset.mean() # Expected value (average fare)
    std_val = subset.std()   # Measure of dispersion (pricing variance)
    
    # Create a dynamic label that incorporates the calculated statistics
    new_label = f"{model} (Mean: ${mean_val:.2f}, Std: {std_val:.2f})"
    model_labels[model] = new_label
    colors_with_stats[new_label] = base_colors[model]

# Map the newly created labels back to the dataframe for plotting
df_model_c['Model_Legend'] = df_model_c['Business_Model'].map(model_labels)

# Step 3: Initialize the plot
plt.figure(figsize=(11, 6.5))

# Step 4: Generate the Kernel Density Estimate (KDE) Plot
# A KDE plot smooths the discrete data into a continuous probability density curve,
# making it ideal for visualizing the shape of price distributions (e.g., right-skewness).
ax = sns.kdeplot(
    data=df_model_c, 
    x='avg_ppm', 
    hue='Model_Legend',       # Differentiate curves by the new business model labels
    palette=colors_with_stats,# Apply the custom colors
    fill=True,                # Fill the area under the curves for better visibility
    common_norm=False,        # Normalize each distribution independently so areas sum to 1
    alpha=0.4,                # Set transparency to allow overlapping areas to be visible
    linewidth=2.5             # Make the outer lines thicker
)

# Step 5: Aesthetic formatting (Academic/Professional Style)
plt.title('Fare Density Distribution by Airline Business Model', fontsize=16, fontweight='bold', pad=15)
plt.xlabel('Average Price Per Mile ($)', fontsize=14)
plt.ylabel('Density (Frequency)', fontsize=14)

# Limit the X-axis to 0.70 to focus on the main distribution and exclude extreme outliers that distort the view
plt.xlim(0, 0.70) 

# Add a subtle background grid
plt.grid(True, alpha=0.3, linestyle='--')

# Move the legend to the upper right and format its title and font size
sns.move_legend(ax, "upper right", title='Business Model', title_fontsize=12, fontsize=11)

# Step 6: Finalize layout, export, and display
plt.tight_layout()
# Save the figure in high resolution (300 DPI) suitable for academic papers
plt.savefig('fare_density_distribution_with_stats.png', dpi=300)
plt.show()


################################################################################################################





###################################################################################################################
####################################### UNCLEANED REGRESSION (ROBUSTNESS) #########################################
###################################################################################################################
df_raw = df.copy()

# Step 1: Defining the Market (Route)
# Concatenating origin and destination airport codes to define the specific competitive market.
df_raw['Route'] = df_raw['ORIGIN'] + "-" + df_raw['DEST']

# Step 2: HHI Calculation for Raw Data
# Calculating total passengers per route to determine the overall market size
route_total_pax_raw = df_raw.groupby('Route')['PASSENGERS'].sum().reset_index()
route_total_pax_raw.rename(columns={'PASSENGERS': 'Total_Pax'}, inplace=True)

# Calculating the passenger volume for each specific carrier on each route
carrier_pax_raw = df_raw.groupby(['Route', 'REPORTING_CARRIER'])['PASSENGERS'].sum().reset_index()

# Merging to calculate the market share (percentage) for each carrier
hhi_df_raw = pd.merge(carrier_pax_raw, route_total_pax_raw, on='Route')
hhi_df_raw['Market_Share'] = (hhi_df_raw['PASSENGERS'] / hhi_df_raw['Total_Pax']) * 100

# Squaring the market shares to give exponential weight to dominant firms (standard HHI methodology)
hhi_df_raw['Share_Squared'] = hhi_df_raw['Market_Share'] ** 2

# Summing the squared shares per route to get the final Herfindahl-Hirschman Index (HHI)
route_hhi_raw = hhi_df_raw.groupby('Route')['Share_Squared'].sum().reset_index()
route_hhi_raw.rename(columns={'Share_Squared': 'HHI'}, inplace=True)

# Step 3: Weighted Average Calculation (The Fixed Part)
# Calculating the base Price Per Mile for each ticket transaction
df_raw['Price_Per_Mile'] = df_raw['MARKET_FARE'] / df_raw['MARKET_DISTANCE']

# Weighting the Price Per Mile by the number of passengers who paid that exact fare.
# This prevents extreme outliers (e.g., one passenger paying $2,000) from disproportionately 
# skewing the airline's actual average yield.
df_raw['Weighted_PPM'] = df_raw['Price_Per_Mile'] * df_raw['PASSENGERS']

# Aggregating at the Route and Carrier level
avg_ppm_raw_temp = df_raw.groupby(['Route', 'REPORTING_CARRIER']).agg(
    Total_Weighted_PPM=('Weighted_PPM', 'sum'),
    Total_Carrier_Pax=('PASSENGERS', 'sum'),
    MARKET_DISTANCE=('MARKET_DISTANCE', 'first')
).reset_index()

# Deriving the final true weighted average price per mile
avg_ppm_raw_temp['avg_ppm'] = avg_ppm_raw_temp['Total_Weighted_PPM'] / avg_ppm_raw_temp['Total_Carrier_Pax']
avg_ppm_raw = avg_ppm_raw_temp.drop(columns=['Total_Weighted_PPM', 'Total_Carrier_Pax'])

# Step 4: Merge and Normalize Variables
final_raw_df = pd.merge(avg_ppm_raw, route_hhi_raw, on='Route')

# Normalizing by 1,000 for numeric stability and interpretability (as done in the main analysis)
final_raw_df['HHI_k'] = final_raw_df['HHI'] / 1000.0
final_raw_df['DIST_k'] = final_raw_df['MARKET_DISTANCE'] / 1000.0

# Step 5: Run Robustness Regression
# Running the fully saturated model (equivalent to Model 6) on the uncleaned raw data
m6_raw = ols("avg_ppm ~ HHI_k + DIST_k + HHI_k:DIST_k + C(REPORTING_CARRIER, Treatment(reference='DL')) + DIST_k:C(REPORTING_CARRIER, Treatment(reference='DL'))", data=final_raw_df).fit()

# Step 6: Create Output Table for Comparison
# Note: 'm6' must be loaded in the environment from the previous script to allow comparison
robustness_table = summary_col(
    [m6, m6_raw], 
    stars=True,
    float_format='%.4f',
    model_names=['(1) Cleaned Data', '(2) Raw Data (Unfiltered)'], # Comparing the two datasets side-by-side
    regressor_order=['Intercept', 'HHI_k', 'DIST_k', 'HHI_k:DIST_k'],
    drop_omitted=True, # Hiding the extensive Fixed Effects rows for readability
    info_dict={
        'R-squared': lambda x: f"{x.rsquared:.3f}",
        'Adj. R-squared': lambda x: f"{x.rsquared_adj:.3f}",
        'Carrier Fixed Effects': lambda x: 'Yes',
        'N Observations': lambda x: f"{int(x.nobs):,}" # Observing the drop in R-squared due to unfiltered noise
    }
)

# Print and Export
print("\n=== ROBUSTNESS CHECK ===")
print(robustness_table)
robustness_table.tables[0].to_csv('robustness_check_summary.csv', encoding='utf-8-sig')





































