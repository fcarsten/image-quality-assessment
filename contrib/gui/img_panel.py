import os

import wx

BITMAP_WDITH = 200
BITMAP_HEIGHT = 200
BORDER_SIZE = 10

PANEL_WIDTH = BITMAP_WDITH + BORDER_SIZE
PANEL_HEIGHT = BITMAP_HEIGHT + BORDER_SIZE + 160  # 60 being a guess for the height of the 3 text fields


class ImagePanel(wx.Panel):
    def __init__(self, parent, filename, image, predictions):
        super(ImagePanel, self).__init__(parent)
        self.image = image
        self.filename = filename
        self.prediction = predictions[0]
        self.tech_score = self.prediction['t_mean_score_prediction']
        self.aesth_score = self.prediction['a_mean_score_prediction']
        self.InitUI(image)

    def InitUI(self, image):
        self.SetBackgroundColour('white')
        self.SetMinSize(wx.Size(PANEL_WIDTH, PANEL_HEIGHT))
        self.SetMaxSize(wx.Size(PANEL_WIDTH, PANEL_HEIGHT))
        img_panel_sizer = wx.BoxSizer(wx.VERTICAL)

        img_panel = wx.Panel(self)
        img_panel.SetBackgroundColour('white')
        img_panel.SetMinSize(wx.Size(PANEL_WIDTH, -1))

        bitmap = wx.StaticBitmap(img_panel, wx.ID_ANY, wx.BitmapFromImage(image))
        bitmap.SetMinSize(wx.Size(BITMAP_WDITH, BITMAP_HEIGHT))
        bitmap.SetMaxSize(wx.Size(BITMAP_WDITH, BITMAP_HEIGHT))
        img_panel.SetMinSize(wx.Size(BITMAP_WDITH, BITMAP_HEIGHT))
        img_panel.SetMaxSize(wx.Size(BITMAP_WDITH, BITMAP_HEIGHT))

        img_panel_sizer.Add(img_panel, 0, flag=wx.LEFT | wx.RIGHT | wx.TOP, border=BORDER_SIZE)

        text_panel = wx.Panel(self)
        text_panel.SetBackgroundColour('white')
        text_panel_sizer = wx.BoxSizer(wx.VERTICAL)

        font = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)
        font.SetPointSize(12)

        hbox_f = wx.BoxSizer(wx.HORIZONTAL)
        st1 = wx.StaticText(text_panel, label=" {0} ".format(os.path.basename(self.filename)))
        st1.SetFont(font)
        hbox_f.Add(st1, 0)

        st1 = wx.StaticText(text_panel, label="             ")
        st1.SetFont(font)
        hbox_f.Add(st1, 1)

        text_panel_sizer.Add(hbox_f, 0)

        hbox_t = wx.BoxSizer(wx.HORIZONTAL)
        st1 = wx.StaticText(text_panel, label=' T Score: ')
        st1.SetFont(font)
        hbox_t.Add(st1, 0)
        self.technical_score_field = wx.StaticText(text_panel,
                                                   label="{0:9.4f}".format(self.prediction['t_mean_score_prediction']))
        self.technical_score_field.SetFont(font)
        hbox_t.Add(self.technical_score_field, 0, flag=wx.RIGHT, border=8)

        text_panel_sizer.Add(hbox_t, 0)

        hbox_a = wx.BoxSizer(wx.HORIZONTAL)
        st1 = wx.StaticText(text_panel, label=' A Score: ')
        st1.SetFont(font)
        hbox_a.Add(st1, 0)
        self.aesthetical_score_field = wx.StaticText(text_panel, label="{0:9.4f}".format(
            self.prediction['a_mean_score_prediction']))
        self.aesthetical_score_field.SetFont(font)
        hbox_a.Add(self.aesthetical_score_field, 0, flag=wx.RIGHT, border=8)

        text_panel_sizer.Add(hbox_a, 0)

        img_panel_sizer.Add(text_panel, 0, flag=wx.LEFT | wx.RIGHT | wx.BOTTOM, border=BORDER_SIZE)

        text_panel.SetSizer(text_panel_sizer)
        # text_panel.SetSizerAndFit(text_panel_sizer)
        self.SetSizerAndFit(img_panel_sizer)
        self.Bind(wx.EVT_PAINT, self.on_paint)

    def on_paint(self, event):
        dc = wx.PaintDC(self)
        x = 0
        y = 0
        w, h = self.GetSize()
        dc.GradientFillLinear((x, y, w, h), self.get_tech_colour(), self.get_aesth_colour())

    def get_tech_colour(self):
        r = ((10 - self.tech_score) / 10.0) * 256.0
        g = (self.tech_score / 10.0) * 256.0
        b = 50
        return wx.Colour(r,g,b)

    def get_aesth_colour(self):
        r = ((10 - self.aesth_score) / 10.0) * 256.0
        g = (self.aesth_score / 10.0) * 256.0
        b = 50
        return wx.Colour(r,g,b)