import wx

#pip install wxPython

class FileDropSource(wx.ListCtrl):
    def __init__(self, parent, files):
        super().__init__(parent, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.InsertColumn(0, "Files")
        for f in files:
            self.InsertItem(self.GetItemCount(), f)
        self.Bind(wx.EVT_LIST_BEGIN_DRAG, self.on_begin_drag)
        # Dark theme for the list
        dark_bg = wx.Colour(30, 30, 30)
        dark_fg = wx.Colour(220, 220, 220)
        self.SetBackgroundColour(dark_bg)
        self.SetForegroundColour(dark_fg)
        self.SetTextColour(dark_fg)

    def on_begin_drag(self, event):
        idx = event.GetIndex()
        file_path = self.GetItemText(idx)
    # Create a data object for dragging
        data = wx.FileDataObject()
        data.AddFile(file_path)
        drop_source = wx.DropSource(self)
        drop_source.SetData(data)
        drop_source.DoDragDrop(flags=wx.Drag_CopyOnly)

class MyFrame(wx.Frame):
    def __init__(self, files):
        super().__init__(None, title="Drag files to another app", size=(400, 300))
        # Dark theme for the frame
        dark_bg = wx.Colour(30, 30, 30)
        dark_fg = wx.Colour(220, 220, 220)
        self.SetBackgroundColour(dark_bg)
        self.SetForegroundColour(dark_fg)
        panel = wx.Panel(self)
        panel.SetBackgroundColour(dark_bg)
        panel.SetForegroundColour(dark_fg)
        self.SetWindowStyle(self.GetWindowStyle() & ~wx.RESIZE_BORDER)
        self.SetSizeHints(self.GetSize(), self.GetSize())
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.file_list = FileDropSource(panel, files)
        sizer.Add(self.file_list, 1, wx.EXPAND | wx.ALL, 10)
        panel.SetSizer(sizer)

def drag_n_drop(files: list[str]):
    # Change the path to a folder with your files
    app = wx.App(False)
    frame = MyFrame(files)
    frame.Show()
    app.MainLoop()
    app.MainLoop()
