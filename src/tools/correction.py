import numpy as np
from global_settings import LED, LED_SPEC
from scipy.optimize import curve_fit
import collections
from scipy.signal import savgol_filter, medfilt
from scipy.interpolate import interp1d
from peakutils import baseline
from scipy.signal import butter, filtfilt


def read_smooth_spectrum(specwl_, spec_, implementation=0, out=True):

    # remove baseline
    if implementation == 0:
        spec_dict = dict(collections.Counter(spec_))
        spec_count, spec_sum = 0, 0
        for s in spec_dict.keys():
            if spec_dict[s] > 10:
                spec_count += spec_dict[s]
                spec_sum += s * spec_dict[s]
        base_filter = spec_sum / spec_count
        base_filter_spec = np.array(spec_) - base_filter
    elif implementation == 1:
        base_filter = np.mean(medfilt(spec_, 2047))
        base_filter_spec = np.array(spec_) - base_filter
    elif implementation == 2:
        base_filter = baseline(np.array(spec_), deg=0)
        base_filter_spec = np.array(spec_) - base_filter
    elif implementation == 3:
        [b, a] = butter(1, 0.0001, btype='highpass')
        base_filter_spec = filtfilt(b, a, spec_)
    else:
        raise Exception('Invalid Implementation Mode')

    # remove outlier
    if out:
        out_filter = medfilt(base_filter_spec, 31)
        out_filter_index = abs(np.array(base_filter_spec) - out_filter) < np.max(base_filter_spec) * 0.2
        out_filter_wl = np.array(specwl_)[out_filter_index]
        out_filter_spec = np.array(base_filter_spec)[out_filter_index]
    else:
        out_filter_wl = specwl_
        out_filter_spec = base_filter_spec

    # interpolate & smooth
    interp = interp1d(out_filter_wl, out_filter_spec, kind='quadratic')
    window_size, poly_order = 21, 3
    specwl = np.linspace(out_filter_wl[0], out_filter_wl[-1], len(specwl_) * 4)
    spec = savgol_filter(interp(specwl), window_size, poly_order, mode='nearest')

    return specwl, spec


def intensity(wl):
    mean, std = 532, 2
    I = (1/(std*np.sqrt(2))) * np.exp(-(1/2) * ((wl - mean) / std) ** 2)
    I = np.array(I)
    return I


def kernel(theta, wl, d, N):
    wls_over_d = wl / d
    inter = (np.sin(N*np.pi*np.sin(theta)/wls_over_d)/(N*np.sin(np.pi*np.sin(theta)/wls_over_d))+1e-4)**2
    return inter


def convolution(foo, d, N):
    wl, I, specwl = foo
    thetaz = np.arcsin(specwl / d)
    spec = [sum(kernel(theta, wl, d, N) * I) for theta in thetaz]
    spec = np.array(spec)
    return spec


def deconvolution(wl, specwl, spec, d, N):
    thetaz = np.arcsin(specwl / d)
    Izs = [kernel(theta, wl, d, N) for theta in thetaz]
    Izs = np.array(Izs)
    Is_ = np.linalg.lstsq(Izs, spec, rcond=None)[0]
    return Is_


def alignment(wl, I, specwl, spec):
    pass


if __name__ == '__main__':
    wl, I = np.array(LED['wl']), np.array(LED['I'])
    specwl, spec = np.array(LED_SPEC['specwl']), np.array(LED_SPEC['spec'])
    popt, pcov = curve_fit(convolution, (wl, I, specwl), spec)
    d, N = popt


# if __name__ == '__main__':
#     wls = np.linspace(480, 520, 5000)
#     thetaz = np.linspace(-np.pi / 2, np.pi / 2, 5000)
#     Is = intensity(wls)
#     interference_Iz = convolution(Is, wls, thetaz)
#     Is_ = deconvolution(interference_Iz, wls, thetaz)
#
#     fig, axes = plt.subplots(1, 3, figsize=(24, 8))
#     axes[0].plot(wls, Is)
#     axes[0].set_xlim(480, 520)
#     axes[1].plot(np.sin(thetaz) * d, interference_Iz)
#     axes[1].set_xlim(480, 520)
#     axes[2].plot(wls, Is_)
#     axes[2].set_xlim(480, 520)
#     plt.show(fig)
