import streamlit as st
import pandas as pd
import numpy as np
import base64

import plotly.express as px
from streamlit import session_state
from PIL import Image
import mtatk


from modules.utils import *

#global variables
reading_type =['Select a reading type','Export kWh', 'Import kWh', 'Demand kW', 'Demand kVA','Demand Power Factor', 'Cost ex GST', 'Carbon kg']
global_nmi_list =['Select a NMI']
global_nmi_list=global_nmi_list+get_nmi_list() #add all nmi's in database to list

customer_list=['Select a customer']
customer_list = customer_list+get_customer_list()


site_list = ['Select a site']

#image path
img_path = "app/imgs/400dpiLogo.jpg"

session_state.live_state=0


# Page: NMI Details
@measure_execution_time
def nmi_page():

    

    if session_state.authentication_status:

        # #configure sidebar
        session_state.authenticator.logout("Logout","sidebar",key='unique_key')
        st.sidebar.title(f"Welcome {st.session_state['name']}")


        #temporary measure as i figure out how to add logo to be contained to top right
        with st.container():
                
            col1, col2, col3 = st.columns(3)

            st.title("NMI Details")      

            with col2:
                st.image(Image.open(img_path),use_column_width=True)
        
        

        #st.markdown('<div class="header-img"></div>', unsafe_allow_html=True,)

        #top  page container
        with st.container():
            

            #set page columns
            col1, col2 =st.columns(2)

            with col1:

                
                customer_in = st.selectbox("Select a customer",options=customer_list,on_change=clear_flag())
                if customer_in != 'Select a customer':

                    #generate a site list based on customer selected 
                    site_list = ['Select a site'] +get_customer_sites(customer_in)

                    site_in = st.selectbox("Select a site",site_list,on_change=clear_flag())

                #update nmi list if specific site is chosen
                if 'site_in' in locals():

                    if site_in !='Select a site' or site_in!=None:
                        nmi_list= get_site_nmis(site_alias=site_in)
                    else:
                        nmi_list=global_nmi_list
                else:
                    nmi_list=global_nmi_list

                nmi_in = st.selectbox("Select a NMI", nmi_list,on_change=clear_flag())
                #read_in = st.selectbox("Select an option", reading_type,on_change=clear_flag())

            with col2:
                start_dt_in = st.date_input("Start Date",on_change=clear_flag())
                end_dt_in = st.date_input("End Date",on_change=clear_flag())
        
        with st.container():

            #set page columns
            col1, col2, col3 = st.columns(3)

            with col2:
                #add submit button
                if st.button("Submit", use_container_width=True):

                    #validate nmi and reading inputs
                    if nmi_in =='Select a NMI':
                        st.warning('Invalid submission. Try again')
                        session_state.sub_key=False

                    else:
                        session_state.sub_key=True

        if session_state.sub_key or session_state.display_details:
            try:
                #middle page container
                with st.container():

                        #st.header("Display map and nmi deets")

                        #site info
                        nmi_site_details = get_nmi_customer(nmi=nmi_in)
                        site_customer = nmi_site_details['billed_entity_alias']
                        #site_size = nmi_site_details['site_size']
                        site_alias = nmi_site_details['site_alias']
                        site_address = nmi_site_details['site_address']
                        nmi_active = nmi_site_details['site_status']

                        #logging.info(site_customer)

                        #setup site and nmi class using nmi_in
                        site_id = get_site_id(nmi=nmi_in)
                        site = mtatk.mta_class_site.Site(site_id=site_id)
                        nmi = mtatk.mta_class_nmi.NMI(nmi=site.site_details.nmi, start_date=start_dt_in, end_date=end_dt_in,api_con = api_con)


                        nmi_details = nmi.standing_data.master_data
                        nmi_reg_details = nmi.standing_data.registers
                        nmi_party_details = nmi.standing_data.roles

                        #logging.info(nmi_details)

                        #try and except as not all sites may have codes
                        try:
                            customer_class_code = nmi_details['CustomerClassificationCode']
                            customer_thresh_code = nmi_details['CustomerThresholdCode']
                        except:
                            customer_class_code = '<N/A>'
                            customer_thresh_code = '<N/A>'
                            
                        jurisdiction_code = nmi_details['JurisdictionCode']

                        #TARIFF INFO
                        #order reg details
                        nmi_reg_details = nmi_reg_details.sort_values('CreationDate',ascending=False)

                        #get tariff code
                        network_tariff_code = nmi_reg_details['NetworkTariffCode'].iloc[0]

                        #only keep required columns from nmi_party_details
                        nmi_party_details=nmi_party_details[['Party','Role','CreationDate']]


                        #replace AUS with australia
                        site_address = site_address.replace("AUS","Australia")

                        #setup columns
                        col1, col2 = st.columns(2)

                        with col1:
                            # Geocode address and display map
                            if site_address:
                                location = geolocator.geocode(site_address, addressdetails=True)
                                if location:
                                    latitude, longitude = location.latitude, location.longitude
                                    location_df = pd.DataFrame(data=[[latitude,longitude]],columns=['lat','lon'])
                                    st.map(location_df, use_container_width=True)
                                else:
                                    st.warning("Address not found")
                

                        with col2:
                            #create details table
                            details_data ={
                                'Detail': ['Master Customer','Site Alias', 'Site Address','Jurisdiction Code','Customer Classification Code', 'Customer Threshold Code','Network Tariff Code','Is NMI Active'],
                                'Value': [site_customer, site_alias,site_address, jurisdiction_code,customer_class_code,customer_thresh_code,network_tariff_code,nmi_active]
                            }

                            details_df = pd.DataFrame(details_data)

                            st.table(details_df)

                            #responsible party table
                            resp_pty_df = pd.DataFrame(nmi_party_details)

                            st.table(resp_pty_df)

                #consumption and generation container
                with st.container():
                        
                        ## PLOT
                          
                        #consumption series
                        consump_ser = nmi.meter_data.consumption_kwh

                        #generation series
                        gen_ser = nmi.meter_data.generation_kwh
                
                        #concat the series into the same df
                        plot_df = pd.DataFrame({'Consumption kWh': consump_ser, 'Generation kWh': gen_ser})
                        
                        # Create line chart with Plotly
                        fig = px.line(plot_df, x=plot_df.index, y= ['Consumption kWh','Generation kWh'], title=f'{nmi_in} - Consumption vs Generation kWh',
                                    labels={
                                        plot_df.index.name:'Date',
                                        'value': 'kWh'
                                    })
                        
                        # Set the legend title
                        fig.update_layout(legend_title_text='Reading Type')

                        #render fig
                        st.plotly_chart(fig, use_container_width=True)


                        ## METRICS
                        col1, col2, col3, col4= st.columns(4)

                        # Calculate the sum of the Series and handle NaN with a ternary expression
                        total_consumption_kWh = round(consump_ser.sum(), 2) if not np.isnan(consump_ser.sum()) else 0
                        total_generation_kWh = round(gen_ser.sum(), 2) if not np.isnan(gen_ser.sum()) else 0

                        with col1:
                            #display total consumption
                            st.metric('Total consumption kWh',total_consumption_kWh)

                        with col2:
                            #display total generation 
                            st.metric('Total generation kWh',total_generation_kWh)


                        ## DOWNLOAD DATA

                        #create df with all metrics
                        download_df = pd.concat([nmi.meter_data.consumption_kwh,nmi.meter_data.generation_kwh],axis=1)

                        # add download button for df
                        csv = convert_df(download_df)

                        #setup columns
                        col1, col2, col3 = st.columns(3)

                        with col3:
                            # b64 = base64.b64encode(csv).decode()
                            # download_link = (f'<a href="data:text/csv;base64;{b64}" download="results.csv">Download Results</a>')
                            # st.markdown(download_link, unsafe_allow_html=True)

                            st.download_button(
                                label="Download data as CSV",
                                data=csv,
                                file_name=f'{nmi_in} - Consumption vs Generation kWh.csv',
                                mime='text/csv',
                                use_container_width=True,
                                on_click=set_flag()
                            )

                # demand container
                with st.container():
                    
                    #demand kW series
                    dem_kw_ser = nmi.meter_data.demand_kw

                    #demand kVA series
                    dem_kva_ser = nmi.meter_data.demand_kva


                    #concat the series into the same df
                    plot_df = pd.DataFrame({'Demand kW': dem_kw_ser, 'Demand kVA': dem_kva_ser})

                    # Create line chart with Plotly
                    fig = px.line(plot_df, x=plot_df.index, y= ['Demand kW','Demand kVA'], title=f'{nmi_in} - Demand kW and Demand kVA',
                                    labels={
                                        plot_df.index.name:'Date',
                                        'value': 'kW'
                                    })
                    
                    # add secondary axis
                    fig.update_yaxes(title_text="kVA", secondary_y=True)
                    
                    # Set the legend title
                    fig.update_layout(legend_title_text='Reading Type')

                    #render fig
                    st.plotly_chart(fig, use_container_width=True)


                    ## METRICS
                    col1, col2, col3, col4= st.columns(4)

                    # Calculate the sum of the Series and handle NaN with a ternary expression
                    max_dem_kw = round(dem_kw_ser.max(), 2) if not np.isnan(dem_kw_ser.max()) else 0
                    max_dem_kva = round(dem_kva_ser.max(), 2) if not np.isnan(dem_kva_ser.max()) else 0
                    min_dem_kw = round(dem_kw_ser.min(), 2) if not np.isnan(dem_kw_ser.min()) else 0
                    min_dem_kva = round(dem_kva_ser.min(), 2) if not np.isnan(dem_kva_ser.min()) else 0

                    with col1:
                        #display max demand kw
                        st.metric('Max Demand kW',max_dem_kw)

                    with col2:
                        #display min demand kw 
                        st.metric('Min Demand kW',min_dem_kw)

                    with col3:
                        #display max demand kva
                        st.metric('Max Demand kVA',max_dem_kva)

                    with col4:
                        #display min demand kva
                        st.metric('Min Demand kVA',min_dem_kva)


                    ## DOWNLOAD DATA
                    #create df with all metrics
                    download_df = pd.concat([nmi.meter_data.demand_kw,nmi.meter_data.demand_kva],axis=1)

                    # add download button for df
                    csv = convert_df(download_df)

                    #setup columns
                    col1, col2, col3 = st.columns(3)

                    with col3:

                        st.download_button(
                            label="Download data as CSV",
                            data=csv,
                            file_name=f'{nmi_in} - Demand kW and Demand kVA.csv',
                            mime='text/csv',
                            use_container_width=True,
                            on_click=set_flag()
                    )

                # power factor container
                with st.container():
       
                    #power factor series
                    pf_ser = nmi.meter_data.powerfactor
                
                    #concat the series into the same df
                    plot_df = pd.DataFrame({'Power Factor': pf_ser})

                    # Create line chart with Plotly
                    fig = px.line(plot_df, x=plot_df.index, y= ['Power Factor'], title=f'{nmi_in} - Power Factor',
                                    labels={
                                        plot_df.index.name:'Date',
                                        'value': 'pf'
                                    })
                    
                    # Set the legend title
                    fig.update_layout(legend_title_text='Reading Type')

                    #render fig
                    st.plotly_chart(fig, use_container_width=True)

                    ## METRICS
                    col1, col2, col3, col4= st.columns(4)

                    # Calculate the sum of the Series and handle NaN with a ternary expression
                    mean_pf = round(pf_ser.mean(), 2) if not np.isnan(pf_ser.mean()) else 0


                    with col1:
                        #display mean power factor
                        st.metric('Mean Power Factor',mean_pf)


                    ## DOWNLOAD DATA

                    #create df with all metrics
                    download_df = pd.concat([nmi.meter_data.powerfactor],axis=1)

                    # add download button for df
                    csv = convert_df(download_df)

                    #setup columns
                    col1, col2, col3 = st.columns(3)

                    with col3:

                        st.download_button(
                            label="Download data as CSV",
                            data=csv,
                            file_name=f'{nmi_in} - Power Factor.csv',
                            mime='text/csv',
                            use_container_width=True,
                            on_click=set_flag()
                    )
                    
                #carbon container
                with st.container():
          
                    #carbon series in tons
                    carbon_ser = nmi.carbon_data.carbon_emissions/1000

                    #concat the series into the same df
                    plot_df = pd.DataFrame({'Carbon tons': carbon_ser})

                    # Create line chart with Plotly
                    fig = px.line(plot_df, x=plot_df.index, y= ['Carbon tons'], title=f'{nmi_in} - Carbon tons',
                                    labels={
                                        plot_df.index.name:'Date',
                                        'value': 'tons'
                                    })
                    
                    # Set the legend title
                    fig.update_layout(legend_title_text='Reading Type')

                    #render fig
                    st.plotly_chart(fig, use_container_width=True)


                    ## METRICS
                    col1, col2, col3, col4= st.columns(4)

                    # Calculate the sum of the Series and handle NaN with a ternary expression
                    total_carbon_tons = round(carbon_ser.sum(), 2) if not np.isnan(carbon_ser.sum()) else 0

                    with col1:
                        #display total carbon tonnes
                        st.metric('Total Carbon tonnes',total_carbon_tons)

                    ## DOWNLOAD DATA

                    #create df with all metrics
                    download_df = pd.concat([nmi.carbon_data.carbon_emissions],axis=1)

                    # add download button for df
                    csv = convert_df(download_df)

                    #setup columns
                    col1, col2, col3 = st.columns(3)

                    with col3:

                        st.download_button(
                            label="Download data as CSV",
                            data=csv,
                            file_name=f'{nmi_in} - Carbon Tons.csv',
                            mime='text/csv',
                            use_container_width=True,
                            on_click=set_flag()
                    )

            except:
                pass

setup_session_states()
nmi_page()
