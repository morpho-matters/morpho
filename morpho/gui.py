
'''
A note on naming conventions:
I realize in this module I've severely overloaded the word "frame".
In this code, "frame" can refer to any of these three things:

* Tkinter GUI frames
* Animation frames
* Frame "structures" that encode how to build an Animation frame

Tkinter frames are usually clear from context, and amongst the other
two, almost always "frame" refers to the frame structures, not actual
frames of animation. In animation frame names, I tried to prefix the
letter "m", as in "mframe" which is meant to mean "aniMation frame".
'''

import tkinter as tk
from tkinter import filedialog, ttk, messagebox
dialog = messagebox  # I like the name "dialog" better

import os
import subprocess as sp

import morpho.engine as eng
import morpho.whitelist as wh

# Current Morpho version
version = 1.0

# fileVersion should only be changed when animations saved with
# an updated version of Morpho can't be played by older versions.
# This is done since some updates won't affect whether or not
# an animation file can be played (e.g. efficiency improvements)
fileVersion = 1.0

# Loading directly into namespace gives users access to
# complex sin, cos, etc. when applying functions
from morpho.functions import *

# Detects infs and nans (real or complex)
isbadnum = eng.isbadnum
# Code tells sp.call() not to make a console window
CREATE_NO_WINDOW = 0x08000000

# Set exportMode to True if you're going to export Morpho
# as a standalone using pyinstaller.
exportMode = False

# Special exception gets raised if user attempts to load an
# invalid animation file.
class VersionError(Exception):
    pass

class FileFormatError(Exception):
    pass

def showStandardError():
    dialog.showerror(
        "Unexpected error",
        "Sorry! An unexpected error occurred."
        )

