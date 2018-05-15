
from __future__ import division  # For Python 2

import pyglet as pg
pyglet = pg
import morpho.giffer as giffer
# import time
import math
import cmath
# import traceback

### CONSTANTS ###
pi = cmath.pi
tau = 2*pi
inf = float("inf")
nan = float("nan")
# Detect infinite or nan (real or complex)
isbadnum = lambda x: math.isnan(abs(x)*0)

### CLASSES ###

class Point(object):
    def __init__(self, pos=0):
        self.pos = pos
        self.strokeWeight = 1
        # self.color = (0,0,0)
        self.fill = (1,0,0)
        self.style = "circle"
        self.size = 15
        self.static = False

    # "color" attribute acts on "fill" attribute
    @property
    def color(self):
        return self.fill

    @color.setter
    def color(self, value):
        self.fill = value


    # Returns a copy of the point object.
    def copy(self):
        P = Point()
        P.pos = self.pos
        P.strokeWeight = self.strokeWeight
        # P.color = self.color
        P.fill = self.fill
        P.style = self.style
        P.size = self.size
        return P

    # Returns "tweened" point between p and q given time t in [0,1]
    def tween(self, other, t, method="spiral"):
        p = self
        q = other
        if type(q) is not Point:
            raise Exception("Can't use tweenPoint() on non-Point types!")
        if p == q: return p.copy()

        T = p.copy()

        # Directly tween non-positional attributes
        T.strokeWeight = tween(p.strokeWeight, q.strokeWeight, t)
        T.fill = colorTween(p.fill, q.fill, t)
        T.size = tween(p.size, q.size, t)
        if method == "spiral":
            r1 = abs(p)
            r2 = abs(q)
            th1 = cmath.phase(p.pos) % tau
            th2 = cmath.phase(q.pos) % tau

            dr = r2 - r1
            dth = argShift(th1, th2)

            r = r1 + t*dr
            th = th1 + t*dth

            T.pos = r*cmath.exp(th*1j)
        elif method == "direct":
            T = p.copy()
            T.pos = tween(p.pos, q.pos, t)
        else:
            raise Exception('Tween method "'+method+'" not recognized!')
        return T

    # Plots the point in the given window with the given view
    # of the complex plane
    def plot(self, view, window):
        S = self
        x,y = screenCoords(S.pos, view, window)
        r = S.size/2

        R,G,B = S.fill
        pg.gl.glLineWidth(S.strokeWeight)
        pg.gl.glColor3f(float(R), float(G), float(B))

        OpenGL_ellipse(x, y, r, r)

    def renderShape(self, window):
        raise Exception("renderShape() doesn't work for now.")
        S = self
        x,y = screenCoords(S.pos, window)
        r = S.size/2

        Pt = createShape(ELLIPSE, x, y, r, r)
        Pt.setFill(S.fill[0], S.fill[1], S.fill[2])
        Pt.setStroke(color(S.color[0], S.color[1], S.color[2]))
        Pt.setStrokeWeight(Pt.strokeWeight)

        return [Pt]

    # Returns the "image" of the point under the function func.
    # The point's style (e.g. fill, size) is preserved.
    def fimage(self, func):
        S = self
        f = func
        if S.static: return S
        fS = S.copy()
        try:
            fS.pos = f(S.pos)
        except:  # Errors map to nan
            fS.pos = nan
        return fS

    def __add__(self, other):
        pos = self.pos + other.pos
        # Eventually should add some sensible way to add colors
        # but for now, color of sum is just default (black)
        return Point(pos)

    def __sub__(self, other):
        return Point(self.pos - other.pos)

    def __neg__(self):
        return Point(-self.pos)

    # Scalar multiplication
    def times(self, c):
        return Point(self.pos * c)

    # Complex multiplication
    def __mul__(self, other):
        z = self.complex()
        w = other.complex()
        S = z*w
        return Point(S.real, S.imag)

    # Complex division
    def __truediv__(self, other):
        z = self.complex()
        w = other.complex()
        S = z/w
        return Point(S.real, S.imag)

    def __abs__(self):
        return abs(self.pos)

    def __str__(self):
        raw = (self.pos, self.col)
        return str(raw)

