# A step-by-step guide on how to run the XRT pipeline

## Starting directory structure:
The main directory (main_dir) can be given any name you like. However, we highly recommend to give it the name of the source you are analyising (e.g. 3C_279). 

In the main directory, copy all the XRT codes (make_base_source_info_file.py, xrt_pc_make_image.py,  xrtpipeline_run.py,  xrt_wt_make_image.py,  xselect_run.py,  xspec_pl_fit.py).

In the main directory, make a subfolder called Swift/ (this name is **non negotiable**) and download ALL the Swift observations you want to analyse in Swift/. The default name of the observations folders is the OBSID number. Again DO NOT change the default name. 

Your folder structure should look like this: 

```
3C_279/ [main_dir]
|
-- make_base_source_info_file.py
-- xrtpipeline_run.py 
-- xrt_pc_make_image.py
-- xrt_wt_make_image.py
-- xselect_run.py
-- xspec_pl_fit.py
-- Swift/
   |
   |-- obsid_1/
   |-- obsid_2/
   |-- obsid_../
   |-- ..
   |-- obsid_N/
```

## XRT pipeline

### Step 0. Activate conda environment, initialize HEASoft and CALDB path
E.g. <br>
```
heainit
caldb
conda activate saple
```

### Step 1. -- Create the file with the relevant information about your source
1. With a text editor, open the code **make_base_source_info_file.py** and change info about the source (RA,DEC,etc) 
2. Run:
   ```
   python make_base_source_info_file.py
   ```
   **Result**: This creates the **base_info.csv** file with all the info that we need about the source for the analysis.

### Step 2. -- Run xrtpipeline
1. Run:
   ```
   python xrtpipeline_run.py > xrtpipeline_run.log
   ```
   **Result**: This will run the main **xrtpipeline** over **all the obsids**; the analysis results are stored in the Swift/xrtout_*obsid* folders
2. **CHECK THE LOG FILE**: search for all instances of "xrtpipeline_0.13.7: Exit" and make sure no errors are reported. [Note: the xrtpipeline version number will depend on your HEASoft installation.]

### Step 3. -- Create the source/background region files for WT and PC
**WT events**: 
1. Edits: in line 73 of **xrt_wt_make_image.py** you can change the src/bkg radius size (e.g. src_wt_size_asec = 50 ##arcsec)
2. Run:
   ```
   python xrt_wt_make_image.py
   ```
   The code will ask for a user input _hit ENTER_ before starting. <br>
   **Result**: in every Swift/xrtout_*obsid* folder, you should have created 5 files: src_wt_fk5.reg, src_wt_phys_centr.reg, src_wt_fk5_centr.reg, bkg_wt_phys, bkg_wt_fk5.reg. In the folder Swift/xrt_png/ you will find the saved WT images with the source and background regions.

**PC events**: 
1. Open with ds9 one XRT/PC event files in one Swift/xrtout_*obsid* (e.g. ds9 Swift/xrtout_00035021001/sw00035021001xpc*po_cl.evt)
2. Select a source region (decide on the size, center on source, and centroid) --> save it as **src_pc.reg** in Swift/
3. Select a bkg region (decide on the size/shape [circle or ellipse]) --> save it as **bkg_pc.reg** in Swift/
4. Run:
   ```
   python xrt_pc_make_image.py 
   ```
   **Result**: in every Swift/xrtout_*obsid* folder, you should have created 1 file: *obsid*_src_cent.reg. In the folder Swift/xrt_pc_png/ and in Swift/xrt_wt_png/ you will find the saved PC and WT images with the source and background regions.

### Step 4. -- Check the images
In the Swift/ folder, you should now see the folder **xrt_pc_png/** and **xrt_wt_png/**. Open it and check the output images to ensure your bkg and source region are well selected. 

**PC images**
+ Ensure no source is present in the background regions created. 
+ Ensure that all src and bkg regions are inside the xrt image. 
  
**WT images**
+ Ensure the source and background region are on the slit. 
           
1. If the source is at the edge of the detector, you can remove the file Swift/xrtout_*obsid*/*xpc*po_cl.evt 
2. If the bkg image is outside some of the frames, you may want to define a different bkg region (step 3).
3. Please refer to the documented problematic cases in Marcotulli \&  \& Torres-Alb&agrave; in prep. (SAPLE) to remove the "bad" observations. 

### Step 5. -- Run xselect to create source and background spectra
Run: 
```
python xselect_run.py 
```
**Result**: This code will create the src.pha; bkg.pha; src_wt.pha and bkg_wt.pha files in the various Swift/xrtout_*obsid*/ folders.
    

## XSPEC FIT 

### Step 6. -- Get the latest XRT RMF file
Copy the latest XRT RMF files for PC and WT you need into the Swift/ folder as **xrt_pc.rmf** and **xrt_wt.rmf**

You can find the latest  response files [here](https://www.swift.ac.uk/analysis/xrt/rmfarf.php).
     
### Step 7. -- Run the powerlaw fit
Run:
```
python xspec_pl_fit.py > xspec_run.log
```
**Results**: 
This code, for every xrtout_obsid does:
+ creates an arf
+ associates the bkg.pha, arf and rmf to the src.pha file
+ groups the source spectrum using optimal binning the source spectrum 
+ fits the spectrum with a tbabs*zpowerlaw using Cash statistics (cstat) and Wilms abundaces (abund wilm)
+ Does the same for WT files 
+ In the Swift/ folder you should have the **params_xspec.csv** file with the spectral fit results: exposure, time of the observation, observation number, instrument of the observation, count rate in the 0.3-10\,\rm keV band, powerlaw index and uncertainty at the 90\% confidence level (C.L.), absorbed powerlaw flux and uncertainty at the 90\% C.L. and unabsorbed powerlaw flux.               
