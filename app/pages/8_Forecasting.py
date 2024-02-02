import streamlit as st
import pandas as pd
import numpy as np
import base64

import plotly.express as px
from streamlit import session_state
from PIL import Image
import mtatk

from modules.utils import setup_session_states, measure_execution_time, clear_flag, get_nmi_list

## GLOBAL VARIABLES
nmi_list =get_nmi_list()
img_path = "app/imgs/400dpiLogo.jpg"
session_state.live_state=0



# Page: NMI Details
@measure_execution_time
def forecasting_page():

    if session_state.authentication_status:

        # #configure sidebar
        session_state.authenticator.logout("Logout","sidebar",key='unique_key')
        st.sidebar.title(f"Welcome {st.session_state['name']}")

        #setup header
        with st.container():
                
            col1, col2, col3 = st.columns(3)

            st.title("Site Forecasts")      

            with col2:
                st.image(Image.open(img_path),use_column_width=True)

        
        #display search box for NMIs
        nmi_in = st.selectbox("Select a NMI", nmi_list,on_change=clear_flag())


        # display graph of load forecast, predispatch cost and price forecast


        # on graph, highlight regions where price forecast than the threshold


        # display tables of top NMI costs for each client 






setup_session_states()
forecasting_page()