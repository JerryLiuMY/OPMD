from datetime import datetime
import os
import numpy as np


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
