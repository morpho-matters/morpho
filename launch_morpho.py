from tkinter import messagebox as dialog
import morpho.gui as gui
import sys

pwd = gui.pwd

def runMRM(filename=pwd+"lastplay.mrm", exportFilename=""):
    try:
        state = gui.GUIstate()
        try:
            state.load(filename)
        except:
            dialog.showerror(
                "Load Error",
                "Morpho can't access lastplay.mrm in its own directory. This is necessary in order to play the animation."
                )
            return

        if exportFilename == "":
            state.run()
        else:
            state.export(exportFilename)
    except:
        gui.showStandardError()
        raise

# If an MRM filename is passed to the script, run it!
if len(sys.argv) == 2:
    runMRM(sys.argv[1])
elif len(sys.argv) == 3: # Two filenames means export MRM to GIF
    runMRM(sys.argv[1], sys.argv[2])
else:  # Normal startup
    gui.startGUI()
