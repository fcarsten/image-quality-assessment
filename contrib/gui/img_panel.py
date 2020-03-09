import os

import wx

BITMAP_WDITH = 200
BITMAP_HEIGHT  = 200
BORDER_SIZE = 10

PANEL_WIDTH = BITMAP_WDITH + BORDER_SIZE
PANEL_HEIGHT = BITMAP_HEIGHT + BORDER_SIZE + 50 # 50 being a guess for the height of the 3 text fields

class ImagePanel(wx.Panel):
    def __init__(self, parent, filename, image, predictions):
        super(ImagePanel, self).__init__(parent)
        self.image = image
        self.filename = filename
        self.prediction = predictions[0]
        self.InitUI(image)

    def InitUI(self, image):
        self.SetBackgroundColour('white')
        self.SetMinSize(wx.Size(PANEL_WIDTH, 260))
        self.SetMaxSize(wx.Size(PANEL_WIDTH, 260))
        vbox = wx.BoxSizer(wx.VERTICAL)

        img_panel = wx.Panel(self)
        img_panel.SetBackgroundColour('white')

        bitmap = wx.StaticBitmap(img_panel, wx.ID_ANY, wx.BitmapFromImage(image))
        bitmap.SetMinSize(wx.Size(BITMAP_WDITH, BITMAP_HEIGHT))
        bitmap.SetMaxSize(wx.Size(BITMAP_WDITH, BITMAP_HEIGHT))
        img_panel.SetMinSize(wx.Size(BITMAP_WDITH, BITMAP_HEIGHT))
        img_panel.SetMaxSize(wx.Size(BITMAP_WDITH, BITMAP_HEIGHT))

        vbox.Add(img_panel, 0, flag=wx.LEFT | wx.RIGHT | wx.TOP, border=BORDER_SIZE)

        font = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)
        font.SetPointSize(12)

        st1 = wx.StaticText(self, label="{0}".format(os.path.basename(self.filename)))
        st1.SetFont(font)
        vbox.Add(st1, 0, flag=wx.LEFT | wx.RIGHT, border=BORDER_SIZE)

        hbox_t = wx.BoxSizer(wx.HORIZONTAL)
        st1 = wx.StaticText(self, label='T Score: ')
        st1.SetFont(font)
        hbox_t.Add(st1, 0, flag=wx.RIGHT, border=20)
        self.technical_score_field = wx.StaticText(self,
                                                   label="{0:9.4f}".format(self.prediction['t_mean_score_prediction']))
        self.technical_score_field.SetFont(font)
        hbox_t.Add(self.technical_score_field, 0, flag=wx.RIGHT, border=8)

        vbox.Add(hbox_t, 0, flag=wx.LEFT | wx.RIGHT, border=BORDER_SIZE)

        hbox_a = wx.BoxSizer(wx.HORIZONTAL)
        st1 = wx.StaticText(self, label='A Score: ')
        st1.SetFont(font)
        hbox_a.Add(st1, 0, flag=wx.RIGHT, border=20)
        self.aesthetical_score_field = wx.StaticText(self, label="{0:9.4f}".format(
            self.prediction['a_mean_score_prediction']))
        self.aesthetical_score_field.SetFont(font)
        hbox_a.Add(self.aesthetical_score_field, 0, flag=wx.RIGHT, border=8)

        vbox.Add(hbox_a, 0, flag=wx.LEFT | wx.RIGHT, border=BORDER_SIZE)

        self.SetSizerAndFit(vbox)
