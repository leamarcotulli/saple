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


# Function to extract the circle parameters from the DS9 region file content
def extract_circle_parameters(filename):
    with open(filename, 'r') as file:
        content = file.readlines()

    for line in content:
        if line.startswith("circle"):
            # Extract the numbers from the circle line using regex
            matches = re.search(r'circle\(([^)]+)\)', line)
            if matches:
                circle_params = matches.group(1).split(',')
                # Convert to floats
                a, b, c = map(float, circle_params)
                return a, b, c
    return None, None, None



def wt_bkg_region_ctr(srcx, srcy, theta, d):
    d = d*2
    x_ctr = srcx - d*np.sin(np.deg2rad(angle))
    y_ctr = srcy + d*np.cos(np.deg2rad(angle))
    
    return x_ctr, y_ctr


try: 
    df = pd.read_csv('base_info.csv')
except: 
    print('Cannot find the base info file.\n'\
          'FIX I:: Run python make_base_source_info.py\n'\
          'FIX II:: Make sure you are in the folder that contains the base_info.csv file.\n') 
    sys.exit(1)




dir_len = len(df['path'])

main_path = str(df['path'][0])
ra_obj = df['ra_obj'][0]
de_obj = df['de_obj'][0]

os.chdir(main_path)

paths_wt = [[] for i in range(dir_len)]
paths_to_save_wt = [[] for i in range(dir_len)]

paths_to_wt_srcs = [[] for i in range(dir_len)]
paths_to_wt_srcs_phys = [[] for i in range(dir_len)]
paths_to_wt_srcs_centr= [[] for i in range(dir_len)]

counter = 0 ###when you do multiple sources at once


src_wt_size_asec = 50 ##arcsec

print("#-----------------------#")
print("The chosen radius for WT region size is: %.1f\n\n arces"%src_wt_size_asec)
print("If you want to change it, press <Crtl+C> and edit line 70\n\n")
print("Otherwise, press <ENTER>") 
input()


#########FIRST SAVE ALL THE SRC in physical coordinates 

if 'Swift' in os.listdir('.'):
    os.chdir('Swift')

    path_reg = os.getcwd()
    
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
                        
                        if isfile(files) and fnmatch(files, '*xwt*po_cl.evt'):# files.endswith('po_cl.evt'):
                            print('found '+files[0:20])

                            with fits.open(files) as hdulist:
                                primary_header = hdulist[0].header
                                angle = primary_header['PA_PNT']
                                ra_x = primary_header['RA_OBJ']
                                dec_y = primary_header['DEC_OBJ']
                            
                            
                            full_path_to_obs = outdir+files
                            src_wt_fk5_reg = outdir+'src_wt_fk5.reg'
                            
                            f = open(src_wt_fk5_reg, 'w+')
                            string = '# Region file format: DS9 version 4.1\n'\
                                     'global color=green dashlist=8 3 width=1 font="helvetica 10 normal roman" select=1 highlite=1 dash=0 fixed=0 edit=1 move=1 delete=1 include=1 source=1\n'\
                                     'fk5\n'\
                                     'circle(%f,%f,%f")'%(ra_x, dec_y,src_wt_size_asec)   
                            f.write(string)
                            f.close()
                                     
                            src_wt_phy_reg = outdir+'src_wt_phys_centr.reg'
                            src_wt_centr_reg = outdir+'src_wt_fk5_centr.reg'
                            paths_wt[counter].append(full_path_to_obs)          
                            #common src/bkg region the user created
                            paths_to_wt_srcs[counter].append(src_wt_fk5_reg)
                            paths_to_wt_srcs_phys[counter].append(src_wt_phy_reg)
                            paths_to_wt_srcs_centr[counter].append(src_wt_centr_reg)
                        else: 
                            continue 
                    os.chdir('..')     
                    
                                   
####NOW SAVE FOR EVERY SOURCE ITS SOURCE REGION IN PHYISICAL COORD & CENTROIDED
###OPEN DS9 & RUN IN THE BACKGROUND

display = "ds9 &\n\
           sleep 10"
os.system(display)

