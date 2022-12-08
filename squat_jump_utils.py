"""
squat_jump_utils.py
    This file contains functions used in
    1_Home.py. These helper functions are
    called from the main home page
    containing the streamlit code.
"""
import pandas as pd
import numpy as np

import plotly.express as px
import plotly.graph_objs as go

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

    check_plotly_output(fig)

    return fig

def create_3D_force_plot(df, position = 'left'):
    """
    This function creates an interactive 3D force plot using
    Matplotlib FuncAnimation. It takes in the read jump dataframe and returns
    a figure.
    Arguments:
        1. df: Dataframe of squat jump data from force plates.
    Return:
        1. fig: An interactive 3D figure for force data.
    """

    if position == 'left':
        df = df[df['Position'] == 'left']
    else:
        df = df[df['Position'] == 'right']

    df = df.reset_index(drop = True)

#     global fig, ax
    fig, ax = plt.subplots(subplot_kw = dict(projection="3d"))

    # Colorbar initiation
    norm = matplotlib.colors.Normalize()
    norm.autoscale(df['ground_force_pt2z'])
    cm = matplotlib.cm.cool
    sm = matplotlib.cm.ScalarMappable(cmap=cm, norm=norm)
    sm.set_array([])

    def get_arrow(idx):
        x = df['ground_force_pt1x'][idx]
        y = df['ground_force_pt1y'][idx]
        z = df['ground_force_pt1z'][idx]
        u = df['ground_force_pt2x'][idx]
        v = df['ground_force_pt2y'][idx]
        w = df['ground_force_pt2z'][idx]

        return x, y, z, u, v, w

#     global quiver
    quiver = ax.quiver(*get_arrow(0), arrow_length_ratio = 0.05, color=cm(norm(df['ground_force_pt2z'][0])))

    ax.set_title(f'3D Force Plot (Position: {position})')

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

    global anim
    anim = FuncAnimation(fig, update, frames = len(df), interval = 0.001, blit = False)

    plt.colorbar(sm, location = 'bottom', label = 'Force (N)')

    plt.show()

    return anim

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
        "Rate of Velocity Acceleration (m/s^3)",
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

def check_plotly_output(fig):
    """
    This function checks if the resulting figure made by Plotly is the right type.
    Arguments:
        1. fig: Figure created using Plotly
    Return:
        RaiseError if not correct type (plotly.graph_objs._figure.Figure).
    """
    # Raise Errors output is unexpected type:
    if type(fig) != go._figure.Figure:
        raise TypeError('Output figure type must be a plotly figure ' +
                         'Instead returned figure type ' +
                         str(type(fig)))
    else:
        return None

def check_matplotlib_output(fig):
    """
    This function checks if the resulting figure made by Matplotlib is the right type.
    Arguments:
        1. fig: Figure created using Matplotlib
    Return:
        RaiseError if not correct type (matplotlib.figure.Figure).
    """
    # Raise Errors output is unexpected type:
    if type(fig) !=  plt.Figure:
        raise TypeError('Output figure type must be a matplotlib figure ' +
                         'Instead returned figure type ' +
                         str(type(fig)))
    else:
        return None
