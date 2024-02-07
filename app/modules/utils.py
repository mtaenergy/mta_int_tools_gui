'''
Utilities module to assist the streamlit app
'''
from mtatk.api_lib.aemo_api_connector import APIConnector
from mtatk.mta_sql.sql_connector import SQLConnector
import streamlit as st
from streamlit import session_state
import pandas as pd
from pathlib import Path
import base64
from datetime import date, datetime
import logging
from geopy.geocoders import Nominatim
import streamlit_authenticator as stauth
import pickle
import json
import time


current_path = Path(__file__).parent.parent.parent
cert = str(current_path/ "kv-mta-MTAENERGY-Prod-20221111.pem")

def measure_execution_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"{func.__name__} took {execution_time:.6f} seconds to execute.")
        return result
    return wrapper


@st.cache_data
def setup_API_con() -> APIConnector:
    """Summary of setup_API_con: Function to setup API Connector object for use in app

    Returns:
        APIConnector:  API Connector object
    """

    #create API Connector object
    api_connector=APIConnector(cert=cert)

    return api_connector

@st.cache_resource
def setup_SQL_con(username: str, password: str) -> SQLConnector:
    """ Summary of setup_SQL_con: Function to setup SQL Connector object for use in app

    Args:
        username (str): username of the account to connect to SQL server
        password (str): password of the account to connect to SQL server

    Returns:
        SQLConnector: SQL Connector object
    """

    #create SQL Connection object
    sql_con = SQLConnector(username=username,password=password)

    return sql_con

@st.cache_data
def setup_geolocator() -> Nominatim:
    """ Summary of setup_geolocator: Function to setup geolocator object for use in app

    Returns:
        Nominatim: geolocator object
    """
    geolocator = Nominatim(user_agent="my_app")

    return geolocator

@st.cache_data
def img_to_bytes(img_path: str) -> str:
    """Summary of img_to_bytes: Function to convert image to base64 string"""

    img_bytes = Path(img_path).read_bytes()
    encoded = base64.b64encode(img_bytes).decode()
    return encoded

def read_login_pem(file_path:str) -> tuple:
    """Summary of read_login_pem: Function to read login.pem file and return lists of names, usernames and passwords

    Args:
        file_path (str): path to login.pem file

    Returns:
        tuple: tuple of lists of names, usernames and passwords
    """

    #set lists
    names_list =[]
    username_list=[]
    password_list=[]

    #logging.info(file_path)

    #open login.pem file and append login details to lists
    with open(f'{file_path}\\logins.pem','r') as file:
        for line in file:
            line=line.strip()
            name, username, password = line.split(',')
            names_list.append(name)
            username_list.append(username)
            password_list.append(password)

    # logging.info(names_list)
    # logging.info(username_list)
    # logging.info(password_list)

    #return lists
    return names_list,username_list, password_list

def setup_authentication()-> tuple:
    """Summary of setup_authentication: Function to setup authentication for app

    Returns:
        tuple: tuple of authenticator object and name of user
    """

    # USER AUTHENTICATION
    names_list,username_list, _ = read_login_pem(Path(__file__).parent.parent.parent)

    #load hashed passwords
    file_path = Path(__file__).parent.parent.parent/"hashed_pw.pkl"
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

    authenticator = stauth.Authenticate(credentials=credentials,cookie_name="mta_gui_cook",key='abcdef',cookie_expiry_days=1)

    return authenticator, name

def setup_session_states():
    """_summary_of_setup_session_states: Function to setup session states for app
    """

    #setup session states
    if 'sub_key' not in session_state:
        session_state['sub_key'] = False

    if 'authentication_status' not in session_state:
        session_state['authentication_status'] = None

    if 'name' not in session_state:
        session_state['name'] = ''

    if 'live_state' not in session_state:
        session_state['live_state'] = 0

    if 'display_details' not in session_state:
        session_state['display_details'] = False

    if 'authenticator' not in session_state:
        session_state['authenticator'] = None



    #reset sub key if returned to dashboard
    #session_state.sub_key=False


    #logging.info(f"Session state post setup {session_state}")

