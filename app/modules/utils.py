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
from datetime import date
import logging
from geopy.geocoders import Nominatim

current_path = Path(__file__).parent.parent.parent
cert = str(current_path/ "kv-mta-MTAENERGY-Prod-20221111.pem")


@st.cache_data
def setup_API_con():

    #create API Connector object
    api_connector=APIConnector(cert=cert)

    return api_connector

@st.cache_resource
def setup_SQL_con(username: str, password: str) -> SQLConnector:

    #create SQL Connection object
    sql_con = SQLConnector(username=username,password=password)

    return sql_con

@st.cache_data
def setup_geolocator():
    geolocator = Nominatim(user_agent="my_app")

    return geolocator

@st.cache_data
def img_to_bytes(img_path):
    img_bytes = Path(img_path).read_bytes()
    encoded = base64.b64encode(img_bytes).decode()
    return encoded

@st.cache_data
def read_login_pem(file_path:str):

    #set lists
    names_list =[]
    username_list=[]
    password_list=[]

    #logging.info(file_path)

    #open login.pem file and append login details to lists
    with open(f'{file_path}/logins.pem','r') as file:
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

'''
GET FUNCTIONS TO SQL DB
'''

@st.cache_data
def get_cost_stat(lookback_op: str):

    #casewhere where depending on the lookback option chosen, the query will be different
    if lookback_op =="Last Month":
        query  = ("SELECT SUM(total_cost_ex_gst) as total_cost "
                  "FROM mtae_ops_billing_billing_records_prod "
                  "WHERE bill_run_end_date >= DATEADD(month, DATEDIFF(month, 0, GETDATE()) - 1, 0) "
                  "AND bill_run_end_date < DATEADD(month, DATEDIFF(month, 0, GETDATE()), 0)")
        
    elif lookback_op == "Last 3 Months":
        query  = ("SELECT SUM(total_cost_ex_gst) as total_cost "
                  "FROM mtae_ops_billing_billing_records_prod "
                  "WHERE bill_run_end_date >= DATEADD(month, DATEDIFF(month, 0, GETDATE()) - 3, 0) "
                  "AND bill_run_end_date < DATEADD(month, DATEDIFF(month, 0, GETDATE()), 0)")
        
    elif lookback_op == "Last 6 Months":
        query  = ("SELECT SUM(total_cost_ex_gst) as total_cost "
                  "FROM mtae_ops_billing_billing_records_prod "
                  "WHERE bill_run_end_date >= DATEADD(month, DATEDIFF(month, 0, GETDATE()) - 6, 0) "
                  "AND bill_run_end_date < DATEADD(month, DATEDIFF(month, 0, GETDATE()), 0)")
        
    elif lookback_op == "Last Year":
        query  = ("SELECT SUM(total_cost_ex_gst) as total_cost "
                  "FROM mtae_ops_billing_billing_records_prod "
                  "WHERE bill_run_end_date >= DATEADD(year, DATEDIFF(year, 0, GETDATE()) - 1, 0) "
                    "AND bill_run_end_date < DATEADD(year, DATEDIFF(year, 0, GETDATE()), 0)")
    else:
        st.error("Invalid date range chosen")

    #logging.info(query)

    #retrieve value from sql
    total_cost = sql_con.query_sql(query=query,database='timeseries')

    #convert to float 
    total_cost_flt= float(total_cost.iloc[0].round(2))

    #convert to str and format to use commas for thousands separator
    total_cost_str = "{:,.2f}".format(total_cost_flt)

    return total_cost_str

@st.cache_data
def get_consump_stat(lookback_op: str):

    #casewhere where depending on the lookback option chosen, the query will be different
    if lookback_op =="Last Month":
        query  = ("SELECT SUM(volume) as total_consump "
                  "FROM mtae_ops_billing_billing_records_prod "
                  "WHERE charge_group = 'Commodity' "
                  "AND bill_run_end_date >= DATEADD(month, DATEDIFF(month, 0, GETDATE()) - 1, 0) "
                  "AND bill_run_end_date < DATEADD(month, DATEDIFF(month, 0, GETDATE()), 0)")
        
    elif lookback_op == "Last 3 Months":
        query  = ("SELECT SUM(volume) as total_consump "
                  "FROM mtae_ops_billing_billing_records_prod "
                  "WHERE charge_group = 'Commodity' "
                  "AND bill_run_end_date >= DATEADD(month, DATEDIFF(month, 0, GETDATE()) - 3, 0) "
                  "AND bill_run_end_date < DATEADD(month, DATEDIFF(month, 0, GETDATE()), 0)")
        
    elif lookback_op == "Last 6 Months":
        query  = ("SELECT SUM(volume) as total_consump "
                  "FROM mtae_ops_billing_billing_records_prod "
                  "WHERE charge_group = 'Commodity' "
                  "AND bill_run_end_date >= DATEADD(month, DATEDIFF(month, 0, GETDATE()) - 6, 0) "
                  "AND bill_run_end_date < DATEADD(month, DATEDIFF(month, 0, GETDATE()), 0)")
        
    elif lookback_op == "Last Year":
        query  = ("SELECT SUM(volume) as total_consump "
                  "FROM mtae_ops_billing_billing_records_prod "
                  "WHERE charge_group = 'Commodity' "
                  "AND bill_run_end_date >= DATEADD(year, DATEDIFF(year, 0, GETDATE()) - 1, 0) "
                    "AND bill_run_end_date < DATEADD(year, DATEDIFF(year, 0, GETDATE()), 0)")
    else:
        st.error("Invalid date range chosen")

    #logging.info(query)

    #retrieve value from sql
    total_consump = sql_con.query_sql(query=query,database='timeseries')

    #convert to float 
    total_consump_flt= float(total_consump.iloc[0].round(2))

    #convert to str and format to use commas for thousands separator
    total_consump_str = "{:,.2f}".format(total_consump_flt)

    return total_consump_str

