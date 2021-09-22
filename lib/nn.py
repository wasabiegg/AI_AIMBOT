import torch
from pathlib import Path
import os


class Yolov5:
    def __init__(self, model_path: Path, proxy=None):
        assert model_path.is_file()

        if proxy is not None:
            os.environ["http_proxy"] = proxy
            os.environ["https_proxy"] = proxy

        try:
            self._model = torch.hub.load(
                "ultralytics/yolov5", "custom", path=str(model_path)
            )
        except Exception as e:
            print(f"warning: {e}")
            self._model = torch.hub.load(
                "ultralytics/yolov5", "custom", path=str(model_path)
            )

        self.__post_init__()

    def __post_init__(self):
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print("Using {} device".format(device))

    def cal(self, img_array):

        return self._model(img_array)
