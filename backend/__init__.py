"""
Quranic Roots Analysis - Backend API Package
Phase 2: Backend API & Analytics Engine

This package provides a comprehensive FastAPI-based backend for analyzing
Quranic root words, morphology, and semantic patterns.
"""

__version__ = "2.0.0"
__author__ = "Quranic Roots Analysis Team"
__description__ = "Advanced API for Quranic linguistic analysis"

# Core components
from analytics import QuranicAnalytics
from config import current_settings, get_settings
from models import *
from utils import *

# API application
from startup import create_application

__all__ = [
    "QuranicAnalytics",
    "current_settings", 
    "get_settings",
    "create_application",
    "buck_to_arabic",
    "arabic_to_buck"
] 