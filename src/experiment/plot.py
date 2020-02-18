import numpy as np
import seaborn as sns
import pandas as pd
sns.set(color_codes=True)


# Section I: Plot a collection of trails for the same wl #
def plot_central_wl(ax, central_wl_trials, trials, actualwl):
    """Plot the histogram of central wavelength for {trials} number of trials"""
    sns.distplot(central_wl_trials, bins=15, label=f'num_trials={trials}', ax=ax)
    ax.set_xlabel('Central Wavelength (nm)')
    ax.set_ylabel('Frequency')
    ax.legend(loc='upper right')
    ax.set_title(f'Central wavelengths histogram: Actual Wavelength = {round(actualwl, 2)}nm')


def plot_peak_spec(ax, peak_spec_trails, trials, exposure):
    """Plot the histogram of peak spectrum for {trials} number of trials"""
    sns.distplot(peak_spec_trails, bins=50, label=f'num_trials={trials}', ax=ax)
    ax.set_xlabel('Peak Intensity (Counts)')
    ax.set_ylabel('Frequency')
    ax.legend(loc='upper right')
    ax.set_title(f'Peak intensities histogram: Exposure Time = {exposure}ms')


def plot_intensity(ax, intensity_trials, trials, exposure):
    """Plot the histogram of total intensity for {trials} number of trials"""
    sns.distplot(intensity_trials, bins=50, label=f'num_trials={trials}', ax=ax)
    ax.set_xlabel('Total Intensity (Counts)')
    ax.set_ylabel('Frequency')
    ax.legend(loc='upper right')
    ax.set_title(f'Total intensities histogram: Exposure Time = {exposure}ms')


def plot_scatter(ax, central_wl_trials, peak_spec_trails, intensity_trials):
    """Plot the scatter plot of peak intensity vs. total intensity for {trials} number of trials"""
    central_wl_trials = np.array(central_wl_trials).reshape(-1, 1)
    peak_spec_trails = np.array(peak_spec_trails).reshape(-1, 1)
    intensity_trials = np.array(intensity_trials).reshape(-1, 1)
    name = ['Central Wavelength', 'Peak Intensity', 'Total Intensity']
    df = pd.DataFrame(np.concatenate([central_wl_trials, peak_spec_trails, intensity_trials], axis=1), columns=name)

    sns.scatterplot(x='Peak Intensity', y='Total Intensity', hue='Central Wavelength', size='Central Wavelength', data=df, ax=ax)
    ax.set_title(f'Peak Intensity vs. Total Intensity Histogram')


def plot_spectrometer_trials(ax0, ax1, ax2, ax3, central_wl_trials, peak_spec_trails, intensity_trials, trials, exposure, actualwl):
    plot_central_wl(ax0, central_wl_trials, trials, actualwl)
    plot_peak_spec(ax1, peak_spec_trails, trials, exposure)
    plot_intensity(ax2, intensity_trials, trials, exposure)
    plot_scatter(ax3, central_wl_trials, peak_spec_trails, intensity_trials)


def plot_power(ax, intensity_trials, trials, implementation):
    """Plot the histogram of measured power & ambient power for {trials} number of trials"""
    sns.distplot(intensity_trials, bins=10, label=f'num_trials={trials}', ax=ax)
    ax.set_ylabel('Frequency')
    ax.legend(loc='upper right')
    if implementation == 'measured':
        ax.set_xlabel('Measured Intensity')
        ax.set_title(f'Measured intensities histogram: PM Mode = SINGLESHOT_MANUAL')
    elif implementation == 'ambient':
        ax.set_xlabel('Ambient Intensity')
        ax.set_title(f'Ambient intensities histogram: PM Mode = SINGLESHOT_MANUAL')


def plot_powermeter_trails(ax0, ax1, intensity_trials, trials, implementation):
    plot_power(ax0, intensity_trials, trials, implementation)
    plot_power(ax1, intensity_trials, trials, implementation)


# Section II: Plot a collection of wls for the same trail #
def plot_power_meters(ax, actualwls, measured_powers, ambient_powers):
    """Plot the measured_powers & ambient_powers for a collection of actualwls"""
    ax.set_xlim(300, 900)
    ax.set_title(f'Power meter intensity: PM Mode = SINGLESHOT_MANUAL')
    ax.plot(actualwls, measured_powers, color='blue', label='measured_lights')
    ax.legend(loc='upper left')
    ax_ = ax.twinx()
    ax_.plot(actualwls, ambient_powers, color='orange', label='ambient_lights')
    ax_.legend(loc='upper right')

    for i, actualwl in enumerate(actualwls):
        ax.annotate(round(actualwl, 2), (actualwls[i], measured_powers[i]))
        ax_.annotate(round(actualwl, 2), (actualwls[i], ambient_powers[i]))


def plot_spectrometers(ax, specwls, specs, exposure):
    """Plot the spectrums for a collection of central spectral wavelengths"""
    ax.set_xlim(300, 900)
    ax.set_title(f'Spectrometer intensity: Exposure Time = {exposure}ms')
    for i in range(len(specwls)):
        ax.plot(specwls[i], specs[i])
        j = np.argmax(specs[i])
        ax.annotate(round(specwls[i][j], 2), (specwls[i][j], specs[i][j]))
