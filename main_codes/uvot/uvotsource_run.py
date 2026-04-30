from astropy.io.fits import getheader 
from astropy.io import fits
import sys, os
import numpy as np
from astropy import units as u
from astropy.coordinates import SkyCoord
#from astroquery.ned import Ned

import os
#import subprocess 
from os.path import isfile, join
import pandas as pd



try: 
    df = pd.read_csv('base_info.csv')
except: 
    print('Cannot find the base info file.\n'\
          'FIX I:: Run python make_base_source_info.py\n'\
          'FIX II:: Make sure you are in the folder that contains the base_info.csv file.\n') 
    sys.exit(1)


main_path = str(df['path'][0])

os.chdir(main_path)


counter = 0

if 'Swift' in os.listdir('.'):
    os.chdir('Swift')
    for observations in os.listdir('.'):

        if os.path.isdir(observations):

            name=str(observations)
			
            if name[0].isdigit():

                number_observation=name
                print('Observation number: ', number_observation)
                os.chdir(name)
				
                #check that there is uvot/ otherwise exit
                check = 0 
                if 'uvot' in os.listdir('.'):
                    print('The folder uvot/ exists in ', name)
                    os.chdir('uvot')  
                    #check that there is image/ otherwise exit
                    if 'image' in os.listdir('.'):
                        print('The folder image/ exists in ', name,'. Running uvotsource.')
                        os.chdir('image') 
						
                        for files in os.listdir('.'):
						
                            if isfile(files) and files.endswith('_sk.img.gz'): 
                                print(files[0:16])
                                src = files[0:16]+"_centr_src.reg"
                                bkg = files[0:16]+"_bkg.reg" 
                                output = files[0:16]+"_photo.fits"

                                if isfile(output):
                                    os.system('rm '+output)

                                string = "uvotsource "+files+"+1 "+src+" "+bkg+" 3 "+output
                                os.system(string)
                        os.chdir('../../../')
                    else:
                        print('The folder image/ does not exist in ', name)	
                        os.chdir('../../')
                        continue 	
                else:
                    print('The folder uvot/ does not exist in ', name)	
                    os.chdir('..')  
                    continue

print("#---------------------------#")
print("Finished -- uvotsource has been run on all observations.")
print("#---------------------------#")


                          

