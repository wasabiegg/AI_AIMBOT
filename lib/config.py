import yaml
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple


@dataclass
class Config:
    # windows settings
    monitor_size: Tuple[int, int]  # (width, height)

    # game settings
    confidence: bool
    box_size: Tuple[str, str]  # (width, height)
    enable_aimbot: bool
    # auto_aim_times: int

    # nn settings
    labels: Tuple[str]

    # application settings
    debug: bool

    # proxy settings
    http_proxy: str


def load_config(config_path: Path) -> Config:
    with open(config_path, "r") as stream:
        c: Dict = yaml.safe_load(stream)

        return Config(
            monitor_size=(
                c["windows"]["monitor_width"],
                c["windows"]["monitor_height"],
            ),
            confidence=c["game"]["confidence"],
            box_size=(c["game"]["box_width"], c["game"]["box_height"]),
            enable_aimbot=c["game"]["enable_aimbot"],
            # auto_aim_times=c["game"]["auto_aim_times"],
            labels=c["nn"]["labels"],
            debug=c["application"]["debug"],
            http_proxy=c["proxy"]["http_proxy"],
        )


# test
def test_load_config():
    pass
