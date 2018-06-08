from tkinter import messagebox as dialog
import morpho.gui as gui
import sys

def runMRM(filename=gui.dotslash+"lastplay.mrm"):
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

        if state.exportFilename == "":
            state.run()
        else:
            state.export()
    except:
        gui.showStandardError()
        raise

# If an MRM filename is passed to the script, run it!
if len(sys.argv) > 1:
    runMRM(sys.argv[-1])
else:  # Normal startup
    gui.startGUI()
