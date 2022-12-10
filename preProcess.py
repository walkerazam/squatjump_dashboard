"""
preProcess.py
Pre-processes data selected by user on streamlit dash.
Returns:
    1. preProcessedData: pre-processed/cleaned dataframe (df)
    2. index_pd: indexes for every jump and their phases (df)
    3. weight: patient mass/weight (float)

"""
import numpy as np
import pandas as pd
from scipy import integrate
from scipy.signal import butter, filtfilt


def jumpSquatPreProcess(data):
    """
    This is the main function that takes in a passed dataframe of patient jumps
    and does pre-processing/cleaning required to calculate jump
    metrics. It returns the cleaned data, along with indexes
    for time (s) per jump phase, and the patient's mass.

    Arguments:
        1. data (df): the raw squat jump dataframe containing jump data
    Returns:
        1. preProcessedData (df): pre-processed/cleaned dataframe
        2. index_pd (df): indexes for every jump and their phases
        3. weight (float): patient mass/weight
    """
    # Check # of columns
    if data.shape[1] != 19:
        raise ValueError("Squat jump CSV file has incorrect number of columns")
    else:
        pass

    # Check column names:
    if 'ground_force1_vx' not in data.columns:
        raise Exception("ground_force1_vx not found")
    if 'ground_force1_vy' not in data.columns:
        raise Exception("ground_force1_vy not found")
    if 'ground_force1_vz' not in data.columns:
        raise Exception("ground_force1_vz not found")
    if 'ground_force2_vx' not in data.columns:
        raise Exception("ground_force2_vx not found")
    if 'ground_force2_vy' not in data.columns:
        raise Exception("ground_force2_vy not found")
    if 'ground_force2_vz' not in data.columns:
        raise Exception("ground_force2_vz not found")
    if 'ground_force1_px' not in data.columns:
        raise Exception("ground_force1_px not found")
    if 'ground_force1_pz' not in data.columns:
        raise Exception("ground_force1_pz not found")
    if 'ground_force2_px' not in data.columns:
        raise Exception("ground_force2_px not found")
    if 'ground_force2_pz' not in data.columns:
        raise Exception("ground_force2_pz not found")

    # Check time is continous
    for ii in range(data.shape[0]-1):
        diff = data['time'][ii+1] - data['time'][ii]
        if np.isclose(diff, 0.001):
            pass
        else:
            raise ValueError("Time series in data not correct. Check to make "
                             "sure data is at 1000 Hz and continous.")

    # Drop unused columns
    data = data.drop(['ground_force1_py',
                      'ground_torque1_x',
                      'ground_torque1_y',
                      'ground_torque1_z',
                      'ground_force2_py',
                      'ground_torque2_x',
                      'ground_torque2_y',
                      'ground_torque2_z'], axis=1)

    # Clean data and add new columns
    # Filter Data Using Butter
    for col_name in data.columns:
        if '_v' in col_name:
            data[col_name] = butter_filter(data[col_name], 5, 1000, 4)
        else:
            pass

    # Add Total Vertical Force Columns
    data['ground_force_totaly'] = data['ground_force1_vy'] + \
        data['ground_force2_vy']

    # Find four contact ranges + if subject steps off the force plate
    c1, c2, c3, c4, off_fp = contact_finder(data['ground_force_totaly'])

    # Replace in air time with zeros
    for in_air in [[c1[1]+1, c2[0]-1], [c2[1]+1,
                   c3[0]-1], [c3[1]+1, c4[0]-1]]:
        data['ground_force1_vy'][in_air[0]:in_air[1]] = 0.0
        data['ground_force2_vy'][in_air[0]:in_air[1]] = 0.0
        data['ground_force_totaly'][in_air[0]:in_air[1]] = 0.0

    # Find ground angles
    ground_force1_angle = find_ground_angle(data['ground_force1_vx'],
                                            data['ground_force1_vy'],
                                            data['ground_force1_vz'])

    ground_force2_angle = find_ground_angle(data['ground_force2_vx'],
                                            data['ground_force2_vy'],
                                            data['ground_force2_vz'])
    data['ground_force1_angle'] = ground_force1_angle
    data['ground_force2_angle'] = ground_force2_angle
    data['ground_force1_angle'] = data['ground_force1_angle'].fillna(0)
    data['ground_force2_angle'] = data['ground_force2_angle'].fillna(0)

    # Derive Vertical Force
    dt = data['time'][1] - data['time'][0]
    force_prime = []
    for n in range(len(data['ground_force_totaly'])-1):
        force_prime.append(
            (
                data['ground_force_totaly'][n + 1] -
                data['ground_force_totaly'][n]
                )/dt
            )
    force_prime.append(force_prime[-1])
    force_prime = pd.DataFrame(force_prime, columns=['force_prime'])

    # Find start and end point of all static periods
    start_index, end_index = find_static_indexes(force_prime, c1, c2, c3, c4)

    # Find largest static periods for all contacts
    start_index_contact = []
    end_index_contact = []
    for contact in [c1, c2, c3, c4]:
        filtered_start_static = filter(lambda idx:
                                       contact[1] >= idx >= contact[0],
                                       start_index)
        filtered_start_static = list(filtered_start_static)

        filtered_end_static = filter(lambda idx:
                                     contact[1] >= idx >= contact[0],
                                     end_index)
        filtered_end_static = list(filtered_end_static)

        contact_start_index, contact_end_index = find_static_period(
            filtered_start_static, filtered_end_static)
        start_index_contact.append(contact_start_index)
        end_index_contact.append(contact_end_index)

    # Find weight using largest static period:
    static_diff = []
    for ii in range(len(start_index_contact)):
        static_diff.append(end_index_contact[ii] - start_index_contact[ii])
    max_diff_index = static_diff.index(max(static_diff))
    start_index_weight = start_index_contact[max_diff_index]
    end_index_weight = end_index_contact[max_diff_index]

    weight = (data['ground_force_totaly']
              [start_index_weight:end_index_weight].mean())/9.81

    # Create cutoffs for contact 2,3, and 4 to help identifcation
    c2_cutoff = (start_index_contact[1] + end_index_contact[1]) // 2
    c3_cutoff = (start_index_contact[2] + end_index_contact[2]) // 2
    if off_fp == 1:
        c4_cutoff = (start_index_contact[3] + end_index_contact[3]) // 2
    else:
        c4_cutoff = c4[1]

    # Identify start and stop of event and phases in each contact:
    # evt = event, ecc = eccentric phase, con = concentric phase
    # = jump number, s/e = start/stop
    contact_list = [c1, c2, c3, c4]
    cutoffs = [0, c2_cutoff, c3_cutoff, c4_cutoff]
    for contact in range(len(contact_list)):
        contact_events = contact_event_finder(data['ground_force_totaly'],
                                              force_prime['force_prime'],
                                              contact + 1,
                                              contact_list[contact],
                                              cutoffs[contact])
        if contact == 0:
            evt1_s = contact_events[0]
            ecc1_s = contact_events[1]
            con1_s = contact_events[2]
        elif contact == 1:
            evt1_e = contact_events[0]
            evt2_s = contact_events[1]
            ecc2_s = contact_events[2]
            con2_s = contact_events[3]
        elif contact == 2:
            evt2_e = contact_events[0]
            evt3_s = contact_events[1]
            ecc3_s = contact_events[2]
            con3_s = contact_events[3]
        elif contact == 3:
            evt3_e = contact_events
        else:
            pass

    # Derive Acceleration, velocity and position by segment
    data['bodyacc_y'] = (data['ground_force_totaly']/weight) - 9.81

    if c1[0] == evt1_s:
        index_list = [evt1_s, evt1_e, evt2_s, evt2_e, evt3_s, evt3_e,
                      c4_cutoff]
    else:
        index_list = [c1[0], evt1_s, evt1_e, evt2_s, evt2_e,
                      evt3_s, evt3_e, c4_cutoff]

    velocity = []
    position = []
    for ii in range(len(index_list)-1):
        acc_segment = data['bodyacc_y'][index_list[ii]:index_list[ii+1]]
        vel_segment = integrate.cumtrapz(acc_segment, dx=dt, initial=0)
        pos_segment = integrate.cumtrapz(vel_segment, dx=dt, initial=0)
        if ii == 0:
            velocity = vel_segment
            position = pos_segment
        else:
            velocity = np.append(velocity, vel_segment)
            position = np.append(position, pos_segment)

    data = data[0:c4_cutoff]
    data['bodyvel_y'] = velocity
    data['bodypos_y'] = position

    # create df for all event index values
    index_pd = {'Jump 1 Start': [evt1_s, ecc1_s, con1_s, ecc1_s, c2[0]],
                'Jump 1 End': [evt1_e, con1_s, c1[1],
                               c1[1], evt1_e],
                'Jump 2 Start': [evt2_s, ecc2_s, con2_s, ecc2_s, c3[0]],
                'Jump 2 End': [evt2_e, con2_s, c2[1],
                               c2[1], evt2_e],
                'Jump 3 Start': [evt3_s, ecc3_s, con3_s, ecc3_s, c4[0]],
                'Jump 3 End': [evt3_e, con3_s, c3[1],
                               c3[1], evt3_e]}
    index_pd = pd.DataFrame(index_pd, index=['Event',
                                             'Eccentric Phase',
                                             'Concentric Phase',
                                             'Jump Phase',
                                             'Landing Phase'])

    # Return
    preProcessedData = data
    return preProcessedData, index_pd, weight