# Path object.
# Consists of a sequence of complex numbers, an interpolation method,
# and path thickness (width)
class Path(object):
    def __init__(self, seq=[0,1]):
        self.seq = seq
        self.interp = "linear"  # This is the only interp method for now.
        self.color = (0,0,0)
        self.width = 3
        self.deadends = set()
        self.static = False

    # Returns a (deep-ish) copy of the path
    def copy(self):
        C = Path()
        C.seq = self.seq[:]
        C.interp = self.interp
        C.color = self.color
        C.width = self.width
        C.deadends = self.deadends.copy()
        C.static = self.static
        return C

    # Returns an interpolated path between itself and another path.
    def tween(self, other, t, method="spiral"):
        p = self
        q = other
        if type(q) is not Path:
            raise Exception("Can't use tweenPath() on non-Path types!")
        if p == q:
            return p.copy()
        # Check for invalid path seq lengths
        if len(p.seq) != len(q.seq):
            raise Exception("Can't tween paths of different seq lengths!")

        T = p.copy()
        T.color = colorTween(p.color, q.color, t)
        # Tween the stroke widths if necessary
        if p.width != q.width:
            T.width = p.width + t*(q.width - p.width)

        if method == "spiral":
            dthList = []
            for n in range(len(p.seq)):
                r1 = abs(p.seq[n])
                r2 = abs(q.seq[n])
                th1 = cmath.phase(p.seq[n]) % tau
                th2 = cmath.phase(q.seq[n]) % tau

                dr = r2-r1
                dth = argShift(th1, th2)
                dthList.append(dth)

                r = r1 + t*dr
                th = th1 + t*dth

                T.seq[n] = r*cmath.exp(th*1j)

            # This clause disconnects two nodes if they are
            # revolving in different directions too much.
            # The value angle_tol represents how far two oppositely
            # revolving nodes have to angularly differ before
            # we disconnect them.
            angle_tol = 0.053
            if 0.01 < t and t < 0.99:
                for n in range(len(dthList)-1):
                    dth1 = dthList[n]
                    dth2 = dthList[n+1]
                    if dth1*dth2 < 0 and abs(dth1-dth2) > angle_tol:
                        T.deadends.add(n)
        elif method == "direct":
            for n in range(len(p.seq)):
                T.seq[n] = twVal = tween(p.seq[n], q.seq[n], t)
                # Deadend unplottable points
                if isbadnum(twVal):
                    T.deadends.add(n-1)
                    T.deadends.add(n)
        else:
            raise Exception('Tween method "'+method+'" not recognized!')

        return T

    # Returns boolean on whether a path has the same
    # color and width as another. This method is useful
    # in optimizing how paths are drawn.
    def matchesStyle(self, other):
        return (self.color == other.color and \
            self.width == other.width and \
            self.static == other.static)

    # Convenience method that sets up the OpenGL lines
    # before glBegin(GL_LINES) is called.
    def setupStyle(self):
        R,G,B = self.color
        pg.gl.glLineWidth(self.width)
        pg.gl.glColor3f(float(R), float(G), float(B))

    # setup is a parameter you probably will never need to
    # worry about. It is used by the frame plot() function
    # to help optimize the drawing of paths.
    # If set to False, plot() will not set up the OpenGL
    # line parameters or call glBegin() or glEnd().
    # It means you must manually do so if needed.
    # This switch is useful in avoiding unnecessary calls to
    # glBegin() and glEnd() when the OpenGL line parameters
    # don't need to be changed.
    # (e.g. when drawing two paths with matching styles)
    def plot(self, view, window, setup=True):
        S = self
        if setup:
            self.setupStyle()
            pg.gl.glBegin(pg.gl.GL_LINES)
        for n in range(len(S.seq)-1):
            if n in S.deadends: continue
            z1 = S.seq[n]
            z2 = S.seq[n+1]

            if isbadnum(z1) or isbadnum(z2): continue

            x1, y1 = screenCoords(z1, view, window)
            x2, y2 = screenCoords(z2, view, window)

            pg.gl.glVertex2f(x1, y1)
            pg.gl.glVertex2f(x2, y2)

            # stroke(S.color[0], S.color[1], S.color[2])
            # strokeWeight(S.width)
            # line(x1, y1, x2, y2)
        if setup: pg.gl.glEnd()

    def renderShape(self, window):
        raise Exception("Don't use this function. It's deprecated (for now).")
        S = self
        lineseq = []

        for n in range(len(S.seq)-1):
            if n in S.deadends: continue
            z1 = S.seq[n]
            z2 = S.seq[n+1]

            if z1 == inf or z2 == inf: continue

            x1, y1 = screenCoords(z1, window)
            x2, y2 = screenCoords(z2, window)

            Line = createShape(LINE, x1, y1, x2, y2)
            Line.setStroke(color(S.color[0], S.color[1], S.color[2]))
            Line.setStrokeWeight(S.width)

            lineseq.append(Line)
        return lineseq

    # Returns the "image" of the path under the complex function func.
    # The path's style (e.g. color, width) are copied.
    def fimage(self, func):
        S = self
        f = func
        if S.static: return S
        fS = S.copy()
        for n in range(len(S.seq)):
            try:
                fS.seq[n] = f(S.seq[n])
            except:  # Errors map to nan
                fS.seq[n] = nan

        # fS.seq = [f(z) for z in S.seq]
        return fS

    # Returns a path that is the concatenation of self with other.
    # Copies self's style parameters, though.
    # Supplying False to the parameter "connectEnds" causes the
    # concatenated path to not connect the last node of self
    # to the first node of other.
    def concat(self, other, connectEnds=True):
        result = self.copy()
        result.seq += other.seq
        len_self = len(self.seq)
        if not connectEnds:
            result.deadends.add(len_self-1)

        # Merge deadends from other into result
        for n in other.deadends:
            result.deadends.add(n+len_self)

        return result

    # For convenience, + does the same thing as self.concat(other)
    def __add__(self, other):
        return self.concat(other)

