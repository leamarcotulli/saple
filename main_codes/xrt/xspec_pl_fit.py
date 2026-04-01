from xspec import *
import sys
import os
from astropy.io.fits import getheader 
from os.path import isfile, join
import numpy as np
from os.path import isfile, join
from fnmatch import fnmatch
import pandas as pd

#######################################

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
nh     = df['nh'][0]
z      = df['z'][0]


os.chdir(main_path)
            

###XSPEC params 

Fit.statMethod = "cstat"
Xset.abund = "wilm"
Xset.cosmo = "67.3,,0.685"
Fit.query = "yes"   


##obsid gamma gamma_err flux(0.3-10 keV) flux_err cstat counts(0.3-10) exposure_time date

if 'Swift' in os.listdir('.'):
    os.chdir('Swift')
    
    res = open('params_xspec.csv', 'w+')
    
    res.write('inst,obs_id,exposure_time[s],start_date,start_date[mjd],count/s(0.3-10),pl_idx,pl_idx_l,pl_idx_h,flux_abs,flux_abs_l,flux_abs_h,flux_unabs,cstat,dof\n')
    
    path_to_rmf = os.getcwd()

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
                    ##PC EVENTS
                    for files in os.listdir('.'):
                        if isfile(files) and fnmatch(files, '*xpc*po_cl.evt'):# files.endswith('po_cl.evt'):
                        
                            inst_tmp = "PC"
                            
                            obsid = files[2:13]
                            hd  = getheader(files)
                            exp_time = round(hd["TSTOP"]-hd["TSTART"])
                            date_start = hd["DATE-OBS"][0:10] ##get only day 
                            tstart_mjd = hd['MJD-BEG']
                            #tstop_mjd = data_uvot.field('MJD-END')[0]
                            
                            if isfile('src_pc_bkg_arf_rmf.pha'):
                                os.system('rm src_pc_bkg_arf_rmf.pha')
                            else:
                                print('First time binning the data.')
                            

                            string_arf = 'xrtmkarf expofile='+files[0:20]+'_ex.img phafile=src_pc.pha srcx=-1 srcy=-1 psfflag=YES outfile=out_pc.arf clobber=yes'
                            os.system(string_arf)
                            
                            ###first add bkg, arf and rmf files
                            f = open(files[0:20]+"_pc_grppha.sh", "w+") #w=write, +=add if the file is not there
                            
                            string0='grppha infile=\'src_pc.pha\' '\
                                    'outfile=\'src_pc_bkg_arf_rmf.pha\' '\
                                    'comm=\'chkey ancrfile out_pc.arf&chkey backfile bkg_pc.pha&chkey '\
                                    'respfile %sxrt_pc.rmf&exit\''%(path_to_rmf)
                            f.write(string0)
                            f.close()
                            os.system('bash '+files[0:20]+'_pc_grppha.sh')
                            
                            ###then bin the spectrum using optimal binning
                            
                            f1 = open(files[0:20]+"_pc_ftgrppha.sh", "w+") #w=write, +=add if the file is not there
                                                        
                            string1 = 'ftgrouppha infile=src_pc_bkg_arf_rmf.pha respfile=../xrt_pc.rmf outfile=src_pc_opt.pha grouptype=opt clobber=yes'
                            f1.write(string1)
                            f1.close()
                            os.system('bash '+files[0:20]+'_pc_ftgrppha.sh')
                            

                            try:
                                AllData('src_pc_opt.pha')
                                s = AllData(1)
                                rate = s.rate[0]
                                if rate==0.:
                                   string = f"{inst_tmp},{obsid},{exp_time},{date_start},{tstart_mjd},0,0,0,0,0,0,0,0,0,0\n"
                                   res.write(string)
                                   continue
                                   
                                Fit.statMethod = "cstat"
                                Xset.abund = "wilm"
                                
                                AllData.ignore("**-0.3, 10.0-**")
                                AllData.ignore("bad")
                                rate0310 = s.rate[0]
                                print('Count rate 0.3--10 keV', rate0310)
                                
                            except:
                            
                                string = f"{inst_tmp},{obsid},{exp_time},{date_start},{tstart_mjd},0,0,0,0,0,0,0,0,0,0\n"
                                res.write(string)
                                continue

                            m1 = Model("tbabs*zpower")
                            
                            m1(1).values = nh/1e22
                            
                            m1(3).values = z
                                                       
                            par1=m1(1)
                            
                            AllModels.show()
                            
                            par1.frozen=True 
                            
                            Fit.nIterations = 100


                            try:
                                Fit.perform()
                            except:
                                #string ='0 0 0 0 0 0 0 0 0 0 0 0\n'
                                string = f"{inst_tmp},{obsid},{exp_time},{date_start},{tstart_mjd},0,0,0,0,0,0,0,0,0,0\n"
                                res.write(string)
                                continue

                            print("Photon index fit: ", m1(2).values)
                            
                            try:
                                Fit.error("2.706 2")
                            except:
                                print('Calculating uncertainties has failed')
                                
                            
                            cstat_val = '%.2f'%Fit.statistic
                            dof = '%.1f'%Fit.dof
                            
                            ##get index and errors
                            index=AllModels(1)(2)
                            indx, b1, c1, d1, e1, f1 = index.values
                            i_l, i_h, z1 = index.error
                            
                            ##get abs flux --> calc err --> get unabs flux
                            AllModels.calcFlux("0.3 10 err")
                            f1 = AllData(1)
                            f, f_l, f_h, p, q, r = f1.flux
                            
                            m1(1).values = 0.
                            
                            AllModels.calcFlux("0.3 10.0")
                            f1 = AllData(1)
                            f_unabs, f_ul, f_uh, p, q, r = f1.flux
                            
                            
                            # Using f-string for formatting
                            
                            string = f"{inst_tmp},{obsid},{exp_time},{date_start},{tstart_mjd},{rate0310},{indx},{i_l},{i_h},{f},{f_l},{f_h},{f_unabs},{cstat_val},{dof}\n"
                             
                            res.write(string)
                            
                            AllData.clear()
                            AllModels.clear()
                        
                        ##WT EVENTS
                        if isfile(files) and fnmatch(files, '*xwt*po_cl.evt'):
                            
                            inst_tmp = "WT"
                            
                            obsid = files[2:13]
                            hd  = getheader(files)
                            exp_time = round(hd["TSTOP"]-hd["TSTART"])
                            date_start = hd["DATE-OBS"][0:10] ##get only day 
                            tstart_mjd = hd['MJD-BEG']
                            
                            if isfile('src_wt_bkg_arf_rmf.pha'):
                                os.system('rm src_wt_bkg_arf_rmf.pha')
                            else:
                                print('first time wt optimal binning')
                            

                            string_arf = 'xrtmkarf expofile='+files[0:20]+'_ex.img phafile=src_wt.pha srcx=-1 srcy=-1 psfflag=YES outfile=out_wt.arf clobber=yes'
                            os.system(string_arf)
                            
                            ###first add bkg, arf and rmf files
                            f = open(files[0:20]+"_wt_grppha.sh", "w+") #w=write, +=add if the file is not there
                            
                            string0='grppha infile=\'src_wt.pha\' '\
                                    'outfile=\'src_wt_bkg_arf_rmf.pha\' '\
                                    'comm=\'chkey ancrfile out_wt.arf&chkey backfile bkg_wt.pha&chkey '\
                                    'respfile %sxrt_wt.rmf&exit\''%(path_to_rmf)
                            f.write(string0)
                            f.close()
                            os.system('bash '+files[0:20]+'_wt_grppha.sh')
                            
                            ###then bin the spectrum using optimal binning
                            
                            f1 = open(files[0:20]+"_wt_ftgrppha.sh", "w+") #w=write, +=add if the file is not there
                                                        
                            string1 = 'ftgrouppha infile=src_wt_bkg_arf_rmf.pha respfile=../xrt_pc.rmf outfile=src_wt_opt.pha grouptype=opt clobber=yes'
                            f1.write(string1)
                            f1.close()
                            os.system('bash '+files[0:20]+'_wt_ftgrppha.sh')
                            

                            try:
                                AllData('src_wt_opt.pha')
                                s = AllData(1)
                                rate = s.rate[0]
                                if rate==0.:
                                   string = f"{inst_tmp},{obsid},{exp_time},{date_start},{tstart_mjd},0,0,0,0,0,0,0,0,0,0\n"
                                   res.write(string)
                                   continue
                                   
                                Fit.statMethod = "cstat"
                                Xset.abund = "wilm"
                                
                                AllData.ignore("**-0.3, 10.0-**")
                                AllData.ignore("bad")
                                rate0310 = s.rate[0]
                                print('Count rate 0.3--10 keV', rate0310)
                                
                            except:
                            
                                string = f"{inst_tmp},{obsid},{exp_time},{date_start},{tstart_mjd},0,0,0,0,0,0,0,0,0,0\n"
                                res.write(string)
                                continue

                            m1 = Model("tbabs*zpower")
                            
                            m1(1).values = nh/1e22
                            
                            m1(3).values = z
                                                       
                            par1=m1(1)
                            
                            AllModels.show()
                            
                            par1.frozen=True 
                            
                            Fit.nIterations = 100
                            
                            

                            try:
                                Fit.perform()
                            except:
                                string =f"{inst_tmp},{obsid},{exp_time},{date_start},{tstart_mjd},0,0,0,0,0,0,0,0,0,0\n"
                                res.write(string)
                                continue

                            print("Photon index fit: ", m1(2).values)
                            
                            try:
                                Fit.error("2.706 2")
                            except:
                                print('Calculating uncertainties has failed')
                                
                            
                            cstat_val = '%.2f'%Fit.statistic
                            dof = '%.1f'%Fit.dof
                            
                            ##get index and errors
                            index=AllModels(1)(2)
                            indx, b1, c1, d1, e1, f1 = index.values
                            i_l, i_h, z1 = index.error
                            
                            ##get abs flux --> calc err --> get unabs flux
                            AllModels.calcFlux("0.3 10 err")
                            f1 = AllData(1)
                            f, f_l, f_h, p, q, r = f1.flux
                            
                            m1(1).values = 0.
                            
                            AllModels.calcFlux("0.3 10.0")
                            f1 = AllData(1)
                            f_unabs, f_ul, f_uh, p, q, r = f1.flux
                            
                            # Using f-string for formatting
                            
                            string = f"{inst_tmp},{obsid},{exp_time},{date_start},{tstart_mjd},{rate0310},{indx},{i_l},{i_h},{f},{f_l},{f_h},{f_unabs},{cstat_val},{dof}\n"
                             
                            res.write(string)
                            
                            AllData.clear()
                            AllModels.clear()   
                                                 
                        else:
                            continue
                    
                    os.chdir('..')
    res.close()

os.chdir(main_path)
 

print("#---------------------------#")
print("Finished -- The XSPEC fit has been run on all observations.")
print("#---------------------------#")
