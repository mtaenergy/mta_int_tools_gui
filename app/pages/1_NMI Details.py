import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
import plotly.express as px
from streamlit import session_state
from PIL import Image
import mtatk


from modules.utils import *

#global variables
reading_type =['Select a reading type','Export kWh', 'Import kWh', 'Export kVARh', 'Import kVARh', 'Cost ex GST', 'Carbon kg']
global_nmi_list =['Select a NMI']
global_nmi_list=global_nmi_list+get_nmi_list() #add all nmi's in database to list

customer_list=['Select a customer','Best and Less Pty Ltd','TJX Australia Pty Ltd']
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

                
                customer_in = st.selectbox("Select a customer",customer_list)
                if customer_in != 'Select a customer':

                    #generate a site list based on customer selected 
                    site_list = ['Select a site'] +get_customer_sites(customer_in)

                    site_in = st.selectbox("Select a site",site_list)

                #update nmi list if specific site is chosen
                if 'site_in' in locals():

                    if site_in !='Select a site' or site_in!=None:
                        nmi_list= get_site_nmis(site_alias=site_in)
                    else:
                        nmi_list=global_nmi_list
                else:
                    nmi_list=global_nmi_list

                nmi_in = st.selectbox("Select a NMI", nmi_list)
                read_in = st.selectbox("Select an option", reading_type)

            with col2:
                start_dt_in = st.date_input("Start Date")
                end_dt_in = st.date_input("End Date")
        
        with st.container():

            #set page columns
            col1, col2, col3 = st.columns(3)

            with col2:
                #add submit button
                if st.button("Submit", use_container_width=True):

                    #validate nmi and reading inputs
                    if nmi_in =='Select a NMI' or read_in == 'Select a reading type':
                        st.write('Invalid submission. Try again')
                        session_state.sub_key=False

                    else:
                        session_state.sub_key=True

        #middle page container
        with st.container():
            if session_state.sub_key:
                #st.header("Display map and nmi deets")

                #setup site and nmi class using nmi_in
                site_id = get_site_id(nmi=nmi_in)
                site = mtatk.mta_class_site.Site(site_id=site_id)
                nmi = mtatk.mta_class_nmi.NMI(nmi=site.site_details.nmi, start_date=start_dt_in, end_date=end_dt_in,CERT=cert)


                #get df entry for thechosen nmi
                # nmi_details = get_nmi_msats_data(nmi=nmi_in)
                # nmi_reg_details = get_nmi_tariff(nmi=nmi_in)
                # nmi_site_details = get_nmi_customer(nmi=nmi_in)
                # nmi_party_details = get_nmi_participants(nmi=nmi_in)


                nmi_details = nmi.standing_data.master_data
                nmi_reg_details = nmi.standing_data.registers
                nmi_party_details = nmi.standing_data.roles
                nmi_site_details = get_nmi_customer(nmi=nmi_in)

                #nmi codes
                customer_class_code = nmi_details['CustomerClassificationCode']
                customer_thresh_code = nmi_details['CustomerThresholdCode']
                jurisdiction_code = nmi_details['JurisdictionCode']

                #TARIFF INFO
                #order reg details
                nmi_reg_details = nmi_reg_details.sort_values('CreationDate',ascending=False)

                #get tariff code
                network_tariff_code = nmi_reg_details['NetworkTariffCode'].iloc[0]

                #site info
                site_customer = nmi_site_details['master_customer']
                site_size = nmi_site_details['site_size']
                site_alias = nmi_site_details['site_alias']
                site_address = nmi_site_details['site_address']

                #only keep required columns from nmi_party_details
                nmi_party_details=nmi_party_details[['Party','Role','CreationDate']]

                #rename colummns
                #nmi_party_details = nmi_party_details.rename(columns={"party": "Party", 'role': 'Role', 'from_date': 'From Date'})

                #replace AUS with australia
                site_address = site_address.replace("AUS","Australia")

                #setup columns
                col1, col2 = st.columns(2)

                with col1:
                    # Geocode address and display map
                    if site_address:
                        geolocator = Nominatim(user_agent="my_app")
                        location = geolocator.geocode(site_address, addressdetails=True)
                        if location:
                            latitude, longitude = location.latitude, location.longitude
                            location_df = pd.DataFrame(data=[[latitude,longitude]],columns=['lat','lon'])
                            st.map(location_df, use_container_width=True)
        

                with col2:
                    #create details table
                    details_data ={
                        'Detail': ['Master Customer','Site Alias', 'Site Size', 'Jurisdiction Code','Customer Classification Code', 'Customer Threshold Code','Network Tariff Code'],
                        'Value': [site_customer, site_alias, site_size, jurisdiction_code,customer_class_code,customer_thresh_code,network_tariff_code]
                    }

                    details_df = pd.DataFrame(details_data)

                    st.table(details_df)

                    #responsible party table
                    resp_pty_df = pd.DataFrame(nmi_party_details)

                    st.table(resp_pty_df)

        #bottom page container
        with st.container():
            if session_state.sub_key:

                meter_data_df= api_con.get_interval_meter_data(nmi=nmi_in,start_date=start_dt_in, end_date=end_dt_in, grouped_by_nmi=True, drop_estimates=False)
    
                #filter for reading type
                if read_in =='Export kWh':
                    plot_df=meter_data_df.loc[meter_data_df['nmi_suffix']=='export_kwh']

                elif read_in =='Import kWh':
                    plot_df=meter_data_df.loc[meter_data_df['nmi_suffix']=='import_kwh']

                else:
                    plot_df=meter_data_df.loc[meter_data_df['nmi_suffix']=='export_kwh']
                

                # Create line chart with Plotly
                fig = px.line(plot_df, x='settlement_datetime', y='reading', title=f'{nmi_in} - {read_in}')

                #render fig
                st.plotly_chart(fig, use_container_width=True)

                # add download button for df
                csv = convert_df(plot_df)

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