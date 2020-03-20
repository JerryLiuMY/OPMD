import os
import matplotlib.pyplot as plt
import seaborn as sns
from global_settings import CALIBRATION_FOLDER
from datetime import datetime
import pickle as pkl
from experiment.experiment import init_photodiode, set_wavelength, measure_power_meter
from tools.utils import build, get_now, create_experiment_dir, times2seconds
from tools.plot import plot_measured_power_hist, plot_ambient_power_hist, plot_power_series
import matplotlib.gridspec as gridspec
import time
sns.set()

POWERMETER_FOLDER = os.path.join(CALIBRATION_FOLDER, 'powermeter')


def run_powermeter(wls, trials, pause):
    new_experiment_dir = create_experiment_dir(POWERMETER_FOLDER)
    init_photodiode(unit="W/cm2")
    for wl in wls:
        actualwl = set_wavelength(wl)
        measured_power_trials = []
        ambient_power_trials = []
        time_trials = []
        for trial in range(trials):
            print(f'{datetime.now()} Working on trial {trial}')
            measured_light, ambient_light = measure_power_meter(repeat=1)
            measured_power_trials.append(measured_light)
            ambient_power_trials.append(ambient_light)
            time_trials.append(datetime.now())
            time.sleep(pause)

        second_trials = times2seconds(time_trials)
        dictionary, df = build(measured_power_trials=measured_power_trials,
                               ambient_power_trials=ambient_power_trials,
                               second_trials=second_trials,
                               wl=wl,
                               actualwl=actualwl,
                               trials=trials,
                               pause=pause)

        # Plot Images
        name = os.path.join(new_experiment_dir, '_'.join([get_now(), 'wl-' + str(wl)]))
        with open(name + '.pkl', 'wb') as h:
            pkl.dump(dictionary, h)
        fig = plt.figure(figsize=(20, 12))
        gs = gridspec.GridSpec(2, 2)
        plot_measured_power_hist(plt.subplot(gs[0, 0]), df, trials)
        plot_ambient_power_hist(plt.subplot(gs[0, 1]), df, trials)
        plot_power_series(plt.subplot(gs[1, :]), df)
        plt.tight_layout()
        fig.savefig(name + '.png')


if __name__ == '__main__':
    wls = [460, 480, 500, 520, 540, 560, 580, 600, 620, 640, 660, 680, 700]
    trials = 400
    run_powermeter(wls, trials)
