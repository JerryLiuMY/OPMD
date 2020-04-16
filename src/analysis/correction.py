import numpy as np
from global_settings import LASER_REAL, LASER_SPEC
import collections
from scipy.signal import savgol_filter, medfilt
from scipy.interpolate import interp1d
from peakutils import baseline
from scipy.signal import butter, filtfilt
import seaborn as sns
sns.set()


def remove_baseline(spec_raw, implementation=0):
    # remove baseline
    if implementation == 0:
        spec_dict = dict(collections.Counter(spec_raw))
        spec_count, spec_sum = 0, 0
        for s in spec_dict.keys():
            if spec_dict[s] > 4:
                spec_count += spec_dict[s]
                spec_sum += s * spec_dict[s]
        base_filter = spec_sum / spec_count
        base_filter_spec = np.array(spec_raw) - base_filter
    elif implementation == 1:
        base_filter = np.mean(medfilt(spec_raw, 2047))
        base_filter_spec = np.array(spec_raw) - base_filter
    elif implementation == 2:
        base_filter = baseline(np.array(spec_raw), deg=0)
        base_filter_spec = np.array(spec_raw) - base_filter
    elif implementation == 3:
        [b, a] = butter(1, 0.0001, btype='highpass')
        base_filter_spec = filtfilt(b, a, spec_raw)
    else:
        raise Exception('Invalid Implementation Mode')

    return base_filter_spec


def smooth_spectrum(specwl_raw, base_filter_spec, out=True):
    # remove outlier
    if out:
        out_filter = medfilt(base_filter_spec, 19)
        out_filter_index = abs(np.array(base_filter_spec) - out_filter) < np.max(base_filter_spec) * 0.07
        out_filter_wl = np.array(specwl_raw)[out_filter_index]
        out_filter_spec = np.array(base_filter_spec)[out_filter_index]
    else:
        out_filter_wl = specwl_raw
        out_filter_spec = base_filter_spec

    # interpolate & smooth
    interp = interp1d(out_filter_wl, out_filter_spec, kind='quadratic')
    window_size, poly_order = 101, 3
    specwl = np.linspace(out_filter_wl[0], out_filter_wl[-1], len(specwl_raw) * 4)
    spec = savgol_filter(interp(specwl), window_size, poly_order, mode='nearest')

    return specwl, spec


def kernel(specwl, wl, N):
    inter = (np.sin(N*np.pi*specwl/wl)/(N*np.sin(np.pi*specwl/wl))+1e-4)**2
    return inter


def convolution(wl, I, specwl, N):
    specwl_, spec_ = np.array(specwl), np.array([sum(kernel(foo, wl, N) * I) for foo in specwl])
    return specwl_, spec_


def deconvolution(wl, specwl, spec, N):
    M = np.array([kernel(foo, wl, N) for foo in specwl])
    wl_, I_ = np.array(wl), np.linalg.lstsq(M, spec)[0]
    return wl_, I_


def load_real(REAL):
    wl_raw, I_raw = np.array(REAL['wl']), np.array(REAL['I'])
    wl = np.linspace(min(wl_raw), max(wl_raw), 50)
    I = interp1d(wl_raw, I_raw)(wl)
    print(f'Real spectrum shape: {np.shape(wl)}')

    return wl, I


def load_measure(SPEC):
    specwl_raw, spec_raw = np.array(SPEC['specwl'])[2500:4300], np.array(SPEC['spec'])[2500:4300]
    specwl = np.linspace(min(specwl_raw), max(specwl_raw), 100000)
    spec = interp1d(specwl_raw, spec_raw)(specwl)
    print(f'Measured spectrum shape: {np.shape(specwl)}')

    return specwl, spec


def diode_bias(wl_, I_, r):
    interp = interp1d(wl_, I_, kind='quadratic')
    specwl = np.arange(int(min(wl_)) + 1, int(max(wl_)))
    spec = interp(specwl)

    wl = np.arange(300, 1300)
    r, rp = r[np.logical_and(wl >= min(specwl), wl <= max(specwl))], r[wl == 556][0]

    real_power = sum(spec)
    meas_power = sum(spec * r) / rp

    return real_power, meas_power, r


if __name__ == '__main__':
    wl, I = load_real(LASER_REAL)
    specwl, spec = load_measure(LASER_SPEC)
    specwl_, spec_ = convolution(wl, I, specwl, 180)