# This is the main GUI window that appears when Morpho launches.
class RootWindow(object):

    def __init__(self, settings=None):
        self.root = tk.Tk()
        self.domain = DomainFrame()
        if settings == None:
            self.settings = getSettings()
        else:
            self.settings = settings

        # Hidden variables
        self.frames = [self.domain]  # Framedata objects
        # maxFrameRate = monitorFrameRate()

        # Variables
        # self.maxFps = 60  # Temporarily hard-coded

        ### SETUP WIDGETS ###

        # Root window title
        self.root.wm_title("Morpho")

        # Main frame
        mainFrame = tk.Frame(self.root)
        mainFrame.pack(side="top")

        # -View subFrame1-
        self.realMin = tk.StringVar(value="-5")
        self.realMax = tk.StringVar(value="5")
        self.imagMin = tk.StringVar(value="-5")
        self.imagMax = tk.StringVar(value="5")

        viewFrame = tk.Frame(mainFrame)
        viewFrame.pack(side="top", padx=20, pady=20)

        # "Imag" label
        tk.Label(master=viewFrame, text="Imag") \
            .grid(sticky="s", padx=5, row=0, column=1)

        # "Real" label
        tk.Label(master=viewFrame, text="Real") \
            .grid(sticky="w", padx=5, row=1, column=0)

        # "View" label
        tk.Label(master=viewFrame, text="VIEW") \
            .grid(padx=10, row=2, column=1)

        # realMin textbox
        realMinBox = tk.Entry(
            master=viewFrame, name="realMin", width=10, textvariable=self.realMin
            )
        realMinBox.grid(row=2, column=0)

        # realMax textbox
        realMaxBox = tk.Entry(
            master=viewFrame, width=10, textvariable=self.realMax
            )
        realMaxBox.grid(row=2, column=2)

        # imagMin textbox
        imagMinBox = tk.Entry(
            master=viewFrame, width=10, textvariable=self.imagMin
            )
        imagMinBox.grid(padx=5, row=3, column=1)

        # imagMax textbox
        imagMaxBox = tk.Entry(
            master=viewFrame, width=10, textvariable=self.imagMax
            )
        imagMaxBox.grid(padx=5, row=1, column=1)

        # -Options subFrame1
        # Variables
        # Window Dimensions
        self.window_width = tk.StringVar(value="600")
        self.window_height = tk.StringVar(value="600")
        # Frame rate
        self.frameRate = tk.StringVar(value="30")
        # Prerender checkbox
        self.prerender = tk.IntVar(value=0)
        # Tween options radio buttons
        self.tweenMethod = tk.IntVar(value=0)
        self.transition = tk.IntVar(value=0)

        # Create subFrame1
        optFrame = tk.Frame(mainFrame)
        optFrame.pack(side="top", padx=20, pady=20)

        # Create widgets

        dimFrame = tk.Frame(optFrame)
        dimFrame.grid(sticky="w", row=0, column=0)

        tk.Label(master=dimFrame,  text="Window Shape:") \
            .grid(row=0, column=0)

        widthBox = \
        tk.Entry(master=dimFrame, width=6, textvariable=self.window_width)
        widthBox.grid(padx=5, row=0, column=1)

        tk.Label(master=dimFrame,  text="X") \
            .grid(padx=5, row=0, column=2)

        heightBox = \
        tk.Entry(master=dimFrame, width=6, textvariable=self.window_height)
        heightBox.grid(padx=5, row=0, column=3)

        tk.Label(master=dimFrame,  text="pixels") \
            .grid(padx=5, row=0, column=4)

        # Scale to View
        scaleFrame = tk.Frame(optFrame)
        scaleFrame.grid(sticky="w", pady=5, row=1, column=0)

        tk.Button(master=scaleFrame,
            text="Scale to View", width=14, command=self.scaleWindow) \
            .grid(row=0, column=0)

        # Separator frame
        tk.Frame(optFrame).grid(row=2, column=0, pady=10)

        # Framerate frame
        fpsFrame = tk.Frame(master=optFrame)
        fpsFrame.grid(sticky="w", row=3, column=0)

        tk.Label(master=fpsFrame,  text="Frame rate:") \
            .grid(padx=5, row=0, column=0)

        fpsBox = \
        tk.Entry(master=fpsFrame, width=5, textvariable=self.frameRate)
        fpsBox.grid(padx=5, row=0, column=1)

        tk.Label(master=fpsFrame,
            text="frames/sec") \
            .grid(padx=5, row=0, column=2)

        # Prerender checkbox
        prerenderFrame = tk.Frame(master=optFrame)
        prerenderFrame.grid(sticky="w", row=4, column=0)

        tk.Checkbutton(master=prerenderFrame,
            text="Prerender", variable=self.prerender) \
            .grid(row=0, column=0)

        # Separator frame
        tk.Frame(optFrame).grid(row=5, column=0, pady=10)

        # Tween method
        tweenFrame = tk.Frame(optFrame)
        tweenFrame.grid(sticky="w", row=6, column=0)

        tk.Label(master=tweenFrame,
            text="Tween Method:") \
            .grid(sticky="w", padx=5, row=0, column=0)

        tk.Radiobutton(master=tweenFrame,
            text="Direct", variable=self.tweenMethod, value=0) \
            .grid(sticky="w", padx=5, row=0, column=1)

        tk.Radiobutton(master=tweenFrame,
            text="Spiral", variable=self.tweenMethod, value=1) \
            .grid(sticky="w", padx=5, row=0, column=2)

        # Transition frame
        transFrame = tk.Frame(optFrame)
        transFrame.grid(sticky="w", row=7, column=0)

        tk.Label(master=transFrame,
            text="Transition:") \
            .grid(sticky="w", padx=5, row=0, column=0)

        tk.Radiobutton(master=transFrame,
            text="Slow-Fast-Slow", variable=self.transition, value=0) \
            .grid(sticky="w", padx=5, row=0, column=1)

        tk.Radiobutton(master=transFrame,
            text="Steady", variable=self.transition, value=1) \
            .grid(sticky="w", padx=5, row=0, column=2)

        # Separator frame
        tk.Frame(optFrame).grid(row=8, column=0, pady=10)

        # Framelist
        listFrame = tk.Frame(optFrame)
        listFrame.grid(sticky="w", row=9, column=0)

        tk.Label(master=listFrame, text="Frames:") \
            .grid(sticky="w", padx=5, row=0, column=0)

        self.listbox = tk.Listbox(master=listFrame, width=35, height=7)
        self.listbox.grid(sticky="w", row=1, column=0)
        # Populate listbox
        for frm in self.frames:
            # Append triple asterisks if it's a hidden frame
            name = frm.name if not frm.hide else frm.name + "***"
            self.listbox.insert("end", name)
        # Bind double-click to edit()
        self.listbox.bind("<Double-Button-1>", self.edit)

        # Select the first entry
        highlight(self.listbox, 0)

        # Modifiers
        modFrame = tk.Frame(listFrame)
        modFrame.grid(sticky="n", row=1, column=1)

        topButton = tk.Button(modFrame, text="TOP", width=5, command=self.top)
        topButton.grid(sticky="w", row=0)

        upButton = tk.Button(modFrame, text="^", width=5, command=self.up)
        upButton.grid(sticky="w", row=1)

        downButton = tk.Button(modFrame, text="v", width=5, command=self.down)
        downButton.grid(sticky="w", row=2)

        botButton = tk.Button(modFrame, text="BOT", width=5, command=self.bot)
        botButton.grid(sticky="w", row=3)

        # Button frame
        bFrame1 = tk.Frame(optFrame)
        bFrame1.grid(sticky="w", row=10)

        tk.Button(bFrame1, text="Edit", width=7, command=self.edit) \
            .grid(sticky="we", padx=5, pady=5, row=0, column=0)

        tk.Button(bFrame1, text="Apply Function", width=14,
            command=self.applyFunc) \
            .grid(sticky="we", padx=5, pady=5, row=0, column=1)

        tk.Button(bFrame1, text="Delete", width=7, command=self.delete) \
            .grid(sticky="we", padx=5, pady=5, row=0, column=2)

        tk.Button(bFrame1, text="Save", width=7, command=self.saveButton) \
            .grid(sticky="we", padx=5, pady=5, row=1, column=0)

        tk.Button(bFrame1, text="PLAY!", width=14, command=self.play) \
            .grid(sticky="we", padx=5, pady=5, row=1, column=1)

        tk.Button(bFrame1, text="Load", width=7, command=self.loadButton) \
            .grid(sticky="we", padx=5, pady=5, row=1, column=2)

        tk.Button(bFrame1, text="Exit", width=5, command=self.exit) \
            .grid(sticky="we", padx=5, pady=5, row=1, column=3)

        # Catch close event
        self.root.protocol("WM_DELETE_WINDOW", self.exit)

        # self.render()


    def render(self):
        # Render GUI
        self.root.mainloop()

    # Updates the listbox based on the current self.frames
    def updateListbox(self):
        # Clear listbox
        self.listbox.delete(0, "end")

        # Populate listbox
        for frm in self.frames:
            # Append triple asterisks if it's a hidden frame
            name = frm.name if not frm.hide else frm.name + "***"
            self.listbox.insert("end", name)

    # Returns the frame structure object corresponding to the
    # currently highlighted name in the Frames listbox.
    def getSelection(self):
        # If no selection, do nothing.
        selection = self.listbox.curselection()
        if len(selection) == 0: return None

        # Get selected frame (not just its name)
        index = int(selection[0])
        return getFrameByName(self.listbox.get(index).replace("***", ""),
            self.frames)

    # Updates the window dimension boxes so that it is in scale
    # with the current View settings.
    def scaleWindow(self):
        # Check GUI state
        if not self.sanityCheck(): return

        # Get height to length ratio

        # Read in widget data
        realMin = float(self.realMin.get())
        realMax = float(self.realMax.get())
        imagMin = float(self.imagMin.get())
        imagMax = float(self.imagMax.get())
        window_width = int(self.window_width.get())
        window_height = int(self.window_height.get())

        aspect = (imagMax - imagMin) / (realMax-realMin)

        # Window dimensions always adjust by SHRINKING a dimension
        # in order to avoid getting absurd window dimensions
        if aspect > 1:  # Tall
            self.window_width.set(str(round(window_height/aspect)))
        elif aspect < 1:
            self.window_height.set(str(round(window_width*aspect)))
        else:
            window_width, window_height = (max(window_width, window_height),)*2
            self.window_width.set(str(window_width))
            self.window_height.set(str(window_height))

    # Buttons
    # Move highlighted frame to the top
    def top(self):
        frm = self.getSelection()
        if frm == None: return

        self.frames.remove(frm)
        self.frames.insert(0, frm)

        self.updateListbox()

        highlight(self.listbox, 0)


    # Move highlighted frame up one
    def up(self):
        frm = self.getSelection()
        if frm == None: return

        # Get index of selected frame. Do nothing if at top.
        i = self.frames.index(frm)
        if i == 0: return

        self.frames.remove(frm)
        self.frames.insert(i-1, frm)

        self.updateListbox()

        highlight(self.listbox, i-1)

    # Move highlighted frame down one
    def down(self):
        frm = self.getSelection()
        if frm == None: return

        i = self.frames.index(frm)
        if i == len(self.frames) - 1: return

        self.frames.remove(frm)
        self.frames.insert(i+1, frm)

        self.updateListbox()

        highlight(self.listbox, i+1)


    # Move highlighted frame to the bottom
    def bot(self):
        frm = self.getSelection()
        if frm == None: return

        self.frames.remove(frm)
        self.frames.append(frm)

        self.updateListbox()

        highlight(self.listbox, len(self.frames)-1)

    # Dummy is needed since edit() is used as a handler
    # to the double-click event of the listbox.
    # Handlers have to except an "event" argument, which
    # I'm not using. Hence I've named the argument "dummy"
    def edit(self, dummy=None):
        # if not self.sanityCheck(): return

        frm = self.getSelection()

        # If no selection, do nothing.
        if frm == None: return

        # Based on frame type, determine which dialog to open
        if frm.type == "domain":
            window = EditDomainWindow(self, frm)
        else:
            window = ApplyWindow(self, frm, newFrame=False)


    def applyFunc(self):
        # if not self.sanityCheck(): return

        frm = self.getSelection()

        # If no selection, do nothing.
        if frm == None: return

        ApplyWindow(self, frm, newFrame=True)

    def delete(self):
        frame = self.getSelection()
        if frame == None: return

        if frame.type == "domain":
            dialog.showerror(
                "Delete Error",
                "You can't delete the Domain frame.")
            return

        # Check for dependencies
        for frm in self.frames:
            if frm.type != "domain" and frm.base == frame.id:
                if not dialog.askyesno(
                    "Delete dependent frames?",
                    "You constructed other frames by applying a function to this frame. Deleting it will delete all frames dependent on it. Proceed?"):
                    return
                break

        self.removeFrameAndDescendents(frame)

        # self.removeFrame(frame)

        # i = self.frames.index(frame)
        # self.frames.remove(frame)

        # self.updateListbox()
        # highlight(self.listbox, min(i, len(self.frames)-1))

    # Removes the given frame structure and all its dependent frames
    def removeFrameAndDescendents(self, frame):
        # Remove the given frame.
        i = self.frames.index(frame)
        self.frames.remove(frame)
        self.updateListbox()
        highlight(self.listbox, min(i, len(self.frames)-1))

        # Check the remaining frames for children and remove them.
        # This while-loop hack is needed because removeFrameAndDescendents()
        # will modify the self.frames list, thus we need to reinitialize
        # the loop every time we call it.
        flag = True
        while flag:
            flag = False
            for frm in self.frames:
                if frm.type != "domain" and frm.base == frame.id:
                    self.removeFrameAndDescendents(frm)
                    flag = True
                    break
            # Exit the while-loop only if we get thru the for-loop unscathed

    # Checks all of the user inputs to make sure they can be validly
    # parsed and turned into a valid animation.
    # Displays an error to the user if a problem was found and returns False.
    # Optionally, displaying an error message can be suppressed by specifying
    # False to the optional argument showerror.
    def sanityCheck(self, showerror=True):
        # Attempt to read in all inputs.
        try:
            realMin = float(self.realMin.get())
            realMax = float(self.realMax.get())
            imagMin = float(self.imagMin.get())
            imagMax = float(self.imagMax.get())
            window_width = int(self.window_width.get())
            window_height = int(self.window_height.get())
            frameRate = float(self.frameRate.get())
            prerender = bool(self.prerender.get())
            tweenMethod = ["direct", "spiral"][self.tweenMethod.get()]
            transition = self.transition.get()
        except ValueError:
            if showerror:
                dialog.showerror(
                    "Error",
                    "One of the entry boxes couldn't be parsed. Please recheck them."
                    )
            return False

        # Now check the values themselves
        if realMin >= realMax:
            if showerror:
                dialog.showerror(
                    "Bad view extents",
                    "Real Min must be less than Real Max.")
            return False
        if imagMin >= imagMax:
            if showerror:
                dialog.showerror(
                    "Bad view extents",
                    "Imaginary Min must be less than Imaginary Max.")
            return False
        if window_width <= 0 or window_height <= 0:
            if showerror:
                dialog.showerror(
                    "Bad window dimensions",
                    "Window dimensions must be positive.")
            return False
        if isbadnum(frameRate) or frameRate <= 0.0:
            if showerror:
                dialog.showerror(
                    "Bad frame rate",
                    "Frame rate must be a positive real number.")
            return False

        # Check that at least one frame is visible
        allHidden = True
        for frm in self.frames:
            if not frm.hide:
                allHidden = False
                break
        if allHidden:
            if showerror:
                dialog.showerror(
                    "Frame error",
                    "All your frames are hidden. You must have at least one visible frame.")
            return False

        return True


    def play(self):
        '''
        This is a hack to get around a bug where successive
        plays of an animation would progressively have
        laggier framerates. This was probably due to
        memory clean up not happening properly.
        To get around this, Morpho saves the current
        animation state in a file locally in its own
        directory and then calls a separate instance
        of itself to read it in and play the animation.
        '''
        # self._run(); return  # Uncomment if debugging the _run() method.

        if not self.sanityCheck(): return

        try:
            self.save("./lastplay.mrm")
        except PermissionError:
            dialog.showerror(
                "File permission error",
                "Morpho doesn't have permission to write files in its own directory. This is required in order to play animations."
                )
            return
        except:
            dialog.showerror(
                "File error",
                "Morpho isn't able to write files in its own directory. This is required in order to play animations."
                )
            return

        # exportMode should be set to True at the beginning of this file
        # if you're about to export Morpho as a standalone.
        # If you're just trying to run the script, exportMode should
        # be set to False.
        if exportMode:
            sp.call("player.exe", creationflags=CREATE_NO_WINDOW)
        else:
            sp.call("python player.py", creationflags=CREATE_NO_WINDOW)

    # This method will ACTUALLY play the animation.
    # The play() method just writes the animation
    # to the disk so that another instance of the GUI can then
    # read it and play it.
    # This is done to circumvent an unknown problem in pyglet
    # that prevented animations from being efficiently played
    # more than once.
    def _run(self):
        # Sanity check GUI inputs
        if not self.sanityCheck(showerror=False):
            raise RuntimeError("Some widgets are unparsable.")

        # Check all function formulas against the whitelist
        if not wh.checkFramelist(self.frames):
            dialog.showerror(
                "Invalid functions",
                "This animation can't be played since some of the function formulas are invalid."
                )
            return
        # If you made it here, then all the function formulas should be safe.

        # Read in all inputs
        realMin = float(self.realMin.get())
        realMax = float(self.realMax.get())
        imagMin = float(self.imagMin.get())
        imagMax = float(self.imagMax.get())
        window_width = int(self.window_width.get())
        window_height = int(self.window_height.get())
        frameRate = float(self.frameRate.get())
        prerender = bool(self.prerender.get())
        tweenMethod = ["direct", "spiral"][self.tweenMethod.get()]
        transition = self.transition.get()

        # Setup basic animation settings
        mation = eng.Animation()
        mation.frameRate = frameRate
        mation.view = [realMin, realMax, imagMin, imagMax]
        mation.windowShape = (window_width, window_height)
        if transition == 1:
            mation.transition = eng.Animation.linear
        mation.tweenMethod = tweenMethod

        # Compile all the frames!
        # First we need the domain frame.
        # Find it and construct it!
        for frm in self.frames:
            if frm.type == "domain": break
        if frm.grid == "Standard":
            domFrame = eng.standardGrid(
                view=mation.view,
                nhorz=frm.nhorz, nvert=frm.nvert,
                hres=frm.horzRes, vres=frm.vertRes,
                hmidlines=frm.horzMidlines,
                vmidlines=frm.vertMidlines,
                BGgrid=frm.BGgrid, axes=frm.axes,
                delay=frm.delay*frameRate)
        else:
            # Resolution is taken to be the maximum supplied res
            # amongst horizontal and vertical
            domFrame = eng.zetaGrid(max(frm.horzRes, frm.vertRes))

        domFrame.id = 0
        domFrame.optimizePaths()

        # Create polar grid from square, centered domain grid
        polargrid = lambda s: Re(s)*exp(Im(s)/imagMax*pi/2*i)

        # Now let's create all the other frames!
        # Construct the (visible) descendents of a parent mframe
        def constructDescendents(parent, ID):
            nonlocal polargrid

            # Get child list of framedata structures
            children = []
            for frm in self.frames:
                if frm.type != "domain" and frm.base == ID:
                    children.append(frm)

            mframes = []
            for child in children:
                # Construct evaluation function
                expr = child.function
                expr = expr.replace("^", "**")  # Pythonize carets

                func = eval("lambda s, polargrid=polargrid: complex(" + expr + ")")

                # Apply the function to the parent frame
                try:
                    mframe = parent.fimage(func)
                except:
                    raise Exception("fimage error")

                mframe.delay = round(child.delay*frameRate)
                mframe.id = child.id
                mframes.append(mframe)
                mframes.extend(constructDescendents(mframe, child.id))
            return mframes


        mframes = [domFrame]
        mframes.extend(constructDescendents(domFrame, ID=0))

        # Isolate visible frames
        visibleFrames = []
        for frm in self.frames:
            if not frm.hide:
                visibleFrames.append(frm)

        # Arrange the mframes in the order of visibleFrames
        rearranged = []
        for frm in visibleFrames:
            for mfrm in mframes:
                if mfrm.id == frm.id:
                    rearranged.append(mfrm)
        mframes = rearranged

        # Add in the frames for the animation!
        mation.keyframes = mframes

        # Get timing for each frame tween
        for n in range(1, len(visibleFrames)):
            mation.frameCount.append(
                max(2, round(visibleFrames[n].tweenDuration*frameRate)))

        # Prerender if necessary
        if prerender:
            mation.prerender()

        # RUN!!!!
        mation.run()

    # Attempt to read in the animation file
    # Check that it's a valid MRM file also.
    # Returns the sections list if successful,
    # returns an empty list if anything fails
    def readMRM(self, filename):
        try:
            with open(filename, "r") as file:
                content = file.read().strip()
                sections = content.split("\n\n")
            preamble = sections[0]
            if preamble != "Morpho animation file":
                raise FileFormatError()
            loadedVersion = float(sections[1])
            if loadedVersion > fileVersion:
                raise VersionError()
        except:
            # Anything goes wrong, return []
            return []

        return sections

    '''
    Updates the GUI state based on the loaded file.
    Standard morpho animation file format (*.mrm):

    Morpho preamble
    Version number
    Basic animation settings
    Frame 1
    Frame 2
    etc.
    '''
    def load(self, filename):
        # Read in file (if possible)
        if not os.path.isfile(filename):
            raise FileNotFoundError
        with open(filename, "r") as file:
            sections = file.read().strip().split("\n\n")
        preamble = sections[0]
        if preamble != "Morpho animation file":
            raise FileFormatError("Invalid morpho animation file")
        try:
            loadedVersion = float(sections[1])
        except (IndexError, ValueError):
            raise FileFormatError("Invalid morpho animation file")
        if loadedVersion > fileVersion:
            raise VersionError("This version of Morpho can't load this animation")

        # Third section is the basic animation settings
        items = sections[2].split("\n")
        basicSettings = {}
        for item in items:
            pair = item.split(" : ")
            basicSettings[pair[0].strip()] = pair[1].strip()

        # Now go frame by frame

        # "Primitive" since the values are all strings,
        # not proper data types
        primitiveFrames = []
        for n in range(3, len(sections)):
            items = sections[n].split("\n")
            settings = {}
            for item in items:
                pair = item.split(" : ")
                settings[pair[0].strip()] = pair[1].strip()
            primitiveFrames.append(settings)

        # Now build the actual framedata objects
        frames = []
        for primFrm in primitiveFrames:
            if primFrm["type"] == "domain":
                frm = DomainFrame(**primFrm)
                frm.id = int(frm.id)
                frm.hide = (frm.hide == "True")
                frm.nhorz = int(frm.nhorz)
                frm.nvert = int(frm.nvert)
                frm.horzRes = float(frm.horzRes)
                frm.vertRes = float(frm.vertRes)
                frm.horzMidlines = (frm.horzMidlines == "True")
                frm.vertMidlines = (frm.vertMidlines == "True")
                frm.axes = (frm.axes == "True")
                frm.BGgrid = (frm.BGgrid == "True")
                frm.BG = str2floatTuple(frm.BG)
                frm.tweenDuration = float(frm.tweenDuration)
                frm.delay = float(frm.delay)
            else:
                frm = RangeFrame(**primFrm)
                frm.id = int(frm.id)
                frm.hide = (frm.hide == "True")
                frm.base = int(frm.base)
                frm.tweenDuration = float(frm.tweenDuration)
                frm.delay = float(frm.delay)
            frames.append(frm)

        self.frames = frames

        # # Update the nextID parameter to be greater than all the
        # # frame ID's currently in the frame list.
        # self.nextID = 1 + max([frm.id for frm in self.frames])

        # Build the basic animation GUI
        self.realMin.set(fl2str(float(basicSettings["realMin"])))
        self.realMax.set(fl2str(float(basicSettings["realMax"])))
        self.imagMin.set(fl2str(float(basicSettings["imagMin"])))
        self.imagMax.set(fl2str(float(basicSettings["imagMax"])))
        self.window_width.set(basicSettings["window_width"])
        self.window_height.set(basicSettings["window_height"])
        self.frameRate.set(fl2str(float(basicSettings["frameRate"])))
        self.prerender.set(int(basicSettings["prerender"] == "True"))
        self.tweenMethod.set(["direct", "spiral"].index(basicSettings["tweenMethod"]))
        self.transition.set(int(basicSettings["transition"]))

        # Refresh the frame list
        self.updateListbox()

    # Saves the GUI state into the given filename.
    # This function will give no warning about overwriting a file!
    # Returns True if save was successful. Else False.
    def save(self, filename):
        # sanityCheck widget inputs
        if not self.sanityCheck(): return

        # Read in all widgets
        realMin = float(self.realMin.get())
        realMax = float(self.realMax.get())
        imagMin = float(self.imagMin.get())
        imagMax = float(self.imagMax.get())
        window_width = int(self.window_width.get())
        window_height = int(self.window_height.get())
        frameRate = float(self.frameRate.get())
        prerender = bool(self.prerender.get())
        tweenMethod = ["direct", "spiral"][self.tweenMethod.get()]
        transition = self.transition.get()

        # Build a dict representing the basic animation settings
        state = {
            "realMin": realMin,
            "realMax": realMax,
            "imagMin": imagMin,
            "imagMax": imagMax,
            "window_width": window_width,
            "window_height": window_height,
            "frameRate": frameRate,
            "prerender": prerender,
            "tweenMethod": tweenMethod,
            "transition": transition
        }

        # Stringify all the data and prepare it to be written
        content = "Morpho animation file\n\n"+str(fileVersion)+"\n\n"
        for key in state:
            content += key + " : " + str(state[key]) + "\n"
        content += "\n"

        for frm in self.frames:
            content += str(frm)
            content += "\n\n"

        content = content.strip()

        # Now write the file!
        with open(filename, "w") as file:
            file.write(content)

    def saveButton(self):
        # sanityCheck
        if not self.sanityCheck(): return

        # Ask the user (possibly repeatedly) where to save the file.
        while True:
            filename = filedialog.asksaveasfilename(
                initialdir="./animations", defaultextension="mrm",
                filetypes=(("Morpho Animation", "*.mrm"),)
                )

            if filename == "": return

            # Try to save the file
            try:
                self.save(filename)
            except PermissionError:
                dialog.showerror(
                    "Permission Error!",
                    "Can't save in that location. Access denied. You'll have to save the file somewhere else."
                    )
                continue
            except:
                dialog.showerror(
                    "Unknown error",
                    "Some unknown error prevented saving in that location. Try saving somewhere else."
                    )
                continue
            break

    def loadButton(self):
        # Show load warning
        if self.settings["showLoadWarning"]:
            if not dialog.askyesno(
                "Load Warning",
                "WARNING: You should be careful before playing any animation file obtained from an untrusted source. There is a small risk that an attacker could inject malicious code into an animation file." \
                +"\n\n" \
                +"However, you do not need to worry about this if you are loading an animation from a trusted source such as your own animations or the preloaded animations." \
                +"\n\n" \
                +"Do you want to see this warning again in the future?"
                ):

                self.settings["showLoadWarning"] = False
                saveSettings(self.settings)

        # Ask the user (possibly repeatedly) for the file to open.
        while True:
            filename = filedialog.askopenfilename(
                initialdir="./animations", defaultextension="mrm",
                filetypes=(("Morpho Animation", "*.mrm"), ("All Files", "*.*"))
                )

            # User canceled.
            if filename == "": return

            # Check that the file exists
            if not os.path.isfile(filename):
                dialog.showerror(
                    "File not found!",
                    "The file couldn't be found.")
                continue

            # Attempt to read in the file
            sections = self.readMRM(filename)
            if len(sections) == 0:
                dialog.showerror(
                    "Invalid file.",
                    "The selected file isn't a valid Morpho Animation file.")
                continue
            break

        # Okay, the file is valid. Let's load it in.
        self.load(filename)

    def exit(self):
        if not dialog.askyesno("Exit Morpho", "Are you sure?"): return
        self.root.destroy()

