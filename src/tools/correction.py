import numpy as np
import matplotlib.pyplot as plt

d = 1000
N = 100


def gaussian_intensity(wls):
    mean, std = 500, 2
    Is = (1/(std*np.sqrt(2))) * np.exp(-(1/2)*((wls-mean)/std)**2)
    return Is


def kernel(theta, wls):
    wls_over_d = wls / d
    interference_Is = (np.sin(N*np.pi*np.sin(theta)/wls_over_d)/(N*np.sin(np.pi*np.sin(theta)/wls_over_d))+1e-4)**2
    return interference_Is


def convolution(Is, wls, thetaz):
    interference_Iz = []
    for theta in thetaz:
        interference_I = sum(kernel(theta, wls) * Is)
        interference_Iz.append(interference_I)
    interference_Iz = np.array(interference_Iz)
    return interference_Iz


def deconvolution(interference_Iz, wls, thetaz):
    interference_Izs = []
    for theta in thetaz:
        interference_Is = kernel(theta, wls)
        interference_Izs.append(interference_Is)
    interference_Izs = np.array(interference_Izs)
    Is_ = np.linalg.lstsq(interference_Izs, interference_Iz, rcond=None)[0]
    return Is_


if __name__ == '__main__':
    wls = np.linspace(480, 520, 5000)
    thetaz = np.linspace(-np.pi / 2, np.pi / 2, 5000)
    Is = gaussian_intensity(wls)
    interference_Iz = convolution(Is, wls, thetaz)
    Is_ = deconvolution(interference_Iz, wls, thetaz)

    fig, axes = plt.subplots(1, 3, figsize=(24, 8))
    axes[0].plot(wls, Is)
    axes[0].set_xlim(480, 520)
    axes[1].plot(np.sin(thetaz) * d, interference_Iz)
    axes[1].set_xlim(480, 520)
    axes[2].plot(wls, Is_)
    axes[2].set_xlim(480, 520)
    plt.show(fig)
