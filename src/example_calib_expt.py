# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

from pyfoxtrot.Client import Client
from OPMD_acq.testbench_funcs import OPMD_TestBench
from OPMD_acq.testbench_funcs import pm_modes

from time import sleep

cl = Client("localhost:50051")
tb = OPMD_TestBench(cl)

wls = [450, 470, 490, 510, 530, 550, 570, 600, 620, 640]

actual_wls = []
specs = []

ambient_light = []
measured_light = []

N_LIGHTMEAS = 10

R1 = []
R2 = []

#setting up photodiodes
tb.setup_photodiode(pm_modes.SINGLESHOT_MANUAL, 1) #in the integrating sphere
tb.photodiode_units = "A"
tb.setup_photodiode(pm_modes.SINGLESHOT_MANUAL, 2) #ambient
tb.photodiode_units = "A"


for wl in wls:
    print("getting spectrum and power for wavelength: %2.2f" % wl)
    tb.wavelength = wl
    sleep(5)
    actual_wls.append(tb.wavelength)
    
    specwls, spec = tb.read_spectrum(200)
    
    specs.append(spec)
    
    ambient = [tb.measure_photodiode(2) for _ in range(10)]
    isphere = [tb.measure_photodiode(1) for _ in range(10)]
    
    ambient_light.append(ambient)
    measured_light.append(isphere)
   
    R1.append(tb.get_photodiode_responsivity(1))
    R2.append(tb.get_photodiode_responsivity(2))
     
#%%
import numpy as np    

measured_light = np.array(measured_light)
av_measured = np.median(measured_light,axis=1)
err_measured = np.std(measured_light, axis=1)