import numpy as np
import matplotlib.pyplot as plt


def intensity(wls):
    mean, std = 532, 2
    Is = (1/(std*np.sqrt(2))) * np.exp(-(1/2)*((wls-mean)/std)**2)
    Is = np.array(Is)
    return Is


def kernel(theta, wls, d, N):
    wls_over_d = wls / d
    inter = (np.sin(N*np.pi*np.sin(theta)/wls_over_d)/(N*np.sin(np.pi*np.sin(theta)/wls_over_d))+1e-4)**2
    return inter


def convolution(Is, wls, wlz, d, N):
    thetaz = np.arcsin(wlz/d)
    Iz = [sum(kernel(theta, wls, d, N) * Is) for theta in thetaz]
    Iz = np.array(Iz)
    return Iz


def deconvolution(Iz, wls, wlz, d, N):
    thetaz = np.arcsin(wlz / d)
    Izs = [kernel(theta, wls, d, N) for theta in thetaz]
    Izs = np.array(Izs)
    Is_ = np.linalg.lstsq(Izs, Iz, rcond=None)[0]
    return Is_


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
