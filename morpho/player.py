from tkinter import messagebox as dialog
import morpho.gui as gui

def main():
    try:
        win = gui.RootWindow(gui.defaultSettings)
        win.root.withdraw()
        try:
            win.load("./lastplay.mrm")
        except:
            dialog.showerror(
                "Load Error",
                "Morpho can't access lastplay.mrm in its own directory. This is necessary in order to play the animation."
                )
            return
        win._run()
    except:
        gui.showStandardError()
        raise