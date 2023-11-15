'''
Python file to generate keys for authenticating users using the app
'''

import pickle
from pathlib import Path
from app.modules.utils import read_login_pem

import streamlit_authenticator as stauth

names_list,username_list, password_list = read_login_pem(file_path=Path(__file__).parent)

hashed_passwords =stauth.Hasher(passwords=password_list).generate()

file_path =Path(__file__).parent/"hashed_pw.pkl"
with file_path.open("wb") as file:
    pickle.dump(hashed_passwords,file)