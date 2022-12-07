from skidl import *
import skidl
from netlister.registry import RegistryMixin, Registry
from netlister.functions import abort
from loguru import logger
from netlister.chipset import Device


import re

class Chips(RegistryMixin, list):
    pass

class Chip(RegistryMixin):
    @staticmethod
    def create(device : Device):
        chip = Chip()
        chip.part = skidl.Part('74xx', device, footprint=footprint, tool_version="kicad_v6")
        chip.pins = pins


    def __init__(self, registry: Registry) -> None:
        super().__init__(registry)
