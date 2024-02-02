import streamlit as st
import pandas as pd
import numpy as np
import base64

import plotly.express as px
import plotly.graph_objects as go
from streamlit import session_state
from PIL import Image
import mtatk

from modules.utils import setup_session_states, measure_execution_time, clear_flag, get_nmi_list, get_site_cost_forecast

## GLOBAL VARIABLES
nmi_list =get_nmi_list()
img_path = "app/imgs/400dpiLogo.jpg"
session_state.live_state=0



# Page: NMI Details
@measure_execution_time
def forecasting_page():

    if session_state.authentication_status:

        # #configure sidebar
        session_state.authenticator.logout("Logout","sidebar",key='unique_key')
        st.sidebar.title(f"Welcome {st.session_state['name']}")

        #setup header
        with st.container():
                
            col1, col2, col3 = st.columns(3)

            st.title("Site Forecasts")      

            with col2:
                st.image(Image.open(img_path),use_column_width=True)

    
        with st.container():

            #display search box for NMIs
            nmi_input = st.selectbox("Select a NMI", nmi_list,on_change=clear_flag())


            # display graph of load forecast, predispatch cost and price forecast
            site_forecast_df = get_site_cost_forecast(nmi_input)

            # Create a Plotly figure
            fig = go.Figure()

            # Add the electricity load trace
            fig.add_trace(go.Scatter(
                x=site_forecast_df['datetime'],
                y=site_forecast_df['load_forecast'],
                mode='lines+markers',
                name='Forecasted Load (kWh)',
                yaxis='y1'  # Use the first y-axis
            ))

            # Add the price trace on the second y-axis
            fig.add_trace(go.Scatter(
                x=site_forecast_df['datetime'],
                y=site_forecast_df['rrp'],
                mode='lines+markers',
                name='Predispatch Price ($)',
                yaxis='y2'  # Use the second y-axis
            ))

            # Add the forecasted cost trace on the second y-axis
            fig.add_trace(go.Scatter(
                x=site_forecast_df['datetime'],
                y=site_forecast_df['cost_forecast'],
                mode='lines+markers',
                name='Forecasted Cost ($)',
                yaxis='y2'  # Use the second y-axis
            ))

            # Define the layout with two y-axes
            fig.update_layout(
                title='Forecasted Load and Price',
                xaxis=dict(title='Date'),
                yaxis=dict(title='Forecasted Load (kWh)', side='left', showgrid=False),
                yaxis2=dict(title='Predispatch Price ($)', overlaying='y', side='right', showgrid=False),
            ) 
            #update plotly cursor to be vertical
            fig.update_layout(hovermode="x unified")

            #set legend to be at top
            fig.update_layout(legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ))

            #render fig
            st.plotly_chart(fig, use_container_width=True)


        # on graph, highlight regions where price forecast than the threshold


        # display tables of top NMI costs for each client 






setup_session_states()
forecasting_page()