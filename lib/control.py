import pynput
import ctypes

SendInput = ctypes.windll.user32.SendInput


def set_pos(x, y, Wd, Hd):
    x = 1 + int(x * 65536.0 / Wd)
    y = 1 + int(y * 65536.0 / Hd)
    extra = ctypes.c_ulong(0)
    ii_ = pynput._util.win32.INPUT_union()
    ii_.mi = pynput._util.win32.MOUSEINPUT(
        x,
        y,
        0,
        (0x0001 | 0x8000),
        0,
        ctypes.cast(ctypes.pointer(extra), ctypes.c_void_p),
    )
    command = pynput._util.win32.INPUT(ctypes.c_ulong(0), ii_)
    SendInput(1, ctypes.pointer(command), ctypes.sizeof(command))


# STATE_LEFT = win32api.GetKeyState(
#     0x01
# )  # Left button down = 0 or 1. Button up = -127 or -128
# STATE_RIGHT = win32api.GetKeyState(
#     0x02
# )  # Right button down = 0 or 1. Button up = -127 or -128


def find_target(pred, origbox, confidence):
    target = None
    target_distance = None
    pred = pred[0]

    for i in range(pred.shape[0]):
        pred_class = int(pred[i][5])
        pred_confidence = float(pred[i][4])

        # if pred_class in (1, 2) and pred_confidence > 0.6:
        if pred_class == 1 and pred_confidence > confidence:
            left = pred[i][0]
            top = pred[i][1]
            right = pred[i][2]
            bottom = pred[i][3]

            # work with raw input off [working with CSGO, will not work with some games with raw input on]
            w = right - left
            h = bottom - top
            # mouseX = origbox[0] + (left + w / 1.5)
            # mouseY = origbox[1] + (top + h / 5)
            mouseX = origbox[0] + (left + w / 3)
            mouseY = origbox[1] + (top + h / 5)

            # find enemy as quick as possible
            # return (mouseX, mouseY)

            # find closest enemy, consuming time alot
            t_target = (mouseX, mouseY)
            t_distance = t_target[0] ** 2 + t_target[1] ** 2
            if (target_distance is None) or t_distance < target_distance:
                target_distance = t_distance
                target = t_target

            # work with raw input on
            # m_y = (bottom - top) / 2 + top
            # m_x = (right - left) / 2 + left

            # o_left, o_top, o_right, o_bottom = origbox
            # box_cross_point = ((o_right - o_left) / 2, (o_bottom - o_top) / 2)

            # offset_x = box_cross_point[0] - m_x
            # offset_y = box_cross_point[1] - m_y

            # t_target = (-offset_x / MOUSEX_OFFSET, -offset_y / MOUSEY_OFFSET)

            # t_distance = t_target[0] ** 2 + t_target[1] ** 2
            # if (target_distance is None) or t_distance < target_distance:
            #     target_distance = t_distance
            #     target = t_target

    return target