# A single (key)frame of animation
class Frame(object):
    def __init__(self, points=[], paths=[]):
        self.points = points
        self.paths = paths
        self.background = (0,0,0)
        self.delay = 0  # frames
        self.optimized = False

    # Returns a (deep-ish) copy of the frame
    def copy(self):
        frame = Frame()
        frame.points = self.points[:]
        frame.paths = self.paths[:]
        frame.background = self.background
        frame.delay = self.delay
        frame.optimized = self.optimized
        return frame

    def tween(self, other, t, method="spiral"):
        p = self
        q = other
        if type(q) is not Frame:
            raise Exception("Can't use tweenFrame() on non-Frame types!")
        if p == q: return p.copy()

        if len(p.points) != len(q.points):
            raise Exception("Can't tween Frames with different number of points!")
        if len(p.paths) != len(q.paths):
            raise Exception("Can't tween Frames with different number of paths!")

        T = p.copy()
        T.delay = 0  # Tweened frames are never delayed
        T.background = colorTween(p.background, q.background, t)
        # In future, T.background will be tweened.
        # Also will take into account T.delay

        for n in range(len(p.points)):
            T.points[n] = p.points[n].tween(q.points[n], t, method)
        for n in range(len(p.paths)):
            T.paths[n] = p.paths[n].tween(q.paths[n], t, method)

        return T

    # This function optimizes a frame for plotting by concatenating
    # all sequential paths of matching style in the path list.
    def optimizePaths(self):
        if self.optimized: return
        if len(self.paths) == 0: return
        paths = []
        basePath = self.paths[0]
        for n in range(1, len(self.paths)):
            currentPath = self.paths[n]
            if basePath.matchesStyle(currentPath):
                basePath = basePath.concat(currentPath, connectEnds=False)
            else:
                paths.append(basePath)
                basePath = currentPath
        paths.append(basePath)
        self.paths = paths
        self.optimized = True

    # Returns a copy of the frame as a FastFrame frame.
    # Note that this will automatically optimize the Paths of
    # the frame!
    def prerender(self, view, window):
        pre = FastFrame()
        pre.background = self.background
        pre.delay = self.delay

        # Batch up the frame point by point
        for point in self.points:
            # batch = pg.graphics.Batch()
            vertices = []
            for th in range(0, 360, 10):
                th *= DEG2RAD
                x,y = screenCoords(point.pos, view, window)
                r = point.size/2
                vertices.append(x + r*math.cos(th))
                vertices.append(y + r*math.sin(th))

            color = tuple(round(255*c) for c in point.fill)
            num_segments = len(vertices)//2
            pre.pointTable_add(vertices, color*num_segments)
            # num_segments = len(vertices)//2
            # batch.add(num_segments, pg.gl.GL_TRIANGLE_FAN, None,
            #     ("v2f", tuple(vertices)),
            #     ("c3B", color*num_segments) )
            # pre.points.append(batch)

        # Populate the pathTable of the fast frame.
        self.optimizePaths()
        for p in range(len(self.paths)):
            path = self.paths[p]
            # batch = pg.graphics.Batch()

            # Get a list of vertices the batch should render
            vertices = []
            for n in range(len(path.seq)-1):
                if n in path.deadends:
                    xy0 = xy1 = (inf, inf)
                else:
                    z0 = path.seq[n]
                    z1 = path.seq[n+1]
                    xy0 = screenCoords(z0, view, window)
                    xy1 = screenCoords(z1, view, window)
                vertices.extend(xy0)
                vertices.extend(xy1)

            # Convert path RGB color into (255,255,255) form
            color = tuple(round(255*c) for c in path.color)
            num_segments = len(vertices)//2

            # batch.add(num_segments, pg.gl.GL_LINES, None,
            #     ("v2f", tuple(vertices)),
            #     ("c3B", color*num_segments) )
            pre.pathTable_add(
                tuple(vertices),
                color*num_segments,
                )
            # pre.paths.append(batch)
            pre.pathWidths.append(path.width)

        return pre

    def plot(self, view, window):
        S = self
        R,G,B = S.background
        pg.gl.glClearColor(R,G,B,1)
        pg.gl.glClear(pg.gl.GL_COLOR_BUFFER_BIT)
        # background(S.background[0], S.background[1], S.background[2])
        for n in range(len(S.paths)):
            obj = S.paths[n]
            prev = S.paths[n-1]
            if n == 0:
                obj.setupStyle()
                pg.gl.glBegin(pg.gl.GL_LINES)
                obj.plot(view, window, setup=False)
            elif not obj.matchesStyle(prev):
                # print(n)
                pg.gl.glEnd()
                obj.setupStyle()
                pg.gl.glBegin(pg.gl.GL_LINES)
                obj.plot(view, window, setup=False)
            else:
                obj.plot(view, window, setup=False)
        if len(S.paths) > 0: pg.gl.glEnd()
        for obj in S.points:
            obj.plot(view, window)

    def fimage(self, func):
        S = self
        f = func
        fS = S.copy()
        fS.paths = [obj.fimage(f) for obj in S.paths]
        fS.points = [obj.fimage(f) for obj in S.points]
        return fS

