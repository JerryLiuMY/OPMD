import os
import time
import matplotlib.pyplot as plt
import numpy as np
from global_settings import CALIBRATION_FOLDER
from datetime import datetime
import pickle as pkl
from experiment.experiment import init_photodiode, measure_boths
from tools.utils import get_now, create_experiment_dir
from scipy.integrate import simps
from experiment.plot import plot_central_wl, plot_peak_spec, plot_intensity, plot_scatter, plot_power

STABILITY_FOLDER = os.path.join(CALIBRATION_FOLDER, 'power')


def run_stability(trials, pause, wls, exposure, repeat):
    """
    The function runs the intensities measurements by both the power meter and spectrometer
    :param trials: (int) number of trials that the measurements are run
    :param wls: (list) a list of wavelengths profiles set by the spectrometer
    :param exposure: (int) exposure time of the spectrometer
    :param repeat: (int) number of iterations within each measurement
    """
    create_experiment_dir(STABILITY_FOLDER)
    init_photodiode("W/cm2")

    actualwls_trials = []
    measured_powers_trials = []
    ambient_powers_trials = []
    specwls_trials = []
    specs_trials = []
    seconds_trails = []

    for trial in range(trials):
        print(f'\nCurrent Time {datetime.now()} Working on trial {trial}')
        actualwls, measured_lights, ambient_lights, specwls, specs, seconds = measure_boths(wls, exposure, repeat)

        actualwls_trials.append(actualwls)
        measured_powers_trials.append(measured_lights)
        ambient_powers_trials.append(ambient_lights)
        specwls_trials.append(specwls)
        specs_trials.append(specs)
        seconds_trails.append(seconds)

        time.sleep(pause)

    # Save Readings
    dictionary = {'actualwls_trials': actualwls_trials,
                  'measured_powers_trials': measured_powers_trials,
                  'ambient_power_trials': ambient_powers_trials,
                  'specwls_trials': specwls_trials,
                  'specs_trials': specs_trials,
                  'seconds_trails': seconds_trails,
                  'wls': wls,
                  'exposure': exposure,
                  'repeat': repeat}

    with open(os.path.join(STABILITY_FOLDER, '_'.join([get_now(), 'trials-'+str(trials)])+'.pkl'), 'wb') as h:
        pkl.dump(dictionary, h)

    actualwls = np.mean(actualwls_trials, axis=0)
    for j in range(np.shape(actualwls_trials)[1]):
        actualwl = actualwls[j]
        measured_power_trials = measured_powers_trials[:, j]
        ambient_power_trials = ambient_powers_trials[:, j]
        specwl_trials = specwls_trials[:, j, :]
        spec_trials = specs_trials[:, j, :]
        second_trials = seconds_trails[:, j]

        central_wl_trials = specwl_trials[np.argmax(spec_trials, axis=-1).reshape(-1, 1)]
        peak_spec_trials = spec_trials[np.argmax(spec_trials, axis=-1).reshape(-1, 1)]
        intensity_trials = [simps(spec_trials[i, :], specwl_trials[i, :]) for i in range(np.shape(actualwls_trials)[0])]

        # Save Figure
        fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(36, 12))
        plot_central_wl(axes[0][0], central_wl_trials, trials, actualwl)
        plot_peak_spec(axes[0][1], peak_spec_trials, trials, exposure)
        plot_intensity(axes[1][0], intensity_trials, trials, exposure)
        plot_scatter(axes[1][1], central_wl_trials, peak_spec_trials, intensity_trials)
        fig.savefig(os.path.join(STABILITY_FOLDER, get_now() + '.png'))

        fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(36, 12))
        plot_power(axes[0], measured_power_trials, trials, implementation='measured')
        plot_power(axes[1], ambient_power_trials, trials, implementation='ambient')
        fig.savefig(os.path.join(new_experiment_dir, '_'.join([get_now(), 'wl-' + str(wl)]) + '.png'))


if __name__ == '__main__':
    wls = [350, 380, 410, 440, 470, 500, 530, 560, 590, 620, 650, 680, 710, 740, 770, 800, 830, 860]