def butter_filter(column, cutoff, fs, order):
    """
    This function filters data using a lowpass butter filter

    Arguments:
        1. column: column from main dataframe
        2. cutoff: Freq for filtered values (int)
        3. fs: Freq of the orginal/raw data column (int)
        4. order: magnitude of filter used (int)
    Returns:
        1. filtered_column: column with butter filter applied
    """
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq

    # butter function from scipy creates butter filter
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    # filtfilt function from scipy applies butter
    filtered_column = filtfilt(b, a, column)
    return filtered_column


def contact_finder(force):
    """
    This function finds the index ranges for when the subject
    is in contact with the ground. For this purpose, subjects must
    jump three times so this function will return four ranges of contact.
    Also, if the subject steps off the force plate, this function return a
    1 (True) or 0 (False) to indicate for other functions.

    Argument:
        1. force: column of force values from dataframe (df)
    Returns:
        1-4. contact_1 through contact_4: 4 list of contacts with a start
        and end index value for each (list)
        5. off_force_plate: value of 1 (True) or 0 (False) if subject stepped
        off force plate at the end (int)
    """
    threshold = 10

    pass_val = 0

    while pass_val == 0:
        if threshold > 100:
            raise RuntimeError("Code unable to detect when subject is in air "
                               "properly")
        else:
            in_air_bool = force < threshold
            start_in_air = []
            end_in_air = []
            for ii in range(len(in_air_bool)-1):
                if in_air_bool[ii] == False and \
                        in_air_bool[ii+1] == True:
                    start_in_air.append(ii+1)
                elif in_air_bool[ii] == True and \
                        in_air_bool[ii + 1] == False:
                    end_in_air.append(ii)
                else:
                    pass

            if (len(start_in_air) == 4 or len(start_in_air) == 3) and \
                    len(end_in_air) == 3:
                pass_val = 1
            else:
                threshold += 5

    contact_1 = [0, start_in_air[0]]
    contact_2 = [end_in_air[0], start_in_air[1]]
    contact_3 = [end_in_air[1], start_in_air[2]]
    if len(start_in_air) == 4:
        contact_4 = [end_in_air[2], start_in_air[3]]
        off_force_plate = 1
    else:
        contact_4 = [end_in_air[2], force.shape[0] - 1]
        off_force_plate = 0

    return contact_1, contact_2, contact_3, contact_4, off_force_plate


