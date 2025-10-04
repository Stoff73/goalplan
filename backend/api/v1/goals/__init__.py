"""
Goals API module.

This module provides RESTful API endpoints for financial goal planning:
- Goal creation and management
- Progress tracking
- Milestone management
- Goal optimization and allocation
"""

from .goals import router

__all__ = ["router"]
