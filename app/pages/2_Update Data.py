## PAGE TO UPDATE DATA IN SQL DATABASES THROUGH GUI

# Options to add
# Update GL Codes
# Update Tariffs
# Update Requests


import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit import session_state
from PIL import Image
import mtatk

from modules.utils import *

#image path
img_path = "app/imgs/400dpiLogo.jpg"

update_options=['Select option to update', 'Update GL Codes']

# Page : Update Data

def update_gl_codes():
    pass

def update_page():

    if session_state.auth_key:

        #temporary measure as i figure out how to add logo to be contained to top right
        with st.container():
                
            col1, col2, col3 = st.columns(3)

            st.title("Update Data")      

            with col2:
                st.image(Image.open(img_path),use_column_width=True)


        #container to choose the option to update
        with st.container():

            col1, col2, col3 = st.columns(3)

            with col1:
                update_in = st.selectbox("Update Option",update_options)

                

        #container to contain update specific form for chosen option
        with st.container():
            if update_in == 'Update GL Codes':
                update_gl_codes()



update_page()
