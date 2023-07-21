## PAGE TO DISPLAY REAL TIME DATA OF SPOT PRICES 
## CAN CHOOSE BETWEEN DISPATCH OR PREDISPATCH

import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit import session_state
from PIL import Image
import mtatk
import time
import asyncio

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


async def display_dispatch_data():

    #get initial data
    lookback_hours = 24
    dispatch_df=get_dispatch_data(lookback_hours)

    #query the database for the data
    while True:
    
        nsw_container = st.empty()

        #display NSW table and graph
        with nsw_container.container():
            col1, col2 = st.columns(2)
            st.header("NSW")
            with col1:
                st.dataframe(dispatch_df[dispatch_df['REGIONID']=='NSW1'])

            with col2:
                plot_df =dispatch_df[dispatch_df['REGIONID']=='NSW1'].copy()
                # Create line chart with Plotly
                fig = px.line(plot_df, x=plot_df['SETTLEMENTDATE'], y= plot_df['RRP'],
                                labels={
                                    plot_df['SETTLEMENTDATE'].name:'Date',
                                    plot_df['RRP'].name: 'RRP' 
                                })
        
                #render fig
                st.plotly_chart(fig, use_container_width=True)

        r= await asyncio.sleep(60)
        nsw_container.empty()

async def display_predispatch_data():

    #get initial data
    predispatch_df=get_predispatch_data_30min()
    st.dataframe(predispatch_df)

    #query the database for the data
    while True:
    
        nsw_container = st.empty()

        #display NSW table and graph
        with nsw_container.container():
            col1, col2 = st.columns(2)
            st.header("NSW")
            with col1:
                st.dataframe(predispatch_df[predispatch_df['REGIONID']=='NSW1'])

            with col2:
                plot_df =predispatch_df[predispatch_df['REGIONID']=='NSW1'].copy()

                # Create line chart with Plotly
                fig = px.line(plot_df, x=plot_df['PRED_DATETIME'], y= plot_df['RRP'],
                                labels={
                                    plot_df['PRED_DATETIME'].name:'Date',
                                    plot_df['RRP'].name: 'RRP' 
                                })
        
                #render fig
                st.plotly_chart(fig, use_container_width=True)

        r= await asyncio.sleep(60)


def _display_state_table(df: pd.DataFrame)->None:
    pass




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
        asyncio.run(display_dispatch_data())

    with tab2:
        st.header("Pre-Dispatch Prices")
        asyncio.run(display_predispatch_data())



setup_session_states()
spot_price_page()