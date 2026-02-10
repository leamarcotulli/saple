Starting directory structure:

PKS_1424/ [main_dir]
|
-- make_base_source_info_file.py
-- uvot_src_bkg_regions.py
-- uvotsource_run.py
-- uvot_source_extract_flux.py
-- UVOT_pipeline_steps.txt
-- Swift/
   |
   |-- obsid_1/
   |-- obsid_1/
   |-- obsid_../

############################
#
#--------UVOT pipeline
#
############################


Step 0. Initialize heasoft and caldb path


Step 1. -- Create the file with the relevant information about your source
    1a. With a text editor, open the code ***make_base_source_info_file.py** and change info about the source (RA,DEC,etc) 
    1b. Run: python make_base_source_info_file.py 
        Result: This creates the **base_info.csv** file with all the info that we need about the source for the analysis.
        
Step 2. -- Create UVOT source and background regions
    2a. Open any UVOT images of the source (e.g. ds9 Swift/00035021001/uvot/image/sw00035021001ubb_sk.img.gz)
    2b. Make a source region of 5" at the source location (save it at src_uvot.reg in Swift/)
    2c. Make a background region close to the source and without anything else in it (~15" but can be more/less, user should choose)
    2d. Run: python uvot_src_bkg_region.py (the code will ask for a user input [hit enter] before starting)
        Result: in every Swift/*obsid*/uvot/image/ folder, you should have created 3 files: sw*obsid*filt_src.reg, sw*obsid*filt_centr_src.reg, sw*obsid*filt_bkg.reg. In the folder Swift/uvot_png/ you will find the saved UVOT images with the source and background regions for every filter. 

Step 3. -- [IMPORTANT] Remove UVOT bad exposures
    3a. In the Swift/ folder, you should now see the folder uvot_png/. Open it and check the output images to ensure your bkg and source region are well selected. 
    3b. Note that the image is zoomed out, so the small source region will appear displaced; IT IS NOT! 
    3c. Ensure no source are present in the background regions created. 
    3d. Ensure that all src and bkg regions are inside the uvot image. 
        d1. If the source is at the edge of the detector, you can remove the uvot/image folder in the obsid directory
        d2. If the bkg image is outside some of the frames, you may want to redifine your bkg region shifts.  
    3e. Ensure that the image was not taken when the telescope lost pointing (e.g. the image has streaks like sources)
    3f. If there are ANY of the above issues, you can remove the corresponding event file file Swift/*obsid*/uvot/image/sw*obsid*filt*sk.evt 
        
Step 4. -- Run uvotsource on all obsids/filt
    4a. Run: python uvotsource_run.py > uvotsource_log.txt & 
        Result: This will run the uvosource on all the observations and filters present in the folder Swift/; check the log file to see when it's done.
        
Step 5. -- Convert magnitudes to flux
    5a. Run: python uvotsource_extract_flux.py
    5b. Result: In the folder Swift/ you should now see the file "uvot_mag_flux_all_epochs_filters.csv" which contains relevant information for your source filters and fluxes. The code gets the info from the uvotsource output AND calculates the extinction corrected flux [erg/cm/s] and errors (not the same as the uvot output). 