@st.cache_data
def setup_colour_themes()-> dict:
    """_summary_of_setup_colour_themes: Function to setup colour themes for app

    Returns:
        dict: dictionary of colour themes for each customer
    """
    # Load the colors from the JSON file
    with open(f'{current_path}/app/themes/customer_theme.json') as file:
        colours = json.load(file)

    # Assign colors to group names
    customer_colour_map = {group: colours[group] for group in colours}

    return customer_colour_map


def update_region_state():
    # Get the current time
    current_time = datetime.now()
    seconds = current_time.second

    logging.info(f"Seconds: {seconds}")

    # Define the time ranges and corresponding values
    time_ranges_values = [
        (0, 12, 0),
        (13, 24, 1),
        (25, 36, 2),
        (37, 48, 3),
        (49, 60, 4)
    ]

    # Check which range the seconds fall into and set the corresponding value
    for range_start, range_end, value in time_ranges_values:
        if range_start <= seconds <= range_end:
            session_state.live_state = value
            break

def replace_entry(entry, search_string: str, replace_string: str):
    if search_string not in entry:
        return replace_string
    else:
        return entry


'''
GET FUNCTIONS TO SQL DB
'''

@st.cache_data
def get_cost_stat(lookback_op: str)-> float:
    """Summary of get_cost_stat: Function to get total cost excluding GST  from billing_records_prod based on lookback option selected

    Args:
        lookback_op (str): lookback option 

    Returns:
        float: total cost excluding GST
    """

    #casewhere where depending on the lookback option chosen, the query will be different
    if lookback_op =="Last Month":
        query  = ("SELECT SUM(total_cost_ex_gst) as total_cost "
                  "FROM vw_billing_records_summary "
                  "WHERE bill_run_end_date >= DATEADD(month, DATEDIFF(month, 0, GETDATE()) - 1, 0) "
                  "AND bill_run_end_date < DATEADD(month, DATEDIFF(month, 0, GETDATE()), 0)")
        
    elif lookback_op == "Last 3 Months":
        query  = ("SELECT SUM(total_cost_ex_gst) as total_cost "
                  "FROM vw_billing_records_summary "
                  "WHERE bill_run_end_date >= DATEADD(month, DATEDIFF(month, 0, GETDATE()) - 3, 0) "
                  "AND bill_run_end_date < DATEADD(month, DATEDIFF(month, 0, GETDATE()), 0)")
        
    elif lookback_op == "Last 6 Months":
        query  = ("SELECT SUM(total_cost_ex_gst) as total_cost "
                  "FROM vw_billing_records_summary "
                  "WHERE bill_run_end_date >= DATEADD(month, DATEDIFF(month, 0, GETDATE()) - 6, 0) "
                  "AND bill_run_end_date < DATEADD(month, DATEDIFF(month, 0, GETDATE()), 0)")
        
    elif lookback_op == "Last Year":
        query  = ("SELECT SUM(total_cost_ex_gst) as total_cost "
                  "FROM vw_billing_records_summary "
                  "WHERE bill_run_end_date >= DATEADD(year, DATEDIFF(year, 0, GETDATE()) - 1, 0) "
                    "AND bill_run_end_date < DATEADD(year, DATEDIFF(year, 0, GETDATE()), 0)")
    else:
        st.error("Invalid date range chosen")

    #logging.info(query)

    #retrieve value from sql
    total_cost = sql_con.query_sql(query=query,database='billing')

    #convert to float 
    total_cost_flt= float(total_cost.iloc[0].round(2))

    #convert to str and format to use commas for thousands separator
    total_cost_str = "{:,.2f}".format(total_cost_flt)

    return total_cost_str

