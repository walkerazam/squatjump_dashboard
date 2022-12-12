"""
test_preProcess.py
This file contains unittests for preProcess
"""

import os
import unittest

import pandas as pd

from squatjump_dashboard.preProcess import jumpSquatPreProcess
#
main_path = os.path.dirname(__file__)
data_path1 = os.path.join(main_path, "../../data/BFR007_squat_jump.csv")
data_path2 = os.path.join(main_path, "../../data/squat_jump_error_test.csv")
test_df1 = pd.read_csv(data_path1, header=6)
preProcessedData, index_pd, weight = jumpSquatPreProcess(test_df1)


class TestpreProcess(unittest.TestCase):
    def test_smoke(self):
        """
        Makes sure preProcess runs
        """
        test_df2 = pd.read_csv(data_path1, header=6)
        jumpSquatPreProcess(test_df2)
        return

    def test_col_number(self):
        """
        Throws ValueError for incorrect number of columns
        """
        test_df3 = pd.read_csv(data_path1, header=6)
        test_df3 = test_df3.drop(['time'], axis=1)
        with self.assertRaises(ValueError):
            jumpSquatPreProcess(test_df3)

    def test_check_col_name(self):
        """
        Throws exception for incorrect column name
        """
        test_df4 = pd.read_csv(data_path1, header=6)
        test_df4 = test_df4.rename(
                            columns={'ground_force1_vx': 'ground_force1_vb'},
                            inplace=True)
        with self.assertRaises(Exception):
            jumpSquatPreProcess(test_df4)

    def test_time(self):
        """
        Throws ValueError for if data is not collected at 1000 Hz
        """
        test_df5 = pd.read_csv(data_path1, header=6)
        new_time = []
        for ii in range(len(test_df5)):
            new_time.append(ii)
        test_df5['time'] = new_time
        with self.assertRaises(ValueError):
            jumpSquatPreProcess(test_df5)

    def test_number_jumps(self):
        """
        Throws RuntimeError if data does not contain three jumps
        """
        test_df6 = pd.read_csv(data_path1, header=6)
        test_df6['ground_force1_vy'] = 120
        test_df6['ground_force2_vy'] = 120
        with self.assertRaises(RuntimeError):
            jumpSquatPreProcess(test_df6)

    def test_unidentified_end(self):
        """
        Throws ValueError if a timestamp for the end of a jump cannot be found
        """
        test_df7 = pd.read_csv(data_path2, header=6)
        with self.assertRaises(ValueError):
            jumpSquatPreProcess(test_df7)

    def test_check_indexes(self):
        """
        Checks if start and end indexes are in the correct order
        """
        index_order = [index_pd['Jump 1 Start'][0],
                       index_pd['Jump 1 Start'][1],
                       index_pd['Jump 1 Start'][2],
                       index_pd['Jump 1 Start'][4],
                       index_pd['Jump 1 End'][0],
                       index_pd['Jump 2 Start'][0],
                       index_pd['Jump 2 Start'][1],
                       index_pd['Jump 2 Start'][2],
                       index_pd['Jump 2 Start'][4],
                       index_pd['Jump 2 End'][0],
                       index_pd['Jump 3 Start'][0],
                       index_pd['Jump 3 Start'][1],
                       index_pd['Jump 3 Start'][2],
                       index_pd['Jump 3 Start'][4],
                       index_pd['Jump 3 End'][0]]

        for index in range(len(index_order)-1):
            self.assertLess(index_order[index], index_order[index+1])

    def test_check_weight(self):
        """
        Checks weight is correct
        """
        self.assertAlmostEqual(weight, 89, places=0)

    def test_check_peak_forces(self):
        """
        Checks jump segments are correct by matching peaks for
        specific jumps
        """
        for ii in range(1, 4):
            col_string_start = 'Jump ' + str(ii) + ' Start'
            col_string_end = 'Jump ' + str(ii) + ' End'
            start = index_pd[col_string_start][0]
            end = index_pd[col_string_end][0]
            max_force = (preProcessedData['ground_force_totaly']
                                         [start:end].max())

            if ii == 1:
                self.assertAlmostEqual(max_force, 2048, places=-1)
            elif ii == 2:
                self.assertAlmostEqual(max_force, 1921, places=-1)
            else:
                self.assertAlmostEqual(max_force, 1936, places=-1)

    def test_check_min_eccentric(self):
        """
        Checks jump segments are correct by matching eccentric mins for
        specific jumps
        """
        for ii in range(1, 4):
            col_string_start = 'Jump ' + str(ii) + ' Start'
            col_string_end = 'Jump ' + str(ii) + ' End'
            start = index_pd[col_string_start][0]
            end = index_pd[col_string_end][2]
            min_force = (preProcessedData['ground_force_totaly']
                                         [start:end].min())

            if ii == 1:
                self.assertAlmostEqual(min_force, 68.29, places=1)
            elif ii == 2:
                self.assertAlmostEqual(min_force, 65.5, places=1)
            else:
                self.assertAlmostEqual(min_force, 65.84, places=1)
