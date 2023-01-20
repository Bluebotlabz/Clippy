# First things, first. Import the wxPython package.
import wx

class ClippyFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(ClippyFrame, self).__init__(*args, style=wx.FRAME_SHAPED|wx.STAY_ON_TOP|wx.FRAME_NO_TASKBAR|wx.NO_FULL_REPAINT_ON_RESIZE|wx.MINIMIZE_BOX|wx.SYSTEM_MENU|wx.CLIP_CHILDREN|wx.CLOSE_BOX,**kwargs)

        self.CenterOnScreen(wx.BOTH)

        self.currentAnimationFrame = 0
        self.delta = wx.Point(0,0)

        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)

        self.bitmap = wx.Bitmap('./bmp/0000.bmp')

        if wx.Platform == "__WXGTK__":
            self.Bind(wx.EVT_WINDOW_CREATE, self.SetWindowShape)
        else:
            self.SetWindowShape()

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_MOTION, self.OnMouseMove)
        self.timer = wx.Timer(self)
        self.timer.Start(100)
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)

    def OnTimer(self, event):
        if (self.currentAnimationFrame < 901):
            self.currentAnimationFrame += 1
        else:
            self.currentAnimationFrame = 0

        self.Draw()

    def Draw(self):
        self.Refresh()

    def OnLeftDown(self, event):
        self.CaptureMouse()
        x, y = self.ClientToScreen(event.GetPosition())
        originx, originy = self.GetPosition()
        dx = x - originx
        dy = y - originy
        self.delta = ((dx, dy))

    def OnLeftUp(self, event):
        if (self.HasCapture()):
            self.ReleaseMouse()

    def OnMouseMove(self, event):
        if event.Dragging() and event.LeftIsDown():
            x, y = self.ClientToScreen(event.GetPosition())
            fp = (x - self.delta[0], y - self.delta[1])
            self.SetPosition(fp)
            #self.widgetsframe.SetPosition(fp)

    def SetWindowShape(self):
        self.SetClientSize((self.bitmap.GetWidth(), self.bitmap.GetHeight()))

        self.region = wx.Region(self.bitmap)
        self.hasShape = self.SetShape(self.region)

    def OnPaint(self, event):
        strNum = str(self.currentAnimationFrame)

        while len(strNum) < 4:
            strNum = '0' + strNum

        self.bitmap = wx.Bitmap('./bmp/' + strNum + '.bmp')
        mask = wx.Mask(self.bitmap, wx.Colour(255,0,255,wx.ALPHA_OPAQUE))
        self.bitmap.SetMask(mask)
        
        self.SetWindowShape()
        dc = wx.AutoBufferedPaintDCFactory(self)
        dc.DrawBitmap(self.bitmap, -1, -1, True)
    

class ClippyApp(wx.App):
    def OnInit(self):
        frame = ClippyFrame(None)
        self.SetTopWindow(frame)
        frame.Show(True)

        return True

app = ClippyApp()
# Start the event loop.
app.MainLoop()