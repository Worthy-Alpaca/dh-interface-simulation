PACKAGE_PARENT = "../.."
SCRIPT_DIR = os.path.dirname(
    os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__)))
)
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

import sys
import os
import math


class Machine:
    def __init__(
        self, machine: str, cph: int, nozHeads: int, SMD: bool, offsets: dict = None
    ) -> None:
        """A Machine Instance

        Args:
            machine (str): The current machine name.
            cph (int): The current machine CPH.
            nozHeads (int): The current amount of nozzle heads.
            SMD (bool): If the machine is a SMD Machine
            offsets (dict, optional): The internal offsets. Defaults to None.
        """
        self.machineName = machine
        self.cph = cph
        self.nozHeads = nozHeads
        self.SMD = SMD
        cps = 3600 / cph
        self.velocity = math.sqrt(180**2 + 180**2) / cps
        self.offsets = offsets

    def getData(self) -> dict:
        """Get all machine properties as a dict.

        Returns:
            dict: The machine properties.
        """
        return {
            "machine": self.machineName,
            "cph": self.cph,
            "nozHeads": self.nozHeads,
            "SMD": self.SMD,
            "offsets": self.offsets,
        }