# This is a special frame object that contains batches of
# prerendered OpenGL vertices. Objects from this class are
# generated from the prerender() method in an Animation
# object, and has the advantage over regular Frames in that
# the plot() function should work WAY faster!
# However, it is a specialized class and so is less versatile
# than the regular Frame class otherwise.
# The correct thing to do is to create all frames you want to
# animate BEFOREHAND as regular Frames, then convert them
# to prerendered Frames as the last step.
# The Animation class's prerender() method does exactly this.
class FastFrame(object):
    def __init__(self):
        self.pointTable = []
        self.pathTable = []
        self.pathWidths = []
        self.background = (0,0,0)
        self.delay = 0

    # Updates the pointTable similarly to how pathTable is updated.
    # See pathTable_add() for more info.
    def pointTable_add(self, vertexData, colorData):
        self.pointTable.append([vertexData, colorData])

    """
    Updates the pathTable. Designed to take in inputs similarly
    to how batch.add() does.

    Example:

    fframe.pathTable_add(
        (20,20, 30,30),
        (0,255,0, 0,255,0)
        )
    """
    def pathTable_add(self, vertexData, colorData):
        # Update pathTable
        self.pathTable.append([vertexData, colorData])

    def plot(self):  # You may want to add a "window" param later
        raise Exception("FastFrame.plot() is no longer implemented.")

        if len(self.paths) != len(self.pathWidths):
            raise Exception("Unequal lengths of paths and pathWidths!")

        R,G,B = self.background
        pg.gl.glClearColor(R,G,B,1)
        pg.gl.glClear(pg.gl.GL_COLOR_BUFFER_BIT)

        for n in range(len(self.paths)):
            pg.gl.glLineWidth(self.pathWidths[n])
            self.paths[n].draw()

        # Plot point batches
        for point in self.points:
            point.draw()

