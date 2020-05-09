# -*- coding: utf-8 -*-

import os
from OPMD_eotest.DataReduction import DataReduction, standard_reduction

from OPMD_eotest.datafile import DataFile, Oxford_data
from OPMD_eotest.imagetypes import LogicalImage

from astropy.io import fits
from warnings import warn

from OPMD_eotest.master_bias import construct_median_bias

from OPMD_eotest.overscan import oxford_serial_overscan_edges_removed, remove_serial_overscan_cti
import json
import numpy as np

from OPMD_eotest.analysis.elaborate_masking import guyonnet_mask

from datetime import datetime

from scipy.ndimage.filters import median_filter
from skimage.morphology import remove_small_objects

from scipy.constants import h,c

PIX_AREA = 10E-4**2 #pixel area in square cm (10um by 10 um)

def get_cti_poscan(chanid,poscan,spscan,soscan):
    prescan_pix = spscan.shape[1]
    oscan_pix = soscan.shape[1]
    if chanid > 8:
        return poscan[:,slice(oscan_pix,-prescan_pix)]
    else:
        return poscan[:,slice(prescan_pix,-oscan_pix)]

def get_cti_soscan(chanid,poscan,spscan,soscan):
    poscan_pix = poscan.shape[0]
    if chanid > 8 : 
        return soscan[poscan_pix:,:]
    else:
        return soscan[:-poscan_pix,:]


def get_EPER_traces(df, chanid):
    hdu = df.get_channel_hdu(chanid=chanid)
    poscan,spscan,soscan = df.get_overscans(hdu)
    pp = get_cti_poscan(chanid,poscan,spscan,soscan)
    ss = get_cti_soscan(chanid,poscan,spscan,soscan)
    
    pp = pp.astype(np.float64) - np.median(pp,axis=0)
    ss = ss.astype(np.float64) - np.median(ss,axis=1).reshape((ss.shape[0],1))
    
    EPER_trace_llel = np.median(pp,axis=1)
    EPER_trace_ser = np.median(ss,axis=0)
    
    if chanid > 8:
        return EPER_trace_llel[::-1], EPER_trace_ser[::-1]
    else:   
        return EPER_trace_llel, EPER_trace_ser
    

def radiometry_calc(df):
    if "J_EN" in df.oxtestcond.header:
        area = df.oxtestcond.header["DIODE_A"]
        wavelen = df.prihdr["MONOWL"]
        energy_per_area = df.oxtestcond.header["J_EN"] / area # J / cm^2
        energy_per_pixel = energy_per_area * PIX_AREA
        energy_per_photon = h*c / (wavelen * 1E-9)
        photons_per_pixel = energy_per_pixel/ energy_per_photon
        return photons_per_pixel


class PTC(DataReduction):
    VARIABLES = ["exps","chans","oscanmd1","oscanmd2","oscanmn1","oscanmn2",
                 "oscanvr1","oscanvr2","oscandvr","mn1","mn2","mn1db","mn2db",
                 "md1","md2","md1db","md2db","vr1","vr2","vr1db","vr2db",
                 "diffmd","diffmn","diffvr","correls","poscanmd1","poscanmd2","poscanvr1","poscanvr2","poscandvr",
                 "photons1", "photons2","temp1","temp2","filename1","filename2"]

    PARAMETERS = {"TRIM" : int}

    def generate_reduction_sets(self,flist):
        bias_fls = [_ for _ in flist if "bias" in _]

        yield bias_fls

        flat_fls = [_ for _ in flist if "flat1" in _ or "flat2" in _]
        exptimes = [float(_.split("_")[3]) for _ in flat_fls]
        #argsort = [exptimes.index(_,pos) for pos,_ in enumerate(sorted(exptimes))]
        argsort = sorted(range(len(exptimes)),key=exptimes.__getitem__)

        gen = (flat_fls[_] for _ in argsort)
        for g in gen:
            yield g, next(gen)


    def get_image_pixels_to_use(self,dat):
        return dat


    def reset_internal_state(self):
        self.firsttime = True
        super().reset_internal_state()


    def get_etime(self,df):
        return df.get_prihdu().header["EXPTIME"]


    def process_files(self,fls):

        TRIM = self._params["TRIM"]

        
        #correctfun = lambda df, hdu: Oxford_data.subtract_oscan_cti_corrected_single(df,hdu,trim=True)
