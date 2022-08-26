from astropy.io import fits
import os
from global_settings import EXPERIMENT_FOLDER
import seaborn as sns
import numpy as np
from sklearn import linear_model
from tqdm import tqdm_notebook
import matplotlib.pyplot as plt
sns.set()


FRAME_FOLDER = os.path.join(EXPERIMENT_FOLDER, 'frames')

file_list = ['PTC20-21-03-05-54-13.fits', 'PTC20-21-03-05-58-39.fits', 'PTC20-21-03-19-19-04.fits',
             'PTC20-21-03-19-19-05.fits', 'PTC20-21-03-19-23-06.fits']
CHANNEL_7 = [5, 6, 7, 10, 11, 4, 13]
CHANNEL_5 = [5, 6, 7, 10]


def load_hdul(file_name):
    hdul = fits.open(os.path.join(FRAME_FOLDER, file_name))
    vbb, wideint = hdul[1].header['VBB'], hdul[1].header['WIDEINT']
    wwideint = hdul[1].header['WWIDEINT'] if 'WWIDEINT' in hdul[1].header else None

    return hdul, vbb, wideint, wwideint


def load_data(hdul, C, cutoff=1):
    channel_data = hdul[1].data[hdul[1].data['chans'] == C]
    mean = channel_data['mn1db'] - channel_data['mn1db'][0]
    diffvr = channel_data['diffvr'] - channel_data['diffvr'][0]

    mean, diffvr = dip_remove(mean, diffvr)
    alpha, gain = gain_fit(mean, diffvr)
    # old_gain = (mean[10] - mean[0]) / (diffvr[10] - diffvr[0])

    mean_el, diffvr_el = mean[: int(400 * cutoff)] * gain, diffvr[: int(400 * cutoff)] * (gain ** 2)
    corr = channel_data['correls'].reshape(400, 10, 10)[:int(400 * cutoff), :, :]

    return mean_el, diffvr_el, corr, gain


def gain_fit(mean, diffvr, cutoff=0.75):
    z = np.polyfit(mean[: int(400 * cutoff)], diffvr[: int(400 * cutoff)], deg=2)
    alpha, gain = z[0], 1/(z[1])

    return alpha, gain


def dip_remove(mean, diffvr, cutoff=0.75):
    mean_raw, diffvr_raw = mean.copy(), diffvr.copy()
    mean, diffvr = mean[: int(400 * cutoff)], diffvr[: int(400 * cutoff)]

    # Polynomial Fit & Residual Fit
    z = np.polyfit(mean, diffvr, deg=2)
    p = np.poly1d(z)
    ransac = linear_model.RANSACRegressor(residual_threshold=30, stop_probability=0.99)
    ransac.fit(mean.reshape(-1, 1), diffvr - p(mean))
    inl_mask = ransac.inlier_mask_
    out_mask = np.logical_not(inl_mask)

    # Second Polynomial Fit
    z = np.polyfit(mean[inl_mask], diffvr[inl_mask], deg=2)
    p = np.poly1d(z)

    # Interpolation
    int_mask = np.logical_and(mean >= max(mean_raw) * 0.18, mean <= max(mean_raw) * 0.4)
    out_mask = np.logical_and(out_mask, int_mask)
    diffvr_el_out = p(mean[out_mask])
    np.place(diffvr, out_mask, diffvr_el_out)

    # join
    mean = np.concatenate([mean, mean_raw[int(400 * cutoff):]])
    diffvr = np.concatenate([diffvr, diffvr_raw[int(400 * cutoff):]])

    return mean, diffvr


def poly_fit(mean_el, diffvr_el, deg):
    z_1 = np.polyfit(mean_el, diffvr_el, deg=1)
    diffvr_el_1 = np.poly1d(z_1)(mean_el)
    z_n = np.polyfit(mean_el, diffvr_el, deg=deg)
    diffvr_el_n = np.poly1d(z_n)(mean_el)

    return diffvr_el_1, diffvr_el_n

def simulation(trials, mean=10**2):
    loss = []
    for _ in tqdm_notebook(np.arange(trials)):
        data = np.random.poisson(mean, int(4096 * 4096 / 16))
        mean, std = np.mean(data), np.std(data)

        inlier_mask = (abs(data - mean) < 3 * std)
        data_in = data[inlier_mask]
        mean_in, std_in = np.mean(data_in), np.std(data_in)

        loss.append((std - std_in) / std)

    return loss


def run_simulation():
    means = [10, 50, 100, 300, 500, 1000, 5000, 10000]
    average_losses = []
    for mean in means:
        loss = simulation(100, mean)
        average_losses.append(np.mean(loss))

    plt.plot(means, average_losses)


# def calculate_correlation_coeffs(dat, nx=10, ny=10):
#     out = np.zeros((nx, ny))
#     s = np.sum(dat**2)
#     for i in range(nx):
#         for j in range(ny):
#             out[i, j] = np.sum(np.roll(dat, (i, j), (0, 1)) * dat) / s
#     return out