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
st.title('Squat Jump Analysis')
st.caption('By: Andrew Ba, Walker Azam, Seoyeon Hong, John Cheng')

st.markdown("**Purpose**: To allow medical professionals to better comprehend \
    patients ACL recovery status & automate identification process.")

# Project information
tab1, tab2 = st.tabs(['Project Abstract', 'Project Motivation'])

with tab1:
    st.markdown("**Abstract**:")
    st.markdown("The purpose of this project was to configure a web \
        application that allows users to analyze force data derived \
        from squat jumps. These squat jumps were done by subjects \
        recovering from ACL-reconstruction surgery. Users are able \
        to interact with the analysis program through the dashboard \
        in Streamlit.")
    st.markdown("Jump data in the form of a CSV can be dragged and \
        dropped in the dash. Metrics, such as peak force, jump height, \
        and timestamps are calculated in the back-end and returned to the \
        user via multiple visualizations. The calculation results can be \
        downloaded as a CSV for further analysis/comparision.")

with tab2:
    st.markdown("**Motivation**:")
    st.markdown("The key motivation was to make an analysis program that \
        is constructive and accessible for users who can diagnose ACL \
        injuries or work with people recovering from ACL reconstruction. \
        These users most likely do not have enough knowledge or time to \
        compute the jump metrics themselves, or are not able to create \
        an automated program from scratch.")
    st.markdown("Another motivation was to create a program that could \
        accurately identify timestamps of jump events in order to \
        automate calculations without user input.")

# Specific Use Case Information
st.markdown("### How To Use:")
st.write("""
    To use this web application dashboard, please directly upload \
    force plate data in the form of a CSV. Force plate data should \
    capture 3 squat jumps for a given patient.
""")
with st.expander("**Information About Accepted Data**"):
    st.write("""
        Data is only accepted in the form of a CSV. The tool automatically \
        removes any headers in the data file.

        For examples of how the data should look and what columns should be \
        included, please look at the data directory included in this \
        project's GitHub page:
        https://github.com/walkerazam/squatjump_dashboard
    """)
st.write("""
    After uploading the jump data as a CSV, back-end \
    processing generates key metrics for the patient \
    that is presented in the dashboard. Metrics are \
    presented in a table view, but can also be donwloaded \
    as a CSV.

    Visualizations can be selected to be viewed based on what \
    the user is seeking to understand.
""")
with st.expander("**Data Privacy**"):
    st.write("""
        This tool does not store any information regarding the data uploaded \
        or the results made. The example data provided is anonymized and is \
        not authorized to be used in any other purpose than this project.
    """)
with st.expander("**Technologies Used**"):
    st.write("""
        This tool was made in Python, using Streamlit. \
        Visualizations were made using common libraries such as \
        plotly and matplotlib. Data processing was done with \
        standard libaries such as NumPy, Pandas, and SciPy.
    """)
