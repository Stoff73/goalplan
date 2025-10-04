"""
Personalization services for user behavior tracking and insights.
"""

from .preference_service import PreferenceService, get_preference_service

__all__ = [
    "PreferenceService",
    "get_preference_service",
]
