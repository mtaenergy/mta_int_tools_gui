## PAGE TO DISPLAY REAL TIME DATA OF SPOT PRICES 
## CAN CHOOSE BETWEEN DISPATCH OR PREDISPATCH

import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit import session_state
from PIL import Image
import mtatk

from modules.utils import *

#image path
img_path = "app/imgs/400dpiLogo.jpg"


def update_spot_price_view_state(option:str)->None:
    """
    Function to update the session state for the spot price page
    """
    if option == "dispatch" or option == "predispatch":
        session_state.spot_price_view = option
    else:
        raise ValueError("Invalid option selected. Make sure the option selected is either dispatch or predispatch")


def spot_price_page():
    if session_state.authentication_status:
        #configure sidebar to have user name
        st.sidebar.title(f"Welcome {st.session_state['name']}")


    #container to select either dispatch or predispatch
    with st.container():
        st.button("Dispatch", use_container_width=True,on_click=update_spot_price_view_state("dispatch"))
        st.button("Pre-Dispatch", use_container_width=True,on_click=update_spot_price_view_state("predispatch"))


    tab1, tab2 = st.tabs(['Dispatch','Pre-Dispatch'])

    with tab1:
        st.header("Dispatch Prices")

    with tab2:
        st.header("Pre-Dispatch Prices")



setup_session_states()
spot_price_page()