## PAGE TO DISPLAY REAL TIME DATA OF SPOT PRICES 
## CAN CHOOSE BETWEEN DISPATCH OR PREDISPATCH

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


# update every 1 min
refresh_count=0
refresh_count=st_autorefresh(interval=60*1000, key="pricerefresh")


def update_spot_price_view_state(option:str)->None:
    """
    Function to update the session state for the spot price page
    """
    if option == "dispatch" or option == "predispatch":
        session_state.spot_price_view = option
    else:
        raise ValueError("Invalid option selected. Make sure the option selected is either dispatch or predispatch")


def display_dispatch_data(state: str):

    #get initial data
    lookback_hours = 24
    dispatch_df=get_dispatch_data(lookback_hours=lookback_hours, region_id=state)

    #display state table and graph
    with st.empty():
        with st.container():

            plot_df =dispatch_df.copy()

            # Create line chart with Plotly
            fig = px.line(plot_df, x=plot_df['SETTLEMENTDATE'], y= plot_df['RRP'],
                            labels={
                                plot_df['SETTLEMENTDATE'].name:'Date',
                                plot_df['RRP'].name: 'RRP' 
                            })
    
            #render fig
            st.plotly_chart(fig, use_container_width=True)

            display_df_info(dispatch_df)


def display_predispatch_30min_data(state: str):

    #get initial data
    predispatch_df=get_predispatch_data_30min(region_id=state)

    #display state table and graph
    with st.empty():
        with st.container():

            plot_df =predispatch_df.copy()

            # Create line chart with Plotly
            fig = px.line(plot_df, x=plot_df['PRED_DATETIME'], y= plot_df['RRP'],
                            labels={
                                plot_df['PRED_DATETIME'].name:'Date',
                                plot_df['RRP'].name: 'RRP' 
                            })
    
            #render fig
            st.plotly_chart(fig, use_container_width=True)

            display_df_info(predispatch_df)


def display_predispatch_5min_data(state: str):

    #get initial data
    predispatch_df=get_predispatch_data_5min(region_id=state)


    #display state table and graph
    with st.empty():
        with st.container():

        
            plot_df =predispatch_df.copy()

            # Create line chart with Plotly
            fig = px.line(plot_df, x=plot_df['INTERVAL_DATETIME'], y= plot_df['RRP'],
                            labels={
                                plot_df['INTERVAL_DATETIME'].name:'Date',
                                plot_df['RRP'].name: 'RRP' 
                            })
    
            #render fig
            st.plotly_chart(fig, use_container_width=True)

            display_df_info(predispatch_df)


def display_df_info(df: pd.DataFrame) -> None:

    #get latest rrp
    latest_rrp = df.iloc[0,:]['RRP']

    #format as string
    latest_rrp_str = "{:,.2f}".format(latest_rrp)

    #get average rrp
    mean_rrp = df['RRP'].mean()

    #format as string
    mean_rrp_str = "{:,.2f}".format(mean_rrp)

    #get max rrp
    max_rrp = df['RRP'].max()

    #format as string
    max_rrp_str = "{:,.2f}".format(max_rrp)

    #get min rrp
    min_rrp = df['RRP'].min()

    #format as string
    min_rrp_str = "{:,.2f}".format(min_rrp)

    #display stats
    with st.container():
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric('Latest RRP $: ', latest_rrp_str)

        with col2:

            st.metric('Mean RRP $: ', mean_rrp_str)

        with col3:
            st.metric('Max RRP $: ', max_rrp_str)

        with col4:

            st.metric('Min RRP $: ', min_rrp_str)


def display_spot_price_view(price_view: str, state:str)->None:
    
    #select the correct view
    if price_view == "Dispatch":
        display_dispatch_data(state=state)

    elif price_view == "Pre-Dispatch 30 Min":
        display_predispatch_30min_data(state=state)

    elif price_view == "Pre-Dispatch 5 Min":
        display_predispatch_5min_data(state=state)

    else:
        raise ValueError("Invalid option selected. Make sure the option selected is a valid option")


def spot_price_page():
    if session_state.authentication_status:

        #display logo
        with st.container():
            col1, col2, col3, col4, col5 = st.columns(5)

            with col3:
                st.image(Image.open(img_path),use_column_width=True)

        #configure sidebar to have user name
        st.sidebar.title(f"Welcome {st.session_state['name']}")
        price_view = st.sidebar.radio("Select a price view option", ("Dispatch", "Pre-Dispatch 30 Min", "Pre-Dispatch 5 Min"))

        tab1, tab2, tab3, tab4, tab5 = st.tabs(['NSW', 'QLD', 'VIC', 'SA', 'TAS'])


        with tab1:
            st.header(f"NSW {price_view}")
            display_spot_price_view(price_view=price_view,state="NSW1")

        with tab2:
            st.header(f"QLD {price_view}")
            display_spot_price_view(price_view=price_view,state="QLD1")

        with tab3:
            st.header(f"VIC {price_view}")
            display_spot_price_view(price_view=price_view,state="VIC1")

        with tab4:
            st.header(f"SA {price_view}")
            display_spot_price_view(price_view=price_view,state="SA1")

        with tab5:
            st.header(f"TAS {price_view}")
            display_spot_price_view(price_view=price_view,state="TAS1")



        if refresh_count % 1 == 0:
            #st.cache_data.clear()
            logging.info(f"Cache cleared")

        
setup_session_states()

if __name__ == "__main__":
    spot_price_page()