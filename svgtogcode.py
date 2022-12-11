# -*- coding: utf-8 -*-
"""
Created on Fri Sep  2 19:37:57 2022

@author: alecf
"""

from principal import *
from svg_to_gcode.svg_parser import parse_file
from svg_to_gcode.compiler import Compiler, interfaces
from svg_to_gcode.formulas import linear_map

class CustomInterface(interfaces.Gcode):
    def __init__(self):
        super().__init__()
        self.fan_speed = 1

    # Override the laser_off method such that it also powers off the fan.
    def laser_off(self):
        return "M107;\n"+"M107;\n"  # Turn off the fan + turn off the laser

    # Override the set_laser_power method
    def set_laser_power(self, power):
        if power < 0 or power > 1:
            raise ValueError(f"{power} is out of bounds. Laser power must be given between 0 and 1. "
                             f"The interface will scale it correctly.")

        return f"M106 S255"  # Turn on the fan + change laser power


