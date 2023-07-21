## PAGE TO DISPLAY REAL TIME DATA OF SPOT PRICES 
## CAN CHOOSE BETWEEN DISPATCH OR PREDISPATCH

import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit import session_state
from PIL import Image
import mtatk

from modules.utils import *

#image path
img_path = "app/imgs/400dpiLogo.jpg"

def spot_price_page():
    if session_state.authentication_status:
        pass



setup_session_states()
spot_price_page()