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
sns.set()

TEST_SPECTROMETER_FOLDER = os.path.join(CALIBRATION_FOLDER, 'spectrometer')


def run_spectrometer(wls, trials, exposure, repeat=1):
    new_experiment_dir = create_experiment_dir(TEST_SPECTROMETER_FOLDER)
    for wl in wls:
        actualwl = set_wavelength(wl)
        central_wl_trials = []
        peak_spec_trails = []
        intensity_trials = []
        for trial in range(trials):
            print(f'{datetime.now()} Working on trial {trial}')
            specwl, spec = measure_spectrometer(exposure, repeat)

            central_wl = specwl[np.argmax(spec)]
            peak_spec = spec[np.argmax(spec)]
            intensity = simps(spec, specwl)

            central_wl_trials.append(central_wl)
            peak_spec_trails.append(peak_spec)
            intensity_trials.append(intensity)

        dictionary = {'actualwl': actualwl,
                      'central_wl_trials': central_wl_trials,
                      'peak_spec_trails': peak_spec_trails,
                      'intensity_trials': intensity_trials,
                      'wl': wl,
                      'trials': trials,
                      'exposure': exposure,
                      'repeat': repeat}

        with open(os.path.join(new_experiment_dir, '_'.join([get_now(), 'wl-'+str(wl)]) + '.pkl'), 'wb') as h:
            pkl.dump(dictionary, h)

        fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(15, 12))
        plot_central_wl(axes[0][0], central_wl_trials, trials, actualwl)
        plot_peak_spec(axes[0][1], peak_spec_trails, trials, exposure)
        plot_intensity(axes[1][0], intensity_trials, trials, exposure)
        plot_scatter(axes[1][1], central_wl_trials, peak_spec_trails, intensity_trials)
        fig.savefig(os.path.join(new_experiment_dir, '_'.join([get_now(), 'wl-' + str(wl)]) + '.png'))


def plot_central_wl(ax, central_wl_trials, trials, actualwl):
    sns.distplot(central_wl_trials, bins=15, label=f'num_trials={trials}', ax=ax)
    ax.set_xlabel('Central Wavelength (nm)')
    ax.set_ylabel('Frequency')
    ax.legend(loc='upper right')
    ax.set_title(f'Central wavelengths histogram: Actual Wavelength = {round(actualwl, 2)}nm')


def plot_peak_spec(ax, peak_spec_trails, trials, exposure):
    sns.distplot(peak_spec_trails, bins=50, label=f'num_trials={trials}', ax=ax)
    ax.set_xlabel('Peak Intensity (Counts)')
    ax.set_ylabel('Frequency')
    ax.legend(loc='upper right')
    ax.set_title(f'Peak intensities histogram: Exposure Time = {exposure}ms')


def plot_intensity(ax, intensity_trials, trials, exposure):
    sns.distplot(intensity_trials, bins=50, label=f'num_trials={trials}', ax=ax)
    ax.set_xlabel('Total Intensity (Counts)')
    ax.set_ylabel('Frequency')
    ax.legend(loc='upper right')
    ax.set_title(f'Total intensities histogram: Exposure Time = {exposure}ms')


def plot_scatter(ax, central_wl_trials, peak_spec_trails, intensity_trials):
    central_wl_trials = np.array(central_wl_trials).reshape(-1, 1)
    peak_spec_trails = np.array(peak_spec_trails).reshape(-1, 1)
    intensity_trials = np.array(intensity_trials).reshape(-1, 1)
    name = ['Central Wavelength', 'Peak Intensity', 'Total Intensity']
    df = pd.DataFrame(np.concatenate([central_wl_trials, peak_spec_trails, intensity_trials], axis=1), columns=name)

    sns.scatterplot(x='Peak Intensity', y='Total Intensity', hue='Central Wavelength', size='Central Wavelength', data=df, ax=ax)
    ax.set_title(f'Peak Intensity vs. Total Intensity Histogram')


if __name__ == '__main__':
    wls = [460, 480, 500, 520, 540, 560, 580, 600, 620, 640, 660, 680, 700]
    trials = 400
    exposure = 300
    run_spectrometer(wls, trials, exposure)
