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
            
            
if 'Swift' in os.listdir('.'):
    os.chdir('Swift')

    path_reg = os.getcwd()
    
    bkg_reg = path_reg+'/bkg_pc.reg'

    for observations in os.listdir('.'):
        if os.path.isdir(observations):
            name=str(observations)

            if name[0].isdigit():

                number_observation=name
                print('Observation number: ', number_observation)			
                path   = os.getcwd()
                
                indir  = path+'/'+number_observation+'/'
                outdir = path+'/xrtout_'+number_observation+'/'
                outdir_name = 'xrtout_'+number_observation

                if outdir_name in os.listdir('.'):
                    print('The folder ', outdir, 'exists in ', name)
                    os.chdir(outdir)
                    
                    for files in os.listdir('.'):
                    
                        ##PC events
                        if isfile(files) and fnmatch(files, '*xpc*po_cl.evt'):
                            print('Event file for PC found: '+files[0:20])
                            
                            if isfile("src_pc.pha"):
                                os.system('rm src_pc.pha')
                            if isfile("bkg_pc.pha"):
                                os.system('rm bkg_pc.pha')                               
                                                                
                            src_obs_reg = files[0:20]+'_src_cent.reg'
                            
                            f = open(files[0:20]+"_pc.xsel", "w+") 

                            string0='xsel'+number_observation+'\n'\
                                    'read events ./'+files+'\n'\
                                    './ \n'\
                                    'yes \n'\
                                    'filter region '+src_obs_reg+'\n'\
                                    'extract spectrum \n'\
                                    'save spectrum src_pc.pha \n'\
                                    'clear region \n'\
                                    'filter region '+bkg_reg+'\n'\
                                    'extract spectrum \n'\
                                    'save spectrum bkg_pc.pha \n'\
                                    'clear region \n'\
                                    'quit \n'\
                                    'no \n'\

                            f.write(string0)
                            f.close()

                            os.system('xselect @'+files[0:20]+'_pc.xsel')
                        else:
                            print("PC file not found in "+files[0:20])    
                            
                        ##WT events    
                        if isfile(files) and fnmatch(files, '*xwt*po_cl.evt'):
                            print('found '+files[0:20])
                            
                            if isfile("src_wt.pha"):
                                os.system('rm src_wt.pha')
                            if isfile("bkg_wt.pha"):
                                os.system('rm bkg_wt.pha')                               
                                                                
                            src_obs_reg = 'src_wt_fk5_centr.reg'
                            bkg_obs_reg = 'bkg_wt_fk5.reg'
                            
                            f = open(files[0:20]+"_wt.xsel", "w+") #w=write, +=add if the file is not there
                        
                            string0='xsel'+number_observation+'\n'\
                                    'read events ./'+files+'\n'\
                                    './ \n'\
                                    'yes \n'\
                                    'filter region '+src_obs_reg+'\n'\
                                    'extract spectrum \n'\
                                    'save spectrum src_wt.pha \n'\
                                    'clear region \n'\
                                    'filter region '+bkg_obs_reg+'\n'\
                                    'extract spectrum \n'\
                                    'save spectrum bkg_wt.pha \n'\
                                    'clear region \n'\
                                    'quit \n'\
                                    'no \n'\
                                    
                            f.write(string0)
                            f.close()

                            os.system('xselect @'+files[0:20]+'_wt.xsel')
                        else:
                            print("WT file not found in "+files[0:20]) 
                            
                    os.chdir("../")
                else:
                    print('The folder ', outdir_name, 'does not exist for ', name)	
                    continue
    os.chdir(main_path)


print("#---------------------------#")
print("Finished -- The XSELECT has been run on all observations.")
print("#---------------------------#")
