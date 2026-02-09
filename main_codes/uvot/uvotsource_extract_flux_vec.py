import os
import pandas as pd
from astropy.io.fits import getheader 
from astropy.io import fits
import sys, os
import numpy as np
from astropy import units as u
from astropy.coordinates import SkyCoord
#from astroquery.ned import Ned

import subprocess 
from os.path import isfile, join
#import extinction

import warnings

# Suppress all warnings
warnings.filterwarnings("ignore")

########################################
#
#--- UVOT Flux determination (from uvotflux task)
#
# Given a count rate in units of counts per second, and a 1-sigma error in the same units, uvotflux will convert the rate into an
# instrumental magnitude (based on UVOT's own filter system) and flux densities in units of erg/s/cm^2/Angstrom. The count rate error is
# propagated through each calculation.  Magnitudes, m, are determined from:
#
# m = ZPT - 2.5 * log_10(C)
#
# where C is a count rate and ZPT is a zero point appropriate to the specific filter.  The zeropoints have been calibrated from standard
# photometry fields and assume all sources have Vega-like spectra. The zero points are stored as FITS keywords within the UVOT CALDB (see
# http://heasarc.gsfc.nasa.gov/docs/heasarc/caldb/swift/docs/uvot/index.html).  Flux densities, F_lam, are calculated by a applying a
# straightforward multiplicative factor to the count rate:
#
# F_lam = FCF * C
#
# FCF is also filter specific and stored as CALDB keywords. Its units are erg/cm^2/angstrom/count.  The conversion factors assume a mean
# gamma-ray burst spectrum.
#
##########################################

#######################


def lambda_to_nu(l):
	c  = 3e10     #cm s-1
	h  = 6.62e-27 #erg s
	nu = c/(l*1e-8) #Hz
	 
	return nu
	

def swift_met_to_mjd(t):
	y = 51910+(t/(60*60*24)) #days
	return y	
	
########################
	

def Al_obs(E_BV, filt): 
    ## from https://arxiv.org/pdf/2308.11664
    ####uvw2, uvm2, uvw1, u, b, v
    filters = np.array(['uw2', 'um2', 'uw1', 'uuu', 'ubb', 'uvv'])
    
    idx = np.where(filters==filt)[0]
    
    R_l = np.array([5.60, 6.99, 4.91, 4.13, 3.41, 2.57])
    
    R_l_s = R_l[idx]
    
    Alambda = E_BV*R_l_s
    
    return Alambda 

def Al_obs_Roming(E_BV, filt): 
    ## from Roming_2009: https://iopscience.iop.org/article/10.1088/0004-637X/690/1/163/pdf
    ####uvw2, uvm2, uvw1, u, b, v
    filters = np.array(['uw2', 'um2', 'uw1', 'uuu', 'ubb', 'uvv'])
    
    idx = np.where(filters==filt)[0]
    
    a_coeff = np.array([-0.0581, 0.0773, 0.4346, 0.9226, 0.9994, 1.0015])
    b_coeff = np.array([ 8.4402, 9.1784, 5.3286, 2.1019, 1.0171, 0.0126])
    
    R_v = 3.1
    
    a_l_s = a_coeff[idx]
    b_l_s = b_coeff[idx]
        
    Alambda = E_BV*(a_l_s*R_v+b_l_s)
    
    return Alambda 

"""
###THIS NEEDS WORK
def Al_obs_Cardelli89(E_BV, filt): 
    ## from Roming_2009: https://iopscience.iop.org/article/10.1088/0004-637X/690/1/163/pdf
    ####uvw2, uvm2, uvw1, u, b, v
    filters   = np.array(['uw2', 'um2', 'uw1', 'uuu', 'ubb', 'uvv'])
    filt_wave = np.array([2030,2231,2634,3501,4329,5402])
    
    idx = np.where(filters==filt)[0]
    
    f = filt_wave[idx]
    print(f)
    
    wave = np.array(f, dtype='double')
    
    A_v = 3.1*E_BV
    
    e = extinction.ccm89(wave, A_v, 3.1, unit="aa")
        
    Alambda = A_v*e
    
    return Alambda, e
"""


def mag_corr_obs(m, Alambda):
	#AB mags
	y = m - Alambda
	return y


def spec_flux_abmag(m, wavel):
    ### www.astronomy.ohio-state.edu/martini.10/usefuldata.html
    ### ABmag = - 2.5 log Fnu - 48.6. 
    ### 3.00x10^18 Fnu/lambda^2 where lambda is in A 
    
    Fnu = 10**((m+48.6)/-2.5) ##erg/cm/s/Hz
    Fwave = 3e18*Fnu/(wavel**2) ##erg/cm/s/A
    
    return Fnu, Fwave



