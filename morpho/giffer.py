import imageio
import os, platform
import subprocess as sp

# Code tells sp.call() not to make a console window
CREATE_NO_WINDOW = 0x08000000

# ALERT:
# os.sep?
# os.curdir?

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
'''
dotslash = os.curdir + os.sep
def makegif(filenames="*", directory=dotslash, saveas="./movie.gif", duration=0.1):
    if filenames == "*": filenames = os.listdir(directory)
    with imageio.get_writer(saveas, mode='I', duration=duration) as writer:
        for filename in filenames:
            image = imageio.imread(directory + "/" + filename)
            writer.append_data(image)

# Optimizes a gif file in place using gifsicle.
# Requires the gifsicle executable to be in the current directory.
def optimizegif(filename):
    if platform.system() == "Windows":
        cmd = ".\\gifsicle.exe -b -O3 --careful " + filename
        sp.call(cmd, creationflags=CREATE_NO_WINDOW)
    else:
        cmd = os.curdir + os.sep + "gifsicle -b O3 --careful " + filename
        sp.call(cmd, creationflags=CREATE_NO_WINDOW)

# def makegif(filenames, directory="./", saveas="./movie.gif", duration=0.1):
#     images = []
#     for filename in filenames:
#         images.append(imageio.imread(directory + "/" + filename))
#     imageio.mimsave(saveas, images)


# filenames = os.listdir("./export")

# makegif(filenames, "./export", duration=1/30)