@st.cache_data
def get_carbon_stat(lookback_op: str):

    #casewhere where depending on the lookback option chosen, the query will be different
    if lookback_op =="Last Month":
        query  = ("SELECT SUM(volume*scaling_factor*loss_factor) as total_carbon "
                  "FROM mtae_ops_billing_billing_records_prod "
                  "WHERE charge_name ='Carbon' "
                  "AND bill_run_end_date >= DATEADD(month, DATEDIFF(month, 0, GETDATE()) - 1, 0) "
                  "AND bill_run_end_date < DATEADD(month, DATEDIFF(month, 0, GETDATE()), 0)")
        
    elif lookback_op == "Last 3 Months":
        query  = ("SELECT SUM(volume*scaling_factor*loss_factor) as total_carbon "
                  "FROM mtae_ops_billing_billing_records_prod "
                  "WHERE charge_name ='Carbon' "
                  "AND bill_run_end_date >= DATEADD(month, DATEDIFF(month, 0, GETDATE()) - 3, 0) "
                  "AND bill_run_end_date < DATEADD(month, DATEDIFF(month, 0, GETDATE()), 0)")
        
    elif lookback_op == "Last 6 Months":
        query  = ("SELECT SUM(volume*scaling_factor*loss_factor) as total_carbon "
                  "FROM mtae_ops_billing_billing_records_prod "
                  "WHERE charge_name ='Carbon' "
                  "AND bill_run_end_date >= DATEADD(month, DATEDIFF(month, 0, GETDATE()) - 6, 0) "
                  "AND bill_run_end_date < DATEADD(month, DATEDIFF(month, 0, GETDATE()), 0)")
        
    elif lookback_op == "Last Year":
        query  = ("SELECT SUM(volume*scaling_factor*loss_factor) as total_carbon "
                  "FROM mtae_ops_billing_billing_records_prod "
                  "WHERE charge_name ='Carbon' "
                  "AND bill_run_end_date >= DATEADD(year, DATEDIFF(year, 0, GETDATE()) - 1, 0) "
                    "AND bill_run_end_date < DATEADD(year, DATEDIFF(year, 0, GETDATE()), 0)")
    else:
        st.error("Invalid date range chosen")

    #logging.info(query)

    #retrieve value from sql
    total_carbon = sql_con.query_sql(query=query,database='timeseries')

    #convert to float 
    total_carbon_flt= float(total_carbon.iloc[0].round(2))

    #convert to str and format to use commas for thousands separator
    total_carbon_str = "{:,.2f}".format(total_carbon_flt)

    return total_carbon_str

@st.cache_data
def get_billing_records_prod_df(columns: str, lookback_op: str):

    #setup start of query
    query = (f"SELECT [bill_run_end_date],[master_customer],{columns} FROM mtae_ops_billing_billing_records_prod ")

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
        query =query + ("WHERE bill_run_start_date >= DATEFROMPARTS(YEAR(GETDATE())-1, 7, 1) "
                        " AND bill_run_start_date < DATEFROMPARTS(YEAR(GETDATE()) , 7, 1)")
        
    elif lookback_op == "Last FY":
        query =query + ("WHERE bill_run_start_date >= DATEFROMPARTS(YEAR(GETDATE())-2, 7, 1) "
                        " AND bill_run_start_date < DATEFROMPARTS(YEAR(GETDATE())-1 , 7, 1)")

    else:
        st.error("Invalid date range chosen")

    #logging.info(query)


    #retrieve df from sql
    billing_df = sql_con.query_sql(query=query,database='timeseries')

    #drop date columns
    billing_df.drop(['bill_run_end_date'],axis=1, inplace=True)

    return billing_df

@st.cache_data
def get_customer_list():

    #setup query
    table_name="mtae_ops_billing_nmi_standing_data_prod"
    query = (f"SELECT * FROM {table_name}")

    #get customer data
    customer_df=sql_con.query_sql(query=query,database='standingdata')

    #setup list
    customer_list = customer_df['master_customer'].unique().tolist()

    return customer_list

