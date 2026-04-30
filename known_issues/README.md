<h1>Kwon issues with SAPLE</h1>

<h2>DS9 and image creation</h2>

1. UNICODE CHARACTERS:<br>
When creating the folder that contains the Swift/ folder (e.g. 3C_279/) you need to ensure that the **folder name** only contains **UNICODE characters**. You will have issues with DS9 otherwise.

2. CALDB:<br>
If you are using DS9 in the CIAO (Chandra analysis software) environment, please only use this environment to run the codes that produce the images of the fields (*_make_image.py). For all other HeaSOFT based codes, open a new terminal and initialize HEASoft, the CALDB path and the saple conda environment as mentioned in the official documentation.

3. Remote server connection:<br>
If using SAPLE on a remote server, you need to ensure you can open the graphical interface of DS9 or you have set up an [X11 virtual frame buffer](https://ds9.si.edu/doc/faq.html#X11). Depending on your connection, there may be a significant delay on opening this window. Therefore, you may need to increase the number of seconds of wait time in the code before DS9 commands are launched.<br>
In the *_make_image.py codes, search for "sleep 10" and change "10" to any number of seconds you may require. 