@st.cache_data
def get_consump_stat(lookback_op: str)-> float:
    """Summary of get_consump_stat: Function to get total consumption from billing_records_prod based on lookback option selected

    Args:
        lookback_op (str): lookback option

    Returns:
        float: total consumption in kwh
    """

    #casewhere where depending on the lookback option chosen, the query will be different
    if lookback_op =="Last Month":
        query  = ("SELECT SUM(volume) as total_consump "
                  "FROM vw_billing_records_summary "
                  "WHERE charge_group = 'Commodity' "
                  "AND bill_run_end_date >= DATEADD(month, DATEDIFF(month, 0, GETDATE()) - 1, 0) "
                  "AND bill_run_end_date < DATEADD(month, DATEDIFF(month, 0, GETDATE()), 0)")
        
    elif lookback_op == "Last 3 Months":
        query  = ("SELECT SUM(volume) as total_consump "
                  "FROM vw_billing_records_summary "
                  "WHERE charge_group = 'Commodity' "
                  "AND bill_run_end_date >= DATEADD(month, DATEDIFF(month, 0, GETDATE()) - 3, 0) "
                  "AND bill_run_end_date < DATEADD(month, DATEDIFF(month, 0, GETDATE()), 0)")
        
    elif lookback_op == "Last 6 Months":
        query  = ("SELECT SUM(volume) as total_consump "
                  "FROM vw_billing_records_summary "
                  "WHERE charge_group = 'Commodity' "
                  "AND bill_run_end_date >= DATEADD(month, DATEDIFF(month, 0, GETDATE()) - 6, 0) "
                  "AND bill_run_end_date < DATEADD(month, DATEDIFF(month, 0, GETDATE()), 0)")
        
    elif lookback_op == "Last Year":
        query  = ("SELECT SUM(volume) as total_consump "
                  "FROM vw_billing_records_summary "
                  "WHERE charge_group = 'Commodity' "
                  "AND bill_run_end_date >= DATEADD(year, DATEDIFF(year, 0, GETDATE()) - 1, 0) "
                    "AND bill_run_end_date < DATEADD(year, DATEDIFF(year, 0, GETDATE()), 0)")
    else:
        st.error("Invalid date range chosen")

    #logging.info(query)

    #retrieve value from sql
    total_consump = sql_con.query_sql(query=query,database='billing')

    #convert to float 
    total_consump_flt= float(total_consump.iloc[0].round(2))

    #convert to str and format to use commas for thousands separator
    total_consump_str = "{:,.2f}".format(total_consump_flt)

    return total_consump_str

@st.cache_data
def get_carbon_stat(lookback_op: str)-> float:
    """Summary of get_carbon_stat: Function to get total carbon from billing_records_prod based on lookback option selected

    Args:
        lookback_op (str): lookback option

    Returns:
        float: total carbon in kg
    """

    #casewhere where depending on the lookback option chosen, the query will be different
    if lookback_op =="Last Month":
        query  = ("SELECT SUM(volume*scaling_factor*loss_factor) as total_carbon "
                  "FROM vw_billing_records_summary "
                  "WHERE charge_name ='Carbon' "
                  "AND bill_run_end_date >= DATEADD(month, DATEDIFF(month, 0, GETDATE()) - 1, 0) "
                  "AND bill_run_end_date < DATEADD(month, DATEDIFF(month, 0, GETDATE()), 0)")
        
    elif lookback_op == "Last 3 Months":
        query  = ("SELECT SUM(volume*scaling_factor*loss_factor) as total_carbon "
                  "FROM vw_billing_records_summary "
                  "WHERE charge_name ='Carbon' "
                  "AND bill_run_end_date >= DATEADD(month, DATEDIFF(month, 0, GETDATE()) - 3, 0) "
                  "AND bill_run_end_date < DATEADD(month, DATEDIFF(month, 0, GETDATE()), 0)")
        
    elif lookback_op == "Last 6 Months":
        query  = ("SELECT SUM(volume*scaling_factor*loss_factor) as total_carbon "
                  "FROM vw_billing_records_summary "
                  "WHERE charge_name ='Carbon' "
                  "AND bill_run_end_date >= DATEADD(month, DATEDIFF(month, 0, GETDATE()) - 6, 0) "
                  "AND bill_run_end_date < DATEADD(month, DATEDIFF(month, 0, GETDATE()), 0)")
        
    elif lookback_op == "Last Year":
        query  = ("SELECT SUM(volume*scaling_factor*loss_factor) as total_carbon "
                  "FROM vw_billing_records_summary "
                  "WHERE charge_name ='Carbon' "
                  "AND bill_run_end_date >= DATEADD(year, DATEDIFF(year, 0, GETDATE()) - 1, 0) "
                    "AND bill_run_end_date < DATEADD(year, DATEDIFF(year, 0, GETDATE()), 0)")
    else:
        st.error("Invalid date range chosen")

    #logging.info(query)

    #retrieve value from sql
    total_carbon = sql_con.query_sql(query=query,database='billing')

    #convert to float 
    total_carbon_flt= float(total_carbon.iloc[0].round(2))

    #convert to str and format to use commas for thousands separator
    total_carbon_str = "{:,.2f}".format(total_carbon_flt)

    return total_carbon_str