class EditDomainWindow(object):

    def __init__(self, parent, frame):

        self.frame = frame

        self.parent = parent

        self.root = tk.Toplevel()
        self.root.bind("<Escape>", self.cancel)

        # Root window title
        self.root.wm_title("Edit Domain")

        # Main frame
        mainFrame = tk.Frame(self.root)
        mainFrame.pack(side="top")

        # Top Frame
        # Grid Type, grid controls
        gridFrame1 = tk.Frame(mainFrame)
        gridFrame1.grid(sticky="w", padx=10, pady=5)

        tk.Label(master=gridFrame1, text="Grid Type:") \
            .grid(sticky="w", padx=5, row=0, column=0)

        self.gridOpts = tk.StringVar(master=self.root, value=frame.grid)
        self.gridMenu = tk.OptionMenu(
            gridFrame1, self.gridOpts, "Standard", "Zeta"
            )
        self.gridMenu.config(width=7)
        self.gridMenu.grid(sticky="w", padx=5, row=0, column=1)

        gridFrame2 = tk.Frame(mainFrame)
        gridFrame2.grid(sticky="w", padx=10, pady=5, row=1)

        tk.Label(master=gridFrame2, text="Horizontal Lines:") \
            .grid(sticky="w", padx=5, row=1, column=0)

        self.nhorz = tk.StringVar(self.root, value=str(frame.nhorz))
        tk.Entry(master=gridFrame2, width=5, textvariable=self.nhorz) \
            .grid(sticky="w", padx=5, row=1, column=1)

        # Separater frame
        tk.Frame(gridFrame2).grid(padx=5, row=1, column=2)

        tk.Label(master=gridFrame2, text="Resolution:") \
            .grid(sticky="w", padx=5, row=1, column=3)

        self.horzRes = tk.StringVar(self.root, value=fl2str(frame.horzRes))
        tk.Entry(master=gridFrame2, width=3, textvariable=self.horzRes) \
            .grid(sticky="w", padx=5, row=1, column=4)

        self.horzMidlines = tk.IntVar(self.root, value=int(frame.horzMidlines))
        tk.Checkbutton(master=gridFrame2,
            text="Midlines", variable=self.horzMidlines) \
            .grid(sticky="w", padx=5, row=1, column=5)

        # Vertical lines

        tk.Label(master=gridFrame2, text="Vertical Lines:") \
            .grid(sticky="w", padx=5, row=2, column=0)

        self.nvert = tk.StringVar(self.root, value=str(frame.nvert))
        tk.Entry(master=gridFrame2, width=5, textvariable=self.nvert) \
            .grid(sticky="w", padx=5, row=2, column=1)

        # Separater frame
        tk.Frame(gridFrame2).grid(padx=5, row=2, column=2)

        tk.Label(master=gridFrame2, text="Resolution:") \
            .grid(sticky="w", padx=5, row=2, column=3)

        self.vertRes = tk.StringVar(self.root, value=fl2str(frame.vertRes))
        tk.Entry(master=gridFrame2, width=3, textvariable=self.vertRes) \
            .grid(sticky="w", padx=5, row=2, column=4)

        self.vertMidlines = tk.IntVar(self.root, value=int(frame.vertMidlines))
        tk.Checkbutton(master=gridFrame2,
            text="Midlines", variable=self.vertMidlines) \
            .grid(sticky="w", padx=5, row=2, column=5)

        checkboxFrame = tk.Frame(mainFrame)
        checkboxFrame.grid(sticky="w", padx=10, pady=5)

        self.axes = tk.IntVar(self.root, value=int(frame.axes))
        tk.Checkbutton(master=checkboxFrame,
            text="Axes", variable=self.axes) \
            .grid(sticky="w", padx=5)

        self.BGgrid = tk.IntVar(self.root, value=int(frame.BGgrid))
        tk.Checkbutton(master=checkboxFrame,
            text="Static BG grid", variable=self.BGgrid) \
            .grid(sticky="w", padx=5, row=0, column=1)

        self.hide = tk.IntVar(self.root, value=int(frame.hide))
        tk.Checkbutton(master=checkboxFrame,
            text="Hidden", variable=self.hide) \
            .grid(sticky="w", padx=5, row=1, column=0)

        timeFrame = tk.Frame(mainFrame)
        timeFrame.grid(sticky="w", padx=10, pady=5)

        tk.Label(master=timeFrame, text="Tween Duration:") \
            .grid(sticky="w", padx=5, row=0, column=0)

        self.tweenDuration = tk.StringVar(self.root,
            value=fl2str(frame.tweenDuration))
        tweenBox = tk.Entry(master=timeFrame, width=5,
            textvariable=self.tweenDuration)
        tweenBox.grid(sticky="w", padx=5, row=0, column=1)
        tweenBox.bind("<Return>", self.ok)

        tk.Label(master=timeFrame, text="seconds") \
            .grid(sticky="w", padx=5, row=0, column=2)

        tk.Label(master=timeFrame, text="Delay:") \
            .grid(sticky="w", padx=5, row=1, column=0)

        self.delay = tk.StringVar(self.root, value=fl2str(frame.delay))
        delayBox = tk.Entry(master=timeFrame, width=5,
            textvariable=self.delay)
        delayBox.grid(sticky="w", padx=5, row=1, column=1)
        delayBox.bind("<Return>", self.ok)

        tk.Label(master=timeFrame, text="seconds") \
            .grid(sticky="w", padx=5, row=1, column=2)

        buttonFrame = tk.Frame(mainFrame)
        buttonFrame.grid(sticky="we", padx=10, pady=5)

        tk.Button(buttonFrame, text="OK", width=7, command=self.ok) \
            .grid(sticky="we", padx=5, pady=5, row=0, column=0)

        tk.Button(buttonFrame, text="Cancel", width=7, command=self.cancel) \
            .grid(sticky="we", padx=5, pady=5, row=0, column=1)

        self.render()

    def render(self):
        self.root.focus_set()
        self.root.grab_set()
        self.root.transient(self.parent.root)
        self.root.wait_window(self.root)

    def ok(self, dummy=None):
        # Sanity check!
        if not self.sanityCheck(): return

        self.frame.grid = self.gridOpts.get()
        self.frame.nhorz = int(self.nhorz.get())
        self.frame.horzRes = float(self.horzRes.get())
        self.frame.horzMidlines = bool(self.horzMidlines.get())
        self.frame.nvert = int(self.nvert.get())
        self.frame.vertRes = float(self.vertRes.get())
        self.frame.vertMidlines = bool(self.vertMidlines.get())
        self.frame.axes = bool(self.axes.get())
        self.frame.BGgrid = bool(self.BGgrid.get())
        self.frame.hide = bool(self.hide.get())
        self.frame.tweenDuration = float(self.tweenDuration.get())
        self.frame.delay = float(self.delay.get())

        self.parent.updateListbox()

        self.root.destroy()

    def cancel(self, dummy=None):
        self.root.destroy()

    # Checks all of the user inputs to make sure they can be validly
    # parsed and turned into a valid animation.
    # Displays an error to the user if a problem was found and returns False.
    # Optionally, displaying an error message can be suppressed by specifying
    # False to the optional argument showerror.
    def sanityCheck(self, showerror=True):
        # Attempt to read in all inputs.
        try:
            nhorz = int(self.nhorz.get())
            horzRes = float(self.horzRes.get())
            nvert = int(self.nvert.get())
            vertRes = float(self.vertRes.get())
            tweenDuration = float(self.tweenDuration.get())
            delay = float(self.delay.get())
        except ValueError:
            if showerror:
                dialog.showerror(
                    "Error",
                    "One of the entry boxes couldn't be parsed. Please recheck them."
                    )
            return False

        # Now check the values themselves
        if nhorz < 0 or nvert < 0:
            if showerror:
                dialog.showerror(
                    "Line count error",
                    "Horizontal and vertical line counts must be nonnegative integers.")
            return False
        if isbadnum(horzRes) or isbadnum(vertRes) or \
            horzRes <= 0 or vertRes <= 0:
            if showerror:
                dialog.showerror(
                    "Resolution error",
                    "Resolution values must be positive real numbers.")
            return False
        if isbadnum(tweenDuration) or tweenDuration < 0:
            if showerror:
                dialog.showerror(
                    "Tween Duration error",
                    "Tween Duration must be a nonnegative real number.")
            return False
        if isbadnum(delay) or delay < 0:
            if showerror:
                dialog.showerror(
                    "Delay error",
                    "Delay must be a nonnegative real number.")
            return False

        return True