#        correctfun = lambda df, hdu: Oxford_data.subtract_oscan_cti_corrected_rowwise(df,hdu,trim=True)
        correctfun = lambda df, hdu: DataFile.subtract_oscan_rowwise(df,hdu,trim=True)
        if not hasattr(self,"_biasframe"):
            print("constructing bias frame...")

            arr = []
            for fl in fls:
                print("processing bias file: " + fl)
                df = DataFile.identify_and_load(fl)
                lim = LogicalImage.ingest(df)
                lim.correct_overscan(correctfun)
                arr.append(lim.data)
            self._biasframe = np.median(arr,axis=0)
            return


        df1 = DataFile.identify_and_load(fls[0])
        df2 = DataFile.identify_and_load(fls[1])

        file_etime = self.get_etime(df1)

        print("processing frame pair:")
        print("file1: " + fls[0])
        print("file2: " + fls[1])

        chanlist = df1.consistent_ordered_chanlist
        for ind,ch in enumerate(chanlist):
            self.exps.append(file_etime)
            self.chans.append(ch)
            
            self.photons1.append(radiometry_calc(df1))
            self.photons2.append(radiometry_calc(df2))
            self.temp1.append(df1.prihdr["CCDTEMP"])
            self.temp2.append(df2.prihdr["CCDTEMP"])
            
            self.filename1.append(df1.hdul.filename())
            self.filename2.append(df2.hdul.filename())
            
            hdu1 = df1.get_channel_hdu(chanid=ch)
            hdu2 = df2.get_channel_hdu(chanid=ch)

            poscan1,spscan1,soscan1 = df1.get_overscans(hdu1)
            poscan2,spscan2,soscan2 = df2.get_overscans(hdu2)

            soscan1_use = oxford_serial_overscan_edges_removed(soscan1,ch)
            soscan2_use = oxford_serial_overscan_edges_removed(soscan2,ch)

            soscan1_use = remove_serial_overscan_cti(soscan1_use)
            soscan2_use = remove_serial_overscan_cti(soscan2_use)

            self.oscanmd1.append(np.median(soscan1_use))
            self.oscanmd2.append(np.median(soscan2_use))
            self.oscanmn1.append(np.mean(soscan1_use))
            self.oscanmn2.append(np.mean(soscan2_use))

            p = poscan1.shape[0]

            poscan1trim = poscan1[20:-20,100:-100]
            poscan2trim = poscan2[20:-20,100:-100]
            self.poscanmd1.append(np.median(poscan1trim))
            self.poscanmd2.append(np.median(poscan2trim))
            self.poscanvr1.append(np.var(poscan1trim))
            self.poscanvr2.append(np.var(poscan2trim))

            poscandiff = poscan1trim - poscan2trim
            self.poscandvr.append(np.var(poscandiff)/2.)

            self.oscanvr1.append(np.var(soscan1_use))
            self.oscanvr2.append(np.var(soscan2_use))

            oscandiff = soscan1_use.astype(np.int32) - soscan2_use.astype(np.int32)
            self.oscandvr.append(np.var(oscandiff)/2.)

            imdata1 = df1.subtract_oscan_rowwise(hdu1,trim=True)
            imdata2 = df2.subtract_oscan_rowwise(hdu2,trim=True)