def find_ground_angle(force_x, force_y, force_z):
    """
    This function finds the relative angle of each leg to the ground.

    Arguments:
        1. force_x: column of force data in x direction (df)
        2. force_y: column of force data in y direction/vertical (df)
        3. force_z: column of force data in z direction (df)
    Returns:
        1. ground_angle: list of ground angle values (list of floats)
    """
    xz = force_x ** 2 + force_z ** 2
    ground_angle = []
    for ii in range(len(force_x)):
        ground_angle.append(
            (
                np.arctan(force_y[ii] / np.sqrt(xz[ii]))
                ) * 180/np.pi
            )
    return ground_angle


def find_static_indexes(force_prime, contact_1, contact_2,
                        contact_3, contact_4):
    """
    This function finds periods of time where subject is static/still.
    Static is defined by the the absolute value of the derivative of
    force is less than 200.

    Arguements:
        1. force_prime: column of the derivative of force (df)
        2-5. contact_1-4: list of start and stop for each contact (list
        of int)
    Returns:
        1. static_start: list of indexes where static periods start (list
        of int)
        2. end_static: list of indexes where static periods end (list
        of int)
    """
    static_bool = []
    for ii in range(len(force_prime)):
        if ii < contact_2[0]:
            is_static = contact_1[1]
        elif contact_2[0] <= ii < contact_3[0]:
            is_static = contact_2[1]
        elif contact_3[0] <= ii < contact_4[0]:
            is_static = contact_3[1]
        else:
            is_static = contact_4[1]

        if abs(force_prime.iloc[ii][0]) < 200 and ii < is_static:
            static_bool.append(True)
        else:
            static_bool.append(False)

    start_static = []
    end_static = []
    for ii in range(len(static_bool)-1):
        if static_bool[ii] == False and \
                static_bool[ii + 1] == True:
            start_static.append(ii)
        elif static_bool[ii] == True and \
                static_bool[ii + 1] == False:
            end_static.append(ii)
        else:
            pass

    return start_static, end_static


