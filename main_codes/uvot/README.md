# A step-by-step guide on how to run the UVOT pipeline

## Starting directory structure:
The main directory (main_dir) can be given any name you like. However, we highly recommend to give it the name of the source you are analyising (e.g. 3C_273). 

In the main directory, copy all the uvot codes ( make_base_source_info_file.py; uvot_src_bkg_regions.py; uvot_source_extract_flux.py).

In the main directory, make a subfolder called Swift/ (this name is non negotiable) and download ALL the Swift observations you want to analyse in Swift/. The default name of the observations folders is the obsid number. Again DO NOT change the default name. 

Your folder structure should look like this: 

```
3C_273/ [main_dir]
|
-- make_base_source_info_file.py
-- uvot_src_bkg_regions.py
-- uvotsource_run.py
-- uvot_source_extract_flux.py
-- UVOT_pipeline_steps.txt
-- Swift/
   |
   |-- obsid_1/
   |-- obsid_2/
   |-- obsid_../
   |-- obsid_N/
```

## UVOT pipeline

### Step 0. Activate conda environment, initialize HEASoft and CALDB path
E.g. <br>
```
conda activate saple
heainit
caldb
```

### Step 1. -- Create the file with the relevant information about your source
1. With a text editor, open the code ***make_base_source_info_file.py** and change info about the source (RA,DEC,etc) 
2. Run:
   ```
   python make_base_source_info_file.py
   ```
   **Result**: This creates the **base_info.csv** file in the main directory with all the info that we need about the source for the analysis.
        
### Step 2. -- Create UVOT source and background regions

1. Open any UVOT images of the source (e.g. ds9 Swift/00035021001/uvot/image/sw00035021001ubb_sk.img.gz)
2. Make a source region of 5" at the source location (save it at src_uvot.reg in Swift/)
3. Make a background region close to the source and without anything else in it (~15" but can be more/less, user should choose)
4. Run:
   ```
   python uvot_src_bkg_region.py > uvot_src_bkg_region.log
   ```
   The code will ask for a user input _hit ENTER_ before starting. <br>
   **Result**: in every Swift/*obsid*/uvot/image/ folder, you should have created 3 files:
   + sw*obsid*filt_src.reg (copy of the original src_uvot.reg; e.g. _sw00035017073um2_src.reg_)
   + sw*obsid*filt_centr_src.reg (centroided version of the src_uvot.reg; e.g. _sw00035017073um2_centr_src.reg_)
   + sw*obsid*filt_bkg.reg  (copy of the original bkg_uvot.reg; e.g. _sw00035017073um2_bkg.reg_).
   
In the folder **Swift/uvot_png/** (created by the code) you will find the **saved ds9 UVOT images** with the source and background regions for every filter. 

### Step 3. -- [IMPORTANT] Remove UVOT bad exposures
1. In the Swift/ folder, you should now see the folder uvot_png/. Open it and check the output images to ensure your bkg and source region are well selected.
2. Note that the image is zoomed out, so the small source region will appear displaced; IT IS NOT!
3. Ensure no source are present in the background regions created.
4. Ensure that all src and bkg regions are inside the uvot image.
5. If the source is at the edge of the detector, you can remove the uvot/image folder in the obsid directory
6. If the bkg image is outside some of the frames, you may want to redifine your bkg region shifts.  
7. Ensure that the image was not taken when the telescope lost pointing (e.g. the image has streaks like sources)
8. If there are ANY of the above issues, you can remove the corresponding event file file Swift/*obsid*/uvot/image/sw*obsid*filt*sk.evt 
        
### Step 4. -- Run uvotsource on all obsids/filt
Run:
```
python uvotsource_run.py > uvotsource.log 
```
**Result**: This will run the uvosource on all the observations and filters present in the folder Swift/; check the log file to see when it's done.
        
### Step 5. -- Convert magnitudes to flux
Run:
```
python uvotsource_extract_flux.py > uvotsource_extract_flux.log 
```
**Result**: In the folder Swift/ you should now see the file "uvot_mag_flux_all_epochs_filters.csv" which contains relevant information for your source filters and fluxes. The code gets the info from the uvotsource output AND calculates the extinction corrected flux [erg/cm/s] and errors (not the same as the uvot output). 
