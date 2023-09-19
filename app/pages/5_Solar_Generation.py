## PAGE TO DISPLAY SOLAR VS GENERATION OF ENERGY MARKET

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit import session_state
from PIL import Image
from streamlit_autorefresh import st_autorefresh
import logging
from modules.utils import setup_session_states, measure_execution_time

img_path = "app/imgs/400dpiLogo.jpg"


def dislay_solar_data(site: str = None):
    pass

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

        #display solar data
        dislay_solar_data()

        #display solar site details
        display_solar_site_details()


setup_session_states()

if __name__ == "__main__":
    solar_page()