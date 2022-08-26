# OPMD

Charge-coupled devices (CCDs) are regular lattices of charge receivers widely used in astronomical imaging. CCDs are generally considered to convert incoming photons into a digital number in each pixel in a linear fashion independent of the condition of surrounding pixels. However, it has been known for some time that the photon transfer curves (PTCs) of flat-field images taken by thick CCDs display abnormal deviations from the expected Poisson photon noise and that the point spread functions (PSFs) of star illuminations tend to broaden with increasing luminosity. This effect is commonly known as the "Brighter-Fatter Effect" (BFE).

This investigation is carried out at the Oxford Physics Microstructure Detector (OPMD) laboratory using an electro-optical test system designed for optimising the operation of CCDs for use in the Large Synoptic Survey Telescope (LSST). The [report](A16731S1_1024507.pdf) is structured as follows:

* First, several stability tests and calibration are carried out to verify the high measurement precision of the test system.
* Next, the investigation studies the brighter-fatter effect of flat-field images by observing the behaviour of the PTC and correlation maps between neighbouring pixels.
  * A quadratic departure of PTC from Poisson statistics and linearly increasing pixel correlations with flux are observed.
  * The correlation coefficients are found to decay rapidly with spatial separation.
* Finally, an electrostatic model that simulates the interaction between the Coulomb field induced by charges stored in CCD pixels and the drift field is presented to explain the observed statistical properties.

## Tests and Calibrations
### Intensity Stability Test
500 power readings are taken with the photodiode over a duration of `4.17 hours` with `30s` intervals between consecutive measurements, in both the integrating sphere and the environment. The Pearson correlation coefficient is very low at `r=-0.046`, suggesting no evidence of stray light leakage into the optical system. 

![alt text](./__resources__/intensity.jpg?raw=true "Title")
**Figure 1:** Measured power of the LED source and the environment in 500 repeated trials over a duration of `4.17 hours`. *Top Left:* Histogram of LED power output measured inside the integrating sphere; *Top Right:* Histogram of ambient light power measured in the environment; *Bottom:* Time-series of the LED and ambient power


### Intensity Stability Test
Raw spectra measured by the spectrometer need to be cleaned and calibrated before actual spectral contents can be obtained. 
- The first step is to remove the bias offset introduced by the analogue-to-digital converter in the downstream circuitry. 
- The second step is to remove outliers caused by bad pixels on the digital sensor. 
- The third step is to interpolate the values at the removed points using a second-order spline interpolation algorithm in Scipy `(Scipy.interpolate.interp1d)`.

![alt text](./__resources__/smooth.jpg?raw=true "Title")
**Figure 2:** The spectra at 12 wavelengths of the Quartz Tungsten Halogen (QTH) lamp. *Top:* Raw spectrum; *Bottom:* Smoothed spectrum

## Flat-Field Experiments
The CCD is illuminated with the same LED source peaked at `556nm` described previously. The operating temperature of the CCD is fixed at `-95 celsius` throughout the experiments. Flat-field images are captured at two backside substrate voltage `BSS=0V` and `-60V` and two collection gate widths `w=3μm` (one gate open) and `w=5μm` (two gates open) respectively. For each BSS and gate width, 400 pairs of flat-field images are taken from zero illumination up to the full well (by gradually increasing integration time from `0s` to `5s`).

### PTC Analysis
![alt text](./__resources__/PTC.jpg?raw=true "Title")
**Figure 3:** *Top Left:* Scaled PTC of four operating channels of CCD E2V-250 in the physical unit of electron charge. Departure from the expected Poisson photon variance `$\sigma_{S}^{2}=\mu$` is observed. *Top Right:* Residuals of the scaled PTCs. They have identical magnitude and grow quadratically with the mean flux. *Bottom:* Residuals of linear and quadratic fit to the four-channel-average PTC.

### Correlation
Spatial correlation between pixels is detected up to a distance of four pixels within the sensitivity limit of the CCD. From the correlation map at `60kel` level , it is observed that correlation is the largest between the nearest neighbours and gradually decays as separation increases. 

![alt text](./__resources__/correlation_map.jpg?raw=true "Title")
**Figure 4:** Flat-field correlation map at `60kel` along the parallel and serial direction. The correlation decreases as pixels get further apart. An anisotropy between the coefficients `$R_{01}$` and `$R_{10}$` is observed. The anisotropy tends to vanish for separation larger than `1 pixel`.

### Restoring Linearity
![alt text](./__resources__/PTC_recovered.jpg?raw=true "Title")
**Figure 5:** Raw PTCs plotted in arbitrary digital unit (ADU) from zero illumination upto `90%` of the full well. Channel 7 has a different response behaviour compared to other channels.
