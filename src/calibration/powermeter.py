import os
import matplotlib.pyplot as plt
import seaborn as sns
from global_settings import CALIBRATION_FOLDER
from datetime import datetime
import pickle as pkl
from experiment.experiment import init_photodiode, set_wavelength, measure_power_meter
from tools.utils import get_now, create_experiment_dir
from experiment.plot import plot_power
sns.set()

POWERMETER_FOLDER = os.path.join(CALIBRATION_FOLDER, 'powermeter')


def run_powermeter(wls, trials):
    new_experiment_dir = create_experiment_dir(POWERMETER_FOLDER)
    init_photodiode(unit="W/cm2")
    for wl in wls:
        actualwl = set_wavelength(wl)
        measured_power_trials = []
        ambient_power_trials = []
        for trial in range(trials):
            print(f'{datetime.now()} Working on trial {trial}')
            measured_light, ambient_light = measure_power_meter(repeat=1)
            measured_power_trials.append(measured_light)
            ambient_power_trials.append(ambient_light)

        dictionary = {'actualwl': actualwl,
                      'measured_power_trials': measured_power_trials,
                      'ambient_trails': ambient_power_trials,
                      'wl': wl,
                      'trials': trials}

        with open(os.path.join(new_experiment_dir, '_'.join([get_now(), 'wl-'+str(wl)]) + '.pkl'), 'wb') as h:
            pkl.dump(dictionary, h)

        fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(15, 12))
        plot_power(axes[0], measured_power_trials, trials, implementation='measured')
        plot_power(axes[1], ambient_power_trials, trials, implementation='ambient')
        fig.savefig(os.path.join(new_experiment_dir, '_'.join([get_now(), 'wl-' + str(wl)]) + '.png'))


if __name__ == '__main__':
    wls = [460, 480, 500, 520, 540, 560, 580, 600, 620, 640, 660, 680, 700]
    trials = 400
    run_powermeter(wls, trials)
