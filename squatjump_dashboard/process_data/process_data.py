"""
process_data.py
Import processed_data dataframe from preprocess.py and generate
    a dataframe for calculation results of each jump
Return:
    1. data - processed data from preprocess.py
    2. index - index table from preprocess.py
    3. calculations - calculation results of each jump
"""
# import numpy as np
import pandas as pd
from scipy.stats import linregress
from squatjump_dashboard.preProcess import jumpSquatPreProcess

G = 9.80665  # Constant for gravitational acceleration


# Main Function
def process_data(data):
    """
    This is the main function that calls on the ProcessData
        object with a passed dataframe containing squat jump data
        from force plates.
    Argument:
        1. data: the raw data containing squat jump information.
    Returns:
        1. data - processed data from preprocess.py
        2. index - index table from preprocess.py
        3. calculations - calculation results of each jump
    """

    # Exception for time column check
    if 'time' not in data:
        raise Exception('[time] column is missing in data')
    time_list = list(data['time'])
    data_length = len(time_list)
    for i in range(data_length):
        if time_list[i] != i / 1000:
            raise Exception('time frame is discontinuous'
                            ' or not in millisecond')

    # Exception for row number check
    if data_length < 3000:
        raise Exception('data size is less than 3000 rows')
    if data_length > 30000:
        raise Exception('data size is large than 50000 rows')

    # Exceptions for column name check
    if 'ground_force1_vx' not in data:
        raise Exception('[ground_force1_vx] column is missing in data')
    if 'ground_force1_vy' not in data:
        raise Exception('[ground_force1_vy] column is missing in data')
    if 'ground_force1_vz' not in data:
        raise Exception('[ground_force1_vz] column is missing in data')
    if 'ground_force1_px' not in data:
        raise Exception('[ground_force2_px] column is missing in data')
    if 'ground_force1_py' not in data:
        raise Exception('[ground_force2_py] column is missing in data')
    if 'ground_force1_pz' not in data:
        raise Exception('[ground_force2_pz] column is missing in data')
    if 'ground_force2_vx' not in data:
        raise Exception('[ground_force2_vx] column is missing in data')
    if 'ground_force2_vy' not in data:
        raise Exception('[ground_force2_vy] column is missing in data')
    if 'ground_force2_vz' not in data:
        raise Exception('[ground_force2_vz] column is missing in data')
    if 'ground_force2_px' not in data:
        raise Exception('[ground_force2_px] column is missing in data')
    if 'ground_force2_py' not in data:
        raise Exception('[ground_force2_py] column is missing in data')
    if 'ground_force2_pz' not in data:
        raise Exception('[ground_force2_pz] column is missing in data')

    # Creating a Processed Data Object
    processed_data = ProcessData(data)

    # Calling functions to get dataframes of processed data,
    #   indexes, and calculation results
    data = processed_data.get_data()
    index = processed_data.get_index()
    calculations = processed_data.get_calculations()

    # Returning the three DFs
    return data, index, calculations