class ApplyWindow(object):

    def __init__(self, parent, frame, newFrame=True):

        self.newFrame = newFrame

        self.parent = parent

        if newFrame:
            # Use given frame as a base to construct a new frame
            self.frame = self.defaultFrame(frame)
        else:
            # Edit the given frame
            self.frame = frame

        self.root = tk.Toplevel()
        self.root.bind("<Escape>", self.cancel)

        # Root window title
        if newFrame:
            self.root.wm_title("Apply Function")
        else:
            self.root.wm_title("Edit " + self.frame.name)

        # Main frame
        mainFrame = tk.Frame(self.root)
        mainFrame.pack(side="top")

        # Top Frame
        topFrame = tk.Frame(mainFrame)
        topFrame.grid(sticky="w", padx=10, pady=10)

        tk.Label(master=topFrame, text="Apply the function:") \
            .grid(sticky="w", padx=5, row=0, column=0)

        subFrame = tk.Frame(topFrame)
        subFrame.grid(sticky="w", row=1, column=0)

        tk.Label(master=subFrame, text="f(s) =") \
            .grid(sticky="w", padx=5, row=0, column=0)

        self.function = tk.StringVar(self.root, value=self.frame.function)
        self.functionBox = tk.Entry(
            master=subFrame, width=30, textvariable=self.function)
        self.functionBox.grid(sticky="w", padx=5, row=0, column=1)
        self.functionBox.bind("<Return>", self.ok)

        # Separator frame
        tk.Frame(topFrame).grid(row=2, column=0, pady=10)

        text = 'to the "' + getFrameByID(self.frame.base, self.parent.frames).name \
            + '" frame,\nand name the resulting frame:'
        tk.Label(master=topFrame, text=text, justify="left") \
            .grid(sticky="w", padx=5, row=3, column=0)

        self.name = tk.StringVar(self.root, value=self.frame.name)
        self.nameBox = tk.Entry(
            master=topFrame, width=15, textvariable=self.name)
        self.nameBox.grid(sticky="w", padx=5, row=4, column=0)
        self.nameBox.bind("<Return>", self.ok)

        self.hide = tk.IntVar(self.root, value=int(self.frame.hide))
        self.hideCheckbox = tk.Checkbutton(master=topFrame,
            text="Hidden", variable=self.hide) \
            .grid(sticky="w", row=5, column=0)

        botFrame = tk.Frame(mainFrame)
        botFrame.grid(sticky="w", padx=10, pady=10, row=1)

        tk.Label(master=botFrame, text="Tween duration:") \
            .grid(sticky="w", padx=5, row=0, column=0)

        self.tweenDuration = tk.StringVar(self.root,
            value=fl2str(self.frame.tweenDuration))
        self.tweenDurBox = tk.Entry(
            master=botFrame, width=5, textvariable=self.tweenDuration)
        self.tweenDurBox.grid(sticky="w", padx=5, row=0, column=1)
        self.tweenDurBox.bind("<Return>", self.ok)

        tk.Label(master=botFrame, text="seconds") \
            .grid(sticky="w", padx=5, row=0, column=2)

        tk.Label(master=botFrame, text="Delay:") \
            .grid(sticky="w", padx=5, row=1, column=0)

        self.delay = tk.StringVar(self.root, value=fl2str(self.frame.delay))
        self.delayBox = tk.Entry(master=botFrame, width=5, textvariable=self.delay)
        self.delayBox.grid(sticky="w", padx=5, row=1, column=1)
        self.delayBox.bind("<Return>", self.ok)

        tk.Label(master=botFrame, text="seconds") \
            .grid(sticky="w", padx=5, row=1, column=2)

        buttonFrame = tk.Frame(mainFrame)
        buttonFrame.grid(sticky="we", padx=10, pady=10, row=2)

        tk.Button(buttonFrame, text="OK", width=7, command=self.ok) \
            .grid(sticky="we", padx=5, pady=5, row=0, column=0)

        tk.Button(buttonFrame, text="Cancel", width=7, command=self.cancel) \
            .grid(sticky="we", padx=5, pady=5, row=0, column=1)

        self.functionBox.focus_set()

        self.render()


    def render(self):
        self.root.focus_set()
        self.root.grab_set()
        self.root.transient(self.parent.root)
        self.root.wait_window(self.root)


    def defaultFrame(self, baseFrame):
        # Next ID is 1 + max ID to guarantee uniqueness
        frm = RangeFrame(base=baseFrame.id,
            id=1+max([frm.id for frm in self.parent.frames]))
            # id=self.parent.nextID)
        # self.parent.nextID += 1

        # Handle name conflicts
        parentNameList = [frm.name for frm in self.parent.frames]
        n = 2
        while frm.name in parentNameList:
            frm.name = "Range " + str(n)
            n += 1

        return frm

    def ok(self, dummy=None):
        # Sanity check
        if not self.sanityCheck(): return

        parentNameList = [frm.name for frm in self.parent.frames]

        self.frame.function = self.function.get()
        self.frame.name = self.name.get().strip()
        self.frame.hide = bool(self.hide.get())
        self.frame.tweenDuration = float(self.tweenDuration.get())
        self.frame.delay = float(self.delay.get())

        if self.newFrame:
            self.parent.frames.append(self.frame)
            self.parent.updateListbox()

            # Highlight the new frame in the listbox
            highlight(self.parent.listbox, len(self.parent.frames)-1)

        else:
            self.parent.updateListbox()

            # Keep original selection highlighted
            i = self.parent.frames.index(self.frame)
            highlight(self.parent.listbox, i)

        self.root.destroy()


    def cancel(self, dummy=None):
        self.root.destroy()

    # Checks all of the user inputs to make sure they can be validly
    # parsed and turned into a valid animation.
    # Displays an error to the user if a problem was found and returns False.
    # Optionally, displaying an error message can be suppressed by specifying
    # False to the optional argument showerror.
    def sanityCheck(self, showerror=True):
        # Attempt to read in all inputs.
        try:
            function = str(self.function.get())
            name = str(self.name.get())
            tweenDuration = float(self.tweenDuration.get())
            delay = float(self.delay.get())
        except ValueError:
            if showerror:
                dialog.showerror(
                    "Error",
                    "One of the entry boxes couldn't be parsed. Please recheck them."
                    )
            return False

        # Now check the values themselves
        parentNameList = [frm.name for frm in self.parent.frames]
        # Boolean condition fun!
        newFrame = self.newFrame
        conflict = (name.strip() in parentNameList)
        nameChanged = (name.strip() != self.frame.name)
        if (newFrame and conflict) or (not newFrame and nameChanged and conflict):
            if showerror:
                dialog.showerror(
                    "Name Conflict!",
                    "The given name conflicts with an already existing frame.")
            return False
        if ":" in function:
            if showerror:
                dialog.showerror(
                    "Function error!",
                    "Functions can't contain colons (:)")
            return False
        if "'" in function or '"' in function:
            if showerror:
                dialog.showerror(
                    "Function error!",
                    "Functions can't contain quotes (\") or apostrophes (')")
            return False
        if ":" in name:
            if showerror:
                dialog.showerror(
                    "Name error!",
                    "Names can't contain colons (:)")
            return False
        if "***" in name:
            if showerror:
                dialog.showerror(
                    "Name error!",
                    "Names can't contain triple asterisks (***)")
            return False
        if name.strip() == "":
            if showerror:
                dialog.showerror(
                    "Name error!",
                    "You must supply a name for the frame.")
            return False
        if isbadnum(tweenDuration) or tweenDuration < 0:
            if showerror:
                dialog.showerror(
                    "Tween Duration error",
                    "Tween Duration must be a nonnegative real number.")
            return False
        if isbadnum(delay) or delay < 0:
            if showerror:
                dialog.showerror(
                    "Delay error",
                    "Delay must be a nonnegative real number.")
            return False

        # Check that the function formula is safe
        if not wh.safeExpr(function):
            if showerror:
                dialog.showerror(
                    "Function Error!",
                    "The function isn't valid.")
            return False
        # If you made it here, the function formula should be safe.

        # Attempt to construct a lambda out of the function
        # formula in order to check for SyntaxError
        # IMP: This should be done AFTER the input has been
        # checked to be a safe expression!
        expr = self.function.get()
        try:
            eval("lambda s: complex(" + expr + ")")
        except SyntaxError:
            if showerror:
                dialog.showerror(
                    "Syntax Error",
                    "The function you entered has invalid syntax.")
            return False

        return True

