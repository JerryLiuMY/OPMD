from OPMD_acq.default_startup import cl, tb, ccdop, ccdtp, conf
import pyqtgraph as pg

#   cl: pyfoxtrot Client (same as used before)
#   tb: pyfoxtrot Testbench (as used before)
#   ccdop: pyfoxtrot OPMD_CCDOP object (to control CCD voltages, timings etc)
#   ccdtp: pyfoxtrot CCD object, which contains metadata about the CCD (not used much interactive)
#   conf: pyfoxtrot conf object, which sets up where data is stored etc

if not ccdop.power:
    ccdop.power = True

ccdop.integration_time = 1.0

# dark frame
ccdop.params.setandapply("LIGHT", 0)  # disable shutter to the slow source
ccdop.params.setandapply("LED_ENABLE", 0)  # disable LED light source
frame, en = ccdop.capture_frame_integrated_radiometry_manual(tb)
print(en)  # energy (in J)
pg.show(frame, title="dark frame")

# light frame
ccdop.params.setandapply("LED_ENABLE", 1)
frame2, en = ccdop.capture_frame_integrated_radiometry_manual(tb)
print(en)

with ccdop.backbias_context(-60.0):
    frame3 = ccdop.capture_frame_simple()

# to change gate width
ccdop.params.setandapply("WIDEINT", 1)  # use two gates to integrate

# to look at how to run experiments, look at the file OPMD_acq/runs/BFE_gatewidth_test.py
# which is the experiment I briefly ran last year for initial gate width testing
