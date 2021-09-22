from termcolor import colored
import cv2
import signal
import sys
from lib.grab import MssCapture
from lib.nn import Yolov5
import torch
from pathlib import Path
from lib.config import load_config, Config
from lib.validate import custom_assert, eprint
import timeit
import time
from lib.control import find_target, set_pos
from win32api import GetKeyState
from win32con import VK_CAPITAL


# 0: auto aim on, 1: auto aim off
# 0: capslock off, 1: capslock on
# You can turn off auto aim by turning capslock on
def get_switch():
    return GetKeyState(VK_CAPITAL)


def start():
    # Base dir
    base_dir = Path(__file__).parent.parent

    # Get cpu or gpu device for predict
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print("[USING] {} device".format(device))

    # Load config
    config_path = base_dir.joinpath("config.yaml")
    custom_assert(config_path.is_file())

    config: Config = load_config(config_path)

    # YOLOv5 weight path
    weight_path = base_dir.joinpath("model").joinpath("weight.pt")
    custom_assert(weight_path.is_file(), f"[WEIGHT] {weight_path} not found")

    # Wait for buffering
    time.sleep(0.4)

    # Load our YOLOv5 object detector with trained weight (5 classes)
    print("[INFO] loading YOLOv5 neural-network from disk...")
    model = Yolov5(weight_path, config.http_proxy)

    # Define screen capture area
    print("[INFO] loading screencapture device...")

    # Log whether aimbot is enabled
    if not config.enable_aimbot:
        print(colored("[INFO] aimbot disabled, using visualizer only...", "yellow"))
    else:
        print(colored("[OKAY] Aimbot enabled!", "green"))

    # Handle Ctrl+C in terminal, release pointers
    def signal_handler(sig, frame):
        # release the file pointers

        print("\n[INFO] cleaning up...")
        cv2.destroyAllWindows()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    # Test for GPU support
    build_info = str("".join(cv2.getBuildInformation().split()))
    if cv2.ocl.haveOpenCL():
        cv2.ocl.setUseOpenCL(True)
        cv2.ocl.useOpenCL()
        print(colored("[OKAY] OpenCL is working!", "green"))
    else:
        print(colored("[WARNING] OpenCL acceleration is disabled!", "yellow"))
    if "CUDA:YES" in build_info:
        print(colored("[OKAY] OpenCV with CUDA support is working!", "green"))
    else:
        print(
            colored(
                """[WARNING] OpenCV with CUDA acceleration is disabled!,
                 you can try to compile OpenCV with CUDA support,
                 but not much improvement to speed""",
                "yellow",
            )
        )

    # create WindowCapture obj
    # window_name = "Counter-Strike: Global Offensive"
    # wincap = WindowCapture(window_name=window_name, region=origbox)

    Wd = config.monitor_size[0]
    Hd = config.monitor_size[1]

    # Loop over frames from the video file stream
    with MssCapture(config.monitor_size, config.box_size) as wincap:
        origbox = wincap.get_box_position()

        while True:
            # right_click = win32api.GetKeyState(0x02)

            # right buttom up
            # if right_click >= 0:
            #     one_punch_done = 0

            # right buttom down
            # if one_punch_done < config.auto_aim_times:

            if config.debug:
                start_time = timeit.default_timer()

            # Get frame
            frame = wincap.shot()

            # Use model to predict result
            result = model.cal(frame)

            # If enable aimbot mode
            # Find target and set mouse pos
            if config.enable_aimbot and get_switch() == 0:
                target = find_target(result.pred, origbox, config.confidence)
                if target is not None:
                    set_pos(*target, Wd, Hd)

            if config.debug:
                # Debug render
                frame = result.render()[0]
                cv2.imshow("Neural Net Vision (Help Me shoot)", frame)
                elapsed = timeit.default_timer() - start_time
                sys.stdout.write(
                    "\r{1} FPS with {0} MS interpolation delay \t".format(
                        int(elapsed * 1000), int(1 / elapsed)
                    )
                )
                sys.stdout.flush()
                if cv2.waitKey(1) & 0xFF == ord("0"):
                    break

    # Clean up resource on exit
    signal_handler(0, 0)


if __name__ == "__main__":
    eprint("Dont't run this script directly")
