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

update_options=['Select option to update', 'Update NMI Details']
global_nmi_list =['Select a NMI']
global_nmi_list=global_nmi_list+get_nmi_list()

#clear flag to display NMI details
session_state.display_details=False
session_state.live_state=0

# Page : Update Data

def update_nmi_sd():
    
    with st.container():

        col1, col2, col3 = st.columns(3)

        with col1:
            #select a nmi
            nmi_in = st.selectbox("Select a NMI", global_nmi_list)

    #display the current details for that nmi
    with st.container():

        if nmi_in != 'Select a NMI':

            st.subheader("Current NMI Details")

            nmi_site_details = get_nmi_customer(nmi=nmi_in)

            #set series as df
            nmi_details_df = pd.DataFrame(nmi_site_details)

            #tranpose the df
            nmi_details_df = nmi_details_df.transpose()

            #display the editable dataframe
            edited_df = st.data_editor(nmi_details_df,use_container_width=True,column_config ={'nmi': None})

            logging.info(edited_df)

            #add a button to submit new dataframe
            col1, col2, col3 = st.columns(3)

            with col2:
                if st.button("Update", use_container_width=True):
                    update_cols = edited_df.columns
                    match_cols =['nmi']
                    table_name = 'mtae_ops_billing_nmi_standing_data_prod'

                    sql_con.update_to_database(update_cols, match_cols,df=edited_df, database='standingdata', table_name=table_name)

def update_page():

    if session_state.authentication_status:

        # #configure sidebar
        session_state.authenticator.logout("Logout","sidebar",key='unique_key')
        st.sidebar.title(f"Welcome {st.session_state['name']}")


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
            if update_in == 'Update NMI Details':
                update_nmi_sd()



setup_session_states()
update_page()
