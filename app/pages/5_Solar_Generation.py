## PAGE TO DISPLAY SOLAR VS GENERATION OF ENERGY MARKET

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit import session_state
from PIL import Image
from streamlit_autorefresh import st_autorefresh
import logging
from modules.utils import setup_session_states, measure_execution_time, get_solar_generation_data, clear_flag, get_solar_sites,get_site_id, get_nem12_data, api_con
from mtatk.mta_class_nmi import NMI

img_path = "app/imgs/400dpiLogo.jpg"


@measure_execution_time
def dislay_solar_data(solar_sites_df: pd.DataFrame):

    #solar site list
    solar_sites_list = solar_sites_df['site_name'].unique().tolist()
    solar_sites_list.remove('Toll Bungaribee 400kW (LGC Meter)')
    

    #container to store date and store selection
    with st.container():
        col1, col2, col3 = st.columns(3)

        with col1:
            start_date=st.date_input("Start Date",value=pd.to_datetime('today')-pd.Timedelta(days=1), on_change=clear_flag())
            start_date_dt=pd.to_datetime(start_date)

        with col2:
            end_date=st.date_input("End Date",value=pd.to_datetime('today'),on_change=clear_flag())
            #add 1 day to end date
            end_date=end_date+pd.Timedelta(days=1)
            end_date_dt=pd.to_datetime(end_date)

        with col3:
            site=st.selectbox("Select a site",options=solar_sites_list,on_change=clear_flag())


    # raise error if start date is after end date
    if start_date > end_date:
        st.error("Start date must be before end date")
        return

    
    #get solar data df
    solar_df = get_solar_generation_data(site=site, start_date=start_date, end_date=end_date)

    #get nmi for chosen site
    nmi = solar_sites_df[solar_sites_df['site_name']==site]['nmi'].values[0]

    #get consumption data
    consumption_df = get_nem12_data(nmi=nmi, start_date=start_date, end_date=end_date, nmi_suffix='export_kwh')

    #filter for date range
    solar_df = solar_df[(solar_df['datetime']>=start_date_dt) & (solar_df['datetime']<=end_date_dt)]

    #dislay in line chart
    with st.container():
        fig =go.Figure()
        fig.add_trace(go.Scatter(x=solar_df['datetime'], y=solar_df['energy_generated_kwh'], mode='lines', name='Solar Generation kWh'))
        fig.add_trace(go.Bar(x=solar_df['datetime'], y=consumption_df['reading'], name='Grid Consumption kWh'))
        
        #update legend position
        fig.update_layout(legend=dict(
            yanchor="top",
            y=1.1,
            x=0,
            orientation='h'
        ),
        yaxis_title='kWh'
        )
        
        st.plotly_chart(fig, use_container_width=True)

    #display solar metrics
    with st.container():

        col1, col2, col3 = st.columns(3)

        with col1:

            #display total solar generation
            total_solar_gen = solar_df['energy_generated_kwh'].sum().round(2)
            st.metric("Total Solar Generation kWh",total_solar_gen)

        with col2:
            #display peak generation
            peak_gen = solar_df['energy_generated_kwh'].max().round(2)
            st.metric("Peak Generation kWh",peak_gen)


    #display site details
    with st.container():
        display_df = solar_sites_df[solar_sites_df['site_name']==site][['site_name','nmi','site_id','data_source',
                                                                        'capacity_kw','mta_lgc_site']].copy()

        #drop duplicates
        display_df.drop_duplicates(inplace=True)

        #if bungaribee, replace capacity with 27*16
        if site == 'Toll Bungaribee 400kW':
            display_df['capacity_kw'] = 27*16

        #rename columns for dislay
        display_df.rename(columns={'site_name':'Site Name','nmi':'NMI','site_id':'Site ID',
                                   'data_source':'Data Source','capacity_kw': 'Capacity-kW',
                                   'mta_lgc_site': 'MTA LGC Site'}, inplace=True)

        #transpose df
        #display_df = display_df.T

        st.dataframe(display_df, use_container_width=True,hide_index=True)
        

@measure_execution_time
def solar_page():
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
        st.header(f"Solar Production")

        #get solar sites df
        solar_sites_df = get_solar_sites()

        #display solar data
        dislay_solar_data(solar_sites_df)



setup_session_states()
solar_page()