"""
NIDS Iron Dome Package
----------------------
A machine-learning based network intrusion detection system 
using Random Forest classifiers.

Copyright (c) 2025 [Your Name]
License: GPLv2
"""

# Expose the core components to the package level
from .engine import NIDSEngine
from .main import NIDS_GUI

# Version control. Don't touch this unless you push a major update.
__version__ = "1.0.0-stable"
__author__ = "root"