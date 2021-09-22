import cv2
import numpy as np
import win32gui
import win32ui
import win32con
import win32api
import mss


def grab_screen(region=None):

    hwin = win32gui.GetDesktopWindow()

    if region:
        left, top, x2, y2 = region
        width = x2 - left + 1
        height = y2 - top + 1
    else:
        width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
        height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
        left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
        top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)

    hwindc = win32gui.GetWindowDC(hwin)
    srcdc = win32ui.CreateDCFromHandle(hwindc)
    memdc = srcdc.CreateCompatibleDC()
    bmp = win32ui.CreateBitmap()
    bmp.CreateCompatibleBitmap(srcdc, width, height)
    memdc.SelectObject(bmp)
    memdc.BitBlt((0, 0), (width, height), srcdc, (left, top), win32con.SRCCOPY)

    signedIntsArray = bmp.GetBitmapBits(True)
    img = np.fromstring(signedIntsArray, dtype="uint8")
    img.shape = (height, width, 4)

    srcdc.DeleteDC()
    memdc.DeleteDC()
    win32gui.ReleaseDC(hwin, hwindc)
    win32gui.DeleteObject(bmp.GetHandle())

    return cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)


def winEnumHandler(hwnd, ctx):
    if win32gui.IsWindowVisible(hwnd):
        print(hex(hwnd), win32gui.GetWindowText(hwnd))


def get_window_names():
    win32gui.EnumWindows(winEnumHandler, None)


def grab_screen_v2(region=None):
    # w = 1920 # set this
    # h = 1080 # set this
    windowname = None

    hwnd = win32gui.FindWindow(None, windowname)
    # hwin = win32gui.GetDesktopWindow()
    # hwd = None

    if region:
        left, top, x2, y2 = region
        w = x2 - left + 1
        h = y2 - top + 1
    else:
        width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
        height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
        left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
        top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)

    wDC = win32gui.GetWindowDC(hwnd)
    dcObj = win32ui.CreateDCFromHandle(wDC)
    cDC = dcObj.CreateCompatibleDC()
    dataBitMap = win32ui.CreateBitmap()
    dataBitMap.CreateCompatibleBitmap(dcObj, w, h)
    cDC.SelectObject(dataBitMap)
    cDC.BitBlt((0, 0), (w, h), dcObj, (left, top), win32con.SRCCOPY)

    signedIntsArray = dataBitMap.GetBitmapBits(True)
    img = np.fromstring(signedIntsArray, dtype="uint8")
    img.shape = (h, w, 4)

    # save screenshot
    # dataBitMap.SaveBitmapFile(cDC, bmpfilenamename)

    # Free Resources
    dcObj.DeleteDC()
    cDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, wDC)
    win32gui.DeleteObject(dataBitMap.GetHandle())

    # get rid of alpha channel, don't need it
    # return img[..., :3]

    return img


class WindowCapture:
    __slots__ = ("_window_name", "_region", "_hwnd")

    def __init__(self, window_name, region):
        self._window_name = window_name
        self._region = region
        self._hwnd = win32gui.FindWindow(None, window_name)

        self.__post_init__()

    def __post_init__(self):
        print(self._window_name)
        print(self._hwnd)
        if self._hwnd is None:
            raise Exception(f"Window not found: {self._window_name}")

        left, top, x2, y2 = self._region

    def shot(self):
        hwnd = self._hwnd
        # hwin = win32gui.GetDesktopWindow()
        # hwd = None

        if self._region:
            left, top, x2, y2 = self._region
            w = x2 - left + 1
            h = y2 - top + 1
        else:
            w = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
            h = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
            left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
            top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)

        wDC = win32gui.GetWindowDC(hwnd)
        dcObj = win32ui.CreateDCFromHandle(wDC)
        cDC = dcObj.CreateCompatibleDC()
        dataBitMap = win32ui.CreateBitmap()
        dataBitMap.CreateCompatibleBitmap(dcObj, w, h)
        cDC.SelectObject(dataBitMap)
        cDC.BitBlt((0, 0), (w, h), dcObj, (left, top), win32con.SRCCOPY)

        signedIntsArray = dataBitMap.GetBitmapBits(True)
        img = np.fromstring(signedIntsArray, dtype="uint8")
        img.shape = (h, w, 4)

        # save screenshot
        # dataBitMap.SaveBitmapFile(cDC, bmpfilenamename)

        # Free Resources
        dcObj.DeleteDC()
        cDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, wDC)
        win32gui.DeleteObject(dataBitMap.GetHandle())

        # cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
        return img

    def close(self):
        # Free Resouces
        pass


# mss capture is faster than win_api
class MssCapture:
    __slots__ = (
        "_sct",
        "_monitor",
        "_monitor_size",
        "_startx",
        "_starty",
        "_endx",
        "_endy",
    )

    # monitor_size is (width, height)
    # region is (width, height)
    def __init__(self, monitor_size, box_size) -> None:
        self._sct = mss.mss()
        self._monitor_size = monitor_size
        self._monitor = self._find_monitor()

        self._startx, self._endx, self._starty, self._endy = self._cal_startx_y(
            *box_size
        )

    def _cal_startx_y(self, cropx, cropy):
        y, x = self._monitor["height"], self._monitor["width"]
        startx = x // 2 - (cropx // 2)
        starty = y // 2 - (cropy // 2)
        return (startx, startx + cropx, starty, starty + cropy)

    def get_box_position(self):
        return (self._startx, self._starty, self._endx, self._endy)

    def _find_monitor(self):
        for monitor in self._sct.monitors:
            if (monitor["width"], monitor["height"]) == self._monitor_size:
                return monitor

    def __enter__(self):
        return self

    def shot(self):
        # return np.asarray(self._sct.grab(self._monitor)).shape(self._h, self._w, 4)
        img = np.asarray(self._sct.grab(self._monitor))
        # print(img.shape)
        # img.shape = (self._h, self._w, 4)
        return img[self._starty : self._endy, self._startx : self._endx, :]

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._sct.close()
