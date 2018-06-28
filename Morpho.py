from tkinter import messagebox as dialog
import morpho.gui as gui
import os, sys

pwd = gui.pwd

def runMRM(filename=pwd+"resources"+os.sep+"lastplay.mrm", exportFilename=""):
    try:
        state = gui.GUIstate()
        try:
            state.load(filename)
        except FileNotFoundError:
            dialog.showerror(
                "File not found",
                "Morpho couldn't find \""+filename+"\". This is necessary in order to play or export the animation."
                )
            return
        except:
            dialog.showerror(
                "Load Error",
                "Morpho could not load \""+filename+"\". This is necessary in order to play or export the animation."
                )
            return

        if exportFilename == "":
            state.run()
        else:
            state.export(exportFilename)
    except:
        gui.showStandardError()

# Parse script parameters
export = False
play = False
argv = sys.argv[:]
while "--export" in argv:
    argv.remove("--export")
    export = True
while "--play" in argv:
    argv.remove("--play")
    play = True


if export:
    if len(argv) != 3:
        raise Exception("--export flag requires exactly two file paths!")
    runMRM(argv[1], argv[2])
if play:
    if len(argv) < 2:
        raise Exception("No MRM supplied to play!")
    runMRM(argv[1])
if not(export) and not(play):
    # If just one parameter, just start up the Morpho GUI normally
    if len(argv) == 1:
        gui.startGUI()
    else:
        gui.startGUI(argv[1])

# if len(argv) == 2:
#     # If load parameter passed, then load MRM, else play MRM
#     if load:
#         pass
#     else:
#         runMRM(argv[1])
# elif len(argv) == 3: # Two filenames means export MRM to GIF
#     runMRM(argv[1], argv[2])
# else:  # Normal startup
#     gui.startGUI()
