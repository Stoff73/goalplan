"""Tax calculation services for UK and SA jurisdictions."""

from .uk_tax_service import uk_tax_service, UKTaxService
from .sa_tax_service import sa_tax_service, SATaxService

__all__ = ["uk_tax_service", "UKTaxService", "sa_tax_service", "SATaxService"]
