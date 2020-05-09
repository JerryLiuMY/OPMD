import numpy as np
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

SMALL_SIZE = 8
MEDIUM_SIZE = 10
BIGGER_SIZE = 12

plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=SMALL_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title


# Section I: Plot a collection of powermeter trials for the same wl #
def plot_measured_power_hist(ax, df, trials):
    """Plot the histogram of measured power for {trials} number of trials"""
    measured_power_trails = df['Measured_Power']
    sns.distplot(measured_power_trails, bins=10, kde=False, norm_hist=False, label=f'num_trials={trials}', ax=ax)
    ax.set_xlabel('Measured Power (W$\cdot$cm$^{2}$)')
    ax.set_ylabel('Counts')
    ax.legend(loc='upper right')

    ax_ = ax.twinx()
    ax_.axis('off')
    sns.kdeplot(measured_power_trails, ax=ax_)
    ax_.get_legend().remove()
    # ax.set_title(f'Measured intensities histogram: PM Mode = SINGLESHOT_MANUAL')


def plot_ambient_power_hist(ax, df, trials):
    """Plot the histogram of ambient power for {trials} number of trials"""
    ambient_power_trails = df['Ambient_Power']
    sns.distplot(ambient_power_trails, bins=10, kde=False, norm_hist=False, label=f'num_trials={trials}', ax=ax)
    ax.set_xlabel('Ambient Power (W$\cdot$cm$^{2}$)')
    ax.set_ylabel('Counts')
    ax.legend(loc='upper right')

    ax_ = ax.twinx()
    sns.kdeplot(ambient_power_trails, label=None, ax=ax_)
    ax_.axis('off')
    ax_.get_legend().remove()
    # ax.set_title(f'Ambient intensities histogram: PM Mode = SINGLESHOT_MANUAL')


def plot_power_series(ax, df):
    """Plot the time series of measured power & ambient power"""
    sns.lineplot(x='Second', y='Measured_Power', data=df, color=sns.color_palette()[0], label='Measured_Power', ax=ax)
    ax.set_xlabel('Time (second)')
    ax.set_ylabel('Measured Power')
    ax.legend(loc='upper left')

    ax_ = ax.twinx()
    sns.lineplot(x='Second', y='Ambient_Power', data=df, color=sns.color_palette()[1], label='Ambient_Power', ax=ax_)
    ax_.set_ylabel('Ambient Power')
    ax_.legend(loc='upper right')
    # ax.set_title(f'Measured & Ambient Power Time Series')


# Section II: Plot a collection of spectrometer trials for the same wl #
def plot_central_wl_hist(ax, df, trials, actualwl):
    """Plot the histogram of central wavelength for {trials} number of trials"""
    central_wl_trials = df['Central_WL']
    sns.distplot(central_wl_trials, bins=15, kde=False, norm_hist=False, label=f'num_trials={trials}', ax=ax)
    ax.set_xlabel('Peak Wavelength (nm)')
    ax.set_ylabel('Counts')
    ax.legend(loc='upper right')

    ax_ = ax.twinx()
    sns.kdeplot(central_wl_trials, ax=ax_)
    ax_.axis('off')
    ax_.get_legend().remove()
    # ax.set_title(f'Central wavelengths histogram: Actual Wavelength = {round(actualwl, 2)}nm')


def plot_peak_spec_hist(ax, df, trials, exposure):
    """Plot the histogram of peak spectrum for {trials} number of trials"""
    peak_spec_trials = df['Peak_Spec']
    sns.distplot(peak_spec_trials, bins=50, kde=False, norm_hist=False, label=f'num_trials={trials}', ax=ax)
    ax.ticklabel_format(axis='x', style='sci', scilimits=(0, 0))
    ax.set_xlabel('Peak Intensity (count)')
    ax.set_ylabel('Counts')
    ax.legend(loc='upper right')

    ax_ = ax.twinx()
    sns.kdeplot(peak_spec_trials, ax=ax_)
    ax_.axis('off')
    ax_.get_legend().remove()
    # ax.set_title(f'Peak intensities histogram: Exposure Time = {exposure}ms')


