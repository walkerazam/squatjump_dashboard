"""
test_process_data.py
This file contains unittests for the file process_data.py.
"""
import unittest
import numpy as np
import pandas as pd
from process_data import process_data

G = 9.80665


class TestProcessData(unittest.TestCase):
    """
    Test class to check the import data and the output of process_data.py
    """

    # Smoke Test
    def test_smoke_test(self):
        """
        Smoke test for process_data.py
        """
        data = pd.read_csv("./data/BFR007_squat_jump.csv", skiprows=6)
        process_data(data)
        print('process_data runs without exceptions, smoke test passed')

    # Edge Tests
    def test_time_column_missing(self):
        """
        Edge test for import data
        Functions returns errors when passed data with missing column.
        """
        data = pd.DataFrame()
        with self.assertRaises(Exception):
            process_data(data)
        print('time column missing detected, edge test passed')

    def test_time_not_continuous(self):
        """
        Edge test for import data
        Functions returns errors when passed data with invalid time data.
        """

        # create an invalid time column
        data = pd.DataFrame({'time': [0, 0.001, 0.002, 0.005]})
        with self.assertRaises(Exception):
            process_data(data)
        print('time discontinuous detected, edge test passed')

    def test_data_size_too_small(self):
        """
        Edge test for import data
        Functions returns errors when passed data with invalid size.
        """

        # create a very small time column with valid values
        data = pd.DataFrame({'time': [0, 0.001, 0.002, 0.003]})
        with self.assertRaises(Exception):
            process_data(data)
        print('data size too small detected, edge test passed')

    def test_data_size_too_large(self):
        """
        Edge test for import data
        Functions returns errors when passed data with invalid size.
        """

        # create a very large time column with valid values
        data = pd.DataFrame()
        time_array = np.zeros(50000)
        for i in range(50000):
            time_array[i] = i/1000
        data['time'] = time_array.tolist()
        with self.assertRaises(Exception):
            process_data(data)
        print('data size too large detected, edge test passed')

    def test_force2_px_column_missing(self):
        """
        Edge test for import data
        Functions returns errors when passed data with missing column.
        """
        data = pd.read_csv("./data/BFR007_squat_jump.csv", skiprows=6)

        # drop a column from data
        data = data.drop(['ground_force2_px'], axis=1)
        with self.assertRaises(Exception):
            process_data(data)
        print('missing column detected, edge test passed')

    # One-shot Tests
    # Compare the expected results from observing the processed data plot
    def test_peak_force(self):
        """
        One-shot test for calculation result of process_data.py
        Passed if the bias rate of peak force is less than 5% tolerance
        """

        # read peak force value from process_data.py
        data = pd.read_csv("./data/BFR007_squat_jump.csv", skiprows=6)
        result = process_data(data)
        cal_result = result[2]
        peak_actual = cal_result.at[1, 'peak_force(N)']

        # compute the bias rate and check if it exceed the tolerance
        peak_expect = 2050
        tolerance = 0.05
        bias_rate = \
            abs((peak_actual - peak_expect)/(peak_actual + peak_expect))
        self.assertLess(bias_rate, tolerance)
        print('bias rate of peak force is less than 5%, test passed')

    def test_cop_displace_right_x(self):
        """
        One-shot test for calculation result of process_data.py
        Passed if the bias rate of COP displacement is less than 5% tolerance
        """
        # read COP displacement value from process_data.py
        data = pd.read_csv("./data/BFR007_squat_jump.csv", skiprows=6)
        result = process_data(data)
        cal_result = result[2]
        cop_actual = cal_result.at[1, 'cop_displace_right_x(cm)']

        # compute the bias rate and check if it exceed the tolerance
        cop_expect = 0.16 - 0.28
        tolerance = 0.05
        bias_rate = abs((cop_actual - cop_expect)/(cop_actual + cop_expect))
        self.assertLess(bias_rate, tolerance)
        print('bias rate of COP displacement is less than 5%, test passed')

    def test_cop_displace_left_z(self):
        """
        One-shot test for calculation result of process_data.py
        Passed if the bias rate of COP displacement is less than 5% tolerance
        """
        # read COP displacement value from process_data.py
        data = pd.read_csv("./data/BFR007_squat_jump.csv", skiprows=6)
        result = process_data(data)
        cal_result = result[2]
        cop_actual = cal_result.at[1, 'cop_displace_left_z(cm)']

        # compute the bias rate and check if it exceed the tolerance
        cop_expect = -0.45 - (-0.75)
        tolerance = 0.05
        bias_rate = abs((cop_actual - cop_expect)/(cop_actual + cop_expect))
        self.assertLess(bias_rate, tolerance)
        print('bias rate of COP displacement is less than 5%, test passed')

    def test_jump_time_observe(self):
        """
        One-shot test for calculation result of process_data.py
        Passed if the bias rate of jump time is less than 5% tolerance
        """
        # read jump time from index table
        data = pd.read_csv("./data/BFR007_squat_jump.csv", skiprows=6)
        result = process_data(data)
        index = result[1]
        start = index.iat[2, 1]
        end = index.iat[4, 0]
        time_actual = (end - start)/1000

        # compute the bias rate and check if it exceed the tolerance
        time_expect = 2.07 - 1.8
        tolerance = 0.05
        bias_rate = \
            abs((time_actual - time_expect)/(time_actual + time_expect))
        self.assertLess(bias_rate, tolerance)
        print('bias rate of jump time is less than 5%, test passed')

    def test_conc_time_observe(self):
        """
        One-shot test for calculation result of process_data.py
        Passed if the bias rate of concentric time is less than 5% tolerance
        """
        # read jump time from index table
        data = pd.read_csv("./data/BFR007_squat_jump.csv", skiprows=6)
        result = process_data(data)
        index = result[1]
        start = index.iat[2, 0]
        end = index.iat[2, 1]
        time_actual = (end - start)/1000

        # compute the bias rate and check if it exceed the tolerance
        time_expect = 1.81 - 1.66
        tolerance = 0.05
        bias_rate = \
            abs((time_actual - time_expect)/(time_actual + time_expect))
        self.assertLess(bias_rate, tolerance)
        print('bias rate of concentric time is less than 5%, test passed')

    def test_take_off_velocity(self):
        """
        One-shot test for calculation result of process_data.py
        Passed if the bias rate of take-off velocity is less than 5% tolerance
        """
        # read take-off velocity from index table
        data = pd.read_csv("./data/BFR007_squat_jump.csv", skiprows=6)
        result = process_data(data)
        cal_result = result[2]
        vel_actual = cal_result.at[1, 'takeoff_v(m/s)']

        # compute jump time from processed data plot
        jump_time = 2.07 - 1.8

        # compute expected take-off velocity
        vel_expect = (jump_time / 2) * G

        # compute the bias rate and check if it exceed the tolerance
        tolerance = 0.05
        print(vel_expect)
        print(vel_actual)
        bias_rate = abs((vel_actual - vel_expect)/(vel_actual + vel_expect))
        self.assertLess(bias_rate, tolerance)
        print('bias rate of take-off velocity is less than 5%, test passed')
