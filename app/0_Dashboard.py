import streamlit as st
from streamlit import session_state
from PIL import Image

from modules.utils import *

#image path
img_path = "app/imgs/400dpiLogo.jpg"


st.set_page_config(
    page_title="MTA Energy Executive Dashboard",
    page_icon=":bar_chart:",
    layout="wide"
)




if 'sub_key' not in session_state:
    session_state['sub_key'] = False

#reset sub key if returned to dashboard
session_state.sub_key=False

#st.sidebar.success("Page selector")

#setup function for home page

def home_page():

    with st.container():
        col1, col2, col3 = st.columns(3)

        st.title("Business Overview")

        with col2:
            st.image(Image.open(img_path),use_column_width=True)


    #container for high level statistics
    with st.container():

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            #number of serviced sites
            num_sites = len(get_nmi_list())

            st.subheader(f'Number of serviced sites: {num_sites}')

home_page()
