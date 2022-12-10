"""
Home.py
    This is the main landing page of the dashboard.
    It also contains the visualizations and
    data processing.
    This file imports functions from various helper files
    to produce, process, and display jump results.
    For more information see:
    https://github.com/walkerazam/squatjump_dashboard
"""
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import streamlit.components.v1 as components
from squat_jump_utils import groundforce_plot, create_COP_plot
from squat_jump_utils import metric_viewer, create_plot_vs_time
from squat_jump_utils import split_by_jump, create_center_pressure_df
from process_data import process_data
from matplotlib.animation import FuncAnimation

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

    metric_df = metric_viewer(calculations_df)
    with st.expander("View Complete Jump Metrics"):
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
    # Giving an option to download metrics
    @st.cache  # noqa: E301
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

    # 3D Animated Plot:

    st.write("## 3D Animation For Forces:")
    df = processed_data.copy()
    # Retrieveing DF with Position
    df_pos = create_center_pressure_df(df)
    # Asking which jump to view:
    jump = st.radio("Select which jump to view:",
                    ('None', '1', '2', '3'))
    if jump != 'None':
        # Creating 2 columns for left and right sides
        left, right = st.columns(2)
        # Create a 3D plot for both directions
        for direction in ['left', 'right']:
            # Splitting our Dataset by the selected jump
            df = split_by_jump(df_pos, index_df, jump)

            # Selecting Leg Position (Left or Right)
            selected_position = direction
            df = df[df['Position'] == selected_position]
            # Resetting index
            df = df.reset_index(drop=True)

            # Creating plot animation
            fig, ax = plt.subplots(figsize=(3.5, 3.5),
                                   subplot_kw=dict(projection="3d"))
            # Colorbar initiation
            norm = matplotlib.colors.Normalize()
            norm.autoscale(df_pos['ground_force_pt2z'])
            cm = matplotlib.cm.cool
            sm = matplotlib.cm.ScalarMappable(cmap=cm, norm=norm)
            sm.set_array([])

            def get_arrow(idx):
                """
                This function returns unit vector arrow position for
                plotting in a 3D space.
                Arguments:
                    1. idx: index of the time for where plot the arrow
                Return:
                    1. coordinates for x, y, z, and magnitude values
                        (u, v, w)
                """
                # x, y, and z = 0 for static start positions
                x = 0
                y = 0
                z = 0
                u = df['ground_force_pt2x'][idx]
                v = df['ground_force_pt2y'][idx]
                w = df['ground_force_pt2z'][idx]
                return x, y, z, u, v, w

            def update(idx):
                """
                This function takes the index for the 3D animation
                in order to update the arrows.
                No returns, but updates Quiver position.
                Arguments:
                    1. idx: the time index for the jump data.
                """
                # Calling on the global quiver
                global quiver
                # Removing the old quiver
                quiver.remove()
                # Replotting based on new idx
                quiver = ax.quiver(
                    *get_arrow(idx), arrow_length_ratio=0.05,
                    color=cm(norm(df['ground_force_pt2z'][idx]))
                    )

            # Quiver plotting:
            quiver = ax.quiver(*get_arrow(0), arrow_length_ratio=0.05,
                               color=cm(norm(df['ground_force_pt2z'][0])))
            # Plot Title:
            plot_title = '3D Force Plot for Jump ' + str(jump) + \
                         ' [' + str(selected_position) + ']'
            ax.set_title(plot_title)
            # X Axis:
            ax.set_xlabel('X Axis')
            ax.set_xlim(min(list(df.ground_force_pt1x) +
                            list(df.ground_force_pt2x)) - 1,
                        max(list(df.ground_force_pt1x) +
                            list(df.ground_force_pt2x)) + 1)
            # Y Axis:
            ax.set_ylabel('Y Axis')
            ax.set_ylim(min(list(df.ground_force_pt1y) +
                            list(df.ground_force_pt2y)) - 1,
                        max(list(df.ground_force_pt1y) +
                            list(df.ground_force_pt2y)) + 1)
            # Z Axis:
            ax.set_zlabel('Force Magnitude')
            ax.set_zlim(min(list(df_pos.ground_force_pt1z) +
                            list(df_pos.ground_force_pt2z)),
                        max(list(df_pos.ground_force_pt1z) +
                            list(df_pos.ground_force_pt2z)) + 1)

            # Animation figure
            anim = FuncAnimation(fig, update, frames=range(0, len(df), 4),
                                 interval=1)
            # Colorbar for magnitude
            plt.colorbar(sm, location='bottom', label='Force (N)')
            # To show in streamlit, saving as jshtml and then showing in
            # every column:
            if direction == 'left':
                with left:
                    components.html(anim.to_jshtml(), height=750,
                                    scrolling=True)
            else:
                with right:
                    components.html(anim.to_jshtml(), height=750,
                                    scrolling=True)


else:
    st.caption("Please Upload a File Above")
