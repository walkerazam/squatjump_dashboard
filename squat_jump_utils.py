"""
squat_jump_utils.py
    This file contains functions used in
    1_Home.py. These helper functions are
    called from the main home page
    containing the streamlit code.
    This file also contains helper functions used
    for testing purposes.
"""
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
import streamlit as st


def groundforce_plot(df, dir):
    """
    This function creates a plot for ground force. It takes in
    the dataframe passed by a user containing squat jump data
    and a dir ('y', 'x', or 'z') and returns a figure.
    Arguments:
        1. df: Squat Jump Data read from a Force Plate.
        2. dir: 'y', 'z', or 'x' representing column name.
    Return:
        1. fig: figure of ground force jump in passed direction.
    """
    # Run DF check:
    check_data(df)
    check_direction(dir)

    # Split left and right legs
    right_cols = [x for x in list(df.columns) if '1' in x]
    right_cols.append('time')
    left_cols = [x for x in list(df.columns) if '2' in x]
    left_cols.append('time')

    right_df = df[right_cols]
    left_df = df[left_cols]

    fig, ax = plt.subplots()
    column_names = [('ground_force1_v' + str(dir)),
                    ('ground_force2_v' + str(dir))]
    ax.plot(right_df['time'], right_df[column_names[0]], alpha=0.5,
            label='Right')
    ax.plot(left_df['time'], left_df[column_names[1]], alpha=0.5, label='Left')

    ax.set_title("Ground Force in the Axis: " + str.upper(dir))
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Force (N)")
    ax.legend()

    return fig


def create_plot_vs_time(df, column):
    """
    This function creates a plot for acceleration/
    velocity/position against time. It takes in
    the dataframe containing processed squat jump data
    from process_data.py, and also a column name
    and returns the appropriate figure.
    Arguments:
        1. df: Squat Jump Dataframe from process_data.
        2. column: 'bodyacc_y', 'bodyvel_y', or
            'bodypos_y' representing column names.
    Return:
        1. fig: figure of column passed against time.
    """
    # Running a check
    check_plot_col_names(column)

    fig, ax = plt.subplots()
    ax.plot(df['time'], df[column], color='#4B2E83')
    ax.set_facecolor("#F8F9FF")
    # For passed column, create appropriate labels
    if column == 'bodyacc_y':
        ax.set_title("Jump Acceleration")
        ax.set_ylabel("Acceleration (m/s^2)")
    elif column == 'bodyvel_y':
        ax.set_title("Jump Velocity")
        ax.set_ylabel("Velocity (m/s)")
    else:
        # If not velocity or acceleration, then position
        ax.set_title("Jump Position")
        ax.set_ylabel("Position (m)")
    ax.set_xlabel("Time (s)")
    # Returning figure
    return fig


@st.cache
def create_COP_plot(df):
    """
    This function creates an interactive COP plot using
    plotly. It takes in the read jump dataframe and returns
    a figure.
    Arguments:
        1. df: Dataframe of squat jump data from force plates.
    Return:
        1. fig: An interactive Plotly figure for COP data.
    """
    # Run DF Check:
    check_data(df)

    # Creating df for plotting center of pressure:
    center_pressure_left = df[['time', 'ground_force1_px',
                               'ground_force1_py',
                               'ground_force1_pz']].copy()
    # Renaming Columns for Left Leg:
    center_pressure_left.rename(columns={
        'ground_force1_px': 'ground_force_px',
        'ground_force1_py': 'ground_force_py',
        'ground_force1_pz': 'ground_force_pz'},
                                inplace=True)
    center_pressure_left['side'] = ['left']*len(center_pressure_left)
    # Renaming Columns for Right Leg:
    center_pressure_right = df[['time', 'ground_force2_px',
                                'ground_force2_py',
                                'ground_force2_pz']].copy()
    center_pressure_right.rename(columns={
        'ground_force2_px': 'ground_force_px',
        'ground_force2_py': 'ground_force_py',
        'ground_force2_pz': 'ground_force_pz'},
                                 inplace=True)
    center_pressure_right['side'] = ['right']*len(center_pressure_right)
    # Joining together with added information for left and right leg
    center_pressure = pd.concat([center_pressure_left,
                                 center_pressure_right],
                                axis=0, ignore_index=True)
    center_pressure.sort_values(by="time", inplace=True)
    # Splitting time into ranges for computational purposes
    center_pressure = center_pressure.groupby(
        [pd.cut(center_pressure.time,
         bins=np.arange(0, round(max(center_pressure.time)), step=.5),
         include_lowest=True), 'side']
        )[['ground_force_px', 'ground_force_pz']].mean()
    # Reset index
    center_pressure = center_pressure.reset_index()

    # Creating plotly figure
    fig = px.scatter(center_pressure, x="ground_force_pz",
                     y="ground_force_px", facet_col="side",
                     animation_frame='time', range_x=[-1.36, -0.40],
                     range_y=[0.02, 0.40])

    # Updating slider
    steps = []
    for i in range(len(fig.data)):
        step = dict(
            method="update",
            args=[{"visible": [False] * len(fig.data)},
                  {"title": "Time: " + str(5 * i)+" seconds"}, ],
            label=str(5 * i))
        step["args"][0]["visible"][i] = True
        steps.append(step)

    # check_plotly_output(fig)

    return fig


