import pandas as pd

PROJECT_FOLDER = '/Users/mingyu/Desktop/OPMD_Mingyu'
CALIBRATION_FOLDER = '/Users/mingyu/Desktop/OPMD_Mingyu/results/calibration'
EXPERIMENT_FOLDER = '/Users/mingyu/Desktop/OPMD_Mingyu/results/experiment'
LASER_REAL = pd.read_csv('tools/laser.csv', header=None, names=['wl', 'I'])
LED_REAL = pd.read_csv('tools/led.csv', header=None, names=['wl', 'I'])
LASER_SPEC = pd.read_csv('tools/laser_spec.csv', header=None, names=['specwl', 'spec'])
LED_SPEC = pd.read_csv('tools/led_spec.csv', header=None, names=['specwl', 'spec'])
