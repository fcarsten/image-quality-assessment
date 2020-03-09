from threading import Thread

import wx
import os
import glob

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


def resizeImageToFit(image: wx.Image, max_width, max_height):
    r_w = max_width * 1.0 / image.GetWidth()
    r_h = max_height * 1.0 / image.GetHeight()

    r = min(r_w, r_h)
    new_width = image.GetWidth() * r
    new_height = image.GetHeight() * r

    image.Rescale(new_width, new_height)


def explode_dirs(filenames: [str]):
    res = []
    for filename in filenames:
        if os.path.isfile(filename):
            res.append(filename)
        elif os.path.isdir(filename):
            file_extensions = ["jpg", "jpeg", "png", "bmp", "gif"]
            for ext in file_extensions:
                img_paths = glob.glob(os.path.join(filename, '*.' + ext))
                res.extend(img_paths)

    return res


class WorkerThread(Thread):

    def __init__(self, notify_window, filenames):
        """Init Worker Thread Class."""
        Thread.__init__(self)
        self._notify_window = notify_window
        self._want_abort = 0
        self.filenames = explode_dirs(filenames)

    def run(self):
        for filename in self.filenames:
            image = wx.Image(filename, wx.BITMAP_TYPE_ANY)
            resizeImageToFit(image, 200, 200)
            prediction = self._notify_window.predict(filename)
            wx.PostEvent(self._notify_window, ResultEvent((filename, image, prediction)))

        wx.PostEvent(self._notify_window, ResultEvent(None))

    def abort(self):
        """abort worker thread."""
        # Method for use by main thread to signal an abort
        self._want_abort = 1
