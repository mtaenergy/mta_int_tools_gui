##PAGE TO DISPLAY TEMPERATURE DATA OVER ELECTRICITY CONSUMPTION

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from streamlit import session_state
from PIL import Image
import logging
from modules.utils import setup_session_states, measure_execution_time,get_weather_sites,get_temperature_data, get_site_id, get_nem12_data, api_con
from mtatk.mta_class_nmi import NMI

img_path = "app/imgs/400dpiLogo.jpg"

@measure_execution_time
def dislay_temp_data(weather_sites_df: pd.DataFrame):

    #nmi site list
    sites_list = weather_sites_df['nmi'].unique().tolist()
    
    #container to store date and store selection
    with st.container():
        col1, col2, col3 = st.columns(3)

        with col1:
            start_date=st.date_input("Start Date",value=pd.to_datetime('today')-pd.Timedelta(days=3))

        with col2:
            end_date=st.date_input("End Date",value=pd.to_datetime('today')-pd.Timedelta(days=2))
            #add 1 day to end date
            end_date=end_date+pd.Timedelta(days=1)

        with col3:
            nmi=st.selectbox("Select a site",options=sites_list)
            site = weather_sites_df[weather_sites_df['nmi']==nmi]['site_alias'].values[0] #set site as corresponding site name for nmi


    # raise error if start date is after end date
    if start_date > end_date:
        st.error("Start date must be before end date")
        return

    #get temp data df
    temp_df = get_temperature_data(site=site, start_date=start_date, end_date=end_date)

    #if temp data empty raise error
    if temp_df.empty:
        st.error("No temperature data available for selected date range")
        return

    #sort by datetime
    temp_df.sort_values(by='datetime',inplace=True)

    #get consumption data
    consumption_df = get_nem12_data(nmi=nmi, start_date=start_date, end_date=end_date, nmi_suffix='export_kwh')

    #dislay in line chart
    with st.container():
        fig = go.Figure()
        #fig.add_trace(go.Scatter(x=temp_df['datetime'], y=temp_df['rel_hum'], mode='lines', name='Relative Humidity %'))
        fig.add_trace(go.Scatter(x=consumption_df['settlement_datetime'], y=consumption_df['reading'], name='Grid Consumption kWh',marker_color='#085A9D',fill='tozeroy',yaxis="y1"))
        fig.add_trace(go.Scatter(x=temp_df['datetime'], y=temp_df['temp'], mode='lines', name='Temperature C',marker_color='#FFBF74',yaxis='y2'))
        
    
        #update legend position
        fig.update_layout(
            legend=dict(
                yanchor="top",
                y=1.1,
                x=0,
                orientation='h'
            ),

            yaxis=dict(
                title="kWh",
                titlefont=dict(
                    color="#4C6271"
                ),
                tickfont=dict(
                    color="#4C6271"
                )
            ),

            yaxis2=dict(
                title="Celsius C",
                titlefont=dict(
                    color="#4C6271"
                ),
                tickfont=dict(
                    color="#4C6271"
                ),
                anchor="x",
                overlaying="y",
                side="right",
                position=1
            )
        )
                
        st.plotly_chart(fig, use_container_width=True)


    #display temp metrics
    with st.container():
        

        col1, col2, col3 = st.columns(3)

        with col1:

            #display max temperature
            max_temp = temp_df['temp'].max().round(2)
            st.metric("Max Temperature (C)",max_temp)

        with col2:
            #display min temperature
            min_temp = temp_df['temp'].min().round(2)
            st.metric("Min Temperature (C)",min_temp)

        with col3:
            #display average temperature
            mean_temp = temp_df['temp'].mean().round(2)
            st.metric("Average Temperature (C)",mean_temp)

###############################################################################################

    #ploty fig for relative humid
    with st.container():

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=consumption_df['settlement_datetime'], y=consumption_df['reading'], name='Grid Consumption kWh',marker_color='#085A9D',fill='tozeroy',yaxis="y1"))
        fig.add_trace(go.Scatter(x=temp_df['datetime'], y=temp_df['rel_hum'], mode='lines', name='Relative Humidity %',marker_color='#e37474',yaxis='y2'))
        
    
        #update legend position
        fig.update_layout(
            legend=dict(
                yanchor="top",
                y=1.1,
                x=0,
                orientation='h'
            ),

            yaxis=dict(
                title="kWh",
                titlefont=dict(
                    color="#4C6271"
                ),
                tickfont=dict(
                    color="#4C6271"
                )
            ),

            yaxis2=dict(
                title="Relative Humidity %",
                titlefont=dict(
                    color="#4C6271"
                ),
                tickfont=dict(
                    color="#4C6271"
                ),
                anchor="x",
                overlaying="y",
                side="right",
                position=1
            )
        )
                
        st.plotly_chart(fig, use_container_width=True)


    #display temp metrics
    with st.container():
        

        col1, col2, col3 = st.columns(3)

        with col1:

            #display max humidity
            max_hum = temp_df['rel_hum'].max().round(2)
            st.metric("Max Humidity %",max_hum)

        with col2:
            #display min humidity
            min_hum = temp_df['rel_hum'].min().round(2)
            st.metric("Min Humidity %",min_hum)

        with col3:
            #display average humidity
            mean_hum = temp_df['rel_hum'].mean().round(2)
            st.metric("Average Humidity %",mean_hum)


    #display site details
    with st.container():
        display_df = weather_sites_df[weather_sites_df['site_alias']==site][['site_alias','nmi','master_customer','site_address',
                                                                        'weather_stat_name']].copy()

        #drop duplicates
        display_df.drop_duplicates(inplace=True)

        #rename columns for dislay
        display_df.rename(columns={'site_alias':'Site Alias','nmi':'NMI','master_customer':'Customer Alias',
                                   'site_address':'Site Address','weather_stat_name': 'Weather Station Name'}, inplace=True)

        st.dataframe(display_df, use_container_width=True,hide_index=True)
    

@measure_execution_time
def meteorological_page():
    if session_state.authentication_status:
        session_state.authenticator.logout("Logout","sidebar",key='unique_key')

        #display logo
        with st.container():
            col1, col2, col3, col4, col5 = st.columns(5)

            with col3:
                st.image(Image.open(img_path),use_column_width=True)

        #configure sidebar to have user name
        st.sidebar.title(f"Welcome {st.session_state['name']}")

        #set header
        st.header(f"Site Meteorological Data")

        #get weather sites df
        weather_sites_df = get_weather_sites()

        #display temp data
        dislay_temp_data(weather_sites_df)


setup_session_states()
meteorological_page()