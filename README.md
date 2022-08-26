# OPMD

Charge-coupled devices (CCDs) are regular lattices of charge receivers widely used in astronomical imaging. CCDs are generally considered to convert incoming photons into a digital number in each pixel in a linear fashion independent of the condition of surrounding pixels. However, it has been known for some time that the photon transfer curves (PTCs) of flat-field images taken by thick CCDs display abnormal deviations from the expected Poisson photon noise and that the point spread functions (PSFs) of star illuminations tend to broaden with increasing luminosity. This effect is commonly known as the "Brighter-Fatter Effect" (BFE).

This investigation is carried out at the Oxford Physics Microstructure Detector (OPMD) laboratory using an electro-optical test system designed for optimising the operation of CCDs for use in the Large Synoptic Survey Telescope (LSST). The [report](final_report.pdf) is structured as follows:

* First, several stability tests and calibration are carried out to verify the high measurement precision of the test system.
* Next, the investigation studies the brighter-fatter effect of flat-field images by observing the behaviour of the PTC and correlation maps between neighbouring pixels.
  * A quadratic departure of PTC from Poisson statistics and linearly increasing pixel correlations with flux are observed.
  * The correlation coefficients are found to decay rapidly with spatial separation.
* Finally, an electrostatic model that simulates the interaction between the Coulomb field induced by charges stored in CCD pixels and the drift field is presented to explain the observed statistical properties.
