# from evaluater.predict import main
import os

import json
from handlers.model_builder import Nima
from handlers.data_generator import TestDataGenerator
from evaluater.predict import image_dir_to_json, image_file_to_json, predict, calc_mean_score

from threading import Thread
import wx

import wx.lib.inspection

os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

# Define notification event for thread completion
EVT_RESULT_ID = wx.NewId()


def EVT_RESULT(win, func):
    """Define Result Event."""
    win.Connect(-1, -1, EVT_RESULT_ID, func)


class ResultEvent(wx.PyEvent):
    """Simple event to carry arbitrary result data."""

    def __init__(self, data):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_RESULT_ID)
        self.data = data


# Button definitions
ID_START = wx.NewId()
ID_STOP = wx.NewId()

# Define notification event for thread completion
EVT_RESULT_ID = wx.NewId()


def EVT_RESULT(win, func):
    """Define Result Event."""
    win.Connect(-1, -1, EVT_RESULT_ID, func)


class ResultEvent(wx.PyEvent):
    """Simple event to carry arbitrary result data."""

    def __init__(self, data):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_RESULT_ID)
        self.data = data


# Thread class that executes processing
class WorkerThread(Thread):
    """Worker Thread Class."""

    def __init__(self, notify_window, filenames):
        """Init Worker Thread Class."""
        Thread.__init__(self)
        self._notify_window = notify_window
        self._want_abort = 0
        self.filenames = filenames

        # This starts the thread running on creation, but you could
        # also make the GUI thread responsible for calling this
        self.start()

    def resizeImageToFit(self, image: wx.Image, max_width, max_height):
        r_w = max_width * 1.0 / image.GetWidth()
        r_h = max_height * 1.0 / image.GetHeight()

        r = min(r_w, r_h);
        new_width = image.GetWidth() * r
        new_height = image.GetHeight() * r
        image.Rescale(new_width, new_height)

    def run(self):
        for filename in self.filenames:
            image = wx.Image(filename, wx.BITMAP_TYPE_ANY)
            self.resizeImageToFit(image, 200, 200)
            prediction = self._notify_window.predict(filename)
            wx.PostEvent(self._notify_window, ResultEvent((filename, image, prediction)))

        wx.PostEvent(self._notify_window, ResultEvent(None))

    def abort(self):
        """abort worker thread."""
        # Method for use by main thread to signal an abort
        self._want_abort = 1


class ImagePanel(wx.Panel):
    def __init__(self, parent, filename, image, predictions):
        super(ImagePanel, self).__init__(parent)
        self.filename = filename
        self.prediction = predictions[0]
        self.InitUI(image)

    def InitUI(self, image):
        self.SetBackgroundColour('white')
        self.SetMinSize(wx.Size(210, 260))
        self.SetMaxSize(wx.Size(210, 260))
        hbox = wx.BoxSizer(wx.VERTICAL);

        img_panel = wx.Panel(self)
        img_panel.SetBackgroundColour('white')

        self.mincol = wx.StaticBitmap(img_panel, wx.ID_ANY,
                                      wx.BitmapFromImage(image))

        self.mincol.SetMinSize(wx.Size(200, 200))
        self.mincol.SetMaxSize(wx.Size(200, 200))

        img_panel.SetMinSize(wx.Size(200, 200))
        #   img_panel.SetMaxSize( wx.Size( 200,200 ) )

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


class MyTextDropTarget(wx.FileDropTarget):

    def __init__(self, nima_frame):
        wx.TextDropTarget.__init__(self)
        self.nima_frame = nima_frame

    def OnDropFiles(self, x, y, filenames):
        print("{}", filenames)
        if (len(filenames) > 0):
            if not self.nima_frame.worker:
                self.nima_frame.worker = WorkerThread(self.nima_frame, filenames)

        return True


class NIMAFrame(wx.Frame):
    base_model_name = "MobileNet"
    a_weight_file = "../models/MobileNet/weights_mobilenet_aesthetic_0.07.hdf5"
    t_weight_file = "../models/MobileNet/weights_mobilenet_technical_0.11.hdf5"

    def __init__(self, parent, title):
        super(NIMAFrame, self).__init__(parent, title=title,
                                        size=(800, 600))

        # And indicate we don't have a worker thread yet
        self.worker = None

        self.InitUI()
        self.Centre()
        self.InitAI()
        # Set up event handler for any worker thread results

        EVT_RESULT(self, self.OnResult)

    def OnResult(self, event):
        """Show Result status."""
        if event.data is None:
            # Thread aborted (using our convention of None return)
            self.worker = None
        else:
            # Process results here

            filename, image, prediction = event.data
            imagePanel = ImagePanel(self.root_panel, filename, image, prediction);

            self.vbox.Add(imagePanel, 0,
                          wx.ALL, 10)
            self.vbox.Layout()
            self.root_panel.FitInside()

        # In either event, the worker is done

    def predict(self, image_source):
        img_format = "jpg"

        if os.path.isfile(image_source):
            image_dir, samples = image_file_to_json(image_source)
        else:
            image_dir = image_source
            samples = image_dir_to_json(image_dir, img_type='jpg')

        data_generator = TestDataGenerator(samples, image_dir, 64, 10, self.a_nima.preprocessing_function(),
                                           img_format=img_format)
        a_predictions = predict(self.a_nima.nima_model, data_generator)
        for i, sample in enumerate(samples):
            sample['a_mean_score_prediction'] = calc_mean_score(a_predictions[i])

        data_generator = TestDataGenerator(samples, image_dir, 64, 10, self.t_nima.preprocessing_function(),
                                           img_format=img_format)
        t_predictions = predict(self.t_nima.nima_model, data_generator)
        for i, sample in enumerate(samples):
            sample['t_mean_score_prediction'] = calc_mean_score(t_predictions[i])

        print(json.dumps(samples, indent=2))
        return samples

    def InitAI(self):
        self.a_nima = Nima(self.base_model_name, weights=None)
        self.a_nima.build()
        self.a_nima.nima_model.load_weights(self.a_weight_file)

        self.t_nima = Nima(self.base_model_name, weights=None)
        self.t_nima.build()
        self.t_nima.nima_model.load_weights(self.t_weight_file)

    def InitUI(self):
        menubar = wx.MenuBar()
        fileMenu = wx.Menu()
        fileItem = fileMenu.Append(wx.ID_EXIT, 'Quit', 'Quit application')
        menubar.Append(fileMenu, '&File')
        self.SetMenuBar(menubar)

        self.Bind(wx.EVT_MENU, self.OnQuit, fileItem)

        self.SetSize((800, 600))
        self.SetTitle('NIMA Scorer')

        self.root_panel = wx.ScrolledCanvas(self)
        # self.root_panel = wx.ScrolledWindow(self)
        self.root_panel.SetBackgroundColour("grey")
        self.root_panel.SetAutoLayout(True)
        self.root_panel.SetScrollRate(10,10)
        dt = MyTextDropTarget(self)
        self.root_panel.SetDropTarget(dt)

        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.root_panel.SetSizer(self.vbox)

    def OnQuit(self, e):
        self.Close()


if __name__ == '__main__':
    app = wx.App()

    frame = NIMAFrame(None, title='Simple application')
    frame.Show()
    wx.lib.inspection.InspectionTool().Show()

    app.MainLoop()
#    main("MobileNet", "../models/MobileNet/weights_mobilenet_aesthetic_0.07.hdf5", "../readme_figures/images_aesthetic", None)
#    main("MobileNet", "../models/MobileNet/weights_mobilenet_aesthetic_0.07.hdf5", "../tobias.jpg", None)
