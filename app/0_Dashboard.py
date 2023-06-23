import streamlit as st
import streamlit_authenticator as stauth
from streamlit import session_state
from PIL import Image
import pickle
from pathlib import Path

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

#reset sub key if returned to dashboard
session_state.sub_key=False

#st.sidebar.success("Page selector")



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
        #run app

        #configure sidebar
        authenticator.logout("Logout","sidebar")
        st.sidebar.title(f"Welcome {name}")

        with st.container():
            col1, col2, col3 = st.columns(3)

            st.title("Business Overview")

            with col2:
                st.image(Image.open(img_path),use_column_width=True)


        #container for high level statistics
        with st.container():

            col1, col2, col3, col4, col5 = st.columns(5)

            with col1:
                #number of serviced sites
                num_sites = len(get_nmi_list())

                st.subheader(f'Number of serviced sites: {num_sites}')

home_page()
