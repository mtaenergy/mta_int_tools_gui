import streamlit as st
import streamlit_authenticator as stauth
from streamlit import session_state
from PIL import Image
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px


st.set_page_config(
    page_title="MTA Energy Executive Dashboard",
    page_icon=":bar_chart:",
    layout="wide"
)


from modules.utils import *

#image path
img_path = "app/imgs/400dpiLogo.jpg"


#define list of all clients
client_list = ['Select a customer','Best and Less Pty Ltd','TJX Australia Pty Ltd']


#setup function for home page
def home_page():

    authenticator, name = setup_authentication()

    name, authentication_status, username  = authenticator.login('Login','main')

    #check auth status
    if authentication_status ==False:
        st.error("Username/password is incorrect")

    if authentication_status==None:
        st.warning("Please enter a username and password")

    if authentication_status:
        #run app

        #configure sidebar
        authenticator.logout("Logout","sidebar",key='unique_key')
        st.sidebar.title(f"Welcome {name}")


        with st.container():
            col1, col2, col3 = st.columns(3)

            st.title("Business Overview")

            with col2:
                st.image(Image.open(img_path),use_column_width=True)

        #container for lookback selector
        with st.container():
            elected_period = st.sidebar.radio("Select Period", ("Last Month", "Last 3 Months", "Last 6 Months", "Last Year", "Last FY", "FY to date"))

            logging.info(elected_period)

            # collect billing df based on elected period
            columns='[nmi],[total_cost_ex_gst],[charge_group],[charge_name],[volume],[scaling_factor],[loss_factor]'
            billing_df=get_billing_records_prod_df(columns=columns, lookback_op=elected_period)

        #container to select  customer
        with st.container():

            col1, col2, col3 = st.columns(3)

            with col3:
                #customer select
                #customer_sel= st.selectbox(" ", client_list)
                pass

        #container for high level statistics
        with st.container():

            col1, col2, col3, col4 = st.columns(4)


            with col1:
                #number of serviced sites
                num_sites = len(billing_df['nmi'].unique().tolist())

                st.metric('Number of serviced sites',num_sites)

            with col2:

                #group by master customer to get cost per customer
                cost_df = billing_df.groupby('master_customer').sum()

                #total costs
                total_cost = cost_df['total_cost_ex_gst'].sum()

                #format float as string
                total_cost_str = "{:,.2f}".format(total_cost)

                st.metric("Total Cost $AUD",total_cost_str)

            with col3:
                #filter for only rows with Commodity as charge group
                consump_df = billing_df.loc[billing_df['charge_group']=='Commodity']
                consump_df = consump_df.groupby('master_customer').sum()

                #total consump
                total_consump = consump_df['volume'].sum()

                #format float as string
                total_consump_str = "{:,.2f}".format(total_consump)

                st.metric("Total Eletricity Consumption kWh",total_consump_str)

            with col4:

                #filter for only rows with Carbon as charge name
                carbon_df = billing_df.loc[billing_df['charge_name']=='Carbon']

                #create new column which is the multiplication of volume, loss factor and scaling factor
                carbon_df['carbon_ton'] = carbon_df['volume']*carbon_df['scaling_factor']*carbon_df['loss_factor']/1000
                carbon_df = carbon_df.groupby('master_customer').sum()

                #total carbon
                total_carbon = carbon_df['carbon_ton'].sum()

                #format float as string
                total_carbon_str = "{:,.2f}".format(total_carbon)

                #total carbon
                st.metric("Total Carbon Emissions ton",total_carbon_str)


        #container with overview charts
        with st.container():

            #make columns
            col1, col2, col3 = st.columns(3)

            with col1:

                fig = px.pie(cost_df, names=cost_df.index, values='total_cost_ex_gst', 
                             title = 'Total Cost ex GST by Customer',color_discrete_sequence=px.colors.sequential.GnBu_r)

                st.plotly_chart(fig, use_container_width=True)

            with col2:

                fig = px.pie(cost_df, names=consump_df.index, values='volume', 
                             title = 'Total Consumption kWh by Customer',color_discrete_sequence=px.colors.sequential.GnBu_r)

                st.plotly_chart(fig, use_container_width=True)

            with col3:

                fig = px.pie(carbon_df, names=carbon_df.index, values='carbon_ton', 
                             title = 'Total Carbon tons by Customer',color_discrete_sequence=px.colors.sequential.GnBu_r)
                
                #GnBu_r

                st.plotly_chart(fig, use_container_width=True)

        #container with vwap per customer
        with st.container():

            billing_commodity = billing_df[billing_df['charge_group'] == 'Commodity']

            vwap_df = pd.DataFrame({
                'commod_$': billing_commodity.groupby('master_customer')['total_cost_ex_gst'].sum(),
                'commod_kwh': billing_commodity.groupby('master_customer')['volume'].sum()
            }).reset_index()

            vwap_df['vwap_commod'] = vwap_df['commod_$'] / vwap_df['commod_kwh'] * 100

            fig = px.bar(vwap_df, x=vwap_df['master_customer'], y='vwap_commod', 
                             title = 'VWAP Commodity by Customer',
                             labels={
                                 'master_customer': 'Customer',
                                 'vwap_commod': 'Commodity VWAP c/kWh'
                             })
            
            fig.update_traces(marker_color='#35ABDE')
            
            st.plotly_chart(fig, use_container_width=True)



setup_session_states()
home_page()