@st.cache_data
def get_billing_records_prod_df(columns: str, lookback_op: str)-> pd.DataFrame:
    """Summary of get_billing_records_prod_df: Function to get billing_records_prod data based on lookback option selected and columns chosen

    Args:
        columns (str): string of columns to select from table alongside bill_run_end_date and billed_entity_alias
        lookback_op (str): lookback option

    Returns:
        pd.DataFrame: dataframe of billing_records_prod data
    """

    # Get the current date
    current_date = date.today()

    # Get the current month
    current_month = current_date.month

    #setup start of query
    query = (f"SELECT [bill_run_end_date],[billed_entity_alias],{columns} FROM vw_billing_records_summary ")

    #casewhere where depending on the lookback option chosen, the query will be different
    if lookback_op =="Last Month":
        query  = query+ ("WHERE bill_run_end_date >= DATEADD(month, DATEDIFF(month, 0, GETDATE()) - 1, 0) "
                  "AND bill_run_end_date < DATEADD(month, DATEDIFF(month, 0, GETDATE()), 0)")
        
    elif lookback_op == "Last 3 Months":
        query  = query + ("WHERE bill_run_end_date >= DATEADD(month, DATEDIFF(month, 0, GETDATE()) - 3, 0) "
                  "AND bill_run_end_date < DATEADD(month, DATEDIFF(month, 0, GETDATE()), 0)")
        
    elif lookback_op == "Last 6 Months":
        query  = query + ("WHERE bill_run_end_date >= DATEADD(month, DATEDIFF(month, 0, GETDATE()) - 6, 0) "
                  "AND bill_run_end_date < DATEADD(month, DATEDIFF(month, 0, GETDATE()), 0)")
        
    elif lookback_op == "Last Year":
        query  = query + ("WHERE bill_run_end_date >= DATEADD(year, DATEDIFF(year, 0, GETDATE()) - 1, 0) "
                    "AND bill_run_end_date < DATEADD(year, DATEDIFF(year, 0, GETDATE()), 0)")
        
    elif lookback_op == "FY to date":
        #if in first half of calendar year
        if current_month <= 6:
            query =query + ("WHERE bill_run_start_date >= DATEFROMPARTS(YEAR(GETDATE())-1, 7, 1) "
                            " AND bill_run_start_date < DATEFROMPARTS(YEAR(GETDATE()) , 7, 1)")
        #else must be in 2nd half of the year
        else:
            query =query + ("WHERE bill_run_start_date >= DATEFROMPARTS(YEAR(GETDATE()), 7, 1) "
                            " AND bill_run_start_date < DATEFROMPARTS(YEAR(GETDATE())+1, 7, 1)")
        
    elif lookback_op == "Last FY":
        #if in first half of calendar year
        if current_month <= 6:
            query =query + ("WHERE bill_run_start_date >= DATEFROMPARTS(YEAR(GETDATE())-2, 7, 1) "
                            " AND bill_run_start_date < DATEFROMPARTS(YEAR(GETDATE())-1 , 7, 1)")
        #else must be in 2nd half of the year    
        else:
            query =query + ("WHERE bill_run_start_date >= DATEFROMPARTS(YEAR(GETDATE())-1, 7, 1) "
                            " AND bill_run_start_date < DATEFROMPARTS(YEAR(GETDATE()) , 7, 1)")

    else:
        st.error("Invalid date range chosen")

    #logging.info(query)


    #retrieve df from sql
    billing_df = sql_con.query_sql(query=query,database='billing')

    #drop date columns
    billing_df.drop(['bill_run_end_date'],axis=1, inplace=True)

    #update Joinpro and chemist warehouse if needed
    billing_df['billed_entity_alias'].replace({'JOINPRO AUSTRALIA PTY LTD':'Joinpro Australia Pty Ltd',
                                           'Chemist Warehouse ': 'Chemist Warehouse Pty Ltd'},inplace=True)

    return billing_df

