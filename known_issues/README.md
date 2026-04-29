<h1>Kwon issues with SAPLE</h1>

<h2>DS9 and image creation</h2>

1. UNICODE CHARACTERS:<br>
When creating the folder that contains the Swift/ folder (e.g. 3C_273) you need to ensure that the folder is created completely with UNICODE characters. You will have issues with DS9 otherwise.

2. CALDB:<br>
If you are using DS9 in the CIAO (Chandra analysis software) environment, please only use this environment to run the codes that produce the images of the field. For all other HeaSOFT based codes, open a new terminal and initialize heasoft, the caldb path and the saple environment as mentioned in the documentation.

3. Remote server connection:<br>
If using SAPLE on a server, you need to ensure you can open the graphical interface of DS9 or you have set up an [X11 virtual frame buffer](https://ds9.si.edu/doc/faq.html#X11). Depending on your connection, there may be a significant delay on opening the window. In case, you need to increase the number of seconds of wait time in the code before launching the DS9 commands.<br>
In the *_make_image.py codes, look for "sleep 10" and change 10 to any number of seconds you may require. 
