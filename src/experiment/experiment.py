from time import sleep
import numpy as np
from pylab import rcParams
from pyfoxtrot.Client import Client
from OPMD_acq.testbench_funcs import OPMD_TestBench, pm_modes

cl = Client("localhost:50051")
tb = OPMD_TestBench(cl)
rcParams['figure.figsize'] = 24, 8


def init_photodiode(unit):
    tb.setup_photodiode(pm_modes.SINGLESHOT_MANUAL, 1)  # integrating sphere
    tb.photodiode_units = unit
    tb.setup_photodiode(pm_modes.SINGLESHOT_MANUAL, 2)  # ambient
    tb.photodiode_units = unit


def set_wavelength(wl):
    # Setup light source
    print("Getting spectrum and power for wavelength: %2.2f" % wl)
    tb.wavelength = int(wl)
    sleep(0)
    actualwl = tb.wavelength

    return actualwl


def measure_power_meter(repeat):
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
    specwl_ = []
    spec_ = []
    for _ in range(int(repeat)):
        specwl, spec = tb.read_spectrum(int(exposure))
        specwl_.append(specwl)
        spec_.append(spec)
    specwl = np.mean(specwl_, axis=0)
    spec = np.mean(spec_, axis=0)

    return specwl, spec


def measure_power_meters(wls, repeat):
    actualwls = []
    measured_lights = []
    ambient_lights = []

    for wl in wls:
        actualwl = set_wavelength(wl)
        measured_light, ambient_light = measure_power_meter(repeat)
        actualwls.append(actualwl)
        measured_lights.append(measured_light)
        ambient_lights.append(ambient_light)

    return actualwls, measured_lights, ambient_lights


def measure_spectrometers(wls, exposure, repeat):
    actualwls = []
    specwls = []
    specs = []

    for wl in wls:
        actualwl = set_wavelength(wl)
        specwl, spec = measure_spectrometer(exposure, repeat)
        actualwls.append(actualwl)
        specwls.append(specwl)
        specs.append(spec)

    return actualwls, specwls, specs


def measure_boths(wls, exposure, repeat):
    actualwls = []
    measured_lights = []
    ambient_lights = []
    specwls = []
    specs = []

    for wl in wls:
        actualwl = set_wavelength(wl)
        measured_light, ambient_light = measure_power_meter(repeat)
        specwl, spec = measure_spectrometer(exposure, repeat)
        actualwls.append(actualwl)
        measured_lights.append(measured_light)
        ambient_lights.append(ambient_light)
        specwls.append(specwl)
        specs.append(spec)

    return actualwls, measured_lights, ambient_lights, specwls, specs