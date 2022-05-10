import sys
import os
import math

PACKAGE_PARENT = "../.."
SCRIPT_DIR = os.path.dirname(
    os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__)))
)
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from pathlib import Path


class Machine:
    """Class that represents a machine"""

    # def __init__(self, name: str, cph: int, nozHeads: int, machineType: str, offsets: dict = None) -> None:
    def __init__(
        self, machine: str, cph: int, nozHeads: int, SMD: bool, offsets: dict = None
    ) -> None:
        self.machineName = machine
        self.cph = cph
        self.nozHeads = nozHeads
        self.SMD = SMD
        cps = 3600 / cph
        self.velocity = math.sqrt(180**2 + 180**2) / cps
        self.offsets = offsets

    def getData(self) -> dict:
        return {
            "machine": self.machineName,
            "cph": self.cph,
            "nozHeads": self.nozHeads,
            "SMD": self.SMD,
            "offsets": self.offsets,
        }
