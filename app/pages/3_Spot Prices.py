## PAGE TO DISPLAY REAL TIME DATA OF SPOT PRICES 
## CAN CHOOSE BETWEEN DISPATCH OR PREDISPATCH

import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit import session_state
from PIL import Image
import mtatk
from streamlit_autorefresh import st_autorefresh
from itertools import cycle, islice 

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


# update every 20 seconds
refresh_count=0
refresh_count=st_autorefresh(interval=20*1000, key="pricerefresh")

states_list=['NSW', 'QLD', 'VIC', 'SA', 'TAS']
states_progress_bar={
    'NSW': 0,
    'QLD': 0.25,
    'VIC': 0.5,
    'SA': 0.75,
    'TAS': 1.0
}


def display_spot_price_view(state: str):
    #get initial data
    lookback_hours = 24
    dispatch_df=get_dispatch_data(lookback_hours=lookback_hours, region_id=state)
    predispatch30min_df=get_predispatch_data_30min(region_id=state)
    predispatch5min_df=get_predispatch_data_5min(region_id=state)

    #drop unneeded columns and rename columns to match
    predispatch30min_df = predispatch30min_df.drop(columns=['TOTALDEMAND','AVAILABLEGENERATION'])
    predispatch5min_df = predispatch5min_df.drop(columns=['TOTALDEMAND','AVAILABLEGENERATION','SS_SOLAR_UIGF','SS_WIND_UIGF'])
    predispatch30min_df.rename(columns={'PRED_DATETIME':'SETTLEMENTDATE'}, inplace=True)
    predispatch5min_df.rename(columns={'INTERVAL_DATETIME':'SETTLEMENTDATE'}, inplace=True)

    #drop any rows in predispatch 30min that overlap with predispatch 5min
    predispatch30min_df = predispatch30min_df[~predispatch30min_df['SETTLEMENTDATE'].isin(predispatch5min_df['SETTLEMENTDATE'])]

    #concatenate dataframes based on rrp
    full_df = pd.concat([dispatch_df,predispatch5min_df,predispatch30min_df], axis=0)
    predispatch_df = pd.concat([predispatch5min_df,predispatch30min_df], axis=0)

    #chop off last row of predispatch df
    predispatch_df=predispatch_df.tail(-1)

    #drop duplicates in full df and reset index
    full_df = full_df.drop_duplicates(subset=['SETTLEMENTDATE']).reset_index(drop=True)

    #display state table and graph
    with st.empty():
        with st.container():

            plot_df =full_df.copy()

            # Create line chart with Plotly
            fig = px.line(plot_df, x=plot_df['SETTLEMENTDATE'], y= plot_df['RRP'],
                            labels={
                                plot_df['SETTLEMENTDATE'].name:'Date',
                                plot_df['RRP'].name: 'RRP',
                                'color': 'Legend' 
                            },
                            color=px.Constant("Pre-Dispatch"),
                            color_discrete_sequence=["#35ABDE"])
            
            
            fig.add_scatter( x=dispatch_df['SETTLEMENTDATE'], y= dispatch_df['RRP'],name='Dispatch')

            #set line color for dispatch
            fig['data'][1]['line']['color']="#085A9D"
            
    
            #render fig
            st.plotly_chart(fig, use_container_width=True)


            st.subheader('Dispatch Metrics')
            display_df_info(dispatch_df,option='dispatch')
            st.subheader('Pre-Dispatch Metrics')
            display_df_info(predispatch_df,option='predispatch')

def display_df_info(df: pd.DataFrame,option: str) -> None:

    #get latest rrp
    latest_rrp = df.iloc[-1,:]['RRP']

    #format as string
    latest_rrp_str = "{:,.2f}".format(latest_rrp)

    #get next rrp for predispatch
    next_rrp = df.iloc[0,:]['RRP']

    #format as string
    next_rrp_str = "{:,.2f}".format(next_rrp)

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
            if option =='dispatch':
                st.metric('Latest RRP $: ', latest_rrp_str)
            elif option =='predispatch':
                st.metric('Next RRP $: ', next_rrp_str)
            else:
                raise ValueError("Invalid option selected. Make sure the option selected is either dispatch or predispatch")

        with col2:

            st.metric('Mean RRP $: ', mean_rrp_str)

        with col3:
            st.metric('Max RRP $: ', max_rrp_str)

        with col4:

            st.metric('Min RRP $: ', min_rrp_str)

def spot_price_page():
    if session_state.authentication_status:

        #display logo
        with st.container():
            col1, col2, col3, col4, col5 = st.columns(5)

            with col3:
                st.image(Image.open(img_path),use_column_width=True)

        #configure sidebar to have user name
        st.sidebar.title(f"Welcome {st.session_state['name']}")

        #set current state in view
        state = states_list[session_state.live_state]


        #display spot price view
        st.header(f"{state} Spot Price")
        display_spot_price_view(state=f"{state}1")

        #display progress bar to show which state is currently being displayed
        st.progress(states_progress_bar[state])


        if refresh_count % 1 == 0:
            #st.cache_data.clear()
            logging.info(f"refresh cleared")
            logging.info(f"index count {session_state.live_state}")

            session_state.live_state +=1
            if session_state.live_state ==len(states_list):
                session_state.live_state=0 

        
setup_session_states()

if __name__ == "__main__":
    spot_price_page()