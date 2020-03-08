import os

from gui.nima_frame import NIMAFrame

import wx.lib.inspection

os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

if __name__ == '__main__':
    app = wx.App()

    frame = NIMAFrame(None, title='NIMA Gui')
    frame.Show()
    wx.lib.inspection.InspectionTool().Show()

    app.MainLoop()
