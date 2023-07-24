## PAGE TO DISPLAY DEMAND VS GENERATION OF ENERGY MARKET

import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit import session_state
from PIL import Image
import mtatk
from streamlit_autorefresh import st_autorefresh

from modules.utils import *

#image path
img_path = "app/imgs/400dpiLogo.jpg"

st.markdown("""
        <style>
               .block-container {
                    padding-top: 0rem;
                    padding-bottom: 0rem;
                }
        </style>
        """, unsafe_allow_html=True)


def generation_page():
    if session_state.authentication_status:

        #display logo
        with st.container():
            col1, col2, col3, col4, col5 = st.columns(5)

            with col3:
                st.image(Image.open(img_path),use_column_width=True)

        #configure sidebar to have user name
        st.sidebar.title(f"Welcome {st.session_state['name']}")

        with st.container():
            generation_view = st.selectbox("Select a generation view option", ("Dispatch", "Pre-Dispatch 30 Min", "Pre-Dispatch 5 Min"),key='gen_select')

        tab1, tab2, tab3, tab4, tab5 = st.tabs(['NSW', 'QLD', 'VIC', 'SA', 'TAS'])



        
setup_session_states()

if __name__ == "__main__":
    generation_page()