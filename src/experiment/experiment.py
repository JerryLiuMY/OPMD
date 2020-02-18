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


def measure_power_meters(wls, repeat):
    """
    Measure the power meter intensities for "repeat" number of repeated experiments for each wavelength in wls
    """
    actualwls = []
    measured_lights = []
    ambient_lights = []
    times = []

    for wl in wls:
        actualwl = set_wavelength(wl)
        time = datetime.now()
        measured_light, ambient_light = measure_power_meter(repeat)

        actualwls.append(actualwl)
        measured_lights.append(measured_light)
        ambient_lights.append(ambient_light)
        times.append(time)

    seconds = times2seconds(times)

    return actualwls, measured_lights, ambient_lights, seconds


def measure_spectrometers(wls, exposure, repeat):
    """
    Measure the spectrometer spectral wavelengths and spectral intensity for "repeat" number of repeated experiments for
    each wavelength in wls
    """
    actualwls = []
    specwls = []
    specs = []
    times = []

    for wl in wls:
        actualwl = set_wavelength(wl)
        time = datetime.now()
        specwl, spec = measure_spectrometer(exposure, repeat)

        actualwls.append(actualwl)
        specwls.append(specwl)
        specs.append(spec)
        times.append(time)

    seconds = times2seconds(times)

    return actualwls, specwls, specs, seconds


def measure_boths(wls, exposure, repeat):
    """
    Measure both the power meter intensities and spectrometer spectral wavelengths and spectral intensity for "repeated"
    number of repeated experiments for each wavelength in wls
    """
    actualwls = []
    measured_lights = []
    ambient_lights = []
    specwls = []
    specs = []
    times = []

    for wl in wls:
        actualwl = set_wavelength(wl)
        time = datetime.now()
        measured_light, ambient_light = measure_power_meter(repeat)
        specwl, spec = measure_spectrometer(exposure, repeat)

        actualwls.append(actualwl)
        measured_lights.append(measured_light)
        ambient_lights.append(ambient_light)
        specwls.append(specwl)
        specs.append(spec)
        times.append(time)

    seconds = times2seconds(times)

    return actualwls, measured_lights, ambient_lights, specwls, specs, seconds
