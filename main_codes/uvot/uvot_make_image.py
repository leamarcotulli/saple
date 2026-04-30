from astropy.io.fits import getheader 
from astropy.io import fits
import sys, os
import numpy as np
from astropy import units as u
from astropy.coordinates import SkyCoord
from os.path import isfile, join
import pandas as pd
from tqdm import tqdm 
import re


def extract_circle_parameters_reg(filename):
    region_types = ["circle", "ellipse", "box", "polygon", "annulus"]
    with open(filename, 'r') as file:
        content = file.readlines()

    for line in content:
        for reg_string in region_types:
            if line.startswith(reg_string):
                # Extract the numbers from the circle line using regex
                matches = re.search(r'%s\(([^)]+)\)'%reg_string, line)
      
    if matches:
        circle_params = matches.group(1).split(',')
        # Convert to floats
        a = float(circle_params[0])
        b = float(circle_params[1])
        return a, b
    else: 
        print("The source region you defined is NOT included in our scripts.")
        print("Please contact us if this is the case.")
        print("")            
        return None, None
              
    return None, None
    
    
try: 
    df = pd.read_csv('base_info.csv')
except: 
    print('Cannot find the base info file.\n'\
          'FIX I:: Run python make_base_source_info.py\n'\
          'FIX II:: Make sure you are in the folder that contains the base_info.csv file.\n') 
    sys.exit(1)


###for now assume only 1 source/1 path 

dir_len = len(df['path'])

main_path = str(df['path'][0])
ra_obj = df['ra_obj'][0]
de_obj = df['de_obj'][0]

user_defined = "yes" #"no" %%%%keep as YES

os.chdir(main_path)


paths = [[] for i in range(dir_len)]

paths_to_srcs = [[] for i in range(dir_len)]

paths_to_cent_srcs = [[] for i in range(dir_len)]

paths_to_bkg = [[] for i in range(dir_len)]

paths_to_save = [[] for i in range(dir_len)]



counter = 0

if 'Swift' in os.listdir('.'):
    os.chdir('Swift')

    path_reg = os.getcwd()
    
    sr = os.path.isfile('%s/src_uvot.reg'%(path_reg))
    br = os.path.isfile('%s/bkg_uvot.reg'%(path_reg))
    
    if sr==False or br==False:
        print('Cannot find the src_uvot.reg AND/OR bkg_uvot.reg in Swift/.\n'\
              'FIX:: Create these regions (Step 2. of the README). \n'\
              )
        sys.exit(1)   

    if os.path.isdir("uvot_png"):
        print("The folder uvot_png/ already exists. Moving on.")
    else:
        os.system('mkdir uvot_png/')
            
    path_out = path_reg+'/uvot_png/'

    for observations in os.listdir('.'):
        if os.path.isdir(observations):
            name=str(observations)
		
            if name[0].isdigit():

                number_observation=name
                print('Observation number: ', number_observation)
                os.chdir(name)
			
                #check that there is uvot otherwise exit
                check = 0 
                if 'uvot' in os.listdir('.'):
                    print('The folder uvot/ exists in ', name)
                    os.chdir('uvot')  

                    if 'image' in os.listdir('.'):
                        print('The folder image/ exists in ', name)
                        os.chdir('image') 
					
                        for files in os.listdir('.'):
    					
                            if isfile(files) and files.endswith('_sk.img.gz'):
                                print(files[0:16])
                                path_obs   = os.getcwd()
                                src_reg = path_obs+'/'+files[0:16]+'_src.reg'
                                src_cent_reg = path_obs+'/'+files[0:16]+'_centr_src.reg'
                                bkg_reg = path_obs+'/'+files[0:16]+'_bkg.reg'
                                    
                                if user_defined=="yes":
                                    os.system('cp %s/src_uvot.reg %s'%(path_reg, src_reg))
                                    os.system('cp %s/bkg_uvot.reg %s'%(path_reg, bkg_reg))


                                full_path_to_obs = path_obs+'/'+files
                                full_path_to_ima = path_out+files[0:20]+'png'
                            
                                paths[counter].append(full_path_to_obs)
                                paths_to_save[counter].append(full_path_to_ima)
                                paths_to_srcs[counter].append(src_reg)
                                paths_to_cent_srcs[counter].append(src_cent_reg)                                
                                paths_to_bkg[counter].append(bkg_reg)
                                
                        os.chdir('../../../')
                    else:
                        print('The folder image/ does not exist in ', name)	
                        os.chdir('../../')
                        continue 	
    
                else:
                    print('The folder uvot/ does not exist in ', name)	
                    os.chdir('..')  
                    continue

                   
###OPEN DS9 & RUN IN THE BACKGROUND
os.chdir(main_path)

display = "ds9 &\n\
           sleep 10"
os.system(display)

###need to add a save centroid region now!!!


for i in range(dir_len):
    with tqdm(total = len(paths[i]), position = 0, desc = "Saving images") as pbar:
        for j in range(len(paths[i])):
            a, b = extract_circle_parameters_reg(paths_to_srcs[i][j])
            image='xpaset -p ds9 fits %s\n\
                   xpaset -p ds9 smooth \n\
                   xpaset -p ds9 scale log \n\
                   xpaset -p ds9 pan to %f %f wcs fk5\n\
                   xpaset -p ds9 zoom to 1 \n\
                   xpaset -p ds9 region load %s\n\
                   xpaset -p ds9 region select all\n\
                   xpaset -p ds9 region centroid\n\
                   xpaset -p ds9 region format ds9\n\
                   xpaset -p ds9 region system wcs\n\
                   xpaset -p ds9 region sky fk5\n\
                   xpaset -p ds9 region save %s\n\
                   xpaset -p ds9 region centroid auto no\n\
                   xpaset -p ds9 region load %s\n\
                   xpaset -p ds9 region select none\n\
                   xpaset -p ds9 saveimage %s\n\
                   xpaset -p ds9 frame clear'%(paths[i][j], a, b, paths_to_srcs[i][j], paths_to_cent_srcs[i][j], paths_to_bkg[i][j], paths_to_save[i][j])
             
            os.system(image)
            pbar.update(1)
                          


print("#---------------------------#")
print("Finished -- The UVOT images have been created for all observations & filters.")
print("#---------------------------#")

