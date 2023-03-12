import streamlit as st
import streamlit_funcs.baytemps as bt

import pymc as pm
import arviz as az

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime as dt
st.set_page_config(layout = "centered")
st.write("# San Francisco Bay Water Temperature Explorer")

d = bt.import_data()
daily_average, da2 = bt.average_daily_data(data = d)

#Creating a year x day matrix of mean temperature values for use in the az.plot_hdi function
interval_data = pd.DataFrame(
    daily_average.loc[
        daily_average.year<=2022,:
    ].pivot(
        index = "year",columns = "doy", values = "Mean"
        )
)
#Imputing missing values (average temperature from all other years)
interval_data = interval_data.fillna(interval_data.mean())

year = st.number_input(
    label = "Enter a year between 1994 and 2023",
    min_value = 1994, max_value = 2023, 
    value = 2022
)

fig, ax = plt.subplots(figsize = (9,6))
#Creating the 90% interval shaded region
az.plot_hdi(
    x = da2.doy, y = interval_data, 
    hdi_prob = 0.9, fill_kwargs = {"label": "5th-95th Percentile (1994-2023)"}
    )
#Average daily temperatures across all years
plt.plot(da2.doy, da2.Mean, label = "Average (1994-2023)", linestyle = "--")

for year_trace in daily_average.year.unique():
    plt.plot(
        daily_average.loc[daily_average.year == year_trace,"doy"],
        daily_average.loc[daily_average.year == year_trace,"Mean"], 
        color = "Grey", alpha = 0.1
    )

#Average daily temperature from selected year
plt.plot(
    daily_average.loc[daily_average.year == year,"doy"],
    daily_average.loc[daily_average.year == year,"Mean"], 
    color = "Red", label = (str(year))
    )
ax.set_xlabel("Day Of Year")
ax.set_ylabel("Average Temperature (\N{DEGREE SIGN}F)")
ax.legend()
st.pyplot(fig)