# # Not used (yet)
# colormap = {
#     "black": (0,0,0),
#     "white": (1,1,1),
#     "red": (1,0,0),
#     "green": (0,1,0),
#     "blue": (0,0,1),
#     "yellow": (1,1,0),
#     "magenta": (1,0,1),
#     "cyan": (0,1,1)
# }

# Creates a standard domain framedata object.
# Optionally, you can specify keyword arguments to modify
# the default dictionary settings.
class DomainFrame(object):

    def __init__(self, **kwargs):
        self.name = "Domain"
        self.type = "domain"
        self.id = 0
        self.hide = False
        self.grid = "Standard"
        self.nhorz = 11
        self.nvert = 11
        self.horzRes = 1
        self.vertRes = 1
        self.horzMidlines = True
        self.vertMidlines = True
        self.axes = True
        self.BGgrid = True
        self.BG = (0,0,0)
        self.tweenDuration = 3
        self.delay = 0

        for kw in kwargs:
            setattr(self, kw, kwargs[kw])

    def __str__(self):
        st = ""
        for kw in self.__dict__:
            st += kw + " : " + str(self.__dict__[kw]) + "\n"
        st = st.strip()
        return st

class RangeFrame(object):

    def __init__(self, **kwargs):
        self.name = "Range"
        self.type = "range"
        self.id = 1
        self.hide = False
        self.function = "s"
        self.base = 0
        self.tweenDuration = 3
        self.delay = 2

        for kw in kwargs:
            setattr(self, kw, kwargs[kw])

    def __str__(self):
        st = ""
        for kw in self.__dict__:
            st += kw + " : " + str(self.__dict__[kw]) + "\n"
        st = st.strip()
        return st