# A sequence of keyframes, tweened.
class Animation(object):

    def __init__(self, keyframes=[]):
        self.keyframes = keyframes

        # frameCount is how many frames to use to tween a keyframe
        # to the next keyframe (including the initial keyframe).
        # It is a list of length one less than that of keyframes.
        self.frameCount = [50]*(len(keyframes)-1)
        self.frameRate = 30

        # The current view of the complex plane.
        # Specified as [real_min, real_max, imag_min, imag_max]
        self.view = [-10,10, -10,10]
        self.windowShape = (800, 800)

        # transition governs how tweening animation proceeds.
        # It is a function that takes a time parameter in the
        # range [0,1] and returns a time parameter in the same
        # range that denotes the interpolation time value for
        # input into the tween() functions.
        # In future, transition function can vary over frame
        self.transition = Animation.slow_fast_slow

        # tweenMethod denotes what style of animation to use.
        # The default is "spiral" in which points on the complex
        # plane "spiral" over to their destinations during a tween.
        # Future will have alternate tweenMethods like "direct".
        self.tweenMethod = "spiral"

        # Prerendering attributes
        self.prerendered = False
        self.vertexMode = "v2f/stream"
        self.colorMode = "c3B/stream"
        self.frames = []
        self.path_batches = []
        self.point_batches = []
        self.path_vlists = []
        self.point_vlists = []

        # Active animation variables
        self.active = False
        self.window = None
        self.update = None
        self.paused = False
        self.currentFrame = 0
        self.delay = 0

    # Returns a (deep-ish) copy of the animation
    def copy(self):
        ani = Animation()
        ani.keyframes = self.keyframes[:]
        ani.frameCount = self.frameCount
        ani.frameRate = self.frameRate
        ani.view = self.view
        ani.transition = self.transition
        ani.tweenMethod = self.tweenMethod
        ani.prerendered = self.prerendered
        ani.frames = self.frames[:]
        ani.batches = self.batches[:]
        ani.vlists = self.vlists[:]

        ani.currentFrame = self.currentFrame
        ani.delay = self.delay
        return ani

    # Convenience function for user. Creates a window object of specified (or not)
    # width and height and automatically associates the animation to that window.
    def setupWindow(self):
        width, height = self.windowShape
        if self.window != None:
            raise Exception("Animation is still associated with an open window!")
        self.window = pg.window.Window(width, height, resizable=True)


    # Runs the animation
    def run(self, window=None):
        if len(self.keyframes) == 0:
            raise Exception("Can't run animation with no keyframes!")
        if len(self.frameCount) != len(self.keyframes) - 1:
            raise Exception("len(frameCount) != len(keyframes)-1")
        # Handle unspecified window parameter
        if window == None:
            # If animation is just paused, treat run() like resume()
            if self.paused:
                self.resume()
                return

            # If the animation has no associated window, set up one.
            if self.window == None: self.setupWindow()
        else:
            # Throw error if the animation is already associated to an
            # open window, and the user is trying to run it in a different
            # window without first closing the original.
            if self.window != None and self.window != window:
                raise Exception("Animation already associated with an open window. Close it first before reassociating.")
            self.window = window

        self.active = True
        self.window.switch_to()  # Focus on this window for rendering.

        def update(dt, mation=self):
            # if not mation.active:
                # print("update() called while inactive")
            if mation.delay > 0:
                pg.clock.unschedule(mation.update)
                pg.clock.schedule_interval(mation.update, \
                    mation.delay/mation.frameRate)
                mation.delay = -1
            elif mation.delay < 0:
                pg.clock.unschedule(mation.update)
                pg.clock.schedule_interval(mation.update, 1.0/mation.frameRate)
                mation.delay = 0

            if mation.prerendered:
                # Negative delay means we're actively delaying, so
                # decrement the currentFrame to fool Pyglet into
                # freezing on the correct frame.
                if mation.delay < 0:
                    mation.currentFrame -= 1
                else:
                    mation.delay = mation.frames[mation.currentFrame].delay

                mation.drawBatchesAccordingTo(mation.frames[mation.currentFrame])

                mation.currentFrame += 1
                if mation.currentFrame >= len(mation.frames):
                    mation.currentFrame = 0
                    mation.active = False
                    # mation.frames = []  # TEMP!!!
                    pg.clock.unschedule(mation.update)

            elif mation.currentFrame >= sum(mation.frameCount):
                mation.currentFrame = 0
                mation.keyframes[-1].plot(mation.view, mation.window)
                mation.active = False
                pg.clock.unschedule(mation.update)

            else:
                if mation.delay < 0: mation.currentFrame -= 1
                # Compute which keyframe and subFrame we need to plot
                keyID = 0
                subFrame = mation.currentFrame
                while subFrame >= mation.frameCount[keyID]:
                    subFrame -= mation.frameCount[keyID]
                    keyID += 1

                if subFrame == 0:
                    frm = mation.keyframes[keyID]
                    if mation.delay >= 0:
                        mation.delay = frm.delay
                else:
                    frm = mation.keyframes[keyID].tween( \
                        mation.keyframes[keyID+1], \
                        mation.transition(subFrame/mation.frameCount[keyID]), \
                        mation.tweenMethod)

                frm.plot(mation.view, mation.window)

                mation.currentFrame += 1

        self.update = update

        @self.window.event
        def on_draw(mation=self):
            pass

        @self.window.event
        def on_close(mation=self):
            # Reset active animation attributes
            mation.active = False
            mation.window = None
            mation.update = None
            mation.paused = False
            mation.currentFrame = 0
            mation.delay = 0

        @self.window.event
        def on_mouse_press(x, y, button, modifiers, mation=self):
            if mation.paused:
                mation.resume()
            else:
                mation.pause()

        # Reset delay attribute
        self.delay = 0

        pg.clock.schedule_interval(self.update, 1.0/self.frameRate)

        pg.app.run()
        pg.app.exit()

    def export(self):
        if len(self.keyframes) == 0:
            raise Exception("Can't export animation with no keyframes!")
        if len(self.frameCount) != len(self.keyframes) - 1:
            raise Exception("len(frameCount) != len(keyframes)-1")

        if self.window == None: self.setupWindow()

        self.active = True
        self.window.switch_to()  # Focus on this window for rendering.

        def update(dt, mation=self):
            animationEnd = False
            # Reached end of animation. Render final keyframe.
            if mation.currentFrame >= sum(mation.frameCount):
                mation.keyframes[-1].plot(mation.view, mation.window)
                mation.active = False
                pg.clock.unschedule(mation.update)
                animationEnd = True
            else:
                # Compute which keyframe and subFrame we need to plot
                keyID = 0
                subFrame = mation.currentFrame
                while subFrame >= mation.frameCount[keyID]:
                    subFrame -= mation.frameCount[keyID]
                    keyID += 1

                if subFrame == 0:
                    frm = mation.keyframes[keyID]
                else:
                    frm = mation.keyframes[keyID].tween( \
                        mation.keyframes[keyID+1], \
                        mation.transition(subFrame/mation.frameCount[keyID]), \
                        mation.tweenMethod)

                frm.plot(mation.view, mation.window)

            # Save current frame as numbered PNG image.
            filename = "./export/" + int2fixedstr(mation.currentFrame, \
                digits=1+int(math.log10(sum(mation.frameCount)))) + ".png"
            pyglet.image.get_buffer_manager().get_color_buffer().save(filename)

            if animationEnd:
                pg.app.exit()
                mation.window.close()
                resetMation()
            else:
                mation.currentFrame += 1

        self.update = update

        @self.window.event
        def on_draw(mation=self):
            pass

        def resetMation(mation=self):
            # Reset active animation attributes
            mation.active = False
            mation.window = None
            mation.update = None
            mation.paused = False
            mation.currentFrame = 0
            mation.delay = 0

        @self.window.event
        def on_close(mation=self):
            resetMation()

        # Reset delay attribute
        self.delay = 0

        pg.clock.schedule_interval(self.update, 1e-12)

        pg.app.run()
        pg.app.exit()

    def pause(self):
        if not self.active: return
        self.paused = True
        pg.clock.unschedule(self.update)

    def resume(self):
        if not self.active: return
        self.paused = False
        pg.clock.schedule_interval(self.update, 1.0/self.frameRate)

    # Prerenders and optimizes the animation and stores
    # all the frames in self.frames
    def prerender(self):
        if self.window == None:
            self.setupWindow()
        mation = self

        # Discard previous prerender data
        mation.prerendered = True
        mation.frames = []
        mation.path_batches = []
        mation.point_batches = []
        mation.path_vlists = []
        mation.point_vlists = []

        if len(mation.keyframes) == 0: return

        currentFrame = 0
        totalFrameCount = sum(mation.frameCount)
        while currentFrame < totalFrameCount:
            # Compute which keyframe and subFrame we need to plot
            keyID = 0
            subFrame = currentFrame
            while subFrame >= mation.frameCount[keyID]:
                subFrame -= mation.frameCount[keyID]
                keyID += 1

            basicFrame = mation.keyframes[keyID].tween( \
                mation.keyframes[keyID+1], \
                mation.transition(subFrame/mation.frameCount[keyID]), \
                mation.tweenMethod)

            # subFrame == 0 means we're at a keyframe:
            # no tweening necessary
            if subFrame == 0:
                basicFrame.delay = mation.keyframes[keyID].delay

            basicFrame.optimizePaths()

            # Prerender the basicFrame and store the resulting
            # FastFrame.
            mation.frames.append(basicFrame.prerender(mation.view,
                mation.window))

            currentFrame += 1

        # Manually handle the final frame
        lastFrame = mation.keyframes[-1].copy()
        lastFrame.optimizePaths()
        mation.frames.append(lastFrame.prerender(mation.view,
            mation.window))

        # Create initial batches.
        # Initialize them to the first frame's tables
        pointTable = self.frames[0].pointTable
        for b in range(len(pointTable)):
            batch = pg.graphics.Batch()
            vlist = batch.add(len(pointTable[b][0])//2, pg.gl.GL_TRIANGLE_FAN, None,
                (self.vertexMode, pointTable[b][0]),
                (self.colorMode, pointTable[b][1])
                )
            self.point_batches.append(batch)
            self.point_vlists.append(vlist)

        pathTable = self.frames[0].pathTable
        for b in range(len(pathTable)):
            batch = pg.graphics.Batch()
            vlist = batch.add(len(pathTable[b][0])//2, pg.gl.GL_LINES, None,
                (self.vertexMode, pathTable[b][0]),
                (self.colorMode, pathTable[b][1])
                )
            self.path_batches.append(batch)
            self.path_vlists.append(vlist)

    def drawBatchesAccordingTo(self, fframe):
        R,G,B = fframe.background
        pg.gl.glClearColor(R,G,B,1)
        pg.gl.glClear(pg.gl.GL_COLOR_BUFFER_BIT)

        # Update the path vertex lists and draw the path batches
        for b in range(len(self.path_batches)):
            # Update vertex lists
            vlist = self.path_vlists[b]
            vlist.vertices = fframe.pathTable[b][0]
            vlist.colors = fframe.pathTable[b][1]

            pg.gl.glLineWidth(fframe.pathWidths[b])
            self.path_batches[b].draw()

        # Update the point vertex lists and draw the point batches
        for b in range(len(self.point_batches)):
            # Update vertex lists
            vlist = self.point_vlists[b]
            vlist.vertices = fframe.pointTable[b][0]
            vlist.colors = fframe.pointTable[b][1]

            pg.gl.glLineWidth(1)
            self.point_batches[b].draw()

    # This function verifies whether or not the animation is playable.
    # Checks for consistency across the frames (so that tweening works)
    # Checks for consistency between batches and fastframe table
    # lengths.
    #
    # (Currently not implemented. Calling it always returns True)
    def verify():
        return True

    # The standard transition function for Animations.
    # It's similar to the one used in 3Blue1Brown.
    slow_fast_slow = lambda t: (math.atan(14*t-7) + 1.4289)/2.8578

    # No special transition. Just transition linearly at a constant
    # speed to the next keyframe.
    linear = lambda t: t