@st.cache_data
def get_nmi_list():

    #get current date
    current_day = date.today().strftime("%Y-%m-%d")

    #setup query
    table_name="mtae_ops_billing_nmi_standing_data_prod"
    query = (f"SELECT * FROM {table_name}")

    #get customer data
    customer_df=sql_con.query_sql(query=query,database='standingdata')
    customer_nmis =  customer_df['nmi'].unique().tolist()

    #get data with nmi frmp data
    table_name= "mtae_ops_nmi_frmp_dates"
    active_nmis_query=(f"SELECT * FROM {table_name} "
                    f"WHERE frmp_end_date >= '{current_day}'")

    #get all nmis that have a frmp_end_date after the end_date of our query
    active_nmis_df = sql_con.query_sql(query=active_nmis_query,database='standingdata')

    #get list of active nmi's
    active_nmi_list=active_nmis_df['nmi'].unique().tolist()

    #determine the intersection between customer nmi list and active nmi list
    nmi_list = list(set(customer_nmis) & set(active_nmi_list))

    return nmi_list

@st.cache_data
def get_nmi_msats_data(nmi: str) -> pd.DataFrame:

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
def get_nmi_tariff(nmi: str):

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
def get_nmi_customer(nmi: str):

    #setup query
    table_name="mtae_ops_billing_nmi_standing_data_prod"
    query = (f"SELECT * FROM {table_name} "
             f"WHERE nmi='{nmi}' "
             f"ORDER BY creation_date desc")

    #get customer data
    nmi_customer_df=sql_con.query_sql(query=query,database='standingdata')

    #return the top row as it is the most up to date
    return nmi_customer_df.iloc[0]

@st.cache_data
def get_nmi_participants(nmi: str):

    #setup query
    table_name="aemo_msats_cats_nmi_participant_relations"
    query = (f"SELECT * FROM {table_name} "
             f"WHERE nmi='{nmi}'")
    
    #get participants data
    nmi_participants_df=sql_con.query_sql(query=query,database='standingdata')

    return nmi_participants_df


## SITE ALIAS FUNCTIONS

@st.cache_data
def get_customer_sites(billied_entity_alias: str):
    """Get the ordered list of sites for a seleted customer

    Args:
        billied_entity_alias (str): _description_

    Returns:
        _type_: _description_
    """

    # #setup query
    # table_name="site"
    # query = (f"SELECT * FROM {table_name} "
    #          f"WHERE billed_entity_alias='{billied_entity_alias}' "
    #          f"ORDER BY site_live_date desc")
    

    # # get df of sites from specific customer
    # customer_bill_df = sql_con.query_sql(query=query,database='billing')


    #setup query
    table_name="mtae_ops_billing_nmi_standing_data_prod"
    query = (f"SELECT [site_alias] FROM {table_name} "
             f"WHERE master_customer = '{billied_entity_alias}' "
             "ORDER BY creation_date")

    #get sites series
    sites=sql_con.query_sql(query=query,database='standingdata')

    #drop duplicates
    sites.drop_duplicates(inplace=True,keep='last')

    #sort and create as list
    sites_list = sorted(sites['site_alias'].unique().tolist())

    #return list of site alias
    return sites_list

@st.cache_data
def get_site_nmis(site_alias: str):

    # #setup query
    # table_name="site"
    # query = (f"SELECT * FROM {table_name} "
    #          f"WHERE site_alias='{site_alias}' "
    #          f"ORDER BY site_live_date desc")
    
    # # get df of nmis from specific site
    # site_bill_df = sql_con.query_sql(query=query,database='billing')


    #get current date
    current_day = date.today().strftime("%Y-%m-%d")

    #setup query
    table_name="mtae_ops_billing_nmi_standing_data_prod"
    query = (f"SELECT * FROM {table_name} "
             f"WHERE site_alias='{site_alias}'")

    #get customer data
    customer_df=sql_con.query_sql(query=query,database='standingdata')
    customer_nmis =  customer_df['nmi'].unique().tolist()

    #get data with nmi frmp data
    table_name= "mtae_ops_nmi_frmp_dates"
    active_nmis_query=(f"SELECT * FROM {table_name} "
                    f"WHERE frmp_end_date >= '{current_day}'")

    #get all nmis that have a frmp_end_date after the end_date of our query
    active_nmis_df = sql_con.query_sql(query=active_nmis_query,database='standingdata')

    #get list of active nmi's
    active_nmi_list=active_nmis_df['nmi'].unique().tolist()

    #determine the intersection between customer nmi list and active nmi list
    nmi_list = list(set(customer_nmis) & set(active_nmi_list))

    return nmi_list


    # #retuen list of nmis
    # return sorted(site_bill_df['site_nmi'].unique().tolist())

@st.cache_data
def get_site_id(nmi: str)->str:
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
    

## PUSH FUNCTIONS

def clear_flag():
    session_state.sub_key=False
    



@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

@st.cache_resource
def startup_site():


    api_con = setup_API_con()

    #get default username and password from logins.pem
    _,username_list, password_list = read_login_pem(Path(__file__).parent.parent.parent)

    #use first line credentials as default login
    username=username_list[0]
    password=password_list[0]

    sql_con = setup_SQL_con(username=username,password=password)

    geolocator = setup_geolocator()

    return api_con, sql_con, geolocator

api_con, sql_con, geolocator = startup_site()