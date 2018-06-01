import wx

app=wx.PySimpleApp()
frame=wx.Frame(None)
frame.SetBackgroundColour((49,51,53))
style = 0
style = style | wx.NO_BORDER
text=wx.TextCtrl(frame, value="Colored text", style=style)
text.SetForegroundColour((255,0,0)) # set text color
# text.SetBackgroundColour((0,0,255)) # set text back color
text.SetEditable(False)
frame.Show(True)
app.MainLoop()