Requirements:
python 2.7 b4bit
pyopenGL 3.12
opencv 3.2.3.18
numpy 1.152
pygame 1.9.4

3 modules:
scene.py is the top level module and runs the glu loop
character.py holds classes required for scene
getMotion.py runs algorithm to exract motion data of video.
run scene.py and press enter to command line prompt to play the scene with extracted motion data in saved text files.
If you would like to run the motion detection alogirthm in getmotion.py and get new data, run scene with user input "y" to command prompt.
Note running getMotion.py will also store images of vector analysis for each frame, in a new directory.