def metric_viewer(calculations_df):
    """
    This function creates a metric table output to be viewed in
    Streamlit.
    Arguments:
        1. calculations_df: a dataframe containing metric calculations,
            as output from process_data.py function process_data
    Return:
        1. metric_df: a dataframe of metrics in a format easy to view
            through streamlit.
    """
    metric_df = calculations_df.copy()  # Creating a copy
    # Updating column names to more readable:
    metric_names = [
        "weight(kg)",
        "Jump Height (cm)",
        "Takeoff Velocity (m/s)",
        "Eccentric Loading Rate (N/s)",
        "Jump Time (s)",
        "Eccentric Time (s)",
        "Concentric Time (s)",
        "Peak Force (N)",
        "Peak Power (W)",
        "Average Concentric Power (W)",
        "Squat Depth (cm)",
        "Left Leg COP Displacement(cm) [Ant.-Post.]",
        "Right Leg COP Displacement(cm) [Ant.-Post.]",
        "Left Leg COP Displacement(cm) [Med.-Lat.]",
        "Right Leg COP Displacement(cm) [Med.-Lat.]"
    ]
    # Renaming columns
    metric_df.columns = metric_names
    # Transposing to better show table
    metric_df = metric_df.iloc[:, 1:].T
    # Renaming columns
    metric_df.columns = ['Jump 1', 'Jump 2', 'Jump 3']
    return metric_df


def split_by_jump(df, index, jump):
    """
    This function splits the processed dataframe of jumps and
    splits it by jump (1, 2 or 3).
    Arguments:
        1. df: the processed jump dataframe containing time.
        2. index: the index dataframe output from process_data.py
        3. jump: an int being either 1, 2 or 3 representing which
            jump to find.
    Return:
        1. jump_df: the dataframe containing values only for a given
            jump.
    """
    # Creating masks for passed jumps
    if jump == 1:
        mask1 = df['time'] >= (index['Jump 1 Start'][0]/1000)
        mask2 = df['time'] <= (index['Jump 1 End'][0]/1000)
    elif jump == 2:
        mask1 = df['time'] >= (index['Jump 2 Start'][0]/1000)
        mask2 = df['time'] <= (index['Jump 2 End'][0]/1000)
    else:
        mask1 = df['time'] >= (index['Jump 3 Start'][0]/1000)
        mask2 = df['time'] <= (index['Jump 3 End'][0]/1000)
    # Filtering
    jump_df = df[mask1 & mask2]
    return jump_df