@st.cache_data
def get_customer_list()-> list:
    """Summary of get_customer_list: Function to get list of customers from standing data
    
    Returns:
        list: list of customers"""

    #setup query
    table_name="customer"
    query = (f"SELECT * FROM {table_name}")

    #get customer data
    customer_df=sql_con.query_sql(query=query,database='billing')

    #setup list
    customer_list = customer_df['customer_alias'].unique().tolist()

    return customer_list

@st.cache_data
def get_nmi_list()-> list:
    """Summary of get_nmi_list: Function to get list of active nmis from standing data as of today

    Returns:
        list: list of nmis
    """


    #setup query
    table_name="site"
    query = (f"SELECT * FROM {table_name} WHERE site_status='Active'")

    #get customer data
    customer_df=sql_con.query_sql(query=query,database='billing')
    nmi_list =  customer_df['site_nmi'].unique().tolist()

    return nmi_list

@st.cache_data
def get_site_id_list()-> list:
    """Summary of get_nmi_list: Function to get list of active site ids from billing data as of today

    Returns:
        list: list of site ids
    """


    #setup query
    table_name="site"
    query = (f"SELECT * FROM {table_name} WHERE site_status='Active'")

    #get site id data
    df=sql_con.query_sql(query=query,database='billing')
    site_id_list =  df['site_id'].unique().tolist()

    return site_id_list


@st.cache_data
def get_nmi_msats_data(nmi: str) -> pd.DataFrame:
    """Summary of get_nmi_msats_data: Function to get msats data for a given nmi

    Args:
        nmi (str): nmi to get msats data for

    Returns:
        pd.DataFrame: dataframe of msats data for nmi
    """

    #setup query
    table_name="aemo_msats_cats_nmi_data"
    query=(f"SELECT * FROM {table_name} "
           f"WHERE nmi='{nmi}' "
           f"ORDER BY from_date desc")
    
    #get msats nmi data
    nmi_msats_df=sql_con.query_sql(query=query,database='standingdata')

    #return the top row as it is the most up to date
    return nmi_msats_df.iloc[0]

@st.cache_data 
def get_nmi_tariff(nmi: str)-> pd.DataFrame:
    """ Summary of get_nmi_tariff: Function to get tariff data for a given nmi

    Args:
        nmi (str): nmi to get tariff data for

    Returns:
        pd.DataFrame: dataframe of tariff data for nmi
    """

    #setup query
    table_name="aemo_msats_cats_register_identifier"
    query = (f"SELECT * FROM {table_name} "
             f"WHERE nmi='{nmi}' "
             f"ORDER BY from_date desc")
    
    #get nmi register id data
    nmi_register_df=sql_con.query_sql(query=query,database='standingdata')

    #return the top row as it is the most up to date
    return nmi_register_df.iloc[0]

@st.cache_data
def get_nmi_customer(nmi: str)-> pd.DataFrame:
    """Summary of get_nmi_customer: Function to get customer data for a given nmi

    Args:
        nmi (str): nmi to get customer data for

    Returns:
        pd.DataFrame: dataframe of customer data for nmi
    """

    #setup query
    table_name="site"
    query = (f"SELECT * FROM {table_name} "
             f"WHERE site_nmi='{nmi}' "
             f"ORDER BY site_live_date desc")

    #get customer data
    nmi_customer_df=sql_con.query_sql(query=query,database='billing')

    #return the top row as it is the most up to date
    return nmi_customer_df.iloc[0]

@st.cache_data
def get_nmi_participants(nmi: str)-> pd.DataFrame:
    """Summary of get_nmi_participants: Function to get participant data for a given nmi

    Args:
        nmi (str): nmi to get participant data for

    Returns:
        pd.DataFrame: dataframe of participant data for nmi
    """

    #setup query
    table_name="aemo_msats_cats_nmi_participant_relations"
    query = (f"SELECT * FROM {table_name} "
             f"WHERE nmi='{nmi}'")
    
    #get participants data
    nmi_participants_df=sql_con.query_sql(query=query,database='standingdata')

    return nmi_participants_df