### HELPERS ###

# Draws an ellipse at the point (x,y) with width 2a
# and height 2b.
# Optionally you can specify dTheta to adjust the angle
# increment in which each vertex of the ellipse is drawn.
# Defaults to 5 degrees.
#
# Importantly: OpenGL_ellipse() assumes you have already specified
# the fill color and stroke width of the ellipse beforehand by
# calling pyglet.gl.glLineWidth() and pyglet.gl.glColor4f()
DEG2RAD = math.pi/180
def OpenGL_ellipse(x, y, a, b, dTheta=10):
    pg.gl.glLineWidth(1)
    pg.gl.glBegin(pyglet.gl.GL_TRIANGLE_FAN)
    for th in range(0,360, dTheta):
        th *= DEG2RAD
        pg.gl.glVertex2f(x + a*math.cos(th), y + b*math.sin(th))
    pg.gl.glEnd()

# Creates a window that animations can take place in.
def createWindow(width=800, height=800):
    return pg.window.Window(width, height)

# Normalizes an RGB triplet into the range [0.0, 1.0]
# RGB can be specified as three separate inputs, or as a
# tuple supplied as one input.
def rgbNormalize(R, G=None, B=None, upperbound=255):
    # If one of the components is missing,
    # assume user supplied RGB as a tuple in the first input.
    if G == None or B == None:
        R,G,B = R
    return (R/upperbound, G/upperbound, B/upperbound)

