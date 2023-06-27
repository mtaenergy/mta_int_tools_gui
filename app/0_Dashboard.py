import streamlit as st
import streamlit_authenticator as stauth
from streamlit import session_state
from PIL import Image
import pickle
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px

from modules.utils import *

#image path
img_path = "app/imgs/400dpiLogo.jpg"


st.set_page_config(
    page_title="MTA Energy Executive Dashboard",
    page_icon=":bar_chart:",
    layout="wide"
)

if 'sub_key' not in session_state:
    session_state['sub_key'] = False

if 'auth_key' not in session_state:
    session_state['auth_key'] = False

#reset sub key if returned to dashboard
session_state.sub_key=False


#define list of all clients
client_list = ['Select a customer','Best and Less Pty Ltd','TJX Australia Pty Ltd']



#setup function for home page
def home_page():

    # USER AUTHENTICATION
    names_list,username_list, _ = read_login_pem(Path(__file__).parent.parent)

    #load hashed passwords
    file_path = Path(__file__).parent.parent/"hashed_pw.pkl"
    with file_path.open("rb") as file:
        hashed_passwords = pickle.load(file)

    #setup credentials dict
    credentials = {
        "usernames":{}
    }

    for un, name, pw in zip(username_list, names_list, hashed_passwords):
        user_dict = {"name":name,"password":pw}
        credentials["usernames"].update({un:user_dict})

    #logging.info(credentials)

    authenticator = stauth.Authenticate(credentials=credentials,cookie_name="mta_gui_cook",key='abcdef',cookie_expiry_days=30)

    name, authentication_status, username  = authenticator.login('Login','main')

    #check auth status
    if authentication_status ==False:
        st.error("Username/password is incorrect")

    if authentication_status==None:
        st.warning("Please enter a username and password")

    if authentication_status:
        session_state.auth_key=True
        #run app

        #configure sidebar
        authenticator.logout("Logout","sidebar")
        st.sidebar.title(f"Welcome {name}")

        with st.container():
            col1, col2, col3 = st.columns(3)

            st.title("Business Overview")

            with col2:
                st.image(Image.open(img_path),use_column_width=True)

        #container for lookback selector
        with st.container():
            elected_period = st.sidebar.radio("Select Period", ("Last Month", "Last 3 Months", "Last 6 Months", "Last Year"))

            logging.info(elected_period)

        #container for high level statistics
        with st.container():

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                #number of serviced sites
                num_sites = len(get_nmi_list())

                st.metric('Number of serviced sites',num_sites)

            with col2:
                #total costs
                st.metric("Total Cost $AUD",get_cost_stat(elected_period))

            with col3:
                #total costs
                st.metric("Total Eletricity Consumption kWh",get_consump_stat(elected_period))

            with col4:
                #total costs
                st.metric("Total Carbon Emissions kg",get_carbon_stat(elected_period))

        #container to select pi chart customer
        with st.container():

            col1, col2, col3 = st.columns(3)

            with col2:
                #customer select
                customer_sel= st.selectbox(" ", client_list)


        #container with overview charts
        with st.container():

            #cost by customer
            columns='[nmi],[total_cost_ex_gst],[charge_group],[charge_name],[volume],[scaling_factor],[loss_factor]'
            billing_df=get_billing_records_prod_df(columns=columns, lookback_op=elected_period)

            #make columns
            col1, col2, col3 = st.columns(3)

            with col1:

                #group by master customer to get cost per customer
                cost_df = billing_df.groupby('master_customer').sum()

                fig = px.pie(cost_df, names=cost_df.index, values='total_cost_ex_gst', 
                             title = 'Total Cost ex GST by Customer',color_discrete_sequence=px.colors.sequential.GnBu_r)

                st.plotly_chart(fig, use_container_width=True)

            with col2:

                #filter for only rows with Commodity as charge group
                consump_df = billing_df.loc[billing_df['charge_group']=='Commodity']
                consump_df = consump_df.groupby('master_customer').sum()

                fig = px.pie(cost_df, names=consump_df.index, values='volume', 
                             title = 'Total Consumption kWh by Customer',color_discrete_sequence=px.colors.sequential.GnBu_r)

                st.plotly_chart(fig, use_container_width=True)

            with col3:

                #filter for only rows with Carbon as charge name
                carbon_df = billing_df.loc[billing_df['charge_name']=='Carbon']

                #create new column which is the multiplication of volume, loss factor and scaling factor
                carbon_df['carbon_ton'] = carbon_df['volume']*carbon_df['scaling_factor']*carbon_df['loss_factor']/1000
                carbon_df = carbon_df.groupby('master_customer').sum()

                fig = px.pie(carbon_df, names=carbon_df.index, values='carbon_ton', 
                             title = 'Total Carbon tons by Customer',color_discrete_sequence=px.colors.sequential.GnBu_r)
                
                #GnBu_r

                st.plotly_chart(fig, use_container_width=True)


            


            

home_page()
