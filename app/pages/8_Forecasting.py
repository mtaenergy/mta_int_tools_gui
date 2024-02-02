import streamlit as st
import pandas as pd
import numpy as np
import base64

import plotly.express as px
from streamlit import session_state
from PIL import Image
import mtatk

from modules.utils import setup_session_states, measure_execution_time


# Page: NMI Details
@measure_execution_time
def forecasting_page():

    if session_state.authentication_status:

        # #configure sidebar
        session_state.authenticator.logout("Logout","sidebar",key='unique_key')
        st.sidebar.title(f"Welcome {st.session_state['name']}")

        
        #display search box for NMIs


        # display graph of load forecast, predispatch cost and price forecast


        # on graph, highlight regions where price forecast than the threshold


        # display tables of top NMI costs for each client 






setup_session_states()
forecasting_page()