import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
from global_settings import CALIBRATION_FOLDER
from datetime import datetime
import pickle as pkl
from experiment.experiment import set_wavelength, measure_spectrometer
from tools.utils import get_now, create_experiment_dir
from scipy.integrate import simps
from experiment.plot import plot_central_wl, plot_peak_spec, plot_intensity, plot_scatter
sns.set()

SPECTROMETER_FOLDER = os.path.join(CALIBRATION_FOLDER, 'spectrometer')


def run_spectrometer(wls, trials, exposure):
    new_experiment_dir = create_experiment_dir(SPECTROMETER_FOLDER)
    for wl in wls:
        actualwl = set_wavelength(wl)
        central_wl_trials = []
        peak_spec_trials = []
        intensity_trials = []
        for trial in range(trials):
            print(f'{datetime.now()} Working on trial {trial}')
            specwl, spec = measure_spectrometer(exposure, repeat=1)

            central_wl = specwl[np.argmax(spec)]
            peak_spec = spec[np.argmax(spec)]
            intensity = simps(spec, specwl)

            central_wl_trials.append(central_wl)
            peak_spec_trials.append(peak_spec)
            intensity_trials.append(intensity)

        dictionary = {'actualwl': actualwl,
                      'central_wl_trials': central_wl_trials,
                      'peak_spec_trails': peak_spec_trials,
                      'intensity_trials': intensity_trials,
                      'wl': wl,
                      'trials': trials,
                      'exposure': exposure}

        with open(os.path.join(new_experiment_dir, '_'.join([get_now(), 'wl-'+str(wl)]) + '.pkl'), 'wb') as h:
            pkl.dump(dictionary, h)

        fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(15, 12))
        plot_central_wl(axes[0][0], central_wl_trials, trials, actualwl)
        plot_peak_spec(axes[0][1], peak_spec_trials, trials, exposure)
        plot_intensity(axes[1][0], intensity_trials, trials, exposure)
        plot_scatter(axes[1][1], central_wl_trials, peak_spec_trials, intensity_trials)
        fig.savefig(os.path.join(new_experiment_dir, '_'.join([get_now(), 'wl-' + str(wl)]) + '.png'))


if __name__ == '__main__':
    wls = [460, 480, 500, 520, 540, 560, 580, 600, 620, 640, 660, 680, 700]
    trials = 400
    exposure = 300
    run_spectrometer(wls, trials, exposure)