def get_dispatch_data(lookback_hours: int)-> pd.DataFrame:
    """Summary of get_dispatch_data: Function to get the most recent dispatch pricedata for the market

    Args:
        lookback_hours (int): number of hours to lookback

    Returns:
        pd.DataFrame: dataframe of dispatch data
    """

    #setup query
    table_name="aemo_emms_dispatch_price"
    timezone_add = 10 #need to set to convert UTC to AEST
    query = (f"SELECT SETTLEMENTDATE,REGIONID,RRP FROM {table_name} "
             f"WHERE SETTLEMENTDATE > DATEADD(HOUR,-{lookback_hours},DATEADD(HOUR,{timezone_add},GETDATE())) "
             f"ORDER BY SETTLEMENTDATE asc")
    
    #get dispatch data
    dispatch_df=sql_con.query_sql(query=query,database='timeseries')

    return dispatch_df

def get_dispatch_demand_data(lookback_hours: int)-> pd.DataFrame:
    """Summary of get_dispatch_data: Function to get the most recent dispatch demand data for the market

    Args:
        lookback_hours (int): number of hours to lookback

    Returns:
        pd.DataFrame: dataframe of dispatch data
    """

    #setup query
    table_name="aemo_emms_dispatch_demand"
    timezone_add = 10 #need to set to convert UTC to AEST
    query = (f"SELECT SETTLEMENTDATE,REGIONID,TOTALDEMAND,AVAILABLEGENERATION FROM {table_name} "
             f"WHERE SETTLEMENTDATE > DATEADD(HOUR,-{lookback_hours},DATEADD(HOUR,{timezone_add},GETDATE())) "
             f"ORDER BY SETTLEMENTDATE asc")
    
    #get dispatch data
    dispatch_df=sql_con.query_sql(query=query,database='timeseries')

    return dispatch_df

def get_predispatch_data_30min()-> pd.DataFrame:
    """Summary of get_predispatch_data: Function to get the most recent predispatch data for the market for 30min intervals

    Returns:
        pd.DataFrame: dataframe of predispatch data
    """

    #setup query
    table_name="aemo_emms_predispatch_30min"
    query = (f"SELECT PRED_DATETIME,REGIONID,RRP,TOTALDEMAND,AVAILABLEGENERATION FROM {table_name} "
             f"WHERE DATETIME = (SELECT MAX(DATETIME) FROM {table_name}) "
             f"ORDER BY PRED_DATETIME asc")
    
    #get predispatch data
    predispatch_df=sql_con.query_sql(query=query,database='timeseries')

    return predispatch_df

def get_predispatch_data_5min()-> pd.DataFrame:
    """Summary of get_predispatch_data: Function to get the most recent predispatch data for the market for 5min intervals

    Returns:
        pd.DataFrame: dataframe of predispatch data
    """

    #setup query
    table_name="aemo_emms_predispatch_5min"
    query = (f"SELECT INTERVAL_DATETIME,REGIONID,RRP,TOTALDEMAND,AVAILABLEGENERATION,SS_SOLAR_UIGF,SS_WIND_UIGF FROM {table_name} "
             f"WHERE RUN_DATETIME = (SELECT MAX(RUN_DATETIME) FROM {table_name})"
             f"ORDER BY INTERVAL_DATETIME asc")
    
    #get predispatch data
    predispatch_df=sql_con.query_sql(query=query,database='timeseries')

    return predispatch_df

