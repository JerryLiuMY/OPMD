from astropy.io import fits
import os
from global_settings import EXPERIMENT_FOLDER
import seaborn as sns
import numpy as np
from sklearn import linear_model
sns.set()

FRAME_FOLDER = os.path.join(EXPERIMENT_FOLDER, 'frames')

file_list = ['PTC20-21-03-05-54-13.fits', 'PTC20-21-03-05-58-39.fits', 'PTC20-21-03-19-19-04.fits',
             'PTC20-21-03-19-19-05.fits', 'PTC20-21-03-19-23-06.fits']
CHANNEL_7 = [5, 6, 7, 10, 11, 4, 13]
CHANNEL_5 = [5, 6, 7, 10, 11]


def load_hdul(file_name):
    hdul = fits.open(os.path.join(FRAME_FOLDER, file_name))
    vbb, wideint = hdul[1].header['VBB'], hdul[1].header['WIDEINT']
    wwideint = hdul[1].header['WWIDEINT'] if 'WWIDEINT' in hdul[1].header else None

    return hdul, vbb, wideint, wwideint


def load_data(hdul, C, cutoff=0.95):
    channel_data = hdul[1].data[hdul[1].data['chans'] == C]
    mean = channel_data['md1'][:int(400*cutoff)]
    diffvr = channel_data['diffvr'][:int(400*cutoff)]
    corr = channel_data['correls'].reshape(400, 10, 10)[:int(400*cutoff), :, :]
    gain = (channel_data['mn1db'][11] - channel_data['mn1db'][1]) / (channel_data['diffvr'][11] - channel_data['diffvr'][1])
    mean_el, diffvr_el = mean * gain, diffvr * (gain ** 2)

    return mean_el, diffvr_el, corr, gain


def inlier(mean_el, diffvr_el):
    z = np.polyfit(mean_el, diffvr_el, deg=2)
    p = np.poly1d(z)
    ransac = linear_model.RANSACRegressor(residual_threshold=100, stop_probability=0.99)
    ransac.fit(mean_el.reshape(-1, 1), diffvr_el - p(mean_el))
    inlier_mask = ransac.inlier_mask_
    outlier_mask = np.logical_not(inlier_mask)

    diffvr_el_out = p(mean_el[outlier_mask])
    np.place(diffvr_el, outlier_mask, diffvr_el_out)

    return mean_el, diffvr_el


def poly_fit(mean_el, diffvr_el, deg):
    z_1 = np.polyfit(mean_el, diffvr_el, deg=1)
    diffvr_el_1 = np.poly1d(z_1)(mean_el)
    z_n = np.polyfit(mean_el, diffvr_el, deg=deg)
    diffvr_el_n = np.poly1d(z_n)(mean_el)

    return diffvr_el_1, diffvr_el_n
