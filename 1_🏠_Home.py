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

# TRYING 3D Plot
    import matplotlib.pyplot as plt
    import matplotlib
    from mpl_toolkits.mplot3d import Axes3D
    from matplotlib.animation import FuncAnimation
    from squat_jump_utils import split_by_jump
    import streamlit.components.v1 as components

    def create_center_pressure_df(df):
        """Creates a dataframe for visualization when given a path to the raw data file
        (Currently the file format is assumed to be identical to BFR007_3d_vectors.csv)"""

        if 'Unnamed: 0' in df.columns:
            df = df.drop('Unnamed: 0', axis = 1)

        center_pressure_left = df[['time', 'ground_force2_pz', 'ground_force2_px', 'ground_force2_vz', \
                               'ground_force2_vx', 'ground_force2_vy']].copy()
        center_pressure_left.rename(columns = {'ground_force2_pz' : 'ground_force_pt1x',
                                               'ground_force2_px' : 'ground_force_pt1y',
                                               'ground_force2_vz' : 'ground_force_pt2x',
                                               'ground_force2_vx' : 'ground_force_pt2y',
                                               'ground_force2_vy' : 'ground_force_pt2z'
                                                }, inplace = True)
        center_pressure_left['ground_force_pt1z'] = [0]*len(center_pressure_left)
        center_pressure_left['Position'] = ['left']*len(center_pressure_left)

        center_pressure_right = df[['time', 'ground_force1_pz', 'ground_force1_px', 'ground_force1_vz', \
                                    'ground_force1_vx', 'ground_force1_vy']].copy()
        center_pressure_right.rename(columns = {'ground_force1_pz' : 'ground_force_pt1x',
                                                'ground_force1_px' : 'ground_force_pt1y',
                                                'ground_force2_vz' : 'ground_force_pt2x',
                                                'ground_force2_vx' : 'ground_force_pt2y',
                                                'ground_force2_vy' : 'ground_force_pt2z'
                                                 }, inplace = True)
        center_pressure_right['ground_force_pt1z'] = [0]*len(center_pressure_left)
        center_pressure_right['Position'] = ['right']*len(center_pressure_right)

        center_pressure = pd.concat([center_pressure_left, center_pressure_right], axis = 0, ignore_index = True)
        center_pressure.sort_values(by = "time", inplace = True)

        return center_pressure

    df = processed_data.copy()
    df = create_center_pressure_df(df)
    df = split_by_jump(df, index_df, 1)
    df = df[df['Position'] == 'left']
    df = df.reset_index(drop = True)

    fig, ax = plt.subplots(subplot_kw = dict(projection="3d"))

    # Colorbar initiation
    norm = matplotlib.colors.Normalize()
    norm.autoscale(df['ground_force_pt2z'])
    cm = matplotlib.cm.cool
    sm = matplotlib.cm.ScalarMappable(cmap=cm, norm=norm)
    sm.set_array([])

    def get_arrow(idx):
        x = 0
        y = 0
        z = 0
        u = df['ground_force_pt2x'][idx]
        v = df['ground_force_pt2y'][idx]
        w = df['ground_force_pt2z'][idx]
        return x, y, z, u, v, w

    quiver = ax.quiver(*get_arrow(0), arrow_length_ratio = 0.05, color=cm(norm(df['ground_force_pt2z'][0])))

    ax.set_title('3D Force Plot')

    ax.set_xlabel('X Axis')
    ax.set_xlim(min(list(df.ground_force_pt1x) + \
                    list(df.ground_force_pt2x)) - 1,
                max(list(df.ground_force_pt1x) + \
                    list(df.ground_force_pt2x)) + 1)

    ax.set_ylabel('Y Axis')
    ax.set_ylim(min(list(df.ground_force_pt1y) + \
                    list(df.ground_force_pt2y)) - 1,
                max(list(df.ground_force_pt1y) + \
                    list(df.ground_force_pt2y)) + 1)

    ax.set_zlabel('Z Axis')
    ax.set_zlim(min(list(df.ground_force_pt1z) + \
                    list(df.ground_force_pt2z)),
                max(list(df.ground_force_pt1z) + \
                    list(df.ground_force_pt2z)) + 1)

    def update(idx):
        global quiver
        quiver.remove()
        quiver = ax.quiver(*get_arrow(idx), arrow_length_ratio = 0.05, color=cm(norm(df['ground_force_pt2z'][idx])))

    # anim = FuncAnimation(fig, update, frames = len(df), interval = 0.3)
    anim = FuncAnimation(fig, update, frames = range(0, len(df), 4), interval = 1)

    plt.colorbar(sm, location='bottom', label='Force (N)')

    components.html(anim.to_jshtml(), height = 1000)


else:
    st.caption("Please Upload a File Above")
