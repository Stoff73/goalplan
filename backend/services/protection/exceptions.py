"""
Custom exceptions for Protection Module services.

This module provides specific exception types for policy management
operations, enabling precise error handling and user-friendly error messages.
"""


class PolicyValidationError(Exception):
    """
    Exception raised when policy data validation fails.

    Used for:
    - Invalid beneficiary percentages
    - Invalid cover amounts
    - Invalid premium amounts
    - Invalid dates
    - Missing required trust details

    Args:
        message: Detailed error message explaining validation failure
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class PolicyNotFoundError(Exception):
    """
    Exception raised when a policy is not found.

    Used for:
    - Policy ID doesn't exist
    - Policy was soft deleted
    - Beneficiary not found

    Args:
        message: Detailed error message
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class PolicyPermissionError(Exception):
    """
    Exception raised when user lacks permission to access/modify policy.

    Used for:
    - User attempting to access another user's policy
    - User attempting to modify another user's policy
    - User attempting to delete another user's policy

    Args:
        message: Detailed error message
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class CoverageAnalysisNotFoundError(Exception):
    """
    Exception raised when a coverage analysis is not found.

    Used for:
    - Analysis ID doesn't exist
    - User has no current analysis

    Args:
        message: Detailed error message
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class CoverageAnalysisValidationError(Exception):
    """
    Exception raised when coverage analysis data validation fails.

    Used for:
    - Invalid input values (negative amounts)
    - Invalid income multiplier
    - Permission errors (user doesn't own analysis)

    Args:
        message: Detailed error message explaining validation failure
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
