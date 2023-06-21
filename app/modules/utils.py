'''
Utilities module to assist the streamlit app
'''
from mtatk.api_lib.aemo_api_connector import APIConnector
from mtatk.mta_sql.sql_connector import SQLConnector
import streamlit as st
import pandas as pd
from pathlib import Path
import base64
from datetime import date

cert=r"C:\Users\Marco Tupaz\MTA Energy\MTA Energy - Documents\IT\AEMO_CSRs/kv-mta-MTAENERGY-Prod-20221111.pem"


def setup_API_con():

    #create API Connector object
    api_connector=APIConnector(cert=cert)

    return api_connector

def setup_SQL_con():

    #create SQL Connection object
    username="mtaenergy_admin"
    password ="Wombat100"
    sql_con = SQLConnector(username=username,password=password)

    return sql_con


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

def get_nmi_participants(nmi: str):

    #setup query
    table_name="aemo_msats_cats_nmi_participant_relations"
    query = (f"SELECT * FROM {table_name} "
             f"WHERE nmi='{nmi}'")
    
    #get participants data
    nmi_participants_df=sql_con.query_sql(query=query,database='standingdata')

    return nmi_participants_df

def img_to_bytes(img_path):
    img_bytes = Path(img_path).read_bytes()
    encoded = base64.b64encode(img_bytes).decode()
    return encoded

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
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

api_con = setup_API_con()
sql_con = setup_SQL_con()