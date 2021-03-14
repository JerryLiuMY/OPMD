#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  4 16:38:30 2018

@author: weatherill
"""

import numpy as np
import os
from OPMD_eotest.datafile import DataFile
#from OPMD_acq.viewer import Viewer
import numpy.ma as ma
from skimage.morphology import label, remove_small_objects

def local_medvar_mask(data,divisor=(77,128)):
    outmed = data.copy()
    outstd = data.copy()
    xsecs = data.shape[0] // divisor[0]
    ysecs = data.shape[1] // divisor[1]
    
    for i in range(xsecs):
        for j in range(ysecs):
            d = data[i*divisor[0] : (i+1) * divisor[0], j*divisor[1] : (j+1)*divisor[1]]
            md = np.median(d)
            std = np.std(d)
            outmed[i*divisor[0] : (i+1) * divisor[0], j*divisor[1] : (j+1)*divisor[1]] = md
            outstd[i*divisor[0] : (i+1) * divisor[0], j*divisor[1] : (j+1)*divisor[1]] = std
            
    return outmed,outstd


def guyonnet_mask(data, divisor=(77,128),thresh_consider=2.0, thresh_limit=3.0):
    
    #calculate local median, std
    medmask,stdmask = local_medvar_mask(data,divisor)
    
    #mask out anything further away than 2 sigma
    masked_dat = data.view(ma.MaskedArray)
    masked_dat.mask = np.abs( (data - medmask) / stdmask) >= thresh_consider
    
    #local median & std again, using only central pixels
    medmask, stdmask  = local_medvar_mask(masked_dat)
    
    anomaly_mask = np.abs((data - medmask)/stdmask) > thresh_limit
    
    #label mask
    labelled_mask = label(anomaly_mask,connectivity=2)
    remove_small_objects(labelled_mask,min_size=2,connectivity=2,in_place=True)

    outview = data.view(ma.MaskedArray)
    outview.mask = (labelled_mask >0 )
    
    return outview


def guyonnet_mask2(data, imdata_mask1, divisor=(77, 128), thresh_consider=2.0, thresh_limit=3.0):
    # calculate local median, std
    medmask, stdmask = local_medvar_mask(data, divisor)

    # mask out anything further away than 2 sigma
    masked_dat = data.view(ma.MaskedArray)
    masked_dat.mask = np.abs((data - medmask) / stdmask) >= thresh_consider

    # local median & std again, using only central pixels
    medmask, stdmask = local_medvar_mask(masked_dat)

    anomaly_mask = np.abs((data - medmask) / stdmask) > thresh_limit

    # label mask
    labelled_mask = label(anomaly_mask, connectivity=2)
    remove_small_objects(labelled_mask, min_size=2, connectivity=2, in_place=True)

    outview = data.view(ma.MaskedArray)
    outview.mask = (labelled_mask > 0)

    imdata_mask1 = imdata_mask1.view(ma.MaskedArray)
    imdata_mask1.imdata_mask1 = (labelled_mask > 0)

    return outview, imdata_mask1

if __name__ == "__main__":
    DATA_DIR = '/data/lsst/Oxford/CCD/E2V-CCD250-034/flat/1/20180603-235903'
    

    DATA_FILE_1 = "E2V-CCD250-034_flat_flat_000.48_flat1_20180604000509.fits"
    DATA_FILE_2 = "E2V-CCD250-034_flat_flat_000.48_flat2_20180604000518.fits"
    
    
    df1 = DataFile.identify_and_load(os.path.join(DATA_DIR,DATA_FILE_1))
    df2 = DataFile.identify_and_load(os.path.join(DATA_DIR,DATA_FILE_2))
    
    
    CHAN = 15
    hdu = df1.get_channel_hdu(chanid=CHAN)
    hdu2 = df2.get_channel_hdu(chanid=CHAN)
    
    dat1 = df1.subtract_oscan_rowwise(hdu)
    dat2 = df2.subtract_oscan_rowwise(hdu2)
    
    
    diffdat = dat1.astype(np.int32) - dat2.astype(np.int32)
    
    masked = guyonnet_mask(diffdat)    
    correls_masked = calculate_correlation_coeffs(masked)
    correls_norm = calculate_correlation_coeffs(diffdat)