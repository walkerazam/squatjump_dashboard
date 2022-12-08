"""
Home.py
    This is the main landing page of the dashboard.
    It also contains the visualizations and
    data processing.
"""
import streamlit as st
import pandas as pd
import numpy as np
from squat_jump_utils import groundforce_plot, create_COP_plot
from squat_jump_utils import metric_viewer, create_plot_vs_time
from process_data import process_data

# Page Configurations
st.set_page_config(
    page_title='Squat Jumps Homepage',
    page_icon='🦵'
)

# Page Header
st.write("""# ACL Squat Jumps""")

# Asking User to Upload a Data File
uploaded_file = st.file_uploader("Choose a Patient CSV file", type='csv',
                                 accept_multiple_files=False)
# Check that a User Uploaded a File:
if uploaded_file is not None:
    # Reading in Data File as df
    df = pd.read_csv(uploaded_file, header=6)

    # Retrieve processed data, index, and calculations
    processed_data, index_df, calculations_df = process_data(df)

    st.metric("Patient's Weight (Kg)",
              np.round(calculations_df.loc[1, 'weight(kg)'], 2))

    # Reporting calculated Metrics:
    st.write("""## Jump Metrics:""")

    # Asking which jump to view:
    selected_jump = st.radio("Select which patient jump to View:",
                             ('1', '2', '3'))
    # Seperating into columns for display
    col1, col2, col3 = st.columns(3)
    col1.metric("Jump Time",
                calculations_df.loc[int(selected_jump), 'jump_time(s)'],
                help='Starts from beginning of loading' +
                '/eccentric phase and ends when patient is in the air')
    col2.metric("Eccentric Phase Time",
                calculations_df.loc[int(selected_jump), 'ecce_time(s)'])
    col3.metric("Concentric Phase Time",
                calculations_df.loc[int(selected_jump), 'conc_time(s)'])

    # Creating a Selectbox for Table View
    table_view = st.selectbox(
        "View Metric's Table?",
        ('No', 'Yes'))
    # Conditionals
    if table_view == 'Yes':
        metric_df = metric_viewer(calculations_df)
        # Displaying table with select rows
        st.table(metric_df.loc[["Jump Height (cm)",
                                "Takeoff Velocity (m/s)",
                                "Eccentric Loading Rate (N/s)",
                                "Jump Time (s)",
                                "Eccentric Time (s)",
                                "Concentric Time (s)",
                                "Peak Force (N)",
                                "Left Leg COP Displacement(cm) [Ant.-Post.]",
                                "Right Leg COP Displacement(cm) [Ant.-Post.]",
                                "Left Leg COP Displacement(cm) [Med.-Lat.]",
                                "Right Leg COP Displacement(cm) [Med.-Lat.]"]])
    else:
        pass

    # Asking if a plot for groundforce should be made
    st.write("## Plots of Ground Force by Leg")
    # Creating a Selectbox
    axis = st.selectbox(
        "Select Axis for Ground Force",
        ('Select Axis', 'X-Axis', 'Y-Axis', 'Z-Axis'))
    # Conditional Statements based on Selectbox options
    if axis == 'X-Axis':
        fig = groundforce_plot(df, 'x')
        st.pyplot(fig)
    elif axis == 'Y-Axis':
        fig = groundforce_plot(df, 'y')
        st.pyplot(fig)
    elif axis == 'Z-Axis':
        fig = groundforce_plot(df, 'z')
        st.pyplot(fig)
    else:
        # If none selected, print a message
        st.caption("None Selected...")

    # Giving users options to plot metrics
    st.write("## Jump Plots:")
    # Creating a multiselect interface
    options = st.multiselect(
        'What metrics would you like to visualize?',
        ['Position', 'Velocity', 'Acceleration'])
    # If there is an option...
    if options is None:
        st.caption("None Selected")
    else:
        # Per plot entry, show the plots
        for option in options:
            if option == 'Position':
                st.pyplot(create_plot_vs_time(processed_data, 'bodypos_y'))
            elif option == 'Velocity':
                st.pyplot(create_plot_vs_time(processed_data, 'bodyvel_y'))
            else:
                st.pyplot(create_plot_vs_time(processed_data, 'bodyacc_y'))

    st.write("## Plotting Center of Pressure:")

    # Creating a selectbox for the COP plot
    interactive_choice = st.selectbox(
        "Create Interactive COP Plot?",
        ('No', 'Yes'))
    if interactive_choice == 'Yes':
        fig = create_COP_plot(df)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.caption("No Interactive Plot Selected")

    # Giving an option to download metrics
    @st.cache
    def convert_df(df):
        # IMPORTANT: Cache the conversion to prevent computation on every rerun
        return df.to_csv().encode('utf-8')
    csv = convert_df(metric_viewer(calculations_df))
    # Adding download button
    st.download_button(
        label="Download Jump Metrics as CSV",
        data=csv,
        file_name='jump_metrics.csv',
        mime='text/csv',
    )

else:
    st.caption("Please Upload a File Above")
