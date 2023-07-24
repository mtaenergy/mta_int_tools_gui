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
from streamlit_autorefresh import st_autorefresh

from modules.utils import *

#image path
img_path = "app/imgs/400dpiLogo.jpg"


# update every 5 mins
refresh_count=0
refresh_count=st_autorefresh(interval=5*1000, key="pricerefresh")


def update_spot_price_view_state(option:str)->None:
    """
    Function to update the session state for the spot price page
    """
    if option == "dispatch" or option == "predispatch":
        session_state.spot_price_view = option
    else:
        raise ValueError("Invalid option selected. Make sure the option selected is either dispatch or predispatch")


def display_dispatch_data():

    #get initial data
    lookback_hours = 24
    dispatch_df=get_dispatch_data(lookback_hours)



    #display NSW table and graph
    with st.empty():
        with st.container():
            st.header("NSW")
            col1, col2 = st.columns(2)
            
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


    #display QLD table and graph
    with st.empty():
        with st.container():
            st.header("QLD")
            col1, col2 = st.columns(2)
            
            with col1:
                st.dataframe(dispatch_df[dispatch_df['REGIONID']=='QLD1'])

            with col2:
                plot_df =dispatch_df[dispatch_df['REGIONID']=='QLD1'].copy()
                # Create line chart with Plotly
                fig = px.line(plot_df, x=plot_df['SETTLEMENTDATE'], y= plot_df['RRP'],
                                labels={
                                    plot_df['SETTLEMENTDATE'].name:'Date',
                                    plot_df['RRP'].name: 'RRP' 
                                })

                #render fig
                st.plotly_chart(fig, use_container_width=True)

    #display VIC table and graph
    with st.empty():
        with st.container():
            st.header("VIC")
            col1, col2 = st.columns(2)
            
            with col1:
                st.dataframe(dispatch_df[dispatch_df['REGIONID']=='VIC1'])

            with col2:
                plot_df =dispatch_df[dispatch_df['REGIONID']=='VIC1'].copy()
                # Create line chart with Plotly
                fig = px.line(plot_df, x=plot_df['SETTLEMENTDATE'], y= plot_df['RRP'],
                                labels={
                                    plot_df['SETTLEMENTDATE'].name:'Date',
                                    plot_df['RRP'].name: 'RRP' 
                                })

                #render fig
                st.plotly_chart(fig, use_container_width=True)

            

def display_predispatch_data(container: st.container):

    #get initial data
    predispatch_df=get_predispatch_data_30min()

    #query the database for the data

    #display NSW table and graph
    with container.container():
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



def _display_state_table(df: pd.DataFrame)->None:
    pass




def spot_price_page():
    if session_state.authentication_status:
        #configure sidebar to have user name
        st.sidebar.title(f"Welcome {st.session_state['name']}")


    tab1, tab2 = st.tabs(['Dispatch','Pre-Dispatch'])


    
    with tab1:
        st.header("Dispatch Prices")
        display_dispatch_data()


    # with tab2:
    #     st.header("Pre-Dispatch Prices")
        
    #     nsw_container_pre = st.empty()
    #     display_predispatch_data(nsw_container_pre)
        

    if refresh_count % 5 == 0:
        st.cache_data.clear()
        logging.info(f"Cache cleared")

    logging.info(f"Refresh Count: {refresh_count}")





setup_session_states()

if __name__ == "__main__":
    spot_price_page()