def getFrameByName(name, framelist):
    for frm in framelist:
        if frm.name == name:
            return frm

def getFrameByID(ID, framelist):
    for frm in framelist:
        if frm.id == ID:
            return frm

# Highlights the specified index of a listbox's items
def highlight(listbox, index):
    listbox.select_set(index)
    listbox.event_generate("<<ListboxSelect>>")

# Better float2str conversion function.
# If a float is equal to an int, don't stringify
# the trailing ".0"
# e.g. fl2str(3.0) -> "3" not "3.0"
def fl2str(x):
    if type(x) is int:
        return str(x)
    return str(x) if x != int(x) else str(x)[:-2]

# Turns the string representation of a tuple of numbers
# into a tuple of corresponding floats.
def str2floatTuple(st):
    return tuple(float(item.strip()) \
        for item in st.replace("(", "").replace(")", "").split(","))

# Default special settings for the GUI
defaultSettings = {
    "showLoadWarning" : True
}

# Read in special settings from file
def getSettings(filename="./settings.dat"):
    try:
        with open(filename, "r") as file:
            raw = file.read()
    except:
        dialog.showerror(
            "File read error",
            "Morpho couldn't read in its external settings file. Default settings will be used."
            )
        return defaultSettings
    raw = raw.strip()
    settings = {}
    for line in raw.split("\n"):
        pair = line.split(":")
        settings[pair[0].strip()] = (pair[1].strip() == "True")
    return settings

# Save current special settings as a file
# Returns True/False based on success/failure
def saveSettings(settings, filename="./settings.dat", showerror=True):
    # Stringify settings
    content = ""
    for key in settings:
        content += key + ":" + str(settings[key]) + "\n"
    content = content.strip()

    # Write the file
    try:
        with open(filename, "w") as file:
            file.write(content)
    except:
        if showerror:
            dialog.showerror(
                "File write error",
                "Morpho couldn't save new settings."
                )
        return False
    return True

# Starts the GUI in the standard way.
# Also implements some error handling.
def startGUI():
    # If this is the first-time launch of Morpho, show off
    # the Power Sequence Animation
    if not os.path.isfile("./settings.dat"):
        # Make this file so the next time Morpho is launched,
        # it doesn't show off.
        if not saveSettings(defaultSettings, showerror=False):
            dialog.showerror(
                "File error",
                "Morpho isn't able to write files in its own directory. This is required in order to play animations."
                )
            return

        if exportMode:
            sp.call("player.exe", creationflags=CREATE_NO_WINDOW)
        else:
            sp.call("python player.py", creationflags=CREATE_NO_WINDOW)

    rootWin = RootWindow()
    try:
        rootWin.render()
    except:
        showStandardError()
        raise