# Function definitions for mag_corr, lambda_to_nu, spec_flux, fluxspec_to_flux, etc., 
# should be imported or defined here

def extract_data_and_save_to_dataframe(directory_path, ebv_value):
    """
    columns = ['filt', 
               'tstart[MET]', 
               'tstop[MET]', 
               'tstart[MJD]', 
               'tstop[MJD]', 
               'nu[hz]', 
               'wave[AA]', 
               'ab_mag', 
               'ab_mag_err', 
               'ab_mag_err_stat',
               'ab_mag_err_syst', 
               'ab_mag_ext_corr', 
               'flux_uvot', 
               'flux_err_stat_uvot', 
               'flux_err_syst_uvot', 
               'flux_bkg_uvot',
               'sflux_hz[erg/cm2/s/Hz]', 
               'sflux_hz_err_d[erg/cm2/s/Hz]', 
               'sflux_hz_err_u[erg/cm2/s/Hz]',  
               'sflux_wave[erg/cm2/s/AA]', 
               'sflux_wave_err_d[erg/cm2/s/AA]', 
               'sflux_wave_err_u[erg/cm2/s/AA]']
     
    data_frame = pd.DataFrame(columns=columns)
    """
    rows = []
    if 'Swift' in os.listdir(directory_path):
        os.chdir(os.path.join(directory_path, 'Swift'))

        for observations in os.listdir('.'):
            if os.path.isdir(observations):
                name = str(observations)
                if name[0].isdigit():
                    number_observation = name
                    print('Observation number: ', number_observation)
                    os.chdir(name)
                    check = 0
                    if 'uvot' in os.listdir('.'):
                        print('The folder uvot/ exists in ', name)
                        os.chdir('uvot')
                        if 'image' in os.listdir('.'):
                            print('The folder image/ exists in ', name)
                            os.chdir('image')
                            
                            for files in os.listdir('.'):
                                if os.path.isfile(files) and files.endswith('_photo.fits'):
                                    tstart, tstop, mag, mag_err = 0., 0., 0., 0.
                                    mag_err_stat, mag_err_syst = 0., 0.
                                    flux, flux_err_stat, flux_err_syst = 0., 0., 0.
                                    print(files[0:16])
                                    
                                    filt = files[13:16]
                                    filt_freq = 0.

                                    for i in range(len(f)):
                                        if f[i] == filt:
                                            filt_freq = lambda_to_nu(float(wavel[i]))
                                            wave_tmp = float(wavel[i])
                                                                        
                                    data = fits.open(files)
                                    data_uvot = data[1].data
                                    tstart_met = data_uvot.field('TSTART')[0]
                                    tstop_met = data_uvot.field('TSTOP')[0]
                                    mag = data_uvot.field('AB_MAG')[0]
                                    mag_err = data_uvot.field('AB_MAG_ERR')[0]
                                    mag_err_stat = data_uvot.field('AB_MAG_ERR_STAT')[0]
                                    mag_err_syst = data_uvot.field('AB_MAG_ERR_SYS')[0]
                                    flux_aa = data_uvot.field('FLUX_AA')[0]
                                    flux_aa_err = data_uvot.field('FLUX_AA_ERR')[0]
                                    flux = data_uvot.field('FLUX_HZ')[0]
                                    flux_err_stat = data_uvot.field('FLUX_HZ_ERR_STAT')[0]
                                    flux_err_syst = data_uvot.field('FLUX_HZ_ERR_SYS')[0]
                                    flux_back = data_uvot.field('FLUX_HZ_BKG')[0]
                                    data.close()
                                    
                                    tstart_mjd = swift_met_to_mjd(tstart_met)
                                    tstop_mjd = swift_met_to_mjd(tstop_met)
                                    
                                    if mag != 99. and mag_err != 99.:
                                        ext_corr = Al_obs_Roming(ebv_value, filt)
                                        mag_corr_ab = mag_corr_obs(mag, ext_corr)
                                        flux_s_hz, flux_s_wave  = spec_flux_abmag(mag_corr_ab, wave_tmp)
                                        
                                        flux_s_hz_u, flux_s_wave_u  = spec_flux_abmag(mag_corr_ab-mag_err, wave_tmp)                
                                        flux_s_hz_d, flux_s_wave_d  = spec_flux_abmag(mag_corr_ab+mag_err, wave_tmp)
                                        flux_err_hz_u, flux_err_wave_u = flux_s_hz_u-flux_s_hz, flux_s_wave_u-flux_s_wave
                                        flux_err_hz_d, flux_err_wave_d = flux_s_hz-flux_s_hz_d, flux_s_wave-flux_s_wave_d
                                        
                                    elif mag != 99. and mag_err == 99.:
                                        ext_corr = Al_obs_Roming(ebv_value, filt)
                                        mag_corr_ab = mag_corr_obs(mag, ext_corr)
                                        flux_s_hz, flux_s_wave  = spec_flux_abmag(mag_corr_ab, wave_tmp)
                                        
                                        flux_err_hz_u, flux_err_wave_u, flux_err_hz_d, flux_err_wave_d  =np.array([0.]), np.array([0.]), np.array([0.]), np.array([0.])
                                        
                                    else:
                                        mag_corr_ab = np.array([0.])
                                        flux_s_hz, flux_s_wave = np.array([0.]), np.array([0.])
                                        flux_err_hz_u, flux_err_wave_u, flux_err_hz_d, flux_err_wave_d  = np.array([0.]), np.array([0.]), np.array([0.]), np.array([0.])
                                    
                                
                                    new_row = {
                                        'filt': filt, 
                                        'tstart[MET]': tstart_met, 
                                        'tstop[MET]': tstop_met, 
                                        'tstart[MJD]': tstart_mjd, 
                                        'tstop[MJD]': tstop_mjd,
                                        'nu[hz]': filt_freq, 
                                        'wave[AA]': wave_tmp,
                                        'ab_mag': mag, 
                                        'ab_mag_err': mag_err,
                                        'ab_mag_err_stat': mag_err_stat, 
                                        'ab_mag_err_syst': mag_err_syst, 
                                        'ab_mag_ext_corr': mag_corr_ab[0],
                                        'flux_uvot': flux, 
                                        'flux_err_stat_uvot': flux_err_stat, 
                                        'flux_err_syst_uvot': flux_err_syst, 
                                        'flux_bkg_uvot': flux_back,
                                        'sflux_hz[erg/cm2/s/Hz]': flux_s_hz[0], 
                                        'sflux_hz_err_d[erg/cm2/s/Hz]': flux_err_hz_d[0],
                                        'sflux_hz_err_u[erg/cm2/s/Hz]': flux_err_hz_u[0],                                         
                                        'sflux_wave[erg/cm2/s/AA]': flux_s_wave[0], 
                                        'sflux_wave_err_d[erg/cm2/s/AA]': flux_err_wave_d[0],
                                        'sflux_wave_err_u[erg/cm2/s/AA]': flux_err_wave_u[0] 
                                        
                                    }
                                    
                                    rows.append(new_row)

                                    
                            os.chdir('../../../')
                        else:
                            print('The folder image/ does not exist in ', name)
                            os.chdir('../../')
                            continue
                    else:
                        print('The folder uvot/ does not exist in ', name)
                        os.chdir('..')
                        continue
        os.chdir('..')
    
    data_frame =  pd.DataFrame(rows)
    
    data_frame.to_csv(os.path.join(directory_path+"/Swift/", "uvot_mag_flux_all_epochs_filters.csv"), index=False)


    	
