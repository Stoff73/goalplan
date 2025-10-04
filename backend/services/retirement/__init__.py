"""
Retirement Services Module

Provides comprehensive UK pension management services including:
- UK Pension CRUD operations and calculations
- Annual Allowance tracking with carry forward
- Retirement income projections

Exports:
    - UKPensionService: Pension management
    - AnnualAllowanceService: Annual Allowance calculations
    - IncomeProjectionService: Retirement income projections
    - Factory functions for service instantiation
"""

from services.retirement.uk_pension_service import (
    UKPensionService,
    get_uk_pension_service,
    ValidationError,
    NotFoundError,
    PermissionError
)
from services.retirement.annual_allowance_service import (
    AnnualAllowanceService,
    get_annual_allowance_service
)
from services.retirement.income_projection_service import (
    IncomeProjectionService,
    get_income_projection_service
)

__all__ = [
    # Services
    'UKPensionService',
    'AnnualAllowanceService',
    'IncomeProjectionService',
    # Factory functions
    'get_uk_pension_service',
    'get_annual_allowance_service',
    'get_income_projection_service',
    # Exceptions
    'ValidationError',
    'NotFoundError',
    'PermissionError',
]
