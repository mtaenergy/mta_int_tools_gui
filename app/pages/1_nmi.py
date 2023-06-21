import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import sqlite3

#global variables
reading_type =['Export kWh', 'Import kWh', 'Export kVARh', 'Import kVARh', 'Cost ex GST', 'Carbon kg']
nmi_list =['nmi1','nmi2','nmi3']


# Page: NMI Details

def nmi_page():
    st.title("NMI Details")

    #top  page container
    with st.beta_container():
        st.header('Enter NMI details here')

        #set page columns
        col1, col2 =st.beta_columns(2)

        with col1:
            nmi_in = st.selectbox("Select a NMI", nmi_list)
            read_in = st.selectbox("Select an option", reading_type)

        with col2:
            start_dt_in = st.text_input("Start Date")
            end_dt_in = st.text_input("End Date")
    
    
    #middle page container


nmi_page()