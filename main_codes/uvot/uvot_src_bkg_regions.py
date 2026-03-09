from astropy.io.fits import getheader 
from astropy.io import fits
import sys, os
import numpy as np
from astropy import units as u
from astropy.coordinates import SkyCoord
from os.path import isfile, join
import pandas as pd
from tqdm import tqdm 

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

user_defined = "yes" #"no" 

##in degrees
#ra_offset = -0.02
#de_offset = -0.02

##in arcseconds
#src_reg_size = 5
#bkg_reg_size = 30


"""
string = f'##################################################################\n'\
         f'# Did you define your own source and background region for uvot using ds9 (Step 2. of the manual)?\n'\
         f'# Then change the variable user_defined="yes" line 33.**\n'\
         f'#----------------#\n'\
         #f'# If instead you have identified identified a suitable offset from your ds9 image between the source and background region\n'\
         #f'# Then change the variable user_defined="no" line 33 and read the following...**\n'\
         #f'#  RECOMMENDED: check at least 1 uvot image to dedice the bkg region offset.**\n'\
         #f'#\n'\
         #f'# The UVOT src region size is set by default to ** {src_reg_size} asec **\n'\
         #f'# The UVOT bkg region size is set by default to ** {bkg_reg_size} asec **\n'\
         #f'# The UVOT offset between bkg and src region is set by default to\n'\
         #f'#  RA : ** {ra_offset} deg **; DEC : ** {de_offset} ** deg \n'\
         #f'#\n'\
         #f'#If you wish to edit, modify lines 32-35.\n'\
         #f'#\n'\
         f'#---- Do you wish to continue?\n (ENTER for yes, Ctrl+C to stop)\n'
"""

string = f'##################################################################\n'\
         f'# Did you define your own source and background region for uvot using ds9 (Step 2. of the manual)?\n'\
         f'# Then change the variable user_defined="yes" line 33.**\n'\
         f'#----------------#\n'\
         f'#---- Do you wish to continue?\n (<ENTER> for yes, <Ctrl+C> to stop)\n'
         
print(string)

input()

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
                                else:
                                    
                                    header=getheader(files)

                                    f = open(files[0:16]+"_src.reg", "w+") #w=write, +=add if the file is not there
                                    d = open(files[0:16]+"_bkg.reg", "w+")
                                    string0='# Region file format: DS9 version 4.1 \n'\
                                    'global color=green dashlist=8 3 width=1 font="helvetica 10 normal roman" '\
                                    'select=1 highlite=1 dash=0 fixed=0 edit=1 move=1 delete=1 include=1 source=1 \n'\
                                    'fk5 \n'\
                                    'circle(%.4f,%.4f,%.f")'%(ra_obj,de_obj,src_reg_size)
        							
                                    string1='# Region file format: DS9 version 4.1 \n'\
                                    'global color=green dashlist=8 3 width=1 font="helvetica 10 normal roman" '\
                                    'select=1 highlite=1 dash=0 fixed=0 edit=1 move=1 delete=1 include=1 source=1 \n'\
                                    'fk5 \n'\
                                    'circle(%.4f,%.4f,%.f")'%(ra_obj+ra_offset,de_obj+de_offset,bkg_reg_size)
        							
                                    f.write(string0)
                                    d.write(string1)
                                    f.close()
                                    d.close()

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
                   xpaset -p ds9 region centroid auto no\n\
                   xpaset -p ds9 region load %s\n\
                   xpaset -p ds9 saveimage %s\n\
                   xpaset -p ds9 frame clear'%(paths[i][j], paths_to_srcs[i][j], paths_to_cent_srcs[i][j], paths_to_bkg[i][j], paths_to_save[i][j])
             
            os.system(image)
            pbar.update(1)
                          


print("#---------------------------#")
print("Finished -- The UVOT images have been created for all observations & filters.")
print("#---------------------------#")

