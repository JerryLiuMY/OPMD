import pickle
import pandas as pd
import numpy as np
from analysis.correction import read_smooth_spectrum

with open('/Users/mingyu/Desktop/OPMD_Mingyu/random/led_spec/20200325-150502.pkl', 'rb') as handle:
    led_spec = pickle.load(handle)
led_spec = pd.DataFrame({'specwl': led_spec['specwls'][0], 'spec': led_spec['specs'][0]})
led_spec.to_csv('/Users/mingyu/Desktop/OPMD_Mingyu/src/tools/led_spec.csv', index=False, header=False)


with open('/Users/mingyu/Desktop/OPMD_Mingyu/random/laser_spec/specs.pkl', 'rb') as handle:
    specs_ = pickle.load(handle)
with open('/Users/mingyu/Desktop/OPMD_Mingyu/random/laser_spec/specwl.pkl', 'rb') as handle:
    specwl_ = pickle.load(handle)

specwls = []
specs = []
for spec_ in specs_:
    specwl, spec = read_smooth_spectrum(specwl_, spec_, out=False)
    specwls.append(specwl)
    specs.append(spec)
specwl = np.mean(specwls, axis=0)
spec = np.mean(specs, axis=0)
laser_spec = pd.DataFrame({'specwl': specwl, 'spec': spec})