@st.cache_data
def get_solar_generation_data(site: str, start_date: str, end_date: str)-> pd.DataFrame:
    table_name='mtae_ops_solar_generated_5min'

    #if the site is bungaribee
    if site == 'Toll Bungaribee 400kW':
        query=(f"SELECT datetime,energy_generated_kwh, site_name  FROM {table_name} "
                f"WHERE datetime >= '{start_date}' "
                f"AND datetime <= '{end_date}' "
                f"AND site_id = 'cb8121b3-6a74-4e8c-8ab3-11bc49a1fb8f'") #search for the specific site id for bungaribee
    else:
        query=(f"SELECT datetime,energy_generated_kwh, site_name  FROM {table_name} "
            f"WHERE datetime >= '{start_date}' "
            f"AND datetime <= '{end_date}' "
            f"AND site_name = '{site}'") #search for the specific site id for bungaribee

    
    #get solar data
    solar_df=sql_con.query_sql(query=query,database='timeseries')

    #convert datetime to pandas datetime
    solar_df['datetime']=pd.to_datetime(solar_df['datetime'])

    #if the entry doesn't have 'Bingo' in column site_name, replace with Toll Bungaribee 400kW
    solar_df['site_name'] = solar_df['site_name'].apply(lambda x: replace_entry(x, search_string='Bingo', replace_string='Toll Bungaribee 400kW'))

    #groupby datetime and site_name and sum energy_generated_kwh
    solar_df=solar_df.groupby(['datetime','site_name']).sum().reset_index()


    #return solar_df
    return solar_df

@st.cache_data
def get_temperature_data(site: str, start_date: str, end_date: str)-> pd.DataFrame:
    table_name='mtae_ops_temp_60min'

    query=(f"SELECT datetime,temp, rel_hum, site_alias  FROM {table_name} "
        f"WHERE datetime >= '{start_date}' "
        f"AND datetime <= '{end_date}' "
        f"AND site_alias = '{site}'")

    #get temp data
    temp_df=sql_con.query_sql(query=query,database='timeseries')

    #convert datetime to pandas datetime
    temp_df['datetime']=pd.to_datetime(temp_df['datetime'])

    #return temp_df
    return temp_df


@st.cache_data
def get_nem12_data(nmi: str, start_date: str, end_date: str, nmi_suffix: str = None)-> pd.DataFrame:
    table_name= 'aemo_msats_mtrd_nem12_prod'
    if nmi_suffix is not None:
        query = (f"SELECT settlement_datetime, reading, nmi, nmi_suffix FROM {table_name} "
                f"WHERE nmi = '{nmi}' and settlement_datetime >= '{start_date}' "
                f"and settlement_datetime < '{end_date}' and nmi_suffix = '{nmi_suffix}'")
    else:
        query = (f"SELECT settlement_datetime, reading, nmi, nmi_suffix FROM {table_name} "
            f"WHERE nmi = '{nmi}' and settlement_datetime >= '{start_date}' "
            f"and settlement_datetime < '{end_date}'")
        
    nem12_df = sql_con.query_sql(query=query,database='timeseries')

    return nem12_df

@st.cache_data
def get_site_cost_forecast(nmi: str=None, site_id: str =None) -> pd.DataFrame:

    #find the associated site_id for the given nmi
    # table_name ='site'

    # if nmi != None:

    #     query = (f"SELECT site_id FROM {table_name} where site_nmi = '{nmi}'")

    # elif site_id != None:

    #     query = (f"SELECT site_id FROM {table_name} where site_id = '{site_id}'")

    # else:
    #     st.error("No nmi or site_id provided")
    #     return None


    # site_id_df = sql_con.query_sql(query=query,database='billing')

    # site_id = site_id_df['site_id'].iloc[0]

    #get the associated forecast for the site_id that is the most recent datetime period
    table_name ='mtae_ops_cost_forecasts'

    query = (f"SELECT * FROM {table_name} where site_id = '{site_id}' and  "
             f"CAST(datetime AS DATE) = (SELECT MAX(CAST(datetime AS DATE)) from {table_name}) or "
             f"CAST(datetime AS DATE) = (SELECT DATEADD(DAY,-1,MAX(CAST(datetime AS DATE))) from {table_name})") 

    forecast_df = sql_con.query_sql(query=query,database='timeseries')

    return forecast_df

@st.cache_data
def get_all_site_forecast() -> pd.DataFrame:
    #get the associated forecast for the site_id that is the most recent datetime period
    table_name ='mtae_ops_cost_forecasts'

    query = (f"SELECT * FROM {table_name} where "
             f"CAST(datetime AS DATE) = (SELECT MAX(CAST(datetime AS DATE)) from {table_name}) or "
             f"CAST(datetime AS DATE) = (SELECT DATEADD(DAY,-1,MAX(CAST(datetime AS DATE))) from {table_name})") 

    forecast_df = sql_con.query_sql(query=query,database='timeseries')

    return forecast_df


