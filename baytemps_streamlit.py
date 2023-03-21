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
st.write("## San Francisco Bay Water Temperature")

d = bt.import_data()
daily_average, da2 = bt.average_daily_data(data = d)


todays_average = daily_average.iloc[-1,5]
yesterdays_average = daily_average.iloc[-2,5]
last_week_average = daily_average.iloc[[-8,-9,-10,-11,-12,-13,-14,-15],5].mean()
day_delta = (todays_average - yesterdays_average).round(1)
week_delta = (todays_average - last_week_average).round(1)
col1,col2,col3 = st.columns(3)
with col1:
    st.metric("Today's Average Temperature", todays_average.round(1))
with col2:
    st.metric("Yesterday's Average Temperature", yesterdays_average.round(1), day_delta)
with col3:
    st.metric("Last Week's Average Temperature", last_week_average.round(1), week_delta)
st.write("#### Most recent time point: "+str(d.iloc[-1,5])+"-"+str(d.iloc[-1,6])+"-"+str(d.iloc[-1,4])+" at "+str(d.iloc[-1,2])+" GMT")

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
    value = 2023
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

plt.grid(axis='y', linestyle = "--")
ax.set_xlabel("Day Of Year")
ax.set_ylabel("Average Temperature (\N{DEGREE SIGN}F)")
ax.set_ylim(bottom = 48, top = 67.5)
ax.set_yticks(np.arange(49,68,1))
ax.legend()
st.pyplot(fig)