####################
try: 
    df = pd.read_csv('base_info.csv')
except: 
    print('Cannot find the base info file.\n'\
          'FIX I:: Run python make_base_source_info.py\n'\
          'FIX II:: Make sure you are in the folder that contains the base_info.csv file.\n') 
    sys.exit(1)


###for now assume only 1 source 

dir_len = len(df['path'])

main_path = str(df['path'][0])
ra_obj = df['ra_obj'][0]
de_obj = df['de_obj'][0]
E_BV   = df['E_BV'][0]

#uvot filters
f = ["uw2", "um2", "uw1", "uuu", "ubb", "uvv"]
#coeff a
a = [-0.0581, 0.0773, 0.4346, 0.9226, 0.9994, 1.0015]
#coeff b
b = [8.4402, 9.1784, 5.3286, 2.1019, 1.0171, 0.0126]
#wave lambda (AA)
wavel = [2030, 2231, 2634, 3501, 4329, 5402]

 
#f, a, b, wavel = np.loadtxt('filters_a_b_wave.txt', unpack=True, dtype=str, usecols=(0,1,2,3))
#ref_m, ref_merr, ref_f, ref_ferr = np.loadtxt('filtersparamuvot.txt', unpack=True, usecols=(2, 4, 6, 8))

counter = 0

###HERE RUN THE CODE

extract_data_and_save_to_dataframe(main_path, E_BV)



print("#---------------------------#")
print("Finished -- The UVOT flux has been extracted for all observations.")
print("#---------------------------#")



