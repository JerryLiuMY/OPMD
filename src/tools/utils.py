from datetime import datetime
import os
import numpy as np
import pandas as pd


def build(**kwargs):
    dictionary = {}
    df = pd.DataFrame()
    if 'measured_power_trials' in kwargs:
        measured_power_trials = np.array(kwargs['measured_power_trials'])
        dictionary['measured_power_trials'] = measured_power_trials
        df['Measured_Power'] = measured_power_trials

    if 'ambient_power_trials' in kwargs:
        ambient_power_trials = np.array(kwargs['ambient_power_trials'])
        dictionary['ambient_power_trials'] = ambient_power_trials
        df['Ambient_Power'] = ambient_power_trials

    if 'central_wl_trials' in kwargs:
        central_wl_trials = np.array(kwargs['central_wl_trials'])
        dictionary['central_wl_trials'] = central_wl_trials
        df['Central_WL'] = central_wl_trials

    if 'peak_spec_trials' in kwargs:
        peak_spec_trials = np.array(kwargs['peak_spec_trials'])
        dictionary['peak_spec_trials'] = peak_spec_trials
        df['Peak_Spec'] = peak_spec_trials

    if 'intensity_trials' in kwargs:
        intensity_trials = np.array(kwargs['intensity_trials'])
        dictionary['intensity_trials'] = intensity_trials
        df['Intensity'] = intensity_trials

    if 'second_trials' in kwargs:
        second_trials = np.array(kwargs['second_trials'])
        dictionary['second_trials'] = second_trials
        df['Second'] = second_trials

    # Parameters
    if 'wl' in kwargs:
        wl = np.array(kwargs['wl'])
        dictionary['wl'] = wl
    if 'actualwl' in kwargs:
        actualwl = np.array(kwargs['actualwl'])
        dictionary['actualwl'] = actualwl
    if 'trials' in kwargs:
        trials = np.array(kwargs['trials'])
        dictionary['trials'] = trials
    if 'pause' in kwargs:
        pause = np.array(kwargs['pause'])
        dictionary['pause'] = pause

    return dictionary, df


def get_now():
    now = datetime.now().strftime('%Y%m%d-%H%M%S')
    return now


def times2seconds(times):
    seconds = [round((time-times[0]).total_seconds(), 2) for time in times]
    return seconds


def create_experiment_dir(base_folder):
    experiment_dirs = next(os.walk(base_folder))[1]
    if len(experiment_dirs) == 0:
        new_experiment_num = 1
    else:
        new_experiment_num = np.max([int(experiment_dir.split('_')[-1]) for experiment_dir in experiment_dirs]) + 1
    new_experiment_dir = os.path.join(base_folder, '_'.join(['experiment', str(new_experiment_num)]))
    os.mkdir(new_experiment_dir)

    return new_experiment_dir


