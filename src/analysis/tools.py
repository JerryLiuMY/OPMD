from astropy.io import fits
import os
from global_settings import EXPERIMENT_FOLDER
import seaborn as sns
sns.set()
FRAME_FOLDER = os.path.join(EXPERIMENT_FOLDER, 'frames')


def load_hdul(file_name):
    hdul = fits.open(os.path.join(FRAME_FOLDER, file_name))
    vbb, wideint = hdul[1].header['VBB'], hdul[1].header['WIDEINT']
    wwideint = hdul[1].header['WWIDEINT'] if 'WWIDEINT' in hdul[1].header else None

    return hdul, vbb, wideint, wwideint


def load_data(hdul, C):
    channel_data = hdul[1].data[hdul[1].data['chans'] == C]
    mean = channel_data['mn1db']
    diffvr = channel_data['diffvr']
    corr = channel_data['correls'].reshape(400, 10, 10)
    gain = (channel_data['mn1db'][11] - channel_data['mn1db'][1]) / (channel_data['diffvr'][11] - channel_data['diffvr'][1])
    mean_el, diffvr_el = mean * gain, diffvr * (gain ** 2)

    return mean_el, diffvr_el, corr, gain