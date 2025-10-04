"""
IHT Planning Services

This module provides comprehensive Inheritance Tax and Estate Planning services:

- Estate Valuation Service: Calculate gross/net estate, IHT with NRB/RNRB
- Gift Analysis Service: Track PETs, apply exemptions, calculate taper relief
- SA Estate Duty Service: Calculate SA Estate Duty with abatement and tiered rates

All services follow async patterns and use Decimal for currency calculations.
"""

from services.iht.estate_valuation_service import (
    EstateValuationService,
    get_estate_valuation_service
)
from services.iht.gift_analysis_service import (
    GiftAnalysisService,
    get_gift_analysis_service
)
from services.iht.sa_estate_duty_service import (
    SAEstateDutyService,
    get_sa_estate_duty_service
)

__all__ = [
    'EstateValuationService',
    'get_estate_valuation_service',
    'GiftAnalysisService',
    'get_gift_analysis_service',
    'SAEstateDutyService',
    'get_sa_estate_duty_service',
]
