from bench.bench import set_wavelength, measure_power_meter, measure_spectrometer
from datetime import datetime
from tools.utils import times2seconds
from bench.bench import init_photodiode
from global_settings import EXPERIMENT_FOLDER
from tools.utils import create_experiment_dir
from tools.utils import get_now
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import os
import pickle as pkl

PHOTOMETRY_FOLDER = os.path.join(EXPERIMENT_FOLDER, 'photometry')


# For LED source wls = [556]
def photometry(wls, exposure, dir, repeat=100):
    """
    Measure both the power meter intensities and spectrometer spectral wavelengths and spectral intensity for "repeated"
    number of repeated experiments for each wavelength in wls
    """
    init_photodiode(unit="W/cm2")
    actualwls = []
    measured_powers = []
    ambient_powers = []
    specwls = []
    specs = []
    times = []

    for wl in wls:
        actualwl = set_wavelength(wl)
        time = datetime.now()
        measured_light, ambient_light = measure_power_meter(repeat)
        specwl, spec = measure_spectrometer(exposure, repeat)

        actualwls.append(actualwl)
        measured_powers.append(measured_light)
        ambient_powers.append(ambient_light)
        specwls.append(specwl)
        specs.append(spec)
        times.append(time)

    seconds = times2seconds(times)
    dictionary = {'measured_powers': measured_powers,
                  'ambient_powers': ambient_powers,
                  'specwls': specwls,
                  'specs': specs,
                  'seconds': seconds,
                  'actualwls': actualwls}

    name = os.path.join(dir, '_'.join([get_now()]))
    with open(name + '.pkl', 'wb') as h:
        pkl.dump(dictionary, h)

    fig = plt.figure(figsize=(20, 8))
    gs = gridspec.GridSpec(1, 2)
    plot_power(plt.subplot(gs[0, 0]), actualwls, measured_powers, ambient_powers, repeat)
    plot_spec(plt.subplot(gs[0, 1]), specwls, specs, exposure, repeat)
    plt.tight_layout()
    fig.savefig(name + '.png')


def plot_power(ax, actualwls, measured_powers, ambient_powers, repeat):
    """Plot the measured_powers & ambient_powers for a collection of actualwls"""
    ax.set_xlim(300, 900)
    ax.set_title(f'Power meter intensity: PM Mode = SINGLESHOT_MANUAL; Repeat = {repeat}')
    ax.plot(actualwls, measured_powers, color='blue', label='measured_lights')
    ax.legend(loc='upper left')
    ax_ = ax.twinx()
    ax_.plot(actualwls, ambient_powers, color='orange', label='ambient_lights')
    ax_.legend(loc='upper right')

    for i, actualwl in enumerate(actualwls):
        ax.annotate(round(actualwl, 2), (actualwls[i], measured_powers[i]))
        ax_.annotate(round(actualwl, 2), (actualwls[i], ambient_powers[i]))


def plot_spec(ax, specwls, specs, exposure, repeat):
    """Plot the spectrums for a collection of central spectral wavelengths"""
    ax.set_xlim(300, 900)
    ax.set_title(f'Spectrometer intensity: Exposure Time = {exposure}ms; Repeat = {repeat}')
    for i in range(len(specwls)):
        ax.plot(specwls[i], specs[i])
        j = np.argmax(specs[i])
        ax.annotate(round(specwls[i][j], 2), (specwls[i][j], specs[i][j]))


if __name__ == '__main__':
    new_experiment_dir = create_experiment_dir(PHOTOMETRY_FOLDER)
    wls, exposure = [460, 480, 500, 520, 540, 560, 580, 600, 620, 640, 660, 680, 700], 300
    photometry(wls, exposure, new_experiment_dir, repeat=100)
