import numpy as np
import seaborn as sns
sns.set(color_codes=True)


# Section I: Plot a collection of powermeter trials for the same wl #
def plot_measured_power_hist(ax, df, trials):
    """Plot the histogram of measured power for {trials} number of trials"""
    measured_power_trails = df['Measured_Power']
    sns.distplot(measured_power_trails, bins=10, label=f'num_trials={trials}', ax=ax)
    ax.set_xlabel('Measured Intensity')
    ax.set_ylabel('Frequency')
    ax.legend(loc='upper right')
    ax.set_title(f'Measured intensities histogram: PM Mode = SINGLESHOT_MANUAL')


def plot_ambient_power_hist(ax, df, trials):
    """Plot the histogram of ambient power for {trials} number of trials"""
    ambient_power_trails = df['Ambient_Power']
    sns.distplot(ambient_power_trails, bins=10, label=f'num_trials={trials}', ax=ax)
    ax.set_xlabel('Ambient Intensity')
    ax.set_ylabel('Frequency')
    ax.legend(loc='upper right')
    ax.set_title(f'Ambient intensities histogram: PM Mode = SINGLESHOT_MANUAL')


def plot_power_series(ax, df):
    """Plot the time series of measured power & ambient power"""
    sns.lineplot(x='Second', y='Measured_Power', data=df, color=sns.color_palette()[0], label='Measured_Power', ax=ax)
    ax.legend(loc='upper left')
    ax_ = ax.twinx()
    sns.lineplot(x='Second', y='Ambient_Power', data=df, color=sns.color_palette()[1], label='Ambient_Power', ax=ax_)
    ax_.legend(loc='upper right')
    ax.set_title(f'Measured & Ambient Power Time Series')


# Section II: Plot a collection of spectrometer trials for the same wl #
def plot_central_wl_hist(ax, df, trials, actualwl):
    """Plot the histogram of central wavelength for {trials} number of trials"""
    central_wl_trials = df['Central_WL']
    sns.distplot(central_wl_trials, bins=15, label=f'num_trials={trials}', ax=ax)
    ax.set_xlabel('Central Wavelength (nm)')
    ax.set_ylabel('Frequency')
    ax.legend(loc='upper right')
    ax.set_title(f'Central wavelengths histogram: Actual Wavelength = {round(actualwl, 2)}nm')


def plot_peak_spec_hist(ax, df, trials, exposure):
    """Plot the histogram of peak spectrum for {trials} number of trials"""
    peak_spec_trials = df['Peak_Spec']
    sns.distplot(peak_spec_trials, bins=50, label=f'num_trials={trials}', ax=ax)
    ax.set_xlabel('Peak Intensity (Counts)')
    ax.set_ylabel('Frequency')
    ax.legend(loc='upper right')
    ax.set_title(f'Peak intensities histogram: Exposure Time = {exposure}ms')


def plot_intensity_hist(ax, df, trials, exposure):
    """Plot the histogram of total intensity for {trials} number of trials"""
    intensity_trials = df['Intensity']
    sns.distplot(intensity_trials, bins=50, label=f'num_trials={trials}', ax=ax)
    ax.set_xlabel('Total Intensity (Counts)')
    ax.set_ylabel('Frequency')
    ax.legend(loc='upper right')
    ax.set_title(f'Total intensities histogram: Exposure Time = {exposure}ms')


def plot_scatter(ax, df):
    """Plot the scatter plot of peak intensity vs. total intensity for {trials} number of trials"""
    sns.scatterplot(x='Peak_Spec', y='Intensity', hue='Central_WL', size='Central_WL', data=df, ax=ax)
    ax.set_title(f'Peak Intensity vs. Total Intensity Histogram')


def plot_wl_series(ax, df):
    sns.lineplot(x='Second', y='Central_WL', data=df, color=sns.color_palette()[0], label='Central_WL', ax=ax)
    ax.legend(loc='upper left')
    ax_ = ax.twinx()
    sns.lineplot(x='Second', y='Peak_Spec', data=df, color=sns.color_palette()[1], label='Peak_Spec', ax=ax_)
    ax_.legend(loc='upper right')
    ax.set_title(f'Central Wavelength & Peak Intensity Time Series')


# Section III: Plot a collection of powermeter wls for the same trial #
def plot_(ax, actualwls, measured_powers, ambient_powers):
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


# Section IV: Plot a collection of spectrometer wls for the same trial #
def plot__(ax, specwls, specs, exposure):
    """Plot the spectrums for a collection of central spectral wavelengths"""
    ax.set_xlim(300, 900)
    ax.set_title(f'Spectrometer intensity: Exposure Time = {exposure}ms')
    for i in range(len(specwls)):
        ax.plot(specwls[i], specs[i])
        j = np.argmax(specs[i])
        ax.annotate(round(specwls[i][j], 2), (specwls[i][j], specs[i][j]))
