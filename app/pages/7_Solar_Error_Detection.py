# import moduels
import pandas as pd
from sqlalchemy import create_engine
import datetime as dt
import warnings
import streamlit as st
import altair as alt
import mtatk
from streamlit import session_state
from PIL import Image
from modules.utils import setup_session_states, measure_execution_time, get_solar_generation_data, clear_flag, get_solar_sites,get_site_id, get_nem12_data, api_con

img_path = "app/imgs/400dpiLogo.jpg"

# function to request data from SQL server
def query_sql(query: str,sql_conn_str: str)-> pd.DataFrame:
    
    try:
        # Create engine
        engine = create_engine(sql_conn_str)

        # Dataframe response
        df = pd.read_sql(sql=query, con=engine)

        # Remove any duplicate records
        df = df.drop_duplicates()

    except:
        print("There was an error with your query. Please try again")

        # return empty DF
        df=pd.DataFrame()

    return df 

def request_data():
    query = "SELECT * FROM dbo.mtae_ops_solar_generated_5min ORDER BY datetime DESC"

    sql_conn_str  = "mssql+pyodbc://mtaenergy_admin:Wombat100@mtaenergy.database.windows.net:1433/sqldb-timeseries-prod?driver=ODBC+Driver+17+for+SQL+Server"

    df = query_sql(query,sql_conn_str)

    # extract dates from datetime
    df['date'] = pd.to_datetime(df['datetime']).dt.date

    # find the date range
    recent_date = df['datetime'].max()
    start_date = recent_date - dt.timedelta(days = 30)

    # extract data within the desired range
    data_range_df = df[(df['datetime'] > start_date) & (df['datetime'] <= recent_date)]

    # group data by site
    df_grouped = data_range_df.groupby(['site_id','date']).agg({'energy_generated_kwh': lambda x: x.sum(min_count=1)}).reset_index()

    return df_grouped

# Function to highlight values less than 1 in red
def highlight_low_values(s):
    if s.name == 'energy_generated_kwh':
        return ['background-color: red' if ((v <= 1) | (pd.isna(v))) else '' for v in s]
    return ['' for _ in s]  # Return an empty list of styles for any other column


def plot_with_highlights(data):
    # Line plot
    line = alt.Chart(data).mark_line().encode(
        x='date:T',  # Added ":T" to specify this is a temporal (date) field
        y='energy_generated_kwh:Q'  # Added ":Q" to specify this is a quantitative field
    )
    
    # Highlight where energy_generated_kwh is 0
    highlight = alt.Chart(data).mark_circle(color='red').encode(
        x=alt.X('date:T', title="Record Date", axis=alt.Axis(format='%d-%m-%Y')),
        y=alt.Y('energy_generated_kwh:Q', title="Solar Generation (kWh)"),
        tooltip='energy_generated_kwh',
        size=alt.value(50)  # Adjust the size of the circle as needed
    ).transform_filter(
        alt.datum.energy_generated_kwh <= 1
    )
    
    return (line + highlight)

def display_solar_error():
    df = request_data()
    # Iterate through unique 'site_id' values
    for location_id in df['site_id'].unique():
        
        location_data = df[df['site_id'] == location_id]
        # print(location_data)
        # site_name = location_data['site_name'].unique()[0] # keep for future if wanting to display site names
        fig1, fig2 = st.columns(2)
        with fig1:
            # Display a line chart with highlighted 0 values for each 'site_id'
            st.subheader(f'Site ID: {location_id}')
            st.altair_chart(plot_with_highlights(location_data), use_container_width=True)

        with fig2:
            # Record the values less than 1
            find_low = location_data['energy_generated_kwh'] <= 1
            find_na = location_data['energy_generated_kwh'].isna()
            find_low_na = find_low | find_na
            low_na_values = location_data[find_low_na][['date', 'energy_generated_kwh']]
            if not low_na_values.empty:
                # Highlight values less than 1 and display only these rows
                styled_low_na_values = low_na_values.style.apply(highlight_low_values)
                st.write("Dates with Errors:")
                st.dataframe(styled_low_na_values)
            else:
                st.write(f"No errors detected.")
        st.write('---')

@measure_execution_time
def solar_error_page():
    if session_state.authentication_status:
        session_state.authenticator.logout("Logout","sidebar",key='unique_key')

        #display logo
        with st.container():
            col1, col2, col3, col4, col5 = st.columns(5)

            with col3:
                st.image(Image.open(img_path),use_column_width=True)

        #configure sidebar to have user name
        st.sidebar.title(f"Welcome {st.session_state['name']}")

        #set header
        st.header(f"Solar Generation Data in the Past 30 Days")

        # plot solar errors
        display_solar_error()

setup_session_states()
solar_error_page()