# First things, first. Import the wxPython package.
from models import ChatGPTModel as OpenAIModel
import simpleaudio as sa
import clipboard
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

        # AI Stuff
        self.AIModel = OpenAIModel()


        self.titleText = wx.StaticText(self, label="What would you like to ask?")
        self.titleText.SetFont(wx.Font(70, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))

        self.responseLabel = wx.StaticText(self, label="Awaiting input.")

        self.TextCTRL = wx.TextCtrl(self, -1, "", wx.DefaultPosition, wx.Size(200,60), style=wx.NO_BORDER|wx.TE_PROCESS_ENTER|wx.TE_MULTILINE)
        wx.CallAfter(self.TextCTRL.SetFocus)


        self.mainBoxSizer = wx.BoxSizer(wx.VERTICAL)
        self.buttonBoxSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.mainBoxSizer.Add(self.titleText, 0, wx.EXPAND|wx.ALL, 5)
        self.mainBoxSizer.Add(self.responseLabel, 0, wx.EXPAND|wx.ALL, 5)
        self.mainBoxSizer.Add(self.TextCTRL, 1, wx.ALL, 5)
        self.mainBoxSizer.AddSpacer(1)
        self.mainBoxSizer.Add(wx.StaticLine(self, size=wx.Size(150, 1)), 0, wx.EXPAND, 5)
        self.mainBoxSizer.AddSpacer(1)
        self.mainBoxSizer.Add(self.buttonBoxSizer, 0, wx.EXPAND|wx.ALL, 0)


        self.optionsButton = wx.Button(self, label="Options")
        self.askButton = wx.Button(self, label="Ask")
        self.buttonBoxSizer.Add(self.optionsButton, 1, wx.ALL, 2)
        self.buttonBoxSizer.Add(self.askButton, 1, wx.ALL, 2)


        # Bind events
        self.askButton.Bind(wx.EVT_BUTTON, self.processPrompt)
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
        self.responseLabel.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)

        # Make window fancy and transparent
        ## if wx.Platform == "__WXGTK__":
        ##     self.Bind(wx.EVT_WINDOW_CREATE, self.SetWindowShape)
        ## else:
        ##     self.SetWindowShape()

        self.SetSizerAndFit(self.mainBoxSizer)

    def OnRightDown(self, event):
        clipboard.copy(self.responseLabel.GetLabelText())

    def SetWindowShape(self):
        self.SetClientSize((self.bitmap.GetWidth(), self.bitmap.GetHeight()))

        self.region = wx.Region(self.bitmap)
        self.hasShape = self.SetShape(self.region)

    def processPrompt(self, event):
        response = self.AIModel.prompt(self.TextCTRL.GetValue())
        size = self.GetSize()
        self.responseLabel.SetLabelText(response)
        self.responseLabel.Wrap(self.GetSize()[0] - 25)
        self.Fit()
        self.SetSize(size[0], self.GetSize()[1])
        #self.responseLabel.Wrap(self.GetSize()[0])
        self.Layout()
        self.GetParent().MoveMsgFrame()

class ClippyFrame(wx.Frame):
    def __init__(self, *args, animations, states, info, **kwargs):
        # Create frame
        super(ClippyFrame, self).__init__(*args, style=wx.FRAME_SHAPED|wx.STAY_ON_TOP|wx.FRAME_NO_TASKBAR|wx.NO_FULL_REPAINT_ON_RESIZE|wx.MINIMIZE_BOX|wx.SYSTEM_MENU|wx.CLIP_CHILDREN|wx.CLOSE_BOX,**kwargs)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)


        # Clippy stuff
        self.currentState = "Showing"
        self.currentAnimation = "Show"
        self.stateQueue = ["IdlingLevel2"]
        self.animationQueue = ["Writing"]
        self.loopCurrentAnimation = False
        self.currentAnimationFrame = 0
        self.idleLevel = 0
        self.endCurrentAnimation = True # Used to trigger usage of "Exit Branch"
        self.bitmap = wx.Bitmap('./Agent/Images/0871.png')

        self.animations = animations
        self.states = states
        self.info = info

        # Clippy Frame
        self.msgFrame = ClippyTextBox(self)
        self.msgFrame.Show(True)



        # Center the frame on screen (set delta for dragging)
        self.CenterOnScreen(wx.BOTH)
        
        self.MoveMsgFrame()
        self.delta = wx.Point(0,0)

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
            if (len(self.animationQueue) > 0):
                self.currentAnimation = self.animationQueue.pop(0)
            elif (len(self.stateQueue) > 0):
                self.currentState = self.stateQueue.pop(0)
                self.currentAnimation = random.choice(self.states[self.currentState])
            else:
                self.currentAnimation = None
                self.currentState = None
                return

        animationFrame = self.animations[self.currentAnimation][self.currentAnimationFrame]

        if (self.endCurrentAnimation and animationFrame["Branches"]['-1'] != None):
            self.currentAnimationFrame = animationFrame["Branches"]['-1']

        # Get image name
        bitmapName = animationFrame["Image"]
        soundName = animationFrame["Sound"]
        if (not bitmapName):
            self.currentAnimationFrame += 1
            self.animationTimer.StartOnce(0)
            return

        self.bitmap = wx.Bitmap('./Agent/Images/' + bitmapName.replace('.bmp', '.png'))
        #mask = wx.Mask(self.bitmap, wx.Colour(255,0,255,wx.ALPHA_OPAQUE))
        mask = wx.Mask(self.bitmap, wx.Colour(0,0,0,wx.ALPHA_TRANSPARENT))
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

        # Handle branching in a totally not hacky way
        if (len(list(animationFrame["Branches"])) > 1):
            branchableFrames = []
            for branch in list(animationFrame["Branches"]):
                branch = int(branch)
                if (branch != -1):
                    for i in range(int(animationFrame["Branches"][str(branch)])):
                        branchableFrames.append(branch)

            while len(branchableFrames) < 100:
                branchableFrames.append(self.currentAnimationFrame + 1)
            
            self.currentAnimationFrame = random.choice(branchableFrames)
        else:
            self.currentAnimationFrame += 1

        self.animationTimer.StartOnce(self.animations[self.currentAnimation][self.currentAnimationFrame-1]["Duration"])



    # Handle drawing of Clippy
    def OnPaint(self, event):      
        dc = wx.AutoBufferedPaintDCFactory(self)
        dc.DrawBitmap(self.bitmap, -1, -1, True)
        self.SetWindowShape()



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
            # TODO: I don't even remember what I meant by "bubble GUI"
            ###
            self.msgFrame.Show(not self.msgFrame.IsShown())

    def OnMouseMove(self, event):
        if event.Dragging() and event.LeftIsDown():
            x, y = self.ClientToScreen(event.GetPosition())
            fp = (x - self.delta[0], y - self.delta[1])
            self.SetPosition(fp)
            self.MoveMsgFrame()
    
    def MoveMsgFrame(self):
        msgPosition = self.GetPosition()
        msgBoxOffset = self.msgFrame.GetSize()
        msgPosition -= msgBoxOffset
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