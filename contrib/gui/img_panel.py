import os

import wx


class ImagePanel(wx.Panel):
    def __init__(self, parent, filename, image, predictions):
        super(ImagePanel, self).__init__(parent)
        self.image = image
        self.filename = filename
        self.prediction = predictions[0]
        self.InitUI(image)

    def InitUI(self, image):
        self.SetBackgroundColour('white')
        self.SetMinSize(wx.Size(210, 260))
        self.SetMaxSize(wx.Size(210, 260))
        hbox = wx.BoxSizer(wx.VERTICAL)

        img_panel = wx.Panel(self)
        img_panel.SetBackgroundColour('white')

        bitmap = wx.StaticBitmap(img_panel, wx.ID_ANY, wx.BitmapFromImage(image))
        bitmap.SetMinSize(wx.Size(200, 200))
        bitmap.SetMaxSize(wx.Size(200, 200))
        img_panel.SetMinSize(wx.Size(200, 200))
        img_panel.SetMaxSize(wx.Size(200, 200))

        hbox.Add(img_panel, 0, flag=wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        font = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)
        font.SetPointSize(12)

        vbox = wx.BoxSizer(wx.VERTICAL)

        st1 = wx.StaticText(self, label="{0}".format(os.path.basename(self.filename)))
        st1.SetFont(font)
        vbox.Add(st1, 0, flag=wx.LEFT | wx.RIGHT, border=10)

        hbox_t = wx.BoxSizer(wx.HORIZONTAL)
        st1 = wx.StaticText(self, label='T Score: ')
        st1.SetFont(font)
        hbox_t.Add(st1, 0, flag=wx.RIGHT, border=20)
        self.technical_score_field = wx.StaticText(self,
                                                   label="{0:9.4f}".format(self.prediction['t_mean_score_prediction']))
        self.technical_score_field.SetFont(font)
        hbox_t.Add(self.technical_score_field, 0, flag=wx.RIGHT, border=8)

        vbox.Add(hbox_t, 0, flag=wx.LEFT | wx.RIGHT, border=10)

        hbox_a = wx.BoxSizer(wx.HORIZONTAL)
        st1 = wx.StaticText(self, label='A Score: ')
        st1.SetFont(font)
        hbox_a.Add(st1, 0, flag=wx.RIGHT, border=20)
        self.aesthetical_score_field = wx.StaticText(self, label="{0:9.4f}".format(
            self.prediction['a_mean_score_prediction']))
        self.aesthetical_score_field.SetFont(font)
        hbox_a.Add(self.aesthetical_score_field, 0, flag=wx.RIGHT, border=8)

        vbox.Add(hbox_a, 0, flag=wx.LEFT | wx.RIGHT, border=10)

        hbox.Add(vbox, 0)
        self.SetSizerAndFit(hbox)
