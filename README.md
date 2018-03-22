# morpho
Transformation Animator

-=About=-

At its most basic, Morpho is a program that lets you "graph" complex-valued functions as an animated "transformation" where the points in the input grid "move over" to their corresponding output points. Although this was the original idea, Morpho has grown to handle linear transformations (i.e. matrix multiplication) as well as more exotic animations.

At this point, I mainly regard Morpho as an educational tool to help visualize otherwise hard to visualize math functions, but I like to think it has wider applications and could be of some use to professionals who may need a quick way to visualize a complicated transformation in the plane.

Morpho was inspired by Grant Sanderson's brilliant Youtube channel 3Blue1Brown, particularly his video on the Riemann Zeta function and his excellent Essence of Linear Algebra series.

-=Requirements=-

Morpho was written in Python 3 and requires three external modules:
- pyglet
- numpy
- mpmath

You should be able to obtain these with the following pip3 commands:

- pip3 install pyglet
- pip3 install numpy
- pip3 install mpmath

-=How to Use=-

Once downloaded, running the script launch_morpho.py should start up Morpho in its out-of-the-box state: you should see the introductory animation play, followed by the main window.

-=How to Export as an Executable=-

As it currently stands, the export process is a little messy. This is largely because there actually need to be two independent executables as part of the export, since the animation player is separate from the GUI.

What follows are the steps I took using pyinstaller:

First, ensure that exportMode is set to True at the top of gui.py. This tells the program to call an external executable for the animation player and not call player.py.

Next run the following pyinstaller commands:

- pyinstaller --windowed launch_morpho.py
- pyinstaller --windowed player.py

Two directories will be created called "build" and "dist", the relevant one being "dist". Within dist, there will be two directories: one called "launch_morpho" and the other "player". You need to merge these two directories together. I usually just cut and paste the contents of "player" into "launch_morpho" skipping any duplicates; once this is complete, I delete the "player" directory and rename the "launch_morpho" directory to "Morpho", as well as the executable "launch_morpho" to "Morpho".

After this, you need to place an "animations" subdirectory into the Morpho directory which will contain any preloaded animations and provide a place for users to save their own animations. Finally, you need to pick an MRM file to be the introductory animation and place it in the main Morpho directory alongside the executables, but rename it "lastplay.mrm". The name "lastplay.mrm" is crucial, as the animation player looks for this file upon the first startup. I usually pick "power seq.mrm" to be the introductory animation. It can be found in animations/preloaded/complex functions/power seq.mrm
