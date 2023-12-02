# =============================================================================
# Import Python modules
# =============================================================================

# Import python modules - Not all of these are used in this program; provided
# for reference
import sys
import pyvisa as visa  # PyVisa info @ http://PyVisa.readthedocs.io/en/stable/
import time
import numpy as np
import re
from quantiphy import Quantity  # pip install quantiphy
import os

# =============================================================================
# Initialize values (some to be overwritten by User Inputs below)
# =============================================================================

VERBOSE_MODE = True
START_FROM_RESET = True
IMPORT_SAVED_FILES = False
trends = False
FREQUENCY1 = 0
FREQUENCY2 = 0
DUTY_CYCLE = '50%'
trig_on_freq_change = False

# =============================================================================
# User Inputs (used with every run)
# =============================================================================

# Set VERBOSE_MODE = False for a more concise console output.  Comment this
# line to display additional info (useful for debug):
#VERBOSE_MODE = False

# Instrument VISA address:
SCOPE_VISA_ADDRESS = 'USB0::0x2A8D::0x039B::CN60531137::0::INSTR'  # EDUX1052G

# I/O timeout in milliseconds:
GENERAL_TIMEOUT = 6000

# Number of waveforms to acquire and transfer:
NUMBER_WAVEFORMS = 5

# Set waveform data format to ASCii (for demo) or WORD (recommended):
WAVEFORM_FORMAT = 'WORD'
#WAVEFORM_FORMAT = 'ASCii'

# Enter a delay in seconds to wait between queries when polling for run status.
# Shorter values provide more accurate time tags but use more CPU resources.
POLLING_INTERVAL = 0.5  # (s)

# Set format for output file to save waveform data:
OUTPUT_FILE = 'CSV'  # CSV, BINARY, BOTH, or NONE

# Load data from output file(s) back into Python:
#IMPORT_SAVED_FILES = True

# If one or more CSV files are saved, open the last one:
OPEN_CSV_FILE = True

# Define save location:
DIRECTORY = 'C:\\Users\\Public\\'

# Comment this to reset the scope and perform the setup under initialize():
#START_FROM_RESET = False

# =============================================================================
# User Inputs (used only when START_FROM_RESET = True)
# =============================================================================

# Set the vertical scale:
VERTICAL_SCALE = 1  # (V/div)
# Set the horizontal scale.  Note this directly impacts measurement resolution
# and accuracy.  Generally, smaller timescales produce fewer measurements that
# are more accurate, whereas larger timescales produce more measurements that
# are less accurate.  No logic has been implemented to report the resolution or
# accuracy to the user.
TIMESCALE = 0.005  # (s/div)