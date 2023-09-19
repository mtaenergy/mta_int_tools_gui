## PAGE TO DISPLAY SOLAR VS GENERATION OF ENERGY MARKET

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit import session_state
from PIL import Image
from streamlit_autorefresh import st_autorefresh
import logging
from modules.utils import setup_session_states, measure_execution_time, get_solar_generation_data, clear_flag, get_solar_sites

img_path = "app/imgs/400dpiLogo.jpg"


def dislay_solar_data(solar_sites_list: list):
    

    #container to store date and store selection
    with st.container():
        col1, col2, col3 = st.columns(3)

        with col1:
            start_date=st.date_input("Start Date",value=pd.to_datetime('today')-pd.Timedelta(days=1), on_change=clear_flag())
            start_date=pd.to_datetime(start_date)

        with col2:
            end_date=st.date_input("End Date",value=pd.to_datetime('today'),on_change=clear_flag())
            end_date=pd.to_datetime(end_date)

        with col3:
            site=st.selectbox("Select a site",options=solar_sites_list,on_change=clear_flag())



    #get solar data df
    solar_df = get_solar_generation_data(site=site)


    #filter for date range
    solar_df = solar_df[(solar_df['datetime']>=start_date) & (solar_df['datetime']<=end_date)]

    #dislay in line chart
    with st.container():
        fig = px.line(solar_df, x='datetime', y='energy_generated_kwh', title=f"Generation for {site}")
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Generation (kWh)",
            legend_title="Legend Title"
        )
        st.plotly_chart(fig, use_container_width=True)

def display_solar_site_details(site: str = None):
    pass


def solar_page():
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
        st.header(f"Solar Production")

        #get solar sites df
        solar_sites_df = get_solar_sites()
        solar_sites_list = solar_sites_df['site_name'].unique().tolist()

        #display solar data
        dislay_solar_data(solar_sites_list)

        #display solar site details
        display_solar_site_details()


setup_session_states()

if __name__ == "__main__":
    solar_page()