# Tweens two RGB colors for 0 <= t <= 1
def colorTween(rgb1, rgb2, t):
    if rgb1 == rgb2: return rgb1

    R1, G1, B1 = rgb1
    R2, G2, B2 = rgb2

    dR = R2 - R1
    dG = G2 - G1
    dB = B2 - B1

    R = R1 + t*dR
    G = G1 + t*dG
    B = B1 + t*dB

    return (R,G,B)

# The most generic tween function.
# Takes two numbers and tweens them
# linearly by the parameter t in [0,1]
def tween(a, b, t):
    return a + t*(b-a)

# Flattens a list of lists into a single list.
def flattenList(a):
    flattened = []
    for sublist in a:
        for item in sublist:
            flattened.append(item)
    return flattened

# Converts an int into a string of fixed length given by the
# parameter digits. Works by prepending zeros if the string
# is too short.
def int2fixedstr(n, digits=3):
    str_n = str(n)
    return "0"*(digits-len(str_n)) + str_n

# Computes the correct amount to shift an angle th1 so that it
# becomes th2 in the shortest possible path
# i.e. a path that does not traverse more than pi radians
# The value returned is called "dth" and should be used in
# expressions like this: th(t) = th1 + t*dth
# However, before using the above expression, make sure th1 and th2
# are modded 2pi.
# (Actually, maybe it's okay if they're not?)
def argShift(th1, th2):
    th1 = th1 % tau
    th2 = th2 % tau

    dth = th2 - th1
    if abs(dth) > pi + 1.189e-12:
        dth = dth - math.copysign(tau, dth)
    return dth

# Converts complex coordinates into screen pixel coordinates
# according to the screen dimensions and the set window values.
def screenCoords(z, view, window):
    a,b,c,d = view

    x = window.width/(b-a) * (z.real - a)
    y = window.height/(d-c) * (z.imag - c)

    return x,y

# Generates a path between the complex numbers z1 and z2
# with the default style parameters.
# Optionally specify the number of steps to take between
# z1 and z2. Defaults to 50.
def line(z1, z2, steps=50):
    steps = int(steps)
    dz = (z2-z1)/steps
    seq = [z1]
    for n in range(1,steps):
        seq.append(z1 + n*dz)
    seq.append(z2)
    return Path(seq)

# Generates a path in the shape of an ellipse centered
# at the complex number z0 with semi-width a and
# semi-height b.
# Optionally specify the angular step dTheta to take
# between each node on the elliptical path (in degs).
# Defaults to 5.
def ellipse(z0, a, b, dTheta=5):
    steps = int(math.ceil(360 / dTheta))
    dTheta *= DEG2RAD  # convert dTheta to radians
    seq = [z0 + a]
    for n in range(1, steps):
        seq.append(z0 + a*math.cos(n*dTheta) + b*1j*math.sin(n*dTheta))
    seq.append(seq[0])
    return Path(seq)


def standardGrid(
    view=[-5,5, -5,5],
    nhorz=10, nvert=10,
    hres=1, vres=1,
    hcolor=(0,0,1), vcolor=(0,0,1),
    hmid=(0.5,0.5,1), vmid=(0.5,0.5,1),
    hwidth=3, vwidth=3,
    hmidlines=True, vmidlines=True,
    BGgrid=True, axes=True,
    delay=0):

    xmin, xmax, ymin, ymax = view

    frm = Frame()
    frm.delay = delay
    staticList = []
    if BGgrid:
        hDimColor = tuple(c/2 for c in hcolor)
        vDimColor = tuple(c/2 for c in vcolor)
        # BG horizontal lines
        for n in range(nhorz):
            y = ymin + n*(ymax-ymin)/(nhorz-1) if nhorz != 1 else (ymin+ymax)/2
            Line = Path([xmin+y*1j, xmax+y*1j])
            Line.color = hDimColor
            Line.width = 1
            Line.static = True
            staticList.append(Line)

        # BG vertical lines
        for n in range(nvert):
            x = xmin + n*(xmax-xmin)/(nvert-1) if nvert != 1 else (xmin+xmax)/2
            Line = Path([x+ymin*1j, x+ymax*1j])
            Line.color = vDimColor
            Line.width = 1
            Line.static = True
            staticList.append(Line)

    # Horizontal lines
    for n in range(nhorz):
        y = ymin + n*(ymax-ymin)/(nhorz-1) if nhorz != 1 else (ymin+ymax)/2
        Line = line(xmin+y*1j, xmax+y*1j, steps=50*hres)
        Line.color = hcolor
        Line.width = hwidth
        frm.paths.append(Line)

        if n == nhorz-1: break

        if hmidlines:
            y = ymin + (n+0.5)*(ymax-ymin)/(nhorz-1)
            Line = line(xmin+y*1j, xmax+y*1j, steps=50*hres)
            Line.color = hmid
            Line.width = 1
            frm.paths.insert(0, Line)

    # Vertical lines
    for n in range(nvert):
        x = xmin + n*(xmax-xmin)/(nvert-1) if nvert != 1 else (xmin+xmax)/2
        Line = line(x+ymin*1j, x+ymax*1j, steps=50*vres)
        Line.color = vcolor
        Line.width = vwidth
        frm.paths.append(Line)

        if n == nvert-1: break

        if vmidlines:
            x = xmin + (n+0.5)*(xmax-xmin)/(nvert-1)
            Line = line(x+ymin*1j, x+ymax*1j, steps=50*vres)
            Line.color = vmid
            Line.width = 1
            frm.paths.insert(0, Line)

    # Need to put in axes conditionally next!
    if axes:
        xAxis = Path([xmin, xmax])
        xAxis.static = True
        xAxis.width = 5
        xAxis.color = (1,1,1)
        frm.paths.append(xAxis)

        yAxis = Path([ymin*1j, ymax*1j])
        yAxis.static = True
        yAxis.width = 5
        yAxis.color = (1,1,1)
        frm.paths.append(yAxis)

    # Assemble the frame!
    frm.paths = staticList + frm.paths
    return frm

