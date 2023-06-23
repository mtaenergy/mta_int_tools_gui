import streamlit as st
import streamlit_authenticator as stauth
from streamlit import session_state
from PIL import Image
import pickle
from pathlib import Path
import plotly.graph_objects as go

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
            elected_period = st.sidebar.radio("Select Period", ("Yesterday", "Last Week", "Last Month", "Last Year"))



        #container for high level statistics
        with st.container():

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                #number of serviced sites
                num_sites = len(get_nmi_list())

                st.metric('Number of serviced sites',num_sites)

            with col2:
                #total costs
                st.metric("Total Cost $AUD",1000)

            with col3:
                #total costs
                st.metric("Total Eletricity Consumption kWh",1000)

            with col4:
                #total costs
                st.metric("Total Carbon Emissions kg",1000)

        #container to select pi chart customer


        #container with pi charts
        with st.container():

            col1, col2 = st.columns(2)

            #customer select
            customer_sel= st.selectbox(" ", client_list)

            with col1:

                if customer_sel !='Select a customer':

                    #pi chart for site consumption

                    labels = ['Category 1', 'Category 2', 'Category 3']
                    values = [30, 40, 30]

                    # Create the pie chart using Plotly
                    fig = go.Figure(data=[go.Pie(labels=labels, values=values)])

                    # Set the chart layout
                    fig.update_layout(title='Consumption kWh Distribution')

                    # Display the pie chart in Streamlit
                    st.plotly_chart(fig)

            
            with col2:

                if customer_sel !='Select a customer':

                    #pi chart for site carbon
                    labels = ['Category 4', 'Category 5', 'Category 6']
                    values = [30, 40, 30]

                    # Create the pie chart using Plotly
                    fig = go.Figure(data=[go.Pie(labels=labels, values=values)])

                    # Set the chart layout
                    fig.update_layout(title='Carbon kg Distribution')

                    # Display the pie chart in Streamlit
                    st.plotly_chart(fig)

home_page()
