"""
process_data.py

Import processed_data datafram from preprocess.py
Return:
    1. ProcessData.py:
    An object to process all the numerical data
    Support to return indexes, lists and Calculation results
"""
# import numpy as np
import pandas as pd
from preProcess import jumpSquatPreProcess
G = 9.80665  # Constant for gravitational acceleration


# Main Function
def process_data(df):
    """
    This is the main function that calls on the ProcessData
    object with a passed dataframe containing squat jump data from
    force plates.
    Arguments:
        1. df: the data containing squat jump information.
    Return:
        1. data: dataframe of the read data (?)
        2. index: dataframe with time index of each jump start/end
            and phases.
        3. calculations: dataframe containing calculated jump metrics.
    """
    # Creating a Processed Data Object
    PD = ProcessData(df)
    # Calling functions to receieve data, indexes, and calculations
    data = PD.get_data()
    index = PD.get_index()
    calculations = PD.get_calculations()
    # Returning the three DFs
    return data, index, calculations


class ProcessData:
    """
    Class object for data processing. To be used in
    calculating jump metrics and identifying phases of
    squat jumps.
    """

    def __init__(self, df):
        """
        Initialize Variables and import data from jumpSquatPreProcess.
        Arguments:
            1. df: jump dataframe.
        """

        # Get indexes and mass from PreProcess by
        # calling on PreProcessing to retrieve index and masses
        self.data, self.index, self.mass = jumpSquatPreProcess(df)

        # Initial variables
        self.jump = 1
        # Calling an empty DF to store results
        self.cal_result: pd.DataFrame()

        # Storing indexes:
        j = self.jump - 1
        self.event_start = self.index.iat[0, 2 * j]
        self.event_end = self.index.iat[0, 2 * j + 1]
        self.ecce_start = self.index.iat[1, 2 * j]
        self.ecce_end = self.index.iat[1, 2 * j + 1]
        self.conc_start = self.index.iat[2, 2 * j]
        self.conc_end = self.index.iat[2, 2 * j + 1]
        self.landing = self.index.iat[4, 2 * j]

        # Lists for y-axis computation (1.- 10.)
        self.time_list = list(self.data['time'])
        self.l_force_list = list(self.data['ground_force1_vy'])
        self.r_force_list = list(self.data['ground_force2_vy'])
        self.force_list = list(self.data['ground_force_totaly'])

        # Will be Replaced # (?)
        self.acce_list, self.velocity_list,\
            self.displace_list = self.setup_a_c_d()

        # TODO: (Comment out when complete):
        # self.acce_list = list(self.data['body_acc'])
        # self.velocity_list = list(self.data['body_vel'])
        # self.displace_list = list(self.data['body_pos'])

        # List for COP (11.& 12.)
        self.lx_cop_list = list(self.data['ground_force1_px'])
        self.rx_cop_list = list(self.data['ground_force2_px'])
        self.lz_cop_list = list(self.data['ground_force1_pz'])
        self.rz_cop_list = list(self.data['ground_force2_pz'])

        # Generate result of squat calculations
        self.generate_df()

    # Set Function for Selecting Certain Jump:
    def set_jump(self, jump=1):
        """
        Reset indexes for the certain jumps
        """
        j = jump - 1
        self.event_start = self.index.iat[0, 2 * j]
        self.event_end = self.index.iat[0, 2 * j + 1]
        self.ecce_start = self.index.iat[1, 2 * j]
        self.ecce_end = self.index.iat[1, 2 * j + 1]
        self.conc_start = self.index.iat[2, 2 * j]
        self.conc_end = self.index.iat[2, 2 * j + 1]
        self.landing = self.index.iat[4, 2 * j]

    # Defining Functions for Returns:
    def get_data(self):
        """Return processed data"""
        return self.data

    def get_index(self):
        """Return index dataframe"""
        return self.index

    def get_calculations(self):
        """Return dataframe of squat calculations results"""
        return self.cal_result

    # Functions for Squat Calculations
    def generate_df(self):
        """
        Creating a dataframe for the 12 squat calculation results of 3 jumps:
        """
        # Creating a empty DF with columns
        df = pd.DataFrame(columns=['weight(kg)', 'jump_height(cm)',
                                   'takeoff_v(m/s)', 'rate_of_v_acce(m/s^3)',
                                   'jump_time(s)', 'ecce_time(s)',
                                   'conc_time(s)', 'peak_force(N)',
                                   'peak_power(W)',
                                   'avg_power_conc(W)',
                                   'squat_depth(cm)',
                                   'cop_displace_left_x(cm)',
                                   'cop_displace_right_x(cm)',
                                   'cop_displace_left_z(cm)',
                                   'cop_displace_right_z(cm)'],
                          index=[1, 2, 3])
        # Adding mass of patient
        df.at[1, 'weight(kg)'] = self.mass
        # Filling in dataframe with values
        for i in range(1, 4):
            self.set_jump(i)
            height, v = self.height_by_v()
            df.at[i, 'jump_height(cm)'] = height
            df.at[i, 'takeoff_v(m/s)'] = v
            df.at[i, 'rate_of_v_acce(m/s^3)'] = self.rate_of_force_ecce()
            df.at[i, 'jump_time(s)'] = (self.conc_end - self.ecce_start) / 1000
            df.at[i, 'ecce_time(s)'] = (self.ecce_end - self.ecce_start) / 1000
            df.at[i, 'conc_time(s)'] = (self.conc_end - self.conc_start) / 1000
            df.at[i, 'peak_force(N)'] = self.get_peak_force()
            df.at[i, 'peak_power(W)'] = self.get_peak_power()
            df.at[i, 'avg_power_conc(W)'] = self.avg_power_conc()
            df.at[i, 'squat_depth(cm)'] = self.get_squat_depth()
            lx, rx, lz, rz = self.get_max_cop_dis()
            df.at[i, 'cop_displace_left_x(cm)'] = lx
            df.at[i, 'cop_displace_right_x(cm)'] = rx
            df.at[i, 'cop_displace_left_z(cm)'] = lz
            df.at[i, 'cop_displace_right_z(cm)'] = rx
        # Storing results
        self.cal_result = df

    # Metric Calulcation Functions:
    def height_by_v(self):
        """
        Function: Jump height from takeoff velocity (cm)
        Returns: max_height of jump, v(0) (velocity at takeoff)
        """
        g = 9.80665
        v0, v_index = self.get_take_off_v()
        max_height = v0**2 / (2 * g) * 100
        return max_height, v0

    def get_take_off_v(self):
        """
        Function: Retrieve take off velocity
        Returns: Start index and velocity at takeoff
        """
        max_velocity = -99999
        max_index = 0
        start = self.event_start
        end = self.event_end

        # Find a peak velocity before takeoff
        for i in range(start, end):
            if self.velocity_list[i] > max_velocity:
                max_velocity = self.velocity_list[i]
                max_index = i

        # Find a constant slop after the peak
        cutoff_rate = 0.001
        v0 = self.velocity_list[max_index]
        v0_slope = self.velocity_list[max_index] - \
            self.velocity_list[max_index-1]
        start_index = max_index
        count = 0
        for j in range(max_index + 1, len(self.velocity_list)):
            v1 = self.velocity_list[j]
            v1_slope = self.velocity_list[j] - self.velocity_list[j-1]
            if abs(v1_slope - v0_slope) / abs(v1_slope) < cutoff_rate:
                if count == 0:
                    v0 = v1
                    v0_slope = v1_slope
                    start_index = j
                else:
                    pass
                count += 1
            else:
                v0 = v1
                v0_slope = v1_slope
                start_index = j
                count = 0

            if count == 100:
                break
        # Raising exception:
        if count != 100:
            raise Exception("Cannot find a constant slope")
        # Returning v0 and start index
        return v0, start_index

    def rate_of_force_ecce(self):
        """
        Function: Rate of force development during eccentric phase
        Returns: Rate of eccentric Force (df/dt)
        """
        start = self.ecce_start
        end = self.ecce_end
        dt = (end - start) / 1000
        df: float = self.acce_list[end] - self.acce_list[start]
        return df/dt

    # 3. Jump time (s)
    # 4. Eccentric phase time (s)
    # 5. Concentric phase time (s)
    def duration(self):
        """
        Function to return the duration of a jump
        """
        time = (self.conc_end - self.ecce_start) / 1000
        return time

    def get_flight_time(self):
        """
        Function to return Flight time (s)-Time when force = 0
        """
        v0, start_index = self.get_take_off_v()
        g = 9.80665
        flight_time = 2 * v0 / g
        return flight_time, start_index

    def get_zero_time(self):
        """
        Function to return time at end of jump
        """
        return (self.landing - self.conc_end)/1000, self.conc_end

    def get_peak_force(self):
        """
        Function to return Peak force for a jump
        """
        peak_force = 0.0
        for i in range(self.event_start, self.event_end):
            peak_force = max(peak_force, self.force_list[i])

        return peak_force

    def get_peak_power(self):
        """
        Function to return peak power:
            Peak power = max (force * velocity)
        """
        peak_power = 0.0
        for i in range(self.event_start, self.event_end):
            cur_power = self.force_list[i] * self.velocity_list[i]
            peak_power = max(peak_power, cur_power)

        return peak_power

    def avg_power_conc(self):
        """
        Function to return Average Power for concentric phase of
            jump.
        """
        start = self.conc_start
        end = self.conc_end
        count = start - end
        sum_power = 0.0
        for i in range(start, end):
            sum_power += self.force_list[i] * self.velocity_list[i]

        avg_power = sum_power / count
        return avg_power

    def get_squat_depth(self):
        """
        Function to return calculation for
            Counter-movement / Squat Depth
        """
        min_displace = 0.0
        for i in range(self.event_start, self.conc_end):
            min_displace = min(min_displace, self.displace_list[i])
        return abs(min_displace)*100

    def get_max_cop_dis(self):
        """
        Function to retrieve center of pressure (COP) displacement
            in the x- and z-directions during concentric phase.
        """
        # Max COP displacement in x-direction
        lx = self.max_cop_distance('l', 'x')
        rx = self.max_cop_distance('r', 'x')
        # Max COP displacement in z-direction
        lz = self.max_cop_distance('l', 'z')
        rz = self.max_cop_distance('r', 'z')
        return lx, rx, lz, rz

    def max_cop_distance(self, foot, axis):
        """
        Function to retrieve the max Center of Pressure
            distance.
        Arguments:
            1. foot: [todo]
            2. axis: [axis]
        Return:
            1. max displacement distance
        """
        if axis == 'x':
            if foot == 'l':
                cop_list = self.lx_cop_list
                origin = self.lx_cop_list[0]
            else:
                cop_list = self.rx_cop_list
                origin = self.rx_cop_list[0]
        else:
            if foot == 'l':
                cop_list = self.lz_cop_list
                origin = self.lz_cop_list[0]
            else:
                cop_list = self.rz_cop_list
                origin = self.rz_cop_list[0]

        # Find the max displacement
        start = self.conc_start
        end = self.conc_end
        max_displace = 0.0
        for i in range(start, end):
            cur_displace = cop_list[i] - origin
            if abs(cur_displace) > abs(max_displace):
                max_displace = cur_displace

        return max_displace*100

    # For temporary acc/vel/pos list
    def setup_a_c_d(self):
        idx = self.index
        first_jump = (idx.iat[0, 0], idx.iat[0, 1])
        second_jump = (idx.iat[0, 2], idx.iat[0, 3])
        third_jump = (idx.iat[0, 4], idx.iat[0, 5])
        a_list = []
        v_list = []
        d_list = []

        for i in range(0, first_jump[0]):
            a_list.append(0)
            v_list.append(0)
            d_list.append(0)
        a_list += force_to_acce(self.force_list[first_jump[0]: first_jump[1]],
                                self.mass)
        v_list += integrate(a_list[first_jump[0]: first_jump[1]])
        d_list += integrate(v_list[first_jump[0]: first_jump[1]])

        for i in range(first_jump[1], second_jump[0]):
            a_list.append(0)
            v_list.append(0)
            d_list.append(0)
        a_list += force_to_acce(self.force_list[second_jump[0]:
                                second_jump[1]], self.mass)
        v_list += integrate(a_list[second_jump[0]: second_jump[1]])
        d_list += integrate(v_list[second_jump[0]: second_jump[1]])

        for i in range(second_jump[1], third_jump[0]):
            a_list.append(0)
            v_list.append(0)
            d_list.append(0)
        a_list += force_to_acce(self.force_list[third_jump[0]: third_jump[1]],
                                self.mass)
        v_list += integrate(a_list[third_jump[0]: third_jump[1]])
        d_list += integrate(v_list[third_jump[0]: third_jump[1]])

        for i in range(third_jump[1], len(self.force_list)):
            a_list.append(0)
            v_list.append(0)
            d_list.append(0)

        return a_list, v_list, d_list


# For temporary acc/vel/pos list
def integrate(input_list, dt=0.001):
    """Integrate list of value once"""

    # Exceptions
    if not isinstance(input_list, list):
        raise Exception("input_list is not a list")
    if len(input_list) == 0:
        raise Exception("input_list is empty")

    # Function Start
    output_list = []
    output_list.append(0)

    for i in range(1, len(input_list)):
        x = (input_list[i - 1] + input_list[i]) / 2
        value = output_list[i - 1] + (x * dt)
        output_list.append(value)

    return output_list


def force_to_acce(input_list, mass):
    """ Transfer force data list to acceleration data list by given mass"""
    # Exceptions
    if not isinstance(input_list, list):
        raise Exception("input_list is not a list")
    if len(input_list) == 0:
        raise Exception("input_list is empty")
    if mass <= 0:
        raise Exception("mass is not a positive value")

    # Function Start
    output_list = []
    for i in range(len(input_list)):
        value = (input_list[i] / mass) - G
        output_list.append(value)

    return output_list
