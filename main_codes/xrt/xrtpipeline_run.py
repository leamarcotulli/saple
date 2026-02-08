from astropy.io.fits import getheader 
from astropy.io import fits
import sys, os
import numpy as np
from astropy import units as u
from astropy.coordinates import SkyCoord
#from astroquery.ned import Ned

import os
import subprocess 
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



if 'Swift' in os.listdir('.'):
    os.chdir('Swift')

    for observations in os.listdir('.'):
        if os.path.isdir(observations):
            name=str(observations)

            if name[0].isdigit():
                number_observation=name

                print('Observation number: ', number_observation)
                os.chdir(name)


                if 'xrt' in os.listdir('.'):
                    print('The folder xrt/ exists in ', name,'. Running xrtpipeline.')
                    os.chdir('..')
                
                    path   = os.getcwd()
                    indir  = name+'/'
                    outdir = 'xrtout_'+name+'/'                            
                    
                    steminputs = 'sw'+name
                    string = "xrtpipeline srcra=OBJECT srcdec=OBJECT indir="+indir+" outdir="+outdir+" steminputs="+steminputs+" clobber=yes"
                    
                    
                    os.system(string)
            
                else:
                    print('The folder xrt/ does not exist in ', name)	
                    os.chdir('..')  
                    continue
            
    os.chdir('../..')
    
print("#---------------------------#")
print("Finished -- The XRTPIPELINE has been run on all observations.")
print("#---------------------------#")
