from astropy.io import fits
import os
from global_settings import EXPERIMENT_FOLDER
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.colors
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


def load_data(hdul, C, cutoff=0.75):
    channel_data = hdul[1].data[hdul[1].data['chans'] == C]
    mean = channel_data['mn1db'] - channel_data['mn1db'][0]
    diffvr = channel_data['diffvr'] - channel_data['diffvr'][0]
    mean, diffvr = dip_remove(mean, diffvr)
    mean, diffvr = mean[: int(400 * cutoff)], diffvr[: int(400 * cutoff)]
    corr = channel_data['correls'].reshape(400, 10, 10)[:int(400 * cutoff), :, :]

    alpha = np.polyfit(mean, diffvr, deg=2)[0]
    gain = 1/(np.polyfit(mean, diffvr, deg=2)[1])
    # old_gain = (mean[10] - mean[0]) / (diffvr[10] - diffvr[0])
    mean_el, diffvr_el = mean * gain, diffvr * (gain ** 2)

    # print('Channel:', C, 'alpha:', alpha, ';', 'gain:', gain, 'old gain:', old_gain)
    # print(abs(old_gain-gain)/gain)

    return mean_el, diffvr_el, corr, gain


def dip_remove(mean_el, diffvr_el, cutoff=0.75):
    mean_el_raw, diffvr_el_raw = mean_el.copy(), diffvr_el.copy()
    mean_el, diffvr_el = mean_el[: int(400 * cutoff)], diffvr_el[: int(400 * cutoff)]

    # Polynomial Fit & Residual Fit
    z = np.polyfit(mean_el, diffvr_el, deg=2)
    p = np.poly1d(z)
    ransac = linear_model.RANSACRegressor(residual_threshold=20, stop_probability=0.99)
    ransac.fit(mean_el.reshape(-1, 1), diffvr_el - p(mean_el))
    inl_mask = ransac.inlier_mask_
    out_mask = np.logical_not(inl_mask)

    # Second Polynomial Fit
    z = np.polyfit(mean_el[inl_mask], diffvr_el[inl_mask], deg=2)
    p = np.poly1d(z)

    # Interpolation
    int_mask = np.logical_and(mean_el >= max(mean_el_raw) * 0.2, mean_el <= max(mean_el_raw) * 0.4)
    out_mask = np.logical_and(out_mask, int_mask)
    diffvr_el_out = p(mean_el[out_mask])
    np.place(diffvr_el, out_mask, diffvr_el_out)

    mean_el = np.concatenate([mean_el, mean_el_raw[int(400 * cutoff):]])
    diffvr_el = np.concatenate([diffvr_el, diffvr_el_raw[int(400 * cutoff):]])

    return mean_el, diffvr_el


def poly_fit(mean_el, diffvr_el, deg):
    z_1 = np.polyfit(mean_el, diffvr_el, deg=1)
    diffvr_el_1 = np.poly1d(z_1)(mean_el)
    z_n = np.polyfit(mean_el, diffvr_el, deg=deg)
    diffvr_el_n = np.poly1d(z_n)(mean_el)

    return diffvr_el_1, diffvr_el_n


def make_bar(ax, x0=0, y0=0, width = 0.5, height=1 , cmap="viridis",
              norm=matplotlib.colors.Normalize(vmin=0, vmax=1), **kwargs ):
    # Make data
    u = np.linspace(0, 2*np.pi, 4+1)+np.pi/4.
    v_ = np.linspace(np.pi/4., 3./4*np.pi, 100)
    v = np.linspace(0, np.pi, len(v_)+2 )
    v[0] = 0 ;  v[-1] = np.pi; v[1:-1] = v_
    x = np.outer(np.cos(u), np.sin(v))
    y = np.outer(np.sin(u), np.sin(v))
    z = np.outer(np.ones(np.size(u)), np.cos(v))

    xthr = np.sin(np.pi/4.)**2 ;  zthr = np.sin(np.pi/4.)
    x[x > xthr] = xthr; x[x < -xthr] = -xthr
    y[y > xthr] = xthr; y[y < -xthr] = -xthr
    z[z > zthr] = zthr  ; z[z < -zthr] = -zthr

    x *= 1./xthr*width; y *= 1./xthr*width
    z += zthr
    z *= height/(2.*zthr)
    #translate
    x += x0; y += y0
    #plot
    ax.plot_surface(x, y, z, cmap=cmap, norm=norm, **kwargs)


def make_bars(ax, x, y, height, width=1):
    widths = np.array(width)*np.ones_like(x)
    x = np.array(x).flatten()
    y = np.array(y).flatten()

    h = np.array(height).flatten()
    w = np.array(widths).flatten()
    norm = matplotlib.colors.Normalize(vmin=0, vmax=h.max())
    for i in range(len(x.flatten())):
        make_bar(ax, x0=x[i], y0=y[i], width = w[i] , height=h[i], norm=norm)


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
