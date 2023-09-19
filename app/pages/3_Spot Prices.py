## PAGE TO DISPLAY REAL TIME DATA OF SPOT PRICES 
## CAN CHOOSE BETWEEN DISPATCH OR PREDISPATCH

import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit import session_state
from streamlit_autorefresh import st_autorefresh
import logging 

from modules.utils import get_dispatch_data, get_predispatch_data_30min, get_predispatch_data_5min, setup_session_states, measure_execution_time

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

#clear flag to display NMI details
session_state.display_details=False


# update every 20 seconds
refresh_count=0
refresh_count=st_autorefresh(interval=20*1000, key="siterefresh")

states_list=['NSW', 'QLD', 'SA', 'TAS', 'VIC']
regions_list=['NSW1', 'QLD1', 'SA1', 'TAS1', 'VIC1']
states_progress_bar={
    'NSW': 0,
    'QLD': 0.25,
    'SA': 0.5,
    'TAS': 0.75,
    'VIC': 1.0
}


def display_spot_price_view(state: str):
    #get initial data
    lookback_hours = 24
    dispatch_df=get_dispatch_data(lookback_hours=lookback_hours)
    predispatch30min_df=get_predispatch_data_30min()
    predispatch5min_df=get_predispatch_data_5min()


    #drop unneeded columns and rename columns to match
    predispatch30min_df = predispatch30min_df.drop(columns=['TOTALDEMAND','AVAILABLEGENERATION'])
    predispatch5min_df = predispatch5min_df.drop(columns=['TOTALDEMAND','AVAILABLEGENERATION','SS_SOLAR_UIGF','SS_WIND_UIGF'])
    predispatch30min_df.rename(columns={'PRED_DATETIME':'SETTLEMENTDATE'}, inplace=True)
    predispatch5min_df.rename(columns={'INTERVAL_DATETIME':'SETTLEMENTDATE'}, inplace=True)

    #drop any rows in predispatch 30min that overlap with predispatch 5min
    predispatch30min_df = predispatch30min_df[~predispatch30min_df['SETTLEMENTDATE'].isin(predispatch5min_df['SETTLEMENTDATE'])]

    #concatenate dataframes based on rrp
    full_df = pd.concat([dispatch_df,predispatch5min_df,predispatch30min_df], axis=0)
    #full_df = pd.concat([dispatch_df,predispatch30min_df], axis=0)
    predispatch_df = pd.concat([predispatch5min_df,predispatch30min_df], axis=0)
    #predispatch_df = pd.concat([predispatch30min_df], axis=0)

    #chop off last row of predispatch df
    predispatch_df=predispatch_df.tail(-10)

    #drop duplicates in full df and reset index
    full_df = full_df.drop_duplicates(subset=['SETTLEMENTDATE','REGIONID']).reset_index(drop=True)

    #display state table and graph
    with st.empty():
        with st.container():

            plot_df =full_df.loc[full_df['REGIONID']==state].copy()

            # Create line chart with Plotly
            fig = px.line(plot_df, x=plot_df['SETTLEMENTDATE'], y= plot_df['RRP'],
                            labels={
                                plot_df['SETTLEMENTDATE'].name:'Date',
                                plot_df['RRP'].name: 'RRP',
                                'color': 'Legend' 
                            },
                            color=px.Constant("Pre-Dispatch"),
                            color_discrete_sequence=["#35ABDE"])
            
            
            fig.add_scatter( x=dispatch_df.loc[dispatch_df['REGIONID']==state]['SETTLEMENTDATE'], y= dispatch_df.loc[dispatch_df['REGIONID']==state]['RRP'],name='Dispatch')

            #set line color for dispatch
            fig['data'][1]['line']['color']="#085A9D"
            
            #render fig
            st.plotly_chart(fig, use_container_width=True)


    with st.empty():
        with st.container():
            col1, col2 = st.columns(2)
            with col1:
                st.subheader('Dispatch Metrics')
                display_df_info(dispatch_df,option='dispatch')
            with col2:
                st.subheader('Pre-Dispatch Metrics')
                display_df_info(predispatch_df,option='predispatch')

def display_df_info(df: pd.DataFrame,option: str) -> None:

    #CREATE SERIES OF EACH METRIC AND THE CONCAT TO DF

    #get series for latest rrp
    latest_rrp = df.loc[df['SETTLEMENTDATE']==df['SETTLEMENTDATE'].max()][['RRP']].reset_index(drop=True).set_index(pd.Index(regions_list)).squeeze()

    #get series for next rrp
    next_rrp = df.loc[df['SETTLEMENTDATE']==df['SETTLEMENTDATE'].min()][['RRP']].iloc[::-1].reset_index(drop=True).set_index(pd.Index(regions_list)).squeeze()

    #get series for mean rrp
    mean_rrp = df.groupby('REGIONID').mean()['RRP']

    #get series for max rrp
    max_rrp = df.groupby('REGIONID').max()['RRP']

    #get series for min rrp
    min_rrp = df.groupby('REGIONID').min()['RRP']

    #combine into one df
    if option =='dispatch':
        metrics_df=pd.DataFrame({'Latest RRP':latest_rrp,'Mean RRP':mean_rrp,'Max RRP':max_rrp,'Min RRP':min_rrp})
    elif option =='predispatch':
        metrics_df=pd.DataFrame({'Next RRP':next_rrp,'Mean RRP':mean_rrp,'Max RRP':max_rrp,'Min RRP':min_rrp})

    # set each metric to be 2 dp
    st.table(metrics_df.applymap('{:.2f}'.format))

@measure_execution_time
def spot_price_page():
    if session_state.authentication_status:
        session_state.authenticator.logout("Logout","sidebar",key='unique_key')

        #display logo
        # with st.container():
        #     col1, col2, col3, col4, col5 = st.columns(5)

        #     with col3:
        #         st.image(Image.open(img_path),use_column_width=True)

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
            logging.info(f" refresh cleared. index count {session_state.live_state}")

            session_state.live_state +=1
            if session_state.live_state ==len(states_list):
                session_state.live_state=0 

            #update_region_state()

       
setup_session_states()

if __name__ == "__main__":
    spot_price_page()