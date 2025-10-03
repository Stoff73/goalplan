"""
Income tax treatment calculator with DTA logic.

This module determines tax treatment for income based on:
- Source country
- User's tax residency (UK/SA)
- Income type
- Double Tax Agreement provisions

Business logic:
- UK resident: Worldwide income taxed in UK (with remittance basis exception for non-doms)
- SA resident: Worldwide income taxed in SA
- Dual resident: DTA tie-breaker rules apply
- Foreign income: May qualify for DTA relief
- Exemptions: PSA (UK), Interest exemption (SA)

Integration:
- Uses UserTaxStatus for residency determination
- Applies UK-SA DTA provisions
- Calculates foreign tax credits
"""

from typing import Dict, Optional
from decimal import Decimal
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date

from models.tax_status import UserTaxStatus

import logging

logger = logging.getLogger(__name__)


class IncomeTaxTreatmentService:
    """
    Calculate tax treatment for income based on:
    - Source country
    - User's tax residency (UK/SA)
    - Income type
    - Double Tax Agreement
    """

    # UK Personal Savings Allowance (2024/25)
    UK_PSA_BASIC_RATE = Decimal('1000')  # £1,000 for basic rate taxpayers
    UK_PSA_HIGHER_RATE = Decimal('500')  # £500 for higher rate taxpayers
    UK_PSA_ADDITIONAL_RATE = Decimal('0')  # £0 for additional rate taxpayers

    # SA Interest Exemption (2024/25)
    SA_INTEREST_EXEMPTION_UNDER_65 = Decimal('23800')  # R23,800 for under 65
    SA_INTEREST_EXEMPTION_65_PLUS = Decimal('34500')  # R34,500 for 65+

    def __init__(self, db: AsyncSession):
        """
        Initialize income tax treatment service.

        Args:
            db: Database session
        """
        self.db = db

    async def calculate_tax_treatment(
        self,
        user_id: UUID,
        income_type: str,
        source_country: str,
        amount: Decimal,
        currency: str,
        tax_year: str
    ) -> Dict:
        """
        Determine applicable jurisdiction and tax treatment.

        Args:
            user_id: User ID
            income_type: Type of income (employment, rental, investment, etc.)
            source_country: Source country code (UK, ZA, US, etc.)
            amount: Income amount
            currency: Currency code
            tax_year: Tax year (e.g., '2023/24')

        Returns:
            dict: {
                'uk_taxable': bool,
                'sa_taxable': bool,
                'uk_tax_treatment': str,
                'sa_tax_treatment': str,
                'dta_relief': bool,
                'foreign_tax_credit_estimated': Decimal,
                'explanation': str,
                'exemptions_applied': list
            }
        """
        # Get user's tax status for the year
        tax_status = await self._get_tax_status(user_id, tax_year)

        if not tax_status:
            logger.warning(f"No tax status found for user {user_id} in tax year {tax_year}")
            return {
                'uk_taxable': False,
                'sa_taxable': False,
                'uk_tax_treatment': 'unknown',
                'sa_tax_treatment': 'unknown',
                'dta_relief': False,
                'foreign_tax_credit_estimated': Decimal('0'),
                'explanation': 'Tax status not set for this tax year. Please update your tax residency information.',
                'exemptions_applied': []
            }

        uk_resident = tax_status.uk_tax_resident
        sa_resident = tax_status.sa_tax_resident
        dual_resident = tax_status.dual_resident
        uk_remittance_basis = tax_status.uk_remittance_basis

        # Initialize result
        result = {
            'uk_taxable': False,
            'sa_taxable': False,
            'uk_tax_treatment': 'not_taxable',
            'sa_tax_treatment': 'not_taxable',
            'dta_relief': False,
            'foreign_tax_credit_estimated': Decimal('0'),
            'explanation': '',
            'exemptions_applied': []
        }

        # Determine taxability based on source and residency
        explanation_parts = []

        # UK source income
        if source_country == 'UK':
            result['uk_taxable'] = True
            result['uk_tax_treatment'] = 'source_country'
            explanation_parts.append(f"UK source {income_type} income is always taxable in the UK.")

            if sa_resident and not dual_resident:
                result['sa_taxable'] = True
                result['sa_tax_treatment'] = 'worldwide_income'
                result['dta_relief'] = True
                explanation_parts.append(
                    "As an SA resident, this income is also taxable in SA (worldwide income basis). "
                    "However, the UK-SA Double Tax Agreement provides relief to avoid double taxation. "
                    "You can claim a foreign tax credit in SA for UK tax paid."
                )

        # SA source income
        elif source_country == 'ZA':
            result['sa_taxable'] = True
            result['sa_tax_treatment'] = 'source_country'
            explanation_parts.append(f"SA source {income_type} income is always taxable in South Africa.")

            if uk_resident and not dual_resident:
                # Check if remittance basis applies
                if uk_remittance_basis:
                    result['uk_taxable'] = False
                    result['uk_tax_treatment'] = 'remittance_basis'
                    explanation_parts.append(
                        "As a UK resident on the remittance basis, this SA income is only taxable in the UK "
                        "if remitted (brought into) the UK. If kept offshore, no UK tax is due."
                    )
                else:
                    result['uk_taxable'] = True
                    result['uk_tax_treatment'] = 'worldwide_income'
                    result['dta_relief'] = True
                    explanation_parts.append(
                        "As a UK resident, this income is also taxable in the UK (worldwide income basis). "
                        "However, the UK-SA Double Tax Agreement provides relief to avoid double taxation. "
                        "You can claim a foreign tax credit in the UK for SA tax paid."
                    )

        # Foreign income (not UK or SA)
        else:
            explanation_parts.append(f"{source_country} source {income_type} income (foreign income).")

            if uk_resident:
                if uk_remittance_basis:
                    result['uk_taxable'] = False
                    result['uk_tax_treatment'] = 'remittance_basis'
                    explanation_parts.append(
                        "As a UK resident on the remittance basis, this foreign income is only taxable in the UK "
                        "if remitted (brought into) the UK."
                    )
                else:
                    result['uk_taxable'] = True
                    result['uk_tax_treatment'] = 'worldwide_income'
                    explanation_parts.append(
                        "As a UK resident, this foreign income is taxable in the UK (worldwide income basis)."
                    )

            if sa_resident:
                result['sa_taxable'] = True
                result['sa_tax_treatment'] = 'worldwide_income'
                explanation_parts.append(
                    "As an SA resident, this foreign income is taxable in SA (worldwide income basis)."
                )

        # Apply exemptions
        result = await self._apply_exemptions(
            result, income_type, amount, currency, tax_status, source_country
        )

        # Handle dual residents
        if dual_resident:
            explanation_parts.append(
                "\n\nNote: You are a dual resident (both UK and SA tax resident). "
                "The UK-SA DTA tie-breaker rules determine your tax residence for treaty purposes. "
                "This affects which country has primary taxing rights. "
                "Please consult a tax advisor to determine your DTA residence."
            )

        result['explanation'] = ' '.join(explanation_parts)

        return result

    async def _apply_exemptions(
        self,
        result: Dict,
        income_type: str,
        amount: Decimal,
        currency: str,
        tax_status: UserTaxStatus,
        source_country: str
    ) -> Dict:
        """
        Apply UK PSA and SA interest exemptions.

        Args:
            result: Tax treatment result to modify
            income_type: Income type
            amount: Income amount
            currency: Currency code
            tax_status: User tax status
            source_country: Source country

        Returns:
            Modified result with exemptions
        """
        exemptions_applied = []

        # UK Personal Savings Allowance (PSA) for interest income
        if income_type == 'investment' and result['uk_taxable'] and source_country in ['UK', 'ZA']:
            # Convert to GBP if needed (simplified - in real implementation, use conversion service)
            amount_gbp = amount if currency == 'GBP' else amount / Decimal('20')  # Rough approximation

            # Determine PSA based on income level (simplified - would need full income calculation)
            # For now, assume basic rate (most common)
            psa_limit = self.UK_PSA_BASIC_RATE

            if amount_gbp <= psa_limit:
                result['uk_tax_treatment'] = 'exempt_psa'
                result['uk_taxable'] = False  # Fully exempt
                exemptions_applied.append(
                    f"UK Personal Savings Allowance (£{psa_limit}): This interest income is exempt from UK tax "
                    f"as it falls within your PSA."
                )
            elif amount_gbp > psa_limit:
                partial_exempt = psa_limit
                exemptions_applied.append(
                    f"UK Personal Savings Allowance (£{psa_limit}): £{partial_exempt} of this interest is exempt. "
                    f"The remaining £{amount_gbp - partial_exempt:.2f} is taxable."
                )

        # SA Interest Exemption
        if income_type == 'investment' and result['sa_taxable'] and source_country in ['UK', 'ZA']:
            # Convert to ZAR if needed
            amount_zar = amount if currency == 'ZAR' else amount * Decimal('20')  # Rough approximation

            # Determine exemption based on age (simplified - would need age from profile)
            # For now, assume under 65
            sa_exemption = self.SA_INTEREST_EXEMPTION_UNDER_65

            if amount_zar <= sa_exemption:
                result['sa_tax_treatment'] = 'exempt_interest'
                result['sa_taxable'] = False  # Fully exempt
                exemptions_applied.append(
                    f"SA Interest Exemption (R{sa_exemption}): This interest income is exempt from SA tax "
                    f"as it falls within your annual exemption."
                )
            elif amount_zar > sa_exemption:
                partial_exempt = sa_exemption
                exemptions_applied.append(
                    f"SA Interest Exemption (R{sa_exemption}): R{partial_exempt} of this interest is exempt. "
                    f"The remaining R{amount_zar - partial_exempt:.2f} is taxable."
                )

        result['exemptions_applied'] = exemptions_applied
        return result

    async def _get_tax_status(self, user_id: UUID, tax_year: str) -> Optional[UserTaxStatus]:
        """
        Get user's tax status for the year.

        Args:
            user_id: User ID
            tax_year: Tax year (e.g., '2023/24')

        Returns:
            UserTaxStatus or None
        """
        # Parse tax year to get start date
        # UK tax year '2023/24' starts on 2023-04-06
        year_start = int(tax_year.split('/')[0])
        effective_date = date(year_start, 4, 6)

        # Get tax status effective at that date
        stmt = select(UserTaxStatus).where(
            UserTaxStatus.user_id == user_id,
            UserTaxStatus.effective_from <= effective_date,
            (UserTaxStatus.effective_to.is_(None)) | (UserTaxStatus.effective_to >= effective_date)
        ).order_by(UserTaxStatus.effective_from.desc())

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    def determine_dta_article(self, income_type: str) -> int:
        """
        Map income types to DTA articles.

        Args:
            income_type: Type of income

        Returns:
            DTA article number
        """
        article_mapping = {
            'employment': 15,  # Article 15: Employment income
            'self_employment': 7,  # Article 7: Business profits
            'investment': 11,  # Article 11: Interest (simplified)
            'rental': 6,  # Article 6: Income from immovable property
            'pension': 17,  # Article 17: Pensions
            'other': 21  # Article 21: Other income
        }

        return article_mapping.get(income_type, 21)
