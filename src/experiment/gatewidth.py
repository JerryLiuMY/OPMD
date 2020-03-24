from OPMD_acq.default_startup import tb, ccdop, ccdtp
from OPMD_acq.experiments.PTC import PTC
from OPMD_acq.config import Config
from OPMD_acq.experiments.ExperimentalRun import ExperimentalRun
from OPMD_acq.e2v_CCD250 import e2v_CCD250
import pyqtgraph as pg
ccd = e2v_CCD250(34)
run = ExperimentalRun("BFE_gatewidth_test",
                      "testing whether BFE depends on collecting gate width")
if not ccdop.power:
    ccdop.power = True

run.metaparam_keys.append("VBB")
run.metaparam_keys.append("WIDEINT")
cf = Config()

# ccdop: pyfoxtrot OPMD_CCDOP object (to control CCD voltages, timings etc)
# ccdtp: pyfoxtrot CCD object, which contains metadata about the CCD (not used much interactive)


def expt():
    print("running PTC with narrow collecting gate")

    for VBB, wideint in [(0.0, 0), (0.0, 1), (-60.0, 0), (-60.0, 1)]:
        expt = PTC(tb, ccdop, ccdtp, notes="gate width BFE tests")
        expt.metaparams["VBB"] = VBB
        expt.metaparams["WIDEINT"] = wideint
        expt.initialize_experiment(minexptime=0.0, maxexptime=5.0, npairs=40, led=True, light=False, nbiases=5,
                                   ignite_lamp=False, radiometry=True, wavelength=550.0, lampcurrent=10.0)
        ccdop.params.setandapply("WIDEINT", wideint)

        with ccdop.backbias_context(float(VBB)):
            yield expt


def dark_frame():
    ccdop.params.setandapply("LIGHT", 0)
    ccdop.params.setandapply("LED_ENABLE", 0)
    ccdop.integration_time = 1.0
    frame, en = ccdop.capture_frame_integrated_radiometry_manual(tb)
    pg.show(frame, title="dark frame")
    print(en)

    with ccdop.backbias_context(-30.0):
        frame = ccdop.capture_frame_simple()

    return frame


def light_frame():
    ccdop.params.setandapply("LED_ENABLE", 1)
    ccdop.integration_time = 1.0
    frame, en = ccdop.capture_frame_integrated_radiometry_manual(tb)
    pg.show(frame, title="light frame")
    print(en)

    with ccdop.backbias_context(-60.0):
        frame = ccdop.capture_frame_simple()

    ccdop.params.setandapply("WIDEINT", 1)

    return frame