def plot_intensity_hist(ax, df, trials, exposure):
    """Plot the histogram of total intensity for {trials} number of trials"""
    intensity_trials = df['Intensity']
    sns.distplot(intensity_trials, bins=50, kde=False, norm_hist=False, label=f'num_trials={trials}', ax=ax)
    ax.ticklabel_format(axis='x', style='sci', scilimits=(0, 0))
    ax.set_xlabel('Total Intensity (count)')
    ax.set_ylabel('Counts')
    ax.legend(loc='upper right')

    ax_ = ax.twinx()
    sns.kdeplot(intensity_trials, ax=ax_)
    ax_.axis('off')
    ax_.get_legend().remove()
    # ax.set_title(f'Total intensities histogram: Exposure Time = {exposure}ms')


def plot_scatter(ax, df):
    """Plot the scatter plot of peak intensity vs. total intensity for {trials} number of trials"""
    sns.scatterplot(x='Peak_Spec', y='Intensity', hue='Central_WL', size='Central_WL', data=df, ax=ax)
    ax.ticklabel_format(axis='both', style='sci', scilimits=(0, 0))
    ax.set_xlabel(f'Peak Intensity (count)')
    ax.set_ylabel(f'Total Intensity (count)')
    # ax.set_title(f'Peak Intensity vs. Total Intensity')


def plot_wl_series(ax, df):
    sns.lineplot(x='Second', y='Central_WL', data=df, color=sns.color_palette()[0], label='Central_WL', ax=ax)
    ax.set_xlabel('Time (second)')
    ax.legend(loc='upper left')

    ax_ = ax.twinx()
    sns.lineplot(x='Second', y='Peak_Spec', data=df, color=sns.color_palette()[1], label='Peak_Spec', ax=ax_)
    ax_.legend(loc='upper right')
    # ax.set_title(f'Central Wavelength & Peak Intensity Time Series')


# Build dataframe and dictionary
def build(**kwargs):
    dictionary = {}
    df = pd.DataFrame()
    if 'measured_power_trials' in kwargs:
        measured_power_trials = np.array(kwargs['measured_power_trials'])
        dictionary['measured_power_trials'] = measured_power_trials
        df['Measured_Power'] = measured_power_trials

    if 'ambient_power_trials' in kwargs:
        ambient_power_trials = np.array(kwargs['ambient_power_trials'])
        dictionary['ambient_power_trials'] = ambient_power_trials
        df['Ambient_Power'] = ambient_power_trials

    if 'central_wl_trials' in kwargs:
        central_wl_trials = np.array(kwargs['central_wl_trials'])
        dictionary['central_wl_trials'] = central_wl_trials
        df['Central_WL'] = central_wl_trials

    if 'peak_spec_trials' in kwargs:
        peak_spec_trials = np.array(kwargs['peak_spec_trials'])
        dictionary['peak_spec_trials'] = peak_spec_trials
        df['Peak_Spec'] = peak_spec_trials

    if 'intensity_trials' in kwargs:
        intensity_trials = np.array(kwargs['intensity_trials'])
        dictionary['intensity_trials'] = intensity_trials
        df['Intensity'] = intensity_trials

    if 'second_trials' in kwargs:
        second_trials = np.array(kwargs['second_trials'])
        dictionary['second_trials'] = second_trials
        df['Second'] = second_trials

    # Parameters
    if 'wl' in kwargs:
        wl = np.array(kwargs['wl'])
        dictionary['wl'] = wl
    if 'actualwl' in kwargs:
        actualwl = np.array(kwargs['actualwl'])
        dictionary['actualwl'] = actualwl
    if 'trials' in kwargs:
        trials = np.array(kwargs['trials'])
        dictionary['trials'] = trials
    if 'pause' in kwargs:
        pause = np.array(kwargs['pause'])
        dictionary['pause'] = pause

    return dictionary, df