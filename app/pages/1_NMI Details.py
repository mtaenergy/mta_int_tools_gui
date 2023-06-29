import streamlit as st
import pandas as pd

import plotly.express as px
from streamlit import session_state
from PIL import Image
import mtatk


from modules.utils import *

#global variables
reading_type =['Select a reading type','Export kWh', 'Import kWh', 'Demand kW', 'Demand kVA','Demand Power Factor', 'Cost ex GST', 'Carbon kg']
global_nmi_list =['Select a NMI']
global_nmi_list=global_nmi_list+get_nmi_list() #add all nmi's in database to list

customer_list=['Select a customer','Best and Less Pty Ltd']
site_list = ['Select a site']

#image path
img_path = "app/imgs/400dpiLogo.jpg"



# Page: NMI Details

def nmi_page():

    if session_state.auth_key:


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
                read_in = st.selectbox("Select an option", reading_type,on_change=clear_flag())

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
                    if nmi_in =='Select a NMI' or read_in == 'Select a reading type':
                        st.warning('Invalid submission. Try again')
                        session_state.sub_key=False

                    else:
                        session_state.sub_key=True

        if session_state.sub_key:
            #middle page container
            with st.container():

                    #st.header("Display map and nmi deets")

                    #case where if the nmi isn't a best and less nmi, then use api
                    #site info
                    nmi_site_details = get_nmi_customer(nmi=nmi_in)
                    site_customer = nmi_site_details['master_customer']
                    site_size = nmi_site_details['site_size']
                    site_alias = nmi_site_details['site_alias']
                    site_address = nmi_site_details['site_address']

                    #logging.info(site_customer)


                    if site_customer != 'Best and Less Pty Ltd':
                    
                        #get df entry for the chosen nmi
                        nmi_details = get_nmi_msats_data(nmi=nmi_in)
                        nmi_reg_details = get_nmi_tariff(nmi=nmi_in)
                        nmi_party_details = get_nmi_participants(nmi=nmi_in)

                        customer_class_code = nmi_details['customer_classification_code']
                        customer_thresh_code = nmi_details['customer_threshold_code']
                        jurisdiction_code = nmi_details['jurisdiction_code']

                        #nmi_reg_details = nmi_reg_details.sort_values(ascending=False)

                        #get tariff code
                        network_tariff_code = nmi_reg_details['network_tariff_code']

                        #rename colummns
                        nmi_party_details=nmi_party_details[['party','role','from_date']]
                        nmi_party_details = nmi_party_details.rename(columns={"party": "Party", 'role': 'Role', 'from_date': 'From Date'})


                    else:

                        #setup site and nmi class using nmi_in
                        site_id = get_site_id(nmi=nmi_in)
                        site = mtatk.mta_class_site.Site(site_id=site_id)
                        nmi = mtatk.mta_class_nmi.NMI(nmi=site.site_details.nmi, start_date=start_dt_in, end_date=end_dt_in,CERT=cert)


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
            

                    with col2:
                        #create details table
                        details_data ={
                            'Detail': ['Master Customer','Site Alias', 'Site Address','Site Size', 'Jurisdiction Code','Customer Classification Code', 'Customer Threshold Code','Network Tariff Code'],
                            'Value': [site_customer, site_alias,site_address, site_size, jurisdiction_code,customer_class_code,customer_thresh_code,network_tariff_code]
                        }

                        details_df = pd.DataFrame(details_data)

                        st.table(details_df)

                        #responsible party table
                        resp_pty_df = pd.DataFrame(nmi_party_details)

                        st.table(resp_pty_df)

            #bottom page container
            with st.container():
                
                    #filter for reading type
                    if site_customer == 'Best and Less Pty Ltd':
                        if read_in =='Export kWh':
                                plot_ser = nmi.meter_data.consumption_kwh

                        elif read_in =='Import kWh':
                                plot_ser = nmi.meter_data.generation_kwh
                 
                        elif read_in == 'Demand kW':
                            plot_ser = nmi.meter_data.demand_kw

                        elif read_in =='Demand kVA':
                            plot_ser = nmi.meter_data.demand_kva

                        elif read_in == 'Demand Power Factor':
                            plot_ser = nmi.meter_data.demand_kw/nmi.meter_data.demand_kva

                            #update series name
                            plot_ser.name = 'Demand Power Factor'
                        
                        else:
                            st.warning("Functionality for this option hasn't been implemented yet")
                            plot_ser = pd.Series()



                    else:

                        meter_data_df= api_con.get_interval_meter_data(nmi=nmi_in,start_date=start_dt_in, end_date=end_dt_in, grouped_by_nmi=True, drop_estimates=False)
        
                        if read_in =='Export kWh':
                                meter_data_df=meter_data_df.loc[meter_data_df['nmi_suffix']=='export_kwh']
                                

                        elif read_in =='Import kWh':
                                plot_ser=meter_data_df.loc[meter_data_df['nmi_suffix']=='import_kwh']

                        else:
                            st.warning("Functionality for this option hasn't been implemented yet")
                            meter_data_df = pd.DataFrame()

                        plot_ser = meter_data_df['reading']
                        plot_ser.index = meter_data_df['settlement_datetime']

                    #st.table(plot_ser)

                    #convert series to df
                    plot_df = pd.DataFrame(plot_ser)

                    # Create line chart with Plotly
                    fig = px.line(plot_df, x=plot_df.index, y= plot_df.columns[0], title=f'{nmi_in} - {read_in}',
                                  labels={
                                     plot_df.index.name:'Date',
                                     plot_df.columns[0]: read_in 
                                  })
                    
                    if read_in == 'Demand Power Factor':
                        fig.update_yaxes(range=[0, 1])

                    #render fig
                    st.plotly_chart(fig, use_container_width=True)

            with st.container():

                #setup columns
                col1, col2, col3 = st.columns(3)

                with col1:
                    #display total consumption
                    if read_in =='Export kWh':
                        st.metric('Total consumption kWh',plot_ser.sum())

                with col2:
                    #display peak consumption
                    if read_in =='Export kWh':
                        st.metric('Peak consumption kWh',plot_ser.max())

                    #display peak kw
                    elif read_in =='Demand kW':
                        st.metric('Peak demand kW',plot_ser.max())

                    #display peak kva
                    elif read_in =='Demand kVA':
                        st.metric('Peak demand kVA',plot_ser.max())

                with col3:

                    #display min kw
                    if read_in =='Demand kW':
                        st.metric('Min demand kW',plot_ser.min())

                    #display min kva
                    elif read_in =='Demand kVA':
                        st.metric('Min demand kVA',plot_ser.min())



            with st.container():
                    
                    if site_customer == 'Best and Less Pty Ltd':
                    
                        #create df with all metrics
                        download_df = pd.concat([nmi.meter_data.consumption_kwh,nmi.meter_data.generation_kwh,nmi.meter_data.demand_kw,nmi.meter_data.demand_kva,nmi.meter_data.demand_kw/nmi.meter_data.demand_kva],axis=1)

                        #update last column name
                        download_df.rename(columns={download_df.columns[-1]: 'demand_pf'}, inplace=True)

                    else:
                         download_df = plot_df

                    # add download button for df
                    csv = convert_df(download_df)


                    #setup columns
                    col1, col2, col3 = st.columns(3)

                    with col2:

                        st.download_button(
                            label="Download data as CSV",
                            data=csv,
                            file_name=f'{nmi_in} - {read_in}.csv',
                            mime='text/csv',
                            use_container_width=True
                    )
nmi_page()