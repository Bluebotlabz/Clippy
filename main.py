# First things, first. Import the wxPython package.
from models import OpenAIModel
import simpleaudio as sa
import random
import json
import wx

with open('./Agent/animations.json') as file:
    animations = json.loads(file.read())

with open('./Agent/states.json') as file:
    states = json.loads(file.read())

with open('./Agent/info.json') as file:
    info = json.loads(file.read())


class ClippyTextBox(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(ClippyTextBox, self).__init__(*args, style=wx.FRAME_SHAPED|wx.STAY_ON_TOP|wx.FRAME_NO_TASKBAR|wx.NO_FULL_REPAINT_ON_RESIZE|wx.MINIMIZE_BOX|wx.SYSTEM_MENU|wx.CLIP_CHILDREN|wx.CLOSE_BOX,**kwargs)
        #self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.SetBackgroundColour(wx.Colour(255, 255, 225))

        self.TextCTRL = wx.TextCtrl(self, style=wx.NO_BORDER|wx.TE_PROCESS_ENTER)

        # Make window fancy and transparent
        ## if wx.Platform == "__WXGTK__":
        ##     self.Bind(wx.EVT_WINDOW_CREATE, self.SetWindowShape)
        ## else:
        ##     self.SetWindowShape()

    def SetWindowShape(self):
        self.SetClientSize((self.bitmap.GetWidth(), self.bitmap.GetHeight()))

        self.region = wx.Region(self.bitmap)
        self.hasShape = self.SetShape(self.region)

class ClippyFrame(wx.Frame):
    def __init__(self, *args, animations, states, info, **kwargs):
        # Create frame
        super(ClippyFrame, self).__init__(*args, style=wx.FRAME_SHAPED|wx.STAY_ON_TOP|wx.FRAME_NO_TASKBAR|wx.NO_FULL_REPAINT_ON_RESIZE|wx.MINIMIZE_BOX|wx.SYSTEM_MENU|wx.CLIP_CHILDREN|wx.CLOSE_BOX,**kwargs)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)


        # Clippy stuff
        self.currentState = "Showing"
        self.currentAnimation = "Show"
        self.nextState = "IdlingLevel2"
        self.nextAnimation = "GetArtsy"
        self.currentAnimationFrame = 0
        self.bitmap = wx.Bitmap('./Agent/Images/0871.bmp')

        self.animations = animations
        self.states = states
        self.info = info

        # Clippy Frame
        self.msgFrame = ClippyTextBox(None)
        self.msgFrame.Show(True)



        # Center the frame on screen (set delta for dragging)
        self.CenterOnScreen(wx.BOTH)
        
        self.MoveMsgFrame()
        self.delta = wx.Point(0,0)

        # AI Stuff
        self.AIModel = OpenAIModel()

        # Make window fancy and transparent
        if wx.Platform == "__WXGTK__":
            self.Bind(wx.EVT_WINDOW_CREATE, self.SetWindowShape)
        else:
            self.SetWindowShape()

        # Bind events
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_MOTION, self.OnMouseMove)



        # Animation system
        self.animationTimer = wx.Timer(self)
        self.animationTimer.StartOnce(10)
        self.Bind(wx.EVT_TIMER, self.AnimationHandler, self.animationTimer)

    def SetWindowShape(self):
        self.SetClientSize((self.bitmap.GetWidth(), self.bitmap.GetHeight()))

        self.region = wx.Region(self.bitmap)
        self.hasShape = self.SetShape(self.region)

    # Handle animation
    def AnimationHandler(self, event):
        # Check animation state
        if (self.currentAnimationFrame >= len(self.animations[self.currentAnimation])):
            self.currentAnimationFrame = 0
            if (self.nextAnimation):
                self.currentAnimation = self.nextAnimation
                self.nextAnimation = None
            elif (self.nextState):
                self.currentState = self.nextState
                self.nextState = None
                self.currentAnimation = random.choice(self.states[self.currentState])
            else:
                self.currentAnimation = None
                self.currentState = None
                return

        # Get image name
        bitmapName = self.animations[self.currentAnimation][self.currentAnimationFrame]["Image"]
        soundName = self.animations[self.currentAnimation][self.currentAnimationFrame]["Sound"]
        if (not bitmapName):
            self.currentAnimationFrame += 1
            self.animationTimer.StartOnce(0)
            return

        self.bitmap = wx.Bitmap('./Agent/Images/' + bitmapName)
        mask = wx.Mask(self.bitmap, wx.Colour(255,0,255,wx.ALPHA_OPAQUE))
        self.bitmap.SetMask(mask)

        # Handle sound stuff
        if (soundName):
            #sound = wx.Sound("./Agent/Audio/" + soundName)
            #sound.Play()
            #wave = sa.WaveObject.from_wave_file("./Agent/Audio/" + soundName)
            #play = wave.play()
            # TODO: Fix sounds
            pass

        # Redraw window
        self.Refresh()
        self.Update()

        # Prepare for next frame
        self.animationTimer.StartOnce(self.animations[self.currentAnimation][self.currentAnimationFrame]["Duration"])
        self.currentAnimationFrame += 1



    # Handle drawing of Clippy
    def OnPaint(self, event):      
        self.SetWindowShape()
        dc = wx.AutoBufferedPaintDCFactory(self)
        dc.DrawBitmap(self.bitmap, -1, -1, True)



    # Movement/"Dragging" code
    def OnLeftDown(self, event):
        self.CaptureMouse()
        x, y = self.ClientToScreen(event.GetPosition())
        self.leftDownOriginX, self.leftDownOriginY = self.GetPosition()
        dx = x - self.leftDownOriginX
        dy = y - self.leftDownOriginY
        self.delta = ((dx, dy))

    def OnLeftUp(self, event):
        if (self.HasCapture()):
            self.ReleaseMouse()

        newX, newY = self.GetPosition()
        if (self.leftDownOriginX == newX and self.leftDownOriginY == newY):
            ###
            # TODO: Implement "bubble GUI"
            ###
            print("NOT MOVED")

    def OnMouseMove(self, event):
        if event.Dragging() and event.LeftIsDown():
            x, y = self.ClientToScreen(event.GetPosition())
            fp = (x - self.delta[0], y - self.delta[1])
            self.SetPosition(fp)
            self.MoveMsgFrame()
            #self.widgetsframe.SetPosition(fp)

    def MoveMsgFrame(self):
        msgPosition = self.GetPosition()
        #self.msgBoxOffset = wx.Point(100, 100)
        self.msgBoxOffset = self.msgFrame.GetSize()
        msgPosition -= self.msgBoxOffset
        self.msgFrame.SetPosition(msgPosition)

class ClippyApp(wx.App):
    def OnInit(self):
        frame = ClippyFrame(None, animations=animations, states=states, info=info)
        self.SetTopWindow(frame)
        frame.Show(True)

        return True

app = ClippyApp()
# Start the event loop.
app.MainLoop()