def find_static_period(start_vals, end_vals):
    """
    This function finds the largest period where subject is static.

    Arguments:
        1. start_vals: List of indexes where subject transitions from
        moving to static
        2. end_vals: List of indexes where subject transitions from static
        to moving
    Returns:
        1. start_index: index where the largest static period starts (int)
        2. end_index: index where the largest static period ends
    """
    static_period = []
    if start_vals[0] > end_vals[0]:
        for ii in range(len(end_vals)-1):
            static_period.append(end_vals[ii + 1]-start_vals[ii])
        max_index = static_period.index(max(static_period))
        start_index = start_vals[max_index]
        end_index = end_vals[max_index + 1]
    else:
        for ii in range(len(end_vals)):
            static_period.append(end_vals[ii] - start_vals[ii])
        max_index = static_period.index(max(static_period))
        start_index = start_vals[max_index]
        end_index = end_vals[max_index]

    return start_index, end_index


def contact_event_finder(force, force_prime, contact_number,
                         contact_index_range, cutoff):
    """
    This functions finds the start and stop indexes for following:
    event/total jump, eccentric phase, and concentric phase.

    Arguments:
        1. force: column of force data from dataframe (df)
        2. force_prime: column of the derivative of force (df)
        3. contact_number: which contact number it is (from 1-4) (int)
        4. contact_index_range: list of start and stop index of the
        contact (list w/ int)
        5. cutoff: index to split contact into two sections in order to
        find end point of the first section and starts on the seconds (int)

    Returns:
        1. event_start: index of when the total jump starts (returned
        for all contacts except last contact) (int)
        2. eccentric_start: index of start of eccentric phase (returned
        for all contacts except last contact) (int)
        3. concentric_start: index of start of concetric phase/end of
        eccentric phase (returned for all contacts except for last
        contact) (int)
        4. event_end: index of when the total jump ends (returned for all
        contacts except first contact) (int)
    """
    start = contact_index_range[0]
    end = contact_index_range[1]
    force_unloading = force_prime < -200

    if contact_number == 1:
        eccentric_pk = force[start:end].max()
        concentric_start = force[force == eccentric_pk].index[0]

        eccentric_min = force[start:concentric_start].min()
        eccentric_start = force[force == eccentric_min].index[0]

        find_event_start = []
        for ii in range(start, eccentric_start-10):
            if force_unloading[ii] == True and ii == 0:
                find_event_start.append(ii)
            elif force_unloading[ii] == False and \
                    force_unloading[ii+1] == True:
                find_event_start.append(ii)
            else:
                pass

        event_start = find_event_start[0]

        return event_start, eccentric_start, concentric_start

    elif contact_number == 2 or contact_number == 3:
        eccentric_pk = force[cutoff:end].max()
        concentric_start = force[force == eccentric_pk].index[0]

        eccentric_min = force[cutoff:concentric_start].min()
        eccentric_start = force[force == eccentric_min].index[0]

        find_event_end = []
        find_event_start = []
        for ii in range(start, eccentric_start - 10):
            if force_unloading[ii] == True and \
                    force_unloading[ii + 1] == False \
                    and ii < cutoff:
                find_event_end.append(ii)
            elif force_unloading[ii] == False and \
                    force_unloading[ii+1] == True \
                    and ii > cutoff:
                find_event_start.append(ii)
            else:
                pass

        event_end = 0
        for ii in range(find_event_end[-1] + 100, cutoff):
            if abs(force_prime[ii]) < 1:
                event_end = ii
                break
            else:
                pass
        if event_end == 0:
            raise ValueError("Code could not identify end of jump correctly. "
                             "Check contact %f" % int(contact_number))

        event_start = find_event_start[0]

        return event_end, event_start, eccentric_start, concentric_start

    elif contact_number == 4:
        find_event_end = []
        for ii in range(start+100, cutoff):
            if force_unloading[ii] == True and \
                    force_unloading[ii+1] == False:
                find_event_end.append(ii)
            else:
                pass

        event_end = find_event_end[-1]

        return event_end