class ProcessData:
    """
    Class object for data processing. To be used in
        calculating jump metrics and identifying
        phases of squat jumps.
    """

    def __init__(self, data):
        """
        Initialize Variables and import data from jumpSquatPreProcess.
        Argument:
            data: the raw data containing squat jump information.
        """

        # Get processed data, indexes and mass from preprocess.py
        self.data, self.index, self.mass = jumpSquatPreProcess(data)

        # Initial default jump = 1
        self.jump = 1

        # Define cal_result as a DataFrame
        self.cal_result: pd.DataFrame()

        # Extract indexes from index table
        j = self.jump - 1
        self.event_start = self.index.iat[0, 2 * j]
        self.event_end = self.index.iat[0, 2 * j + 1]
        self.ecce_start = self.index.iat[1, 2 * j]
        self.ecce_end = self.index.iat[1, 2 * j + 1]
        self.conc_start = self.index.iat[2, 2 * j]
        self.conc_end = self.index.iat[2, 2 * j + 1]
        self.landing = self.index.iat[4, 2 * j]

        # Extract Lists from processed data for y-axis computation (1.- 10.)
        self.time_list = list(self.data['time'])
        self.l_force_list = list(self.data['ground_force1_vy'])
        self.r_force_list = list(self.data['ground_force2_vy'])
        self.force_list = list(self.data['ground_force_totaly'])

        self.acce_list = list(self.data['bodyacc_y'])
        self.velocity_list = list(self.data['bodyvel_y'])
        self.displace_list = list(self.data['bodypos_y'])

        # Extract Lists from processed data Lists for COP (11.& 12.)
        self.rx_cop_list = list(self.data['ground_force1_px'])
        self.lx_cop_list = list(self.data['ground_force2_px'])
        self.rz_cop_list = list(self.data['ground_force1_pz'])
        self.lz_cop_list = list(self.data['ground_force2_pz'])

        # Generate dataframe of computed results of squat calculations
        self.generate_cal_result()

    # Set Function for Selecting a Certain Jump
    def set_jump(self, jump=1):
        """
        Reset indexes for the certain jumps
        Argument:
            jump - first, second or third jump
        """
        j = jump - 1
        self.event_start = self.index.iat[0, 2 * j]
        self.event_end = self.index.iat[0, 2 * j + 1]
        self.ecce_start = self.index.iat[1, 2 * j]
        self.ecce_end = self.index.iat[1, 2 * j + 1]
        self.conc_start = self.index.iat[2, 2 * j]
        self.conc_end = self.index.iat[2, 2 * j + 1]
        self.landing = self.index.iat[4, 2 * j]

    # Get Functions for Returns
    def get_data(self):
        """Return processed data dataframe"""
        return self.data

    def get_index(self):
        """Return index dataframe"""
        return self.index

    def get_calculations(self):
        """Return dataframe of squat calculations result"""
        return self.cal_result

    # Functions for Squat Calculations
    def generate_cal_result(self):
        """
        Creating a dataframe for the 12 squat calculation results of 3 jumps:
        """
        # Creating a empty DF with columns
        cal_result = pd.DataFrame(columns=['weight(kg)', 'jump_height(cm)',
                                           'takeoff_v(m/s)',
                                           'rate_of_v_acce(m/s^3)',
                                           'jump_time(s)', 'ecce_time(s)',
                                           'conc_time(s)', 'peak_force(N)',
                                           'peak_power(W)',
                                           'avg_power_conc(W)',
                                           'squat_depth(cm)',
                                           'cop_displace_right_x(cm)',
                                           'cop_displace_left_x(cm)',
                                           'cop_displace_right_z(cm)',
                                           'cop_displace_left_z(cm)'],
                                  index=[1, 2, 3])

        # Adding mass of patient
        cal_result.at[1, 'weight(kg)'] = self.mass

        # Filling in dataframe with values for each jump
        for i in range(1, 4):
            self.set_jump(i)
            height, vel = self.height_by_v()
            cal_result.at[i, 'jump_height(cm)'] = height
            cal_result.at[i, 'takeoff_v(m/s)'] = vel
            cal_result.at[i, 'rate_of_v_acce(m/s^3)'] \
                = self.rate_of_force_ecce()
            cal_result.at[i, 'jump_time(s)'] \
                = (self.conc_end - self.ecce_start) / 1000
            cal_result.at[i, 'ecce_time(s)'] \
                = (self.ecce_end - self.ecce_start) / 1000
            cal_result.at[i, 'conc_time(s)'] \
                = (self.conc_end - self.conc_start) / 1000
            cal_result.at[i, 'peak_force(N)'] = self.get_peak_force()
            cal_result.at[i, 'peak_power(W)'] = self.get_peak_power()
            cal_result.at[i, 'avg_power_conc(W)'] = self.avg_power_conc()
            cal_result.at[i, 'squat_depth(cm)'] = self.get_squat_depth()
            right_x, left_x, right_z, left_z = self.get_max_cop_dis()
            cal_result.at[i, 'cop_displace_right_x(cm)'] = right_x
            cal_result.at[i, 'cop_displace_left_x(cm)'] = left_x
            cal_result.at[i, 'cop_displace_right_z(cm)'] = right_z
            cal_result.at[i, 'cop_displace_left_z(cm)'] = left_z

        # Storing results
        self.cal_result = cal_result

    # Metric Calculation Functions:
    def height_by_v(self):
        """
        Function to get Jump height from takeoff velocity.
        Returns:
            1. max_height: max height of a jump (cm)
            2. vel: take-off velocity(m/s)
        """
        vel = self.get_take_off_v()
        max_height = vel ** 2 / (2 * G) * 100
        return max_height, vel

    def get_take_off_v(self):
        """
        Function to compute the take-off velocity.
        Return:
            vel: take-off velocity (m/s)
        """
        max_velocity = -99999
        max_idx = 0
        start = self.event_start
        end = self.landing

        # Find a peak velocity before takeoff
        for i in range(start, end):
            if self.velocity_list[i] > max_velocity:
                max_velocity = self.velocity_list[i]
                max_idx = i

        # Find a constant slop after the peak to find the start point
        #   where the patient is on the air
        cutoff_rate = 0.001
        vel = self.velocity_list[max_idx]
        vel_slope = self.velocity_list[max_idx]-self.velocity_list[max_idx-1]
        count = 0

        for j in range(max_idx + 1, len(self.velocity_list)):
            vel_cur = self.velocity_list[j]
            vel_cur_slope = self.velocity_list[j] - self.velocity_list[j - 1]

            # if the slope difference is less the the cutoff_rate
            # we assume that the slope is constant at this frame
            slope_diff = vel_slope - vel_cur_slope
            if abs(slope_diff) / abs(vel_cur_slope) < cutoff_rate:
                if count == 0:
                    vel = vel_cur
                    vel_slope = vel_cur_slope
                else:
                    pass
                #
                count += 1
            else:
                vel = vel_cur
                vel_slope = vel_cur_slope
                count = 0

            # If a constant slope is found, break
            if count == 100:
                break

        # if a constant sloop cannot be found, raise exception
        if count != 100:
            raise Exception("Cannot find a constant slope")
        return vel

    def rate_of_force_ecce(self):
        """
        Function to return the rate of force development during
            eccentric phase by linear regression.
        Return:
            rate_of_f: rate of force during eccentric phase (N/s)
        """
        start = self.ecce_start
        end = self.ecce_end

        # get time and force values in eccentric phase
        time = self.time_list[start: end]
        force = self.force_list[start: end]

        # apply linear regression and return its slope as ratio
        regress = linregress(time, force)
        rate_of_force = regress.slope

        return rate_of_force

    def get_peak_force(self):
        """
        Function to return Peak force for a jump.
        Return:
            peak_force(N)
        """
        peak_force = 0.0
        # find the peak force in the force_list
        for i in range(self.event_start, self.event_end):
            peak_force = max(peak_force, self.force_list[i])

        return peak_force

    def get_peak_power(self):
        """
        Function to return peak power
        Return:
            peak_power(W)
        """
        peak_power = 0.0
        # Find the max power where power = force * velocity
        for i in range(self.event_start, self.event_end):
            cur_power = self.force_list[i] * self.velocity_list[i]
            peak_power = max(peak_power, cur_power)
        return peak_power

    def avg_power_conc(self):
        """
        Function to return Average Power during concentric phase.
        Return:
            avg_power: the average power (W)
        """
        start = self.conc_start
        end = self.conc_end
        count = start - end
        sum_power = 0.0

        # Sum the power value for each frame and compute average
        for i in range(start, end):
            sum_power += self.force_list[i] * self.velocity_list[i]

        avg_power = sum_power / count
        return avg_power

    def get_squat_depth(self):
        """
        Function to return the Counter-movement / Squat Depth.
        Return:
            Squat Depth (cm)
        """
        min_displace = 0.0
        # Find the lowest position before take-off
        for i in range(self.event_start, self.conc_end):
            min_displace = min(min_displace, self.displace_list[i])
        return abs(min_displace) * 100

    def get_max_cop_dis(self):
        """
        Function to retrieve the maximum center of pressure (COP)
            displacement during concentric phase for each foot
            in the x-direction and z-directions.
        Returns:
            1. right_x: max COP displacement of right foot on X-axis(cm)
            2. left_x: max COP displacement of left foot on X-axis(cm)
            3. right_z: max COP displacement of right foot on Z-axis(cm)
            4. left_x: max COP displacement of left foot on Z-axis(cm)
        """
        # Max COP displacement in x-direction
        right_x = self.max_cop_distance('r', 'x')
        left_x = self.max_cop_distance('l', 'x')

        # Max COP displacement in z-direction
        right_z = self.max_cop_distance('r', 'z')
        left_z = self.max_cop_distance('l', 'z')

        # Return the four results
        return right_x, left_x, right_z, left_z

    def max_cop_distance(self, foot, axis):
        """
        Function to retrieve the max Center of Pressure
            displacement for a certain foot and axis
        Arguments:
            1. foot: left foot or right foot
            2. axis: X-axis or Z-axis
        Return:
            max displacement distance (cm)
        """

        # Identify for the four different cases
        if axis == 'x':
            if foot == 'r':
                cop_list = self.rx_cop_list
                origin = self.rx_cop_list[self.conc_start]
            else:
                cop_list = self.lx_cop_list
                origin = self.lx_cop_list[self.conc_start]
        else:
            if foot == 'r':
                cop_list = self.rz_cop_list
                origin = self.rz_cop_list[self.conc_start]
            else:
                cop_list = self.lz_cop_list
                origin = self.lz_cop_list[self.conc_start]

        # Find the max absolute displacement
        start = self.conc_start
        end = self.conc_end
        max_displace = 0.0
        for i in range(start, end):
            cur_displace = cop_list[i] - origin
            if abs(cur_displace) > abs(max_displace):
                max_displace = cur_displace

        return max_displace
