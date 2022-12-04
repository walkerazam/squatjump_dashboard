import pandas as pd
import numpy as np
# from scipy import integrate
from scipy.signal import butter, filtfilt


def jumpSquatPreProcess(data):
    '''
    This function takes in a passed dataframe of patient jumps
    and does pre-processing/cleaning required to calculate jump
    metrics. It returns the cleaned data, along with indexes
    for time (s) per jump phase, and the patient's mass.

    Arguments:
        1. data: the squatjump dataframe containing jump data
    Returns:
        1. preProcessedData: pre-processed/cleaned dataframe
        2. index_pd: jump indexes
        3. weight: patient mass/weight
    '''
    # Drop unused columns
    data = data.drop(['ground_force1_py',
                      'ground_torque1_x',
                      'ground_torque1_y',
                      'ground_torque1_z',
                      'ground_force2_py',
                      'ground_torque2_x',
                      'ground_torque2_y',
                      'ground_torque2_z'], axis=1)

    # Filter Data Using Butter
    def butter_lowpass_filter(data, cutoff, fs, order):
        '''
        Butter
        '''
        nyq = 0.5 * fs
        normal_cutoff = cutoff / nyq
        # Get the filter coefficients 
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        y = filtfilt(b, a, data)
        return y

    for col_name in data.columns:
        if '_v' in col_name:
            data[col_name] = butter_lowpass_filter(data[col_name], 5, 1000, 4)
        else:
            pass

    # Add Total Vertical Force Columns
    data['ground_force_totaly'] = data['ground_force1_vy'] + \
        data['ground_force2_vy']

    # Find where subject is in air
    threshold = 10

    pass_val = 0

    while pass_val == 0:
        in_air_bool = data['ground_force_totaly'] < threshold
        start_in_air = []
        end_in_air = []
        for n in range(len(in_air_bool)-1):
            if in_air_bool[n] == False and in_air_bool[n + 1] == True:
                start_in_air.append(n+1)
            elif in_air_bool[n] == True and in_air_bool[n + 1] == False:
                end_in_air.append(n)
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
        contact_4 = [end_in_air[2], data.shape[0] - 1]
        off_force_plate = 0

    # 8 replace in air time with zeros
    for in_air in [[contact_1[1]+1, contact_2[0]-1], [contact_2[1]+1,
                   contact_3[0]-1], [contact_3[1]+1, contact_4[0]-1]]:
        data['ground_force1_vy'][in_air[0]:in_air[1]] = 0.0
        data['ground_force2_vy'][in_air[0]:in_air[1]] = 0.0
        data['ground_force_totaly'][in_air[0]:in_air[1]] = 0.0

    # Add relative ground angles
    xz1 = data['ground_force1_vx'] ** 2 + data['ground_force1_vz'] ** 2
    xz2 = data['ground_force2_vx'] ** 2 + data['ground_force2_vz'] ** 2
    ground_force1_angle = []
    ground_force2_angle = []
    for n in range(len(data['time'])):
        ground_force1_angle.append(
            (
                np.arctan(data['ground_force1_vy'][n] / np.sqrt(xz1[n]))
                ) * 180/np.pi
            )
        ground_force2_angle.append(
            (
                np.arctan(data['ground_force2_vy'][n] / np.sqrt(xz2[n]))
                ) * 180/np.pi
            )

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
                data['ground_force_totaly'][n + 1] - data['ground_force_totaly'][n]
                )/dt
            )
    force_prime.append(force_prime[-1])

    force_prime = pd.DataFrame(force_prime, columns=['force_prime'])

    # Find Subject Weight
    # Weight_bool-array of boolean where subject is mostly static and not
    # in the air
    weight_bool = []
    for num in range(len(data)):
        if abs(force_prime['force_prime'][num]) < 200 and in_air_bool[num] == False:
            weight_bool.append(True)
        else:
            weight_bool.append(False)

    # Start and end_static find transitions from true to false or false to true
    start_static = []
    end_static = []

    for num in range(len(weight_bool)-1):
        if weight_bool[num] == False and weight_bool[num + 1] == True:
            start_static.append(num)
        elif weight_bool[num] == True and weight_bool[num + 1] == False:
            end_static.append(num)
        else:
            pass

    # Static period function finds largest static period's indexes
    # in a given range
    def findStaticPeriod(start_vals, end_vals):
        '''
        function
        '''
        static_period = []
        if start_vals[0] > end_vals[0]:
            for num in range(len(end_vals)-1):
                static_period.append(end_vals[num + 1]-start_vals[num])
            max_index = static_period.index(max(static_period))
            start_index = start_vals[max_index]
            end_index = end_vals[max_index + 1]
        else:
            for num in range(len(end_vals)):
                static_period.append(end_vals[num] - start_vals[num])
            max_index = static_period.index(max(static_period))
            start_index = start_vals[max_index]
            end_index = end_vals[max_index]

        return start_index, end_index

    weight_start_index, weight_end_index = findStaticPeriod(start_static, end_static)


    weight = data['ground_force_totaly'][weight_start_index:weight_end_index].mean()/9.81

    # Find static periods in second, third contact
    # and fourth contact (if needed)
    start_index_c234 = []
    end_index_c234 = []
    for contact in [contact_2, contact_3, contact_4]:
        filtered_start_static = filter(lambda index: contact[1] >= index >= contact[0],start_static)
        filtered_start_static = list(filtered_start_static)

        filtered_end_static = filter(lambda index: contact[1] >= index >= contact[0],end_static)
        filtered_end_static = list(filtered_end_static)

        contact_start_index, contact_end_index = findStaticPeriod(filtered_start_static, filtered_end_static)
        start_index_c234.append(contact_start_index)
        end_index_c234.append(contact_end_index)

    c2_cutoff = (start_index_c234[0] + end_index_c234[0]) // 2
    c3_cutoff = (start_index_c234[1] + end_index_c234[1]) // 2
    if off_force_plate == 1:
        c4_cutoff = (start_index_c234[2] + end_index_c234[2]) // 2
    else:
        c4_cutoff = contact_4[1]

    # Solve for 1st event start , start & stop of eccentric,
    # start & stop of concentric
    contact_1_prime_bool = force_prime['force_prime'][contact_1[0]:contact_1[1]] < -200

    ecc_pk1 = data['ground_force_totaly'][contact_1[0]:contact_1[1]].max()
    ecc_pk1_ind = data[data['ground_force_totaly'] == ecc_pk1].index.values
    con1_s = ecc_pk1_ind[0]

    ecc_start1 = data['ground_force_totaly'][contact_1[0]:con1_s].min()
    ecc_start1_ind = data[data['ground_force_totaly'] == ecc_start1].index.values
    ecc1_s = ecc_start1_ind[0]

    c1f2t = []
    for n in range(contact_1[0],ecc1_s-10):
        if contact_1_prime_bool[n] == True and n == 0:
            c1f2t.append(n)
        elif contact_1_prime_bool[n] == False and contact_1_prime_bool[n + 1] == True:
            c1f2t.append(n)
        else:
            pass

    evt1_s = c1f2t[0]

    # Solve for 1st event stop, landing start stop, 2nd event start,
    # start & stop of eccentric, start & stop of concentric
    contact_2_prime_bool = force_prime['force_prime'][contact_2[0]:contact_2[1]] < -200

    ecc_pk2 = data['ground_force_totaly'][c2_cutoff:contact_2[1]].max()
    ecc_pk2_ind = data[data['ground_force_totaly'] == ecc_pk2].index.values
    con2_s = ecc_pk2_ind[0]

    ecc_start2 = data['ground_force_totaly'][c2_cutoff:con2_s].min()
    ecc_start2_ind = data[data['ground_force_totaly'] == ecc_start2].index.values
    ecc2_s = ecc_start2_ind[0]

    c2t2f_land = []
    c2f2t = []
    for n in range(contact_2[0],con2_s-10):
        if contact_2_prime_bool[n] == True and contact_2_prime_bool[n + 1] == False and n < c2_cutoff:
            c2t2f_land.append(n)
        elif contact_2_prime_bool[n] == False and contact_2_prime_bool[n + 1] == True and n > c2_cutoff:
            c2f2t.append(n)
        else:
            pass

    for nn in range(c2t2f_land[-1] + 100, c2_cutoff):
        if abs(force_prime['force_prime'][nn]) < 1:
            break
        else:
            pass

    evt1_e = nn
    evt2_s = c2f2t[0]


    # Solve for 2nd event stop, landing start stop,
    # 3rd event start, start & stop of eccentric, start & stop of concentric
    contact_3_prime_bool = force_prime['force_prime'][contact_3[0]:contact_3[1]] < -200

    ecc_pk3 = data['ground_force_totaly'][c3_cutoff:contact_3[1]].max()
    ecc_pk3_ind = data[data['ground_force_totaly'] == ecc_pk3].index.values
    con3_s = ecc_pk3_ind[0]

    ecc_start3 = data['ground_force_totaly'][c3_cutoff:con3_s].min()
    ecc_start3_ind = data[data['ground_force_totaly'] == ecc_start3].index.values
    ecc3_s = ecc_start3_ind[0]

    c3t2f_land = []
    c3f2t = []
    for n in range(contact_3[0],con3_s-10):
        if contact_3_prime_bool[n] == True and contact_3_prime_bool[n + 1] == False and n < c3_cutoff:
            c3t2f_land.append(n)
        elif contact_3_prime_bool[n] == False and contact_3_prime_bool[n + 1] == True and n > c3_cutoff:
            c3f2t.append(n)
        else:
            pass

    for nn in range(c3t2f_land[-1] + 100, c3_cutoff):
        if abs(force_prime['force_prime'][nn]) < 1:
            break
        else:
            pass

    evt2_e = nn
    evt3_s = c3f2t[0]

    # Solve for 3rd event stop, landing start stop
    contact_4_prime_bool = force_prime['force_prime'][contact_4[0]:c4_cutoff] < -200

    c4t2f = []

    for n in range(contact_4[0] + 100, c4_cutoff):
        if contact_4_prime_bool[n] == True and contact_4_prime_bool[n + 1] == False:
            c4t2f.append(n)
        else:
            pass

    evt3_e = c4t2f[-1]

    # Integrate
    data = data[0:c4_cutoff]

    index_pd = {'Jump 1 Start': [evt1_s, ecc1_s, con1_s, ecc1_s, contact_2[0]],
                'Jump 1 End': [evt1_e, con1_s, contact_1[1],
                               contact_1[1], evt1_e],
                'Jump 2 Start': [evt2_s, ecc2_s, con2_s, ecc2_s, contact_3[0]],
                'Jump 2 End': [evt2_e, con2_s, contact_2[1],
                               contact_2[1], evt2_e],
                'Jump 3 Start': [evt3_s, ecc3_s, con3_s, ecc3_s, contact_4[0]],
                'Jump 3 End': [evt3_e, con3_s, contact_3[1],
                               contact_3[1], evt3_e]}
    index_pd = pd.DataFrame(index_pd, index=['Event',
                                             'Eccentric Phase',
                                             'Concentric Phase',
                                             'Jump Phase',
                                             'Landing Phase'])

    preProcessedData = data

    return preProcessedData, index_pd, weight
