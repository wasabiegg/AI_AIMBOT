from lib import hms
import os
import sys
from lib.validate import eprint


def main():
    if os.name != "nt":
        eprint("only windows supported, quiting!")
        sys.exit(1)

    # Clear terminal
    os.system("cls")

    print(
        """
    ====================================
     HelpMeShoot: Neural-Network Aimbot (v1.0.0)
    ====================================

    [INFO] press '0' to quit or ctrl+C in console..."""
    )

    hms.start()


if __name__ == "__main__":
    main()
