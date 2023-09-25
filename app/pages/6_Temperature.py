##PAGE TO DISPLAY TEMPERATURE DATA OVER ELECTRICITY CONSUMPTION

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit import session_state
from PIL import Image
import logging
from modules.utils import setup_session_states, measure_execution_time, get_site_id, get_nem12_data, api_con
from mtatk.mta_class_nmi import NMI

img_path = "app/imgs/400dpiLogo.jpg"

@measure_execution_time
def temperature_page():
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
        st.header(f"Site Temperature vs Electricity Consumption")

        #get solar sites df
        #weather_sites_df = get_weather_stations()

        #display solar data
        #dislay_solar_data(solar_sites_df)


setup_session_states()
temperature_page()