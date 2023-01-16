### Installing Dependencies

```
$ python3 -m venv venv
$ source .\venv\Scripts\Activate
$ pip install requirements.txt
```

# About this repository

This repo contains a series of resources related to analyzing the water temperatures of the San Francisco Bay.

- Raw hourly data between the years 1994 and 2023 can be found in Data/water_temp. Each year exists as it's own .csv
- An annotated analysis and associated code, written as a jupyter notebook, can be found in analysis.ipynb.
- An interactive visualization dashboard can be found in baytemps_streamlit.py. After initializing the virtual envioronment and installing the dependencies, this application can be run by typing `streamlit run baytemps_streamlit.py` in the terminal.