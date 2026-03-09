from fnmatch import fnmatch
from astropy.io.fits import getheader 
from astropy.io import fits
import sys, os
import numpy as np
from astropy import units as u
from astropy.coordinates import SkyCoord
import os
from os.path import isfile, join
import pandas as pd
from tqdm import tqdm 
import re


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

os.chdir(main_path)

paths = [[] for i in range(dir_len)]
paths_to_save = [[] for i in range(dir_len)]

paths_to_srcs = [[] for i in range(dir_len)]
paths_to_bkg  = [[] for i in range(dir_len)]
paths_to_obs_srcs = [[] for i in range(dir_len)]


counter = 0 ###when you do multiple sources at once


if 'Swift' in os.listdir('.'):
    os.chdir('Swift')

    path_reg = os.getcwd()
    src_reg = path_reg+'/src_pc.reg'
    bkg_reg = path_reg+'/bkg_pc.reg'
    
    if os.path.isdir("xrt_png"):
        print("Print xrt_png/ already exists")
    else:
        os.system('mkdir xrt_png/')

    path_out = path_reg+'/xrt_png/'

    for observations in os.listdir('.'):
        if os.path.isdir(observations):
            name=str(observations)
            

            if name[0].isdigit():
                
                number_observation=name
                
                print('Observation number: ', number_observation)			
                
                path_obs   = os.getcwd()

                outdir = path_obs+'/xrtout_'+number_observation+'/'
                outdir_name = 'xrtout_'+number_observation
                
                print('xrtoutdir name: ', outdir_name)
                
                if outdir_name in os.listdir('.'):
                    print('The folder ', outdir, 'exists for obsid ', name)
                    os.chdir(outdir)
                                      
                    
                    for files in os.listdir('.'):
                        
                        if isfile(files) and fnmatch(files, '*xpc*po_cl.evt'):# files.endswith('po_cl.evt'):
                            print('found '+files[0:20])
                            
                            full_path_to_obs = outdir+files
                            full_path_to_ima = path_out+files[0:20]+'.png'
                            
                            src_obs_reg = outdir+files[0:20]+'_src_cent.reg'
                                                        
                            paths[counter].append(full_path_to_obs)
                            paths_to_save[counter].append(full_path_to_ima)
                            
                            #common src/bkg region the user created
                            paths_to_srcs[counter].append(src_reg)
                            paths_to_bkg[counter].append(bkg_reg)
                            #paths to src region which has been located at centroid
                            paths_to_obs_srcs[counter].append(src_obs_reg)

                        else: 
                            continue 
                    os.chdir('..')        
                                                                             

###OPEN DS9 & RUN IN THE BACKGROUND

display = "ds9 &\n\
           sleep 10"
os.system(display)


for i in range(dir_len):
    with tqdm(total = len(paths[i]), position = 0, desc = "Saving images") as pbar:
        for j in range(len(paths[i])): 
            image='xpaset -p ds9 fits %s\n\
                   xpaset -p ds9 smooth \n\
                   xpaset -p ds9 scale log \n\
                   xpaset -p ds9 zoom to fit \n\
                   xpaset -p ds9 region load %s\n\
                   xpaset -p ds9 region select all\n\
                   xpaset -p ds9 region centroid\n\
                   xpaset -p ds9 region format ds9\n\
                   xpaset -p ds9 region system wcs\n\
                   xpaset -p ds9 region sky fk5\n\
                   xpaset -p ds9 region save %s\n\
                   xpaset -p ds9 region load %s\n\
                   xpaset -p ds9 region select all\n\
                   xpaset -p ds9 region centroid\n\
                   xpaset -p ds9 saveimage %s\n\
                   xpaset -p ds9 frame clear\n'%(paths[i][j], paths_to_srcs[i][j], paths_to_obs_srcs[i][j],\
                                               paths_to_bkg[i][j], paths_to_save[i][j])
            os.system(image)
            pbar.update(1)


#load ../src.reg -saveimage %s_ima.jpeg -exit'
               
print("#---------------------------#")
print("Finished -- The XRT PC images have been created.")
print("#---------------------------#")
                                                               
                                    

