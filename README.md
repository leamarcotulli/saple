# SAPLE: Swift Analysis Pipeline for Lightcurve Extraction
Welcome to SAPLE, the Swift Analysis Pipeline for Lightcurve Extraction. The codes contained in this folder will allow you to: 

1. Run the **UVOT analysis pipeline** on any number of observations you have for one astrophysical source & extract **_absorption corrected_ specific fluxes** and related uncertainties for all observations and filters;

2. Run the **XRT analysis pipeline** on any number of observations you have for one astrophysical source & extract the **_powerlaw spectral_ information** -- absorbed and unabsorbed flux, and photon index and related uncertainties -- for all observations;

# Disclaimer

This semi-automated pipelines are **not meant to substitute, but to complement** all the fantastic tools the _Swift_ team has set up. We highly encourage any user to go through the documentation [here](https://www.swift.ac.uk/analysis/index.php) to properly understand the steps that our pipeline streamlines.

In particular, the [XRT Swift tools](https://www.swift.ac.uk/user_objects/) are optimized for source detection, stacking of spectra and images, and producing XRT flux light-curves. The SAPLE XRT pipeline is optimized to provide lightcurves in both flux and photon index (see next section), the latter not provided by the official tools at the moment. Therefore, we strongly recommend to use the XRT Swift tools unless you want to obtain the lightcurve information SAPLE provides.



# What is different in SAPLE?

1. A **UVOT semi-automated pipeline** that also returns the _absorption corrected_ specific fluxes for your source, a tool which to our knowledge is not available yet to the community;

2. For both XRT and UVOT, the user will produce a **user made source and background regions** and visually check the images for artifacts/issues with the exposure. The XRT online tool to build products runs these checks in the background (and likely much better than any of us can do), but does not allow for user input. With SAPLE, you will be able to make your own choices for source/background regions; the flexibility SAPLE provides also means it should be used with caution, as the official tools are more robust against potential issues with the observations.

3. For XRT, you will be able extract a **lightcurve of both flux and photon index** (with associated uncertainties, assuming a redshifted powerlaw spectrum). We caution the users that pileup issues in the observations are currently not corrected for or flagged by the pipeline (again, something that the XRT Swift tool are optimal for; read [this thread](https://www.swift.ac.uk/analysis/xrt/pileup.php) if you are dealing with bright sources). In the future, we plan to introduce different models or fitting strategies, such as using the Bayesian X-ray Analysis software ([BXA](https://johannesbuchner.github.io/BXA/index.html)). 

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
- [x]  tqdm
- [x]  re

# How to use SAPLE?
The main codes for the SAPLE analysis are stored in main_codes/xrt and main_codes/uvot.

The user has to carefully follow the step-by-step guide for each instrument if they want SAPLE to work. 

<ins>For XRT follow the instructions at:</ins> **main_codes/xrt/README.md**

<ins>For UVOT follow the instructions at:</ins> **main_codes/uvot/README.md**

If you would like to have SAPLE data products but for some reason you are not able to use the pipeline, we are **happy to run SAPLE for you** and provide you with the necessary data products. The condition for us to do this is an _invitation of co-authorship_ into your publication using SAPLE. Please send us an email to inquire about this (see contact info below).  


## If you use SAPLE, please cite: 
Marcotulli \& Torres-Alb&agrave in prep. (SAPLE) <br>

## Publications that have already used SAPLE:
Publications that have used SAPLE in its beta version:<br>
[Penil et al. 2024a](https://ui.adsabs.harvard.edu/abs/2024MNRAS.52710168P/abstract)<br>
[Penil et al. 2024b](https://ui.adsabs.harvard.edu/abs/2024MNRAS.529.1365P/abstract)<br>
Publications that have used SAPLE in its full version:<br>
Giannoli et al. in prep.<br>
Nelson et al. in prep.<br>


## Main Developers & Testers : Lea Marcotulli & N&uacute;ria Torres-Alb&agrave;
If any problems arise, please submit an issue on github OR contact us by email: [lea.marcotulli@desy.de](mailto:lea.marcotulli@desy.de) ; [nuria@virginia.edu](mailto:nuria@virginia.edu) <br><br>