# Plots a standard input grid for the Zeta function.
# Optionally specify a resolution factor.
def zetaGrid(res=1):
    paths = []
    thins = []

    # Low res Lines
    # Horizontal
    for y in range(-4, -1):
        Line = line(-7+y*1j, 7+y*1j, 14*res)
        Line.color = (0,0,1)
        Line.width = 3
        paths.append(Line)

        # thin Lines
        thin = Line.copy()
        thin.seq = [z+0.5*1j for z in Line.seq]
        thin.color = (0.5, 0.5, 1)
        thin.width = 1
        thins.append(thin)
    for y in range(2, 5):
        Line = line(-7+y*1j, 7+y*1j, 14*res)
        Line.color = (0,0,1)
        Line.width = 3
        paths.append(Line)

        # thin Lines
        if y == 4: continue
        thin = Line.copy()
        thin.seq = [z+0.5*1j for z in Line.seq]
        thin.color = (0.5, 0.5, 1)
        thin.width = 1
        thins.append(thin)

    # Vertical
    for x in range(-7, 0):
        Line = line(x-4j, x+4j, 8*res)
        Line.color = (0,0,1)
        Line.width = 3
        paths.append(Line)

        # thin Lines
        thin = Line.copy()
        thin.seq = [z+0.5 for z in Line.seq]
        thin.color = (0.5, 0.5, 1)
        thin.width = 1
        thins.append(thin)

    for x in range(3, 8):
        Line = line(x-4j, x+4j, 8*res)
        Line.color = (0,0,1)
        Line.width = 3
        paths.append(Line)

        # thin Lines
        if x == 7: continue
        thin = Line.copy()
        thin.seq = [z+0.5 for z in Line.seq]
        thin.color = (0.5, 0.5, 1)
        thin.width = 1
        thins.append(thin)

    # Higher res Lines
    # Horizontal
    for y in range(-1, 2):
        Line = line(-7+y*1j, y*1j, 7*res)
        Line += line(y*1j, 2+y*1j, 20*res)
        Line += line(2+y*1j, 7+y*1j, 5*res)
        Line.color = (0,0,1)
        Line.width = 3
        paths.append(Line)

        # thin Lines
        thin = Line.copy()
        thin.seq = [z + 0.5*1j for z in Line.seq]
        thin.color = (0.5, 0.5, 1)
        thin.width = 1
        thins.append(thin)

    # Vertical
    for x in range(0, 3):
        Line = line(x-4j, x-1j, 3*res)
        Line += line(x-1j, x+1j, 20*res)
        Line += line(x+1j, x+4j, 3*res)
        Line.color = (0,0,1)
        Line.width = 3
        if x != 1: paths.append(Line)

        # thin Lines
        thin = Line.copy()
        thin.seq = [z + 0.5 for z in Line.seq]
        thin.color = (0.5, 0.5, 1)
        thin.width = 1
        thins.append(thin)

    # Extra Lines
    # Horizontal
    for y in range(-19, 20):
        if y % 5 == 0: continue
        y = y/10
        Line = line(-7+y*1j, y*1j, 10*res)
        Line += line(y*1j, 2+y*1j, res*int(75 - abs(y)*60) if abs(y) < 1 else 10*res)
        Line += line(2+y*1j, 7+y*1j, 6*res)
        Line.color = rgbNormalize(191, 87, 0)
        Line.width = 1
        thins.append(Line)

    # Vertical
    for x in range(-19, 40):
        if x % 5 == 0: continue
        x = x/10
        Line = line(x-4j, x-1j, 4*res)
        Line += line(x-1j, x+1j, res*int(75 - abs(x-1)*60) if abs(x-1) < 1 else 10*res)
        Line += line(x+1j, x+4j, 4*res)
        Line.color = (0.8, 0.8, 0)
        Line.width = 1
        thins.append(Line)

    paths = thins + paths

    # Axes
    xAxis = Path([-8, 8])
    xAxis.static = True
    xAxis.width = 5
    xAxis.color = (1,1,1)

    yAxis = Path([-8j, 8j])
    yAxis.static = True
    yAxis.width = 5
    yAxis.color = (1,1,1)

    paths.append(xAxis); paths.append(yAxis)

    return Frame(paths=paths)

# Same as ZetaGrid(), but makes the thick grid lines
# thin, which helps the visuals of the Zeta function.
def zetaGridFinal():
    frm = zetaGrid()
    for path in frm.paths:
        if path.width == 3:
            path.width = 1
    return frm
