"""
test_squat_jump_utils.py
    This file contains unittests for the file
    squat_jump_utils.py.
"""
import numpy as np
import pandas as pd
import unittest
import plotly.graph_objs as go
from squat_jump_utils import groundforce_plot, create_COP_plot, check_plotly_output


# Defining the TestCase class from unittest module
class Test_Squat_Jump_Utils(unittest.TestCase):

    def test_df_shape(self):
        """
        This function checks that the groundforce_plot &
        create_COP_plot
        functions returns errors when passed df with incorrect data
        shape.
        """
        # Initiate values (random DF with 4 columns):
        df = pd.DataFrame(np.random.randn(100, 4), columns=list('ABCD'))

        # Check for a value error:
        with self.assertRaises(ValueError):
            groundforce_plot(df, 'x')

    def test_df_cols(self):
        """
        This function checks that the groundforce_plot &
        create_COP_plot
        functions returns errors when passed df with incorrect data
        shape.
        """
        # Initiate values (random DF with 4 columns):
        df = pd.DataFrame(np.random.randn(100, 4), columns=list('ABCD'))

        # Check for a value error:
        with self.assertRaises(ValueError):
            create_COP_plot(df)

    def test_direction(self):
        """
        This function checks that the groundforce_plot
        function returns error when passed direction with incorrect values.
        """
        # Initiate values (random DF with 19 columns):
        df = pd.DataFrame(np.random.randn(100, 19))

        # Check for a value error:
        with self.assertRaises(ValueError):
            groundforce_plot(df, 'a')

    def check_plotly_output(self):
        """
        This function checks if the COP plot function
        using Plotly returns the expected type.
        """
        # read sample csv for testing
        df = pd.read_csv('/data/BFR003_squat_jump.csv')
        # error message in case if test case fails
        message = "Return object should be a Plotly figure"
        # assertIsInstance() to check if obj is instance of class
        self.assertIsInstance(create_COP_plot(df), go._figure.Figure, message)
