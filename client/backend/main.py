"""
This module controls a Varian 634 spectrometer setup, including initialization
of an Arduino board and a NI-PCI 6221 card. It manages data acquisition and
processing for spectrometry analysis.
"""

import time
import serial
import numpy as np
from pyfirmata import Arduino, util

