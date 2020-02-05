from time import sleep
import numpy as np
import os
import matplotlib.pyplot as plt
from global_settings import CALIBRATION_FOLDER
from datetime import datetime
import pickle as pkl
from experiment.experiment import init_photodiode, set_wavelength, measure_spectrometer, measure_spectrometers , measure_boths
from experiment.plot import plot_power_meter, plot_spectrometer
from tools.utils import get_now

TIME_STABILITY_FOLDER = os.path.join(CALIBRATION_FOLDER, 'time_stability')
TEST_SPECTROMETER_FOLDER = os.path.join(CALIBRATION_FOLDER, 'test_spectrometer')


def run_time_stability(trials, pause, wls, exposure, repeat):
    """
    The function runs the intensities measurements by both the power meter and spectrometer
    :param trials: (int) number of trials that the measurements are run
    :param pause: (float) time interval between two trials
    :param wls: (list) a list of wavelengths profiles set by the spectrometer
    :param exposure: (int) exposure time of the spectrometer
    :param repeat: (int) number of iterations within each measurement
    """

    init_photodiode("W/cm2")
    for trial in range(trials):
        print(f'\nCurrent Time {datetime.now()} Working on trial {trial}')
        sleep(pause)
        actualwls, measured_lights, ambient_lights, specwls, specs = measure_boths(wls, exposure, repeat)

        # Save Readings
        dictionary = {'actualwls': actualwls,
                      'measured_lights': measured_lights,
                      'ambient_lights': ambient_lights,
                      'specwls': specwls,
                      'specs': specs,
                      'exposure': exposure}

        with open(os.path.join(TIME_STABILITY_FOLDER, get_now() + '.pkl'), 'wb') as h:
            pkl.dump(dictionary, h)

        # Save Figure
        fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(24, 8))
        plot_power_meter(axes[0], actualwls, measured_lights, ambient_lights)
        plot_spectrometer(axes[1], specwls, specs, exposure)
        fig.savefig(os.path.join(TIME_STABILITY_FOLDER, get_now() + '.png'))


def run_test_spectrometer(trials, wls, exposure, repeat):
    fig, ax = plt.subplots(figsize=(18, 12))
    central_wl_trials = []
    for trial in range(trials):
        print(f'\nCurrent Time {datetime.now()} Working on trial {trial}')
        actualwls, specwls, specs = measure_spectrometers(wls, exposure, repeat)
        central_wl = specwls[0][np.argmax(specs[0])]
        central_wl_trials.append(central_wl)

    ax.hist(central_wl_trials)
    fig.savefig(os.path.join(TIME_STABILITY_FOLDER, get_now() + '.png'))

    return central_wl_trials, fig


def run_intensity_stability():
    pass


def run_wavelength_stability():
    pass

def theoretical_throughput():
    # A superposition of efficiency of light source, light guide, beam splitter
    # + spectrometer / integrating sphere & diode
    pass
