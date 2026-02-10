# SAPLE: Swift Analysis Pipeline for Lightcurve Extraction
Welcome to SAPLE, the Swift Analysis Pipeline for Lightcurve Extraction. The codes contained in this folder will allow you to: 

1. Run the **UVOT analysis pipeline** on any number of observations you have for one astrophysical source & extract **_absorption corrected_ specific fluxes** derived from an XSPEC fit for all observations and filters;

2. Run the **XRT analysis pipeline** on any number of observations you have for one astrophysical source & extract the **_powerlaw spectral_ information** (flux and photon index) for all observations;

# Disclaimer

This semi-automated pipelines are not meant to substitute, but to complement all the fantastic tools the _Swift_ team has set up. We highly encourage any user to go through the documentation [here](https://www.swift.ac.uk/analysis/index.php) to properly understand the steps that our pipeline streamlines.

# What is different in SAPLE?

1. A **UVOT semi-automated pipeline** that also returns the _absorption corrected_ specific fluxes for your source, a tool which to our knowledge is not available yet to the community;

2. For both XRT and UVOT, the user will produce a **user made source and background regions** and visually check the images for artifacts/issues with the exposure. The XRT online tool to build products runs these checks in the background (and likely much better than any of us can do), but does not allow for user input. With SAPLE, you will be able to make your own (maybe bad) choices for source/background regions.

3. For XRT, you will be able extract a **lightcurve of both flux and photon index** (with associated uncertainties).

4. Upcoming developments [ongoing]: stay tuned for the incorporation of BXA! 

# Prerequisites to using SAPLE

The user needs to install the latest version of [HEASoft](https://heasarc.gsfc.nasa.gov/docs/software/lheasoft/) together with the latest __Swift__ [CALDB](https://heasarc.gsfc.nasa.gov/docs/heasarc/caldb/caldb_intro.html) files on their local computer or try it on a [SciServer](https://heasarc.gsfc.nasa.gov/docs/sciserver/) heasoft environment. The developers have not tested it in the latter, so if you try and some issue arise, please do let us know.

**[IMPORTANT]** -- you need to make sure [**pyXSPEC**](https://heasarc.gsfc.nasa.gov/docs/software/xspec/python/html/buildinstall.html) works before going any further! 

Create your own conda environment:
```
conda create --name sample
```
Then install the following required python packages : 
- [x]  astropy
- [x]  sys
- [x]  os
- [x]  numpy
- [x]  pandas
- [x]  warnings
- [x]  fnmatch

# How to use SAPLE?
The main codes for the SAPLE analysis are stored in main_codes/xrt and main_codes/uvot.

The user has to carefully follow the step-by-step guide for each instrument if they want SAPLE to work. 

For XRT follow the instructions at: **main_codes/xrt/XRT_pipeline_steps.md**

For UVOT follow the instructions at: **main_codes/uvot/UVOT_pipeline_steps.md**

## If you use SAPLE, you better cite: 
TBD (SAPLE) <br>
UVOT/XRT/Swift papers I use in the analyis <br>
links to the nh stuff <br>

## Papers that used SAPLE: 
Pablo's ; Tiffany's student; Vittoria (?)


## Main Developers & Testers : Lea Marcotulli & N&uacute;ria Torres-Alb&agrave;
If any issue arise, please submit an issue on github OR contact us by email: [lea.marcotulli@desy.de](mailto:lea.marcotulli@desy.de)

