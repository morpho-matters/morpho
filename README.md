# morpho
Transformation Animator

Version 1.1.0

-=About=-

At its most basic, Morpho is a program that lets you "graph" complex-valued functions as an animated "transformation" where the points in the input grid "move over" to their corresponding output points. Although this was the original idea, Morpho has grown to handle linear transformations (i.e. matrix multiplication) as well as more exotic animations.

At this point, I mainly regard Morpho as an educational tool to help visualize otherwise hard to visualize math functions, but I like to think it has wider applications and could be of some use to professionals who may need a quick way to visualize a complicated transformation in the plane.

Morpho was inspired by Grant Sanderson's brilliant Youtube channel 3Blue1Brown, particularly his video on the Riemann Zeta function and his excellent Essence of Linear Algebra series.

-=Requirements=-

Morpho was written in Python 3 and requires four external modules:
- pyglet
- numpy
- mpmath
- imageio

You should be able to obtain these with the following pip3 commands:

- pip3 install pyglet
- pip3 install numpy
- pip3 install mpmath
- pip3 install imageio

-=Additional instructions for Mac users=-

Pyinstaller seems to have some difficulty handling the tkinter module in some installations of Python 3. If you run into this problem, you might try using the Homebrew installation of Python 3 which worked for me.

If you're on an older version of Mac, after installing the above modules, you may also need to uninstall and reinstall pillow. Try this if you can't get Morpho to run properly on Mac:
- pip3 uninstall pillow
- pip3 install pillow==5.0.0

-=How to Use=-

Once downloaded, running the script Morpho.py should start up Morpho in its out-of-the-box state: you should see the introductory animation play, followed by the main window.

-=How to Export as an Executable=-

The export process is a lot simpler than the last time around. What follows are the steps I took using pyinstaller (which can be obtained via the command "pip3 install pyinstaller").

First, ensure that exportMode is set to True at the top of gui.py. This tells the program to call an external executable when playing animations and not call the script Morpho.py thru Python itself.

Depending on your platform, run the following pyinstaller commands:

- pyinstaller --windowed Morpho.py (on Windows)
- pyinstaller Morpho.py (on Mac)

Two directories will be created called "build" and "dist", the relevant one being "dist" (you can delete "build"). Within "dist" there will be a single directory called "Morpho". Copy and paste the "animations" and "resources" directories into the "dist" directory and you're done.
