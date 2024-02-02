import streamlit as st
import pandas as pd
import numpy as np
import base64

import plotly.express as px
import plotly.graph_objects as go
from streamlit import session_state
from PIL import Image
import mtatk

from modules.utils import setup_session_states, measure_execution_time, clear_flag, get_nmi_list, get_site_id_list, get_site_cost_forecast, get_all_site_forecast, get_site_id

## GLOBAL VARIABLES
nmi_list =get_nmi_list()
site_id_list = get_site_id_list()
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

            site_id_input = st.selectbox("Select a Site ID", site_id_list,on_change=clear_flag())

            if nmi_input:

                site_forecast_df = get_site_cost_forecast(nmi=nmi_input)

            if site_id_input:

                site_forecast_df = get_site_cost_forecast(site_id=site_id_input)

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

        #add site details and metrics to the page
        with st.container():

            col1, col2 = st.columns(2)

            with col1:
                #display site details
                site_id = get_site_id(nmi_input)
                site = mtatk.Site(site_id)
                st.subheader("Site Details")
                st.write(f"**Site ID:** {site_id}")
                st.write(f"**Site Name:** {site.site_details.alias}")
                st.write(f"**Customer:** {site.site_details.billed_entity_alias}")

            with col2:

                #get time of peak cost
                peak_cost_time = site_forecast_df['datetime'][site_forecast_df['cost_forecast'].idxmax()]

                #display site metrics
                st.subheader("Site Metrics")
                st.write(f"**Average Load:** {site_forecast_df['load_forecast'].mean():.2f} kWh")
                st.write(f"**Average Cost:** ${site_forecast_df['cost_forecast'].mean():.2f}/kWh")
                st.write(f"**Total Cost:** ${site_forecast_df['cost_forecast'].sum():.2f} ")
                st.write(f"**Peak Cost:** ${site_forecast_df['cost_forecast'].max():.2f} ")
                st.write(f"**Peak Cost Time:** {peak_cost_time}")

        # on graph, highlight regions where price forecast exceeds the threshold
            


        # display tables of top NMI costs for each client 
        with st.container():

            st.subheader("Top 10 NMIs by Cost")
            all_site_forecast_df = get_all_site_forecast()
            
            #groupby site_id and sum cost
            total_site_cost = all_site_forecast_df.groupby('site_id')['cost_forecast'].sum().reset_index()

            #sort by cost and get the top 10
            top_10_sites = total_site_cost.sort_values('cost_forecast',ascending=False).head(10).reset_index(drop=True)

            #display the top 10 sites
            st.table(top_10_sites)


setup_session_states()
forecasting_page()