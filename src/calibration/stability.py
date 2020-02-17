from time import sleep
import numpy as np
import os
import matplotlib.pyplot as plt
from global_settings import CALIBRATION_FOLDER
from datetime import datetime
import pickle as pkl
from experiment.experiment import init_photodiode, measure_boths
from experiment.plot import plot_power_meters, plot_spectrometers
from tools.utils import get_now, create_experiment_dir

STABILITY_FOLDER = os.path.join(CALIBRATION_FOLDER, 'stability')


def run_stability(trials, wls, exposure, repeat):
    """
    The function runs the intensities measurements by both the power meter and spectrometer
    :param trials: (int) number of trials that the measurements are run
    :param wls: (list) a list of wavelengths profiles set by the spectrometer
    :param exposure: (int) exposure time of the spectrometer
    :param repeat: (int) number of iterations within each measurement
    """
    init_photodiode("W/cm2")
    for trial in range(trials):
        print(f'\nCurrent Time {datetime.now()} Working on trial {trial}')
        actualwls, measured_lights, ambient_lights, specwls, specs = measure_boths(wls, exposure, repeat)

        # Save Readings
        dictionary = {'actualwls': actualwls,
                      'measured_lights': measured_lights,
                      'ambient_lights': ambient_lights,
                      'specwls': specwls,
                      'specs': specs,
                      'wls': wls,
                      'exposure': exposure,
                      'repeat': repeat}

        with open(os.path.join(STABILITY_FOLDER, '_'.join([get_now(), 'trial-'+str(trial)])+'.pkl'), 'wb') as h:
            pkl.dump(dictionary, h)

        # Save Figure
        fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(24, 8))
        plot_power_meters(axes[0], actualwls, measured_lights, ambient_lights)
        plot_spectrometers(axes[1], specwls, specs, exposure)
        fig.savefig(os.path.join(STABILITY_FOLDER, get_now() + '.png'))
        plt.show(fig)


if __name__ == '__main__':
    wls = [350, 380, 410, 440, 470, 500, 530, 560, 590, 620, 650, 680, 710, 740, 770, 800, 830, 860]