#            imdata1 = df1.subtract_oscan_cti_corrected_rowwise(hdu1,trim=True)
#            imdata2 = df2.subtract_oscan_cti_corrected_rowwise(hdu2,trim=True)

            #trim off edges
            imdata1 = self.get_image_pixels_to_use(imdata1)
            imdata2 = self.get_image_pixels_to_use(imdata2)


            imdata1 = imdata1[TRIM:-TRIM,TRIM:-TRIM]
            imdata2 = imdata2[TRIM:-TRIM,TRIM:-TRIM]
            imdata2 = imdata2 / np.mean(imdata2) * np.mean(imdata1)

            imdata_mask1 = guyonnet_mask(imdata1)
            imdata_mask2 = guyonnet_mask(imdata2)
            

            self.mn1.append(np.mean(imdata_mask1))
            self.mn2.append(np.mean(imdata_mask2))

            self.md1.append(np.median(imdata_mask1))
            self.md2.append(np.median(imdata_mask2))

            self.vr1.append(np.var(imdata_mask1))
            self.vr2.append(np.var(imdata_mask2))

            biasdat = self._biasframe[ind]
            biasdat = self.get_image_pixels_to_use(biasdat)
            biasdat = biasdat[TRIM:-TRIM,TRIM:-TRIM]

            self.mn1db.append(np.mean(imdata_mask1 - biasdat))
            self.mn2db.append(np.mean(imdata_mask2 - biasdat))

            self.md1db.append(np.median(imdata_mask1 - biasdat))
            self.md2db.append(np.median(imdata_mask2 - biasdat))

            self.vr1db.append(np.var(imdata_mask1 - biasdat))
            self.vr2db.append(np.var(imdata_mask2 - biasdat))

            diffim = imdata_mask1 - imdata_mask2
            diffim_mask = guyonnet_mask(diffim)
            diffmd = np.median(diffim_mask)
            self.diffmd.append(diffmd)
            self.diffmn.append(np.mean(diffim_mask))
            self.diffvr.append(np.var(diffim_mask)/2.)

#            mask = simple_masking(diffim)
#            mask = thrash_masking(diffim)
#            diffim -= diffmd
#            diffim[mask] = 0.0

            self.correls.append(calculate_correlation_coeffs_new(imdata_mask1, diffim_mask,10,10).ravel())


#%%

class BinnedPTC(PTC):
    PARAMETERS = {"BINSER" : int,
                  "BINLLEL": int,
                  "TRIM" : int}

    def get_image_pixels_to_use(self,dat):
        binser = self._params["BINSER"]
        binllel = self._params["BINLLEL"]

        llel_bin_pixels = np.array_split(dat,binllel+1,axis=0)[-1]
        ser_bin_pixels = np.array_split(llel_bin_pixels,binser+1,axis=1)[-1]

        return ser_bin_pixels


class InversionThreshold(PTC):
    def generate_reduction_sets(self,flist):
        bias_fls = [_ for _ in flist if "bias" in _]

        yield bias_fls

        flat_fls = [_ for _ in flist if "flat1" in _ or "flat2" in _]
        dates = [int(_.split("_")[-1].split(".fits")[0]) for _ in flat_fls]
        argsort = sorted(range(len(dates)),key=dates.__getitem__)

        gen = (flat_fls[_] for _ in argsort)
        for g in gen:
            yield g, next(gen)


    def get_etime(self,df):
        return df.oxtestcond.header["V_RD1ST"]


class CICPTC(PTC):
    def get_etime(self,df):
        return df.oxtestcond.header["PNPUMP"]


def calculate_correlation_coeffs(dat,nx=10,ny=10):
    out = np.zeros((nx,ny))
    s = np.sum(dat**2)
    for i in range(nx):
        for j in range(ny):
            out[i,j] = np.sum( np.roll(dat,(i,j),(0,1)) * dat) / s
    return out


def calculate_correlation_coeffs_fast(dat,nx=10,ny=10):
    out = np.zeros((nx,ny))
    s = np.sum(dat**2)
    for i in range(nx):
        for j in range(ny):
            slc0 = slice(0,dat.shape[0]-i)
            slc1 = slice(0,dat.shape[1]-j)
            out[i,j] = np.sum(dat[slc0,slc1] * dat[i:,j:]) / s

    return out


def calculate_correlation_coeffs_new(imdata_mask, dat,nx=10,ny=10):
    out = np.zeros((nx,ny))
    s = np.sum(imdata_mask)*2
    for i in range(nx):
        for j in range(ny):
            out[i,j] = np.sum( np.roll(dat,(i,j),(0,1)) * dat) / s
    return out


def simple_masking(dat):
    ma = dat > (3 * np.std(dat))
    return remove_small_objects(ma,min_size=2)

def thrash_masking(dat):
    ma = np.abs(dat) > (4 * np.std(dat))
    return remove_small_objects(ma,min_size=2)


if __name__ == "__main__":
    pass
