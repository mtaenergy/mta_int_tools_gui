## PAGE TO DISPLAY DEMAND VS GENERATION OF ENERGY MARKET

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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


#clear flag to display NMI details
session_state.display_details=False


# update every 1 min
refresh_count=0
refresh_count=st_autorefresh(interval=20*1000, key="generationrefresh")

states_list=['NSW', 'QLD', 'SA', 'TAS', 'VIC']
states_progress_bar={
    'NSW': 0,
    'QLD': 0.25,
    'SA': 0.5,
    'TAS': 0.75,
    'VIC': 1.0
}


def display_gen_data(state: str):
    #get initial data
    lookback_hours = 24
    dispatch_df=get_dispatch_demand_data(lookback_hours=lookback_hours)
    predispatch30min_df=get_predispatch_data_30min()
    predispatch5min_df=get_predispatch_data_5min()

    #filter for state
    dispatch_df=dispatch_df[dispatch_df['REGIONID']==state]
    predispatch30min_df=predispatch30min_df[predispatch30min_df['REGIONID']==state]
    predispatch5min_df=predispatch5min_df[predispatch5min_df['REGIONID']==state]

    #drop unneeded columns and rename columns to match
    predispatch30min_df = predispatch30min_df.drop(columns=['RRP'])
    predispatch5min_df = predispatch5min_df.drop(columns=['RRP','SS_SOLAR_UIGF','SS_WIND_UIGF'])
    predispatch30min_df.rename(columns={'PRED_DATETIME':'SETTLEMENTDATE'}, inplace=True)
    predispatch5min_df.rename(columns={'INTERVAL_DATETIME':'SETTLEMENTDATE'}, inplace=True)

    #drop any rows in predispatch 30min that overlap with predispatch 5min
    predispatch30min_df = predispatch30min_df[~predispatch30min_df['SETTLEMENTDATE'].isin(predispatch5min_df['SETTLEMENTDATE'])]

    #concatenate dataframes based on rrp
    full_df = pd.concat([dispatch_df,predispatch5min_df,predispatch30min_df], axis=0)
    predispatch_df = pd.concat([predispatch5min_df,predispatch30min_df], axis=0)

    #cut off overlap with dispatch df
    predispatch_df = predispatch_df.tail(-1)



    #drop duplicates in full df and reset index
    full_df = full_df.drop_duplicates(subset=['SETTLEMENTDATE']).reset_index(drop=True)

    #display state table and graph
    with st.empty():
        with st.container():

            plot_df =full_df.copy()



            fig =go.Figure()

            fig.add_trace(go.Scatter(x=predispatch_df['SETTLEMENTDATE'], y=predispatch_df['AVAILABLEGENERATION'], name='Pre-Dispatch - Available Generation (MW)', marker_color='#35ABDE',fill='tozeroy'))
            fig.add_trace(go.Scatter(x=dispatch_df['SETTLEMENTDATE'], y=dispatch_df['AVAILABLEGENERATION'], name='Dispatch - Available Generation (MW)', marker_color='#085A9D',fill='tozeroy'))
            fig.add_trace(go.Scatter(x=plot_df['SETTLEMENTDATE'], y=plot_df['TOTALDEMAND'], name='Total Demand (MW)', marker_color='#FFBF74'))

            #update legend position
            fig.update_layout(legend=dict(
                yanchor="top",
                y=1.1,
                x=0,
                orientation='h'
            ),
            yaxis_title='MW'
            )
    
            #render fig
            st.plotly_chart(fig, use_container_width=True)



def display_UIGF_data(state: str):
    #get initial data
    predispatch_df=get_predispatch_data_5min()
    predispatch_df=predispatch_df[predispatch_df['REGIONID']==state]

    #filter for just UIGF
    UIGF_df = predispatch_df[['SS_SOLAR_UIGF','SS_WIND_UIGF']]

    #take the sum of each UIGF
    UIGF_df = pd.DataFrame(UIGF_df.sum())

    #add column names
    UIGF_df.rename(columns={0:'totals'}, inplace=True)


    #display pie chart of UIGF breakdown
    fig = px.pie(UIGF_df, values='totals', names=UIGF_df.index, title='UIGF Breakdown')

    #render fig
    st.plotly_chart(fig, use_container_width=True)


def display_gen_view(state:str)->None:

    col1, col2 = st.columns([0.3,0.7])

    with col1:
            display_UIGF_data(state=state)

    with col2:
    
            display_gen_data(state=state)


def generation_page():
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
        st.header(f"{state} Market Generation")
        display_gen_view(state=f"{state}1")

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
    generation_page()