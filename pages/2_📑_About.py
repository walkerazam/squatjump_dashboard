"""
About.py
    This file conatins code for the About Page
    that will be used in the Squat Jumps Dashboard
    for Streamlit.

    This file mainly conatins text information about
    the dashboard's usage and information...
"""
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title='Squat Jumps About Page',
    page_icon='📑'
)

# Page Contents
st.title('ACL Squat Jump Analysis')
st.caption('By: Andrew Ba, Walker Azam, Seoyeon Hong, John Cheng')

st.markdown("**Purpose**: To allow doctors/physicians to better comprehend \
    patients ACL recovery status & automate identification process")
