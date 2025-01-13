'''
Python file to generate keys for authenticating users using the app
'''

import pickle
from pathlib import Path
from app.modules.utils import get_logins, CREDENTIALS
import streamlit_authenticator as stauth

from mtatk.mta_sql.sql_utils import SessionManager

session_manager = SessionManager(db_configs=CREDENTIALS.azure_sql_conn_str)
names_list,username_list, password_list, _ = get_logins(session_manager)

hashed_passwords =stauth.Hasher(passwords=password_list).generate()

file_path =Path(__file__).parent/"hashed_pw.pkl"
with file_path.open("wb") as file:
    pickle.dump(hashed_passwords,file)