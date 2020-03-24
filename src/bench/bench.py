from time import sleep
import numpy as np
from pylab import rcParams
from pyfoxtrot.Client import Client
from OPMD_acq.testbench_funcs import OPMD_TestBench, pm_modes
from datetime import datetime
from tools.utils import times2seconds

cl = Client("localhost:50051")
tb = OPMD_TestBench(cl)
rcParams['figure.figsize'] = 24, 8


def init_photodiode(unit):
    tb.setup_photodiode(pm_modes.SINGLESHOT_MANUAL, 1)  # integrating sphere
    tb.photodiode_units = unit
    tb.setup_photodiode(pm_modes.SINGLESHOT_MANUAL, 2)  # ambient
    tb.photodiode_units = unit


def set_wavelength(wl):
    print("Setting the wavelength of the slow source to: %2.2f" % wl)
    if abs(wl - tb.wavelength) < 0.1:
        tb.wavelength = int(wl)
        sleep(1)

    else:
        tb.wavelength = int(wl)
        sleep(10)

    actualwl = tb.wavelength

    return actualwl


def measure_power_meter(repeat):
    """
    Measure the power meter intensity for "repeat" number of repeated experiments
    :param repeat: (int) The number of repeated experiments
    :return measured_light: (int) average intensity of the light source
    :return ambient_light: (int) average intensity of the ambient light
    """
    measured_light_ = []
    ambient_light_ = []

    for _ in range(int(repeat)):
        measured_light = tb.measure_photodiode(1)
        ambient_light = tb.measure_photodiode(2)
        measured_light_.append(measured_light)
        ambient_light_.append(ambient_light)
    measured_light = np.mean(measured_light_, axis=0)
    ambient_light = np.mean(ambient_light_, axis=0)

    return measured_light, ambient_light


def measure_spectrometer(exposure, repeat):
    """
    Measure the spectrometer central wavelength and peak intensity for "repeat" number of repeated experiments
    :param exposure: (int) The exposure time of the spectrometer
    :param repeat: (int) The number of repeated experiments
    :return specwl: (list) The spectral wavelength of the spectrometer
    :return spec: (int) The spectral intensity at the wavelengths
    """

    specwl_ = []
    spec_ = []

    for _ in range(int(repeat)):
        specwl, spec = tb.read_smooth_spectrum(int(exposure), implementation=1)
        specwl_.append(specwl)
        spec_.append(spec)
    specwl = np.mean(specwl_, axis=0)
    spec = np.mean(spec_, axis=0)

    return specwl, spec
