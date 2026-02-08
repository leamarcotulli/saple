import os
import numpy as np
import pandas as pd


########################################################
#
#Insert the relevant info about your source here
#Keep the input as lists, even if you only have 1 source
#
########################################################

##Source Name

source_name = ['3C 273']

path = os.getcwd()

base_folder_path = [path]

##RA and DEC in [DEGREES] https://ned.ipac.caltech.edu/

ra_obj  = [187.277915] 
dec_obj = [2.052388]

##Redshift 
z  = [0.158]


##NH [cm^-2, Mean from https://www.swift.ac.uk/analysis/nhtot/index.php] or https://heasarc.gsfc.nasa.gov/cgi-bin/Tools/w3nh/w3nh.pl]
nh = [1.68e20]

##Dust Extinction [Mean from  https://www.swift.ac.uk/analysis/nhtot/index.php] or https://irsa.ipac.caltech.edu/applications/DUST/]

E_BV = [0.019]

#####################################

data = {'source_name': source_name,
        'ra_obj': ra_obj,
        'de_obj': dec_obj,
        'nh': nh,
        'z': z,
        'E_BV': E_BV,
        'path': base_folder_path}
      
df = pd.DataFrame(data) 

df.to_csv('base_info.csv', index=False)
