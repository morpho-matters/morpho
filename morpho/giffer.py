import imageio
import os, platform
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
dotslash = os.curdir + os.sep
def makegif(filenames="*", directory=dotslash, saveas=dotslash+"movie.gif", \
    duration=0.1):
    # Lower overflows
    if type(duration) is int or type(duration) is float:
        duration = min(duration, 655)
    else:
        for i in range(len(duration)):
            duration[i] = min(duration[i], 655)

    if filenames == "*": filenames = os.listdir(directory)
    with imageio.get_writer(saveas, mode='I', duration=duration) as writer:
        for filename in filenames:
            image = imageio.imread(directory + os.sep + filename)
            writer.append_data(image)

# Optimizes a gif file in place using gifsicle.
# Requires the gifsicle executable to be in the current directory.
# WARNING: Does NOT check that filename arg is sanitized.
# Check yourself before using it!
def optimizegif(filename):
    if not os.path.isfile(filename):
        raise FileNotFoundError
    if platform.system() == "Windows":
        cmd = [".\\gifsicle.exe", "-b", "O3", "--careful", filename]
        # cmd = '.\\gifsicle.exe -b -O3 --careful "' + filename + '"'
        sp.call(cmd, creationflags=CREATE_NO_WINDOW)
    else:
        # cmd = os.curdir + os.sep + 'gifsicle -b O3 --careful "' + filename + '"'
        cmd = [dotslash+"gifsicle", "-b", "O3", "--careful", filename]
        sp.call(cmd)
