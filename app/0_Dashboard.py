import streamlit as st
from streamlit import session_state


st.set_page_config(
    page_title="MTA Energy Executive Dashboard",
    page_icon=":bar_chart:",
    layout="wide"
)

st.title("Business Overview")


if 'sub_key' not in session_state:
    session_state['sub_key'] = False

#reset sub key if returned to dashboard
session_state.sub_key=False

#st.sidebar.success("Page selector")
