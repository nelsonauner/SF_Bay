import pandas as pd
import numpy as np
import streamlit as st

def doy(month,day):
    months = [31,28,31,30,31,30,31,31,30,31,30,31]
    return sum(months[0:month-1])+day

@st.experimental_memo(ttl = 60*60)
def import_data():
    """
    An argument-less function that imports all of the hourly SF Bay water data
    
    Returns:
        d (pd.DataFrame) - A dataframe containing hourly San Francisco Bay water temperatures between 1994 and 2023
    """

    d = pd.read_csv("https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?product=water_temperature&application=NOS.COOPS.TAC.PHYSOCEAN&begin_date=19930414&end_date=19940413&station=9414290&time_zone=GMT&units=english&interval=h&format=csv")
    for year in np.arange(start = 1994, stop = 2023):
        url = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?product=water_temperature&application=NOS.COOPS.TAC.PHYSOCEAN&begin_date="+str(year)+"0414&end_date="+str(year+1)+"0413&station=9414290&time_zone=GMT&units=english&interval=h&format=csv"
        #file = "data/water_temp/"+str(year)+".csv"
        year_data = pd.read_csv(url)
        d = pd.concat([d,year_data])
    d["Date Time"] = pd.to_datetime(d["Date Time"])
    d["Date Time"] = d["Date Time"].astype("str")
    d[["date","time"]] = d["Date Time"].str.split(" ", expand = True)   
    
    #Cleaning up the dataframe
    d.rename(columns = {d.columns[1]:"temp"}, inplace = True)
    d = d.loc[:,["date", "time", "temp"]]
    d.loc[d.temp == "-","temp"] = np.nan
    d.temp = d.temp.astype("float")
    d.reset_index(inplace = True)

    #Formatting year, month, day columns
    d.date = pd.to_datetime(d.date)
    d.date = d.date - pd.Timedelta(hours = 7)
    d["year"] = d.date.dt.year
    d["month"] = d.date.dt.month
    d["day"] = d.date.dt.day
   
    #Remove Feb29
    d = d[~((d.date.dt.month == 2) & (d.date.dt.day == 29))]
    
    #Tag each day with day of year, assuming no leap years
    d["doy"] = 0
    for i in d.index:
        d["doy"][i] = doy(d.month[i], d.day[i])



    return d

@st.experimental_memo
def average_daily_data(data: pd.DataFrame):
    """
    Takes the raw hourly temperature data and summarizes it into daily averages

    Arguments:
        data (pd.DataFrame): Raw hourly temperature data, the same dataframe returned by import_data
    
    Returns:
        daily_average (pd.DataFrame): A dataframe containing the average temperature for every individual day going back to 1994
        da2 (pd.DataFrame): A dataframe containing the averate temperature for every day of the year across all years
    """
    #Calculating averages for each day for every DOY in the dataset (within each year)
    daily_average = data.groupby(by = ["year", "month", "day","doy"], as_index = False).agg(Mean = ("temp", np.mean), Sd = ("temp", np.std))
    daily_average.sort_values(by = ["year","month","doy"], inplace = True)
    daily_average.reset_index(inplace = True)

    #Daily average across all years
    da2 = daily_average.groupby(by = ["doy","month","day"], as_index = False).agg(Mean = ("Mean", np.mean), Sd = ("Mean", np.std), N = ("Mean", len))
    da2.sort_values(by = ["doy"], inplace = True)
    da2.reset_index(inplace = True)


    return daily_average, da2