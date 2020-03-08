import json
import os

import wx

from evaluater.predict import image_file_to_json, image_dir_to_json, predict
from gui.img_load_worker import EVT_RESULT, WorkerThread
from gui.img_panel import ImagePanel
from handlers.data_generator import TestDataGenerator
from handlers.model_builder import Nima
from utils.utils import calc_mean_score


class NIMAFileDropTarget(wx.FileDropTarget):

    def __init__(self, nima_frame):
        super(NIMAFileDropTarget, self).__init__()
        self.nima_frame = nima_frame

    def OnDropFiles(self, x, y, filenames):
        print("{}", filenames)
        if len(filenames) > 0:
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
            imagePanel = ImagePanel(self.root_panel, filename, image, prediction)

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
        self.root_panel.SetScrollRate(10, 10)
        dt = NIMAFileDropTarget(self)
        self.root_panel.SetDropTarget(dt)

        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.root_panel.SetSizer(self.vbox)

    def OnQuit(self, e):
        self.Close()