def create_center_pressure_df(df):
    """
    Creates a dataframe for visualization
    when given a path to the raw data file.
    Arguments:
        1. df: processed_df containing vector data
    Return:
        1. center_pressure: df containing translated
            column names and position.
    """
    # Seperating Left Leg Data
    center_pressure_left = df[['time',
                               'ground_force2_pz',
                               'ground_force2_px',
                               'ground_force2_vz',
                               'ground_force2_vx',
                               'ground_force2_vy']].copy()
    # Renaming columns:
    center_pressure_left.rename(columns={
        'ground_force2_pz': 'ground_force_pt1x',
        'ground_force2_px': 'ground_force_pt1y',
        'ground_force2_vz': 'ground_force_pt2x',
        'ground_force2_vx': 'ground_force_pt2y',
        'ground_force2_vy': 'ground_force_pt2z'
                                            }, inplace=True)
    center_pressure_left['ground_force_pt1z'] = [0] * \
        len(center_pressure_left)
    # Adding a new column Position
    center_pressure_left['Position'] = ['left'] * len(center_pressure_left)
    # Seperating Right Leg Data
    center_pressure_right = df[['time',
                                'ground_force1_pz',
                                'ground_force1_px',
                                'ground_force1_vz',
                                'ground_force1_vx',
                                'ground_force1_vy']].copy()
    # Homogenizing column names for right leg also
    center_pressure_right.rename(columns={
        'ground_force1_pz': 'ground_force_pt1x',
        'ground_force1_px': 'ground_force_pt1y',
        'ground_force2_vz': 'ground_force_pt2x',
        'ground_force2_vx': 'ground_force_pt2y',
        'ground_force2_vy': 'ground_force_pt2z'
                                            }, inplace=True)
    center_pressure_right['ground_force_pt1z'] = [0] * \
        len(center_pressure_left)
    # Adding column for Position
    center_pressure_right['Position'] = ['right'] * \
        len(center_pressure_right)
    # Rejoining our two dataframes
    center_pressure = pd.concat([center_pressure_left,
                                 center_pressure_right],
                                axis=0, ignore_index=True)
    # Sorting by time
    center_pressure.sort_values(by="time", inplace=True)
    # Returning the dataset with Position
    return center_pressure


# Helper functions below:
def check_data(df):
    """
    This function checks that the passed dataframe has the correct shape
    (19 columns) since forceplate outputs are consistent.
    Arguments:
        1. df: Patient forceplate data containing variable rows,
            but having set 19 columns.
    Return:
        RaiseError if not correct shape or not a pandas dataframe.
    """
    # Raise Errors based on correct types of data passed:
    if (type(df) is pd.DataFrame) is False:
        raise TypeError('Data type received for "data" must be a pandas ' +
                        'DataFrame. Instead recieved data type ' +
                        str(type(df)))
    # Raise Errors if there are not 3 columns in the dataset:
    elif df.shape[1] != 19:
        raise ValueError('Data shape passed has wrong number of columns. ' +
                         'Expected to have 19 columns instead got ' +
                         str(df.shape[1]) + ' columns.')
    # Raise error is there are missing values:
    elif df.isna().sum().sum() >= 1:
        raise ValueError('Data contains missing values!')
    else:
        return None


def check_direction(dir):
    """
    This function checks that the direction input is
    either 'x', 'y', or 'z'. Else raises error!
    Arguments:
        1. dir: string value of either x, y, or z.
    Return:
        RaiseError if not string or an accepted direction.
    """
    # Raise Errors based on correct types of direction passed:
    if (type(dir) is str) is False:
        raise TypeError('Direction passed is not accepted!')
    # Raise Errors if direction is not x, y or z:
    elif (dir in ['x', 'y', 'z']) is False:
        raise ValueError('Direction passed can only be ' +
                         'x, y, or z.')
    else:
        return None


def check_matplotlib_output(fig):
    """
    This function checks if the resulting figure made by Matplotlib is
    the right type.
    Arguments:
        1. fig: Figure created using Matplotlib
    Return:
        RaiseError if not correct type (matplotlib.figure.Figure).
    """
    # Raise Errors output is unexpected type:
    if type(fig) != plt.Figure:
        raise TypeError('Output figure type must be a matplotlib figure ' +
                        'Instead returned figure type ' +
                        str(type(fig)))
    else:
        return None


def check_plot_col_names(column):
    """
    This function checks that the passed column name for the
    plot against time function is valid.
    Arguments:
        1. column: A passed column name. Can be bodypos_y,
            bodyacc_y, or bodyvel_y.
    Return:
        RaiseError if not correct accepted column name.
    """
    # Raise Errors output is unexpected type:
    if column not in ['bodyacc_y', 'bodyvel_y', 'bodypos_y']:
        raise ValueError('Passed Column Name is not Valid.')
    else:
        return None