## SITE ALIAS FUNCTIONS

@st.cache_data
def get_customer_sites(billied_entity_alias: str)-> pd.DataFrame:
    """Get the ordered list of sites for a seleted customer

    Args:
        billied_entity_alias (str):alias for the billing entity

    Returns:
        pd.DataFrame: dataframe of sites for customer
    """


    #setup query
    table_name="site"
    query = (f"SELECT [site_alias] FROM {table_name} "
             f"WHERE billed_entity_alias = '{billied_entity_alias}' "
             "ORDER BY site_live_date desc")

    #get sites series
    sites=sql_con.query_sql(query=query,database='billing')

    #drop duplicates
    sites.drop_duplicates(inplace=True,keep='last')

    #sort and create as list
    sites_list = sorted(sites['site_alias'].unique().tolist())

    #return list of site alias
    return sites_list

@st.cache_data
def get_site_nmis(site_alias: str)-> pd.DataFrame:
    """Get the ordered list of nmis for a seleted site

    Args:
        site_alias (str): alias for the site

    Returns:
        pd.DataFrame: dataframe of nmis for site
    """

    #get current date
    current_day = date.today().strftime("%Y-%m-%d")

    #setup query
    table_name="site"
    query = (f"SELECT * FROM {table_name} "
             f"WHERE site_alias='{site_alias}' AND site_status='Active'")

    #get customer data
    customer_df=sql_con.query_sql(query=query,database='billing')
    nmi_list =  customer_df['site_nmi'].unique().tolist()

    return nmi_list

@st.cache_data
def get_site_id(nmi: str)->str:
    """Get the site id for a given nmi

    Args:
        nmi (str): nmi to get site id for

    Returns:
        str: site id for nmi
    """
    #setup query
    table_name="site"
    query = (f"SELECT * FROM {table_name} "
             f"WHERE site_nmi='{nmi}' "
             f"ORDER BY site_live_date desc")
    
    # get row containing the desired site id
    site_id_df = sql_con.query_sql(query=query,database='billing') 

    #get value of site_id
    site_id = site_id_df['site_id'].iloc[0]

    return site_id
    
@st.cache_data
def get_solar_sites()-> pd.DataFrame:
    table_name='mtae_ops_client_solar_sites'
    query=(f"SELECT * FROM {table_name}")

    #get solar site data
    solar_sites_df=sql_con.query_sql(query=query,database='standingdata')

    return solar_sites_df

@st.cache_data
def get_weather_sites()-> pd.DataFrame:
    table_name='mtae_ops_nmi_weather_stations'
    query=(f"SELECT nmi, billed_entity_alias, site_alias, site_address, weather_stat_name FROM {table_name}")

    #get weather site data
    weather_sites_df=sql_con.query_sql(query=query,database='standingdata')

    return weather_sites_df

## PUSH FUNCTIONS
def clear_flag():
    """_summary_: Function to clear the flag for the push button
    """
    session_state.sub_key=False

def set_flag():
    """_summary_: Function to clear the flag for the push button
    """
    session_state.display_details=True
    
@st.cache_data
def convert_df(df: pd.DataFrame)->bytes:
    """_summary_: Function to convert a dataframe to a csv file

    Args:
        df (pd.DataFrame): dataframe to convert

    Returns:
        bytes: csv file
    """
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv(encoding='utf-8').encode('utf-8')

@st.cache_resource
def startup_site():


    #startup auth keys
    setup_session_states()

    #setup API connection
    api_con = setup_API_con()

    #get default username and password from logins.pem
    _,username_list, password_list = read_login_pem(Path(__file__).parent.parent.parent)

    #use first line credentials as default login
    username=username_list[0]
    password=password_list[0]

    #setup SQL connection
    sql_con = setup_SQL_con(username=username,password=password)

    #setup connection to geolocator API
    geolocator = setup_geolocator()

    return api_con, sql_con, geolocator


api_con, sql_con, geolocator = startup_site()




