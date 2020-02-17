import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set(color_codes=True)


def plot_power_meters(ax, actualwls, measured_lights, ambient_lights):
    ax.set_xlim(300, 900)
    ax.set_title(f'Power meter intensity: PM Model = SINGLESHOT_MANUAL')
    ax.plot(actualwls, measured_lights, color='blue', label='measured_lights')
    ax.legend(loc='upper left')
    ax_ = ax.twinx()
    ax_.plot(actualwls, ambient_lights, color='orange', label='ambient_lights')
    ax_.legend(loc='upper right')

    for i, actualwl in enumerate(actualwls):
        ax.annotate(round(actualwl, 2), (actualwls[i], measured_lights[i]))
        ax_.annotate(round(actualwl, 2), (actualwls[i], ambient_lights[i]))


def plot_spectrometers(ax, specwls, specs, exposure):
    ax.set_xlim(300, 900)
    ax.set_title(f'Spectrometer intensity: Exposure Time = {exposure}ms')
    for i in range(len(specwls)):
        ax.plot(specwls[i], specs[i])
        j = np.argmax(specs[i])
        ax.annotate(round(specwls[i][j], 2), (specwls[i][j], specs[i][j]))
