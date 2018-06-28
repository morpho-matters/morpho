import imageio
import os, sys, platform
import subprocess as sp

# Code tells sp.call() not to make a console window (for Windows)
CREATE_NO_WINDOW = 0x08000000

'''
Compiles the set of image files into an animated gif.
INPUTS:
filenames = List of filenames (or file paths)
directory = Directory of the filenames (defaults to "./")
saveas    = filename of the exported gif
duration  = Duration of each frame in seconds.
            Can be a single number to apply to all frames,
            or a list denoting the duration of each filename.
            Defaults to 0.1 seconds.
            Maximum: 655 seconds. If any duration exceeds this value,
            it will be lowered to the maximum.
'''
# Get location of the Morpho directory.
pwd = os.sep.join(sys.argv[0].split(os.sep)[:-1])
if os.sep not in pwd:
    pwd = os.curdir
pwd += os.sep
def makegif(filenames="*", directory=pwd, saveas=pwd+"movie.gif", \
    duration=0.1):
    # Lower overflows
    if type(duration) is int or type(duration) is float:
        duration = min(duration, 655)
    else:
        for i in range(len(duration)):
            duration[i] = min(duration[i], 655)

    if filenames == "*": filenames = os.listdir(directory)
    initializegif(saveas)
    with imageio.get_writer(saveas, mode='I', duration=duration) as writer:
        for filename in filenames:
            image = imageio.imread(directory + os.sep + filename)
            writer.append_data(image)

# Optimizes a gif file in place using gifsicle.
# Requires the gifsicle executable to be in the current directory.
def optimizegif(filename):
    if not os.path.isfile(filename):
        raise FileNotFoundError
    if platform.system() == "Windows":
        cmd = [pwd+"resources\\gifsicle.exe", "-b", "-O3", "--careful", filename]
        sp.call(cmd, creationflags=CREATE_NO_WINDOW)
    else:
        cmd = [pwd+"resources"+os.sep+"gifsicle", "-b", "-O3", "--careful", filename]
        sp.call(cmd)

# Attempts to initialize an empty GIF file.
# If file already exists, does nothing.
# Although this is not technically necessary for GIF creation,
# it allows a way to test a filepath's validity.
def initializegif(filename):
    # if filename exists, then nothing needs to be done.
    if os.path.isfile(filename):
        return
    # Try to make the file.
    with open(filename, "a") as file:
        pass