for i in range(dir_len):
    for k in range(len(paths_wt[i])):            
        image_wt='xpaset -p ds9 fits %s\n\
                  xpaset -p ds9 scale log \n\
                  xpaset -p ds9 region load %s\n\
                  xpaset -p ds9 region select all\n\
                  xpaset -p ds9 region centroid\n\
                  xpaset -p ds9 region format ds9\n\
                  xpaset -p ds9 region system physical\n\
                  xpaset -p ds9 region sky fk5\n\
                  xpaset -p ds9 region save %s\n\
                  xpaset -p ds9 region format ds9\n\
                  xpaset -p ds9 region system wcs\n\
                  xpaset -p ds9 region sky fk5\n\
                  xpaset -p ds9 region save %s\n\
                  xpaset -p ds9 frame clear'%(paths_wt[i][k], paths_to_wt_srcs[i][k],\
                                           paths_to_wt_srcs_phys[i][k], paths_to_wt_srcs_centr[i][k])
        os.system(image_wt)  


#print(os.getcwd())

os.chdir(main_path)

paths_to_wt_bkg  = [[] for i in range(dir_len)]
paths_to_wt_bkg_fk5 = [[] for i in range(dir_len)]


if 'Swift' in os.listdir('.'):
    os.chdir('Swift')

    path_reg = os.getcwd()
    

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
                        
                        if isfile(files) and fnmatch(files, '*xwt*po_cl.evt'):# files.endswith('po_cl.evt'):
                            print('found '+files[0:20])
                            
                            ##make background region
                            full_path_to_ima = path_out+files[0:20]+'.png'
                            paths_to_save_wt[counter].append(full_path_to_ima)      
                                                 
                            src_wt_x, src_wt_y, src_wt_size = extract_circle_parameters('src_wt_phys_centr.reg')
                                                       

                            with fits.open(files) as hdulist:
                                primary_header = hdulist[0].header
                                angle = primary_header['PA_PNT']
                                ra_x = primary_header['RA_OBJ']
                                dec_y = primary_header['DEC_OBJ']
                            
                            dra  = np.abs(ra_obj-ra_x)*60*60
                            ddec = np.abs(de_obj-dec_y)*60*60
                            
                            if dra>src_wt_size*2.36 or ddec>src_wt_size*2.36:
                                print("!!!WARNING, header file pointing is offset by more than region size %.2f arcsec"%(src_wt_size*2.36))
                                                        
                            bkg_wt_x, bkg_wt_y = wt_bkg_region_ctr(src_wt_x, src_wt_y, angle, src_wt_size)
                            
                            string = '# Region file format: DS9 version 4.1\n'\
                                     'global color=green dashlist=8 3 width=1 font="helvetica 10 normal roman" select=1 highlite=1 dash=0 fixed=0 edit=1 move=1 delete=1 include=1 source=1\n'\
                                     'physical\n'\
                                     'circle(%f,%f,%f)'%(bkg_wt_x, bkg_wt_y,src_wt_size)
                                     
                            f = open("bkg_wt_phys.reg", "w+")
                            f.write(string)
                            f.close()
                            
                            bkg_reg = outdir+'bkg_wt_phys.reg'
                            bkg_reg_fk5 = outdir+'bkg_wt_fk5.reg'
                            
                            paths_to_wt_bkg[counter].append(bkg_reg)
                            paths_to_wt_bkg_fk5[counter].append(bkg_reg_fk5)

                        else: 
                            continue 
                    os.chdir('..')
                    
### NOW SAVE FOR EVERY SOURCE ITS BKG REGION IN PHYISICAL COORD & CENTROIDED
### OPEN DS9 & RUN IN THE BACKGROUND


for i in range(dir_len):
    with tqdm(total = len(paths_wt[i]), position = 0, desc = "Saving images") as pbar:
        for k in range(len(paths_wt[i])):              
            image_wt='xpaset -p ds9 fits %s\n\
                      xpaset -p ds9 scale log \n\
                      xpaset -p ds9 region load %s\n\
                      xpaset -p ds9 region format ds9\n\
                      xpaset -p ds9 region system wcs\n\
                      xpaset -p ds9 region sky fk5\n\
                      xpaset -p ds9 region save %s\n\
                      xpaset -p ds9 region load %s\n\
                      xpaset -p ds9 saveimage %s\n\
                      xpaset -p ds9 frame clear'%(paths_wt[i][k], paths_to_wt_bkg[i][k],\
                                               paths_to_wt_bkg_fk5[i][k], paths_to_wt_srcs_phys[i][k],\
                                               paths_to_save_wt[i][k])
            os.system(image_wt)  
            pbar.update(1)


print("#---------------------------#")
print("Finished -- The XRT WT images have been created.")
print("#---------------------------#")


