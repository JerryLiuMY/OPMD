import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
import pickle as pkl
from global_settings import CALIBRATION_FOLDER
from datetime import datetime
from bench.bench import set_wavelength, measure_spectrometer
from calibration.plots import build
from calibration.tools import get_now, create_experiment_dir, times2seconds
from scipy.integrate import simps
from calibration.plots import plot_central_wl_hist, plot_peak_spec_hist, plot_intensity_hist, plot_scatter, plot_wl_series
import matplotlib.gridspec as gridspec
import time
sns.set()

SPECTROMETER_FOLDER = os.path.join(CALIBRATION_FOLDER, 'spectrometer')


def spectrometer_test(wl, trials, pause, exposure, dir, repeat=1):
    actualwl = set_wavelength(wl)
    central_wl_trials = []
    peak_spec_trials = []
    intensity_trials = []
    time_trials = []
    for trial in range(trials):
        print(f'{datetime.now()} Working on trial {trial}')
        specwl, spec = measure_spectrometer(exposure, repeat=repeat)

        central_wl = specwl[np.argmax(spec)]
        peak_spec = spec[np.argmax(spec)]
        intensity = simps(spec, specwl)

        central_wl_trials.append(central_wl)
        peak_spec_trials.append(peak_spec)
        intensity_trials.append(intensity)
        time_trials.append(datetime.now())
        time.sleep(pause)

    second_trials = times2seconds(time_trials)
    dictionary, df = build(central_wl_trials=central_wl_trials,
                           peak_spec_trials=peak_spec_trials,
                           intensity_trials=intensity_trials,
                           second_trials=second_trials,
                           wl=wl,
                           actualwl=actualwl,
                           trials=trials,
                           pause=pause)

    # Plot Images
    name = os.path.join(dir, '_'.join([get_now(), 'wl-'+str(wl)]))
    with open(name + '.pkl', 'wb') as h:
        pkl.dump(dictionary, h)

    fig = plt.figure(figsize=(20, 12))
    gs = gridspec.GridSpec(3, 2)
    plot_central_wl_hist(plt.subplot(gs[0, 0]), df, trials, actualwl)
    plot_peak_spec_hist(plt.subplot(gs[0, 1]), df, trials, exposure)
    plot_intensity_hist(plt.subplot(gs[1, 0]), df, trials, exposure)
    plot_scatter(plt.subplot(gs[1, 1]), df)
    plot_wl_series(plt.subplot(gs[2, :]), df)
    plt.tight_layout()
    fig.savefig(os.path.join(name + '.png'))


if __name__ == '__main__':
    wls, trials, pause, exposure = [460, 480, 500, 520, 540, 560, 580, 600, 620, 640, 660, 680, 700], 400, 50, 300
    new_experiment_dir = create_experiment_dir(SPECTROMETER_FOLDER)
    for wl in wls:
        new_experiment_dir(wl, trials, pause, exposure, dir, repeat=1)
