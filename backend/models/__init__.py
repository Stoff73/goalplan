"""
Database models for GoalPlan application.

This package contains all SQLAlchemy ORM models organized by domain.
"""

from .user import User, EmailVerificationToken, UserStatus
from .session import UserSession, LoginAttempt
from .two_factor import User2FA
from .tax_status import UserTaxStatus, UKSRTData, SAPresenceData, UKDomicileStatus
from .income import UserIncome, IncomeTaxWithholding, ExchangeRate
from .profile import UserProfileHistory, EmailChangeToken
from .net_worth_snapshot import NetWorthSnapshot
from .savings_account import SavingsAccount, AccountBalanceHistory
from .life_assurance import (
    LifeAssurancePolicy,
    PolicyBeneficiary,
    PolicyTrustDetail,
    PolicyDocument,
)
from .investment import (
    InvestmentAccount,
    InvestmentHolding,
    TaxLot,
    DividendIncome,
    CapitalGainRealized,
    TaxAdvantagedInvestment,
)
from .recommendation import (
    Recommendation,
    RecommendationType,
    RecommendationPriority,
)
from .retirement import (
    UKPension,
    UKPensionContribution,
    UKPensionDBDetails,
    AnnualAllowanceTracking,
    StatePensionForecast,
    PensionType,
    PensionStatus,
    ContributionFrequency,
    TaxReliefMethod,
    DBSchemeType,
    IndexationType,
    InvestmentStrategy,
    SARetirementFund,
    SAFundContribution,
    SARetirementDeductionLimits,
    SAFundType,
    SAFundStatus,
)
from .estate_iht import (
    EstateAsset,
    EstateLiability,
    IHTCalculation,
    SAEstateDutyCalculation,
    Gift,
    IHTExemption,
    AssetType,
    LiabilityType,
    GiftType,
    ExemptionType,
)
from .scenario import (
    Scenario,
    ScenarioAssumption,
    ScenarioResult,
    ScenarioType,
    ScenarioStatus,
)
from .personalization import (
    UserPreference,
    UserBehavior,
    PersonalizedInsight,
    PreferenceType,
    ActionType,
    InsightType,
)

__all__ = [
    "User",
    "EmailVerificationToken",
    "UserStatus",
    "UserSession",
    "LoginAttempt",
    "User2FA",
    "UserTaxStatus",
    "UKSRTData",
    "SAPresenceData",
    "UKDomicileStatus",
    "UserIncome",
    "IncomeTaxWithholding",
    "ExchangeRate",
    "UserProfileHistory",
    "EmailChangeToken",
    "NetWorthSnapshot",
    "SavingsAccount",
    "AccountBalanceHistory",
    "LifeAssurancePolicy",
    "PolicyBeneficiary",
    "PolicyTrustDetail",
    "PolicyDocument",
    "InvestmentAccount",
    "InvestmentHolding",
    "TaxLot",
    "DividendIncome",
    "CapitalGainRealized",
    "TaxAdvantagedInvestment",
    "Recommendation",
    "RecommendationType",
    "RecommendationPriority",
    "UKPension",
    "UKPensionContribution",
    "UKPensionDBDetails",
    "AnnualAllowanceTracking",
    "StatePensionForecast",
    "PensionType",
    "PensionStatus",
    "ContributionFrequency",
    "TaxReliefMethod",
    "DBSchemeType",
    "IndexationType",
    "InvestmentStrategy",
    "SARetirementFund",
    "SAFundContribution",
    "SARetirementDeductionLimits",
    "SAFundType",
    "SAFundStatus",
    "EstateAsset",
    "EstateLiability",
    "IHTCalculation",
    "SAEstateDutyCalculation",
    "Gift",
    "IHTExemption",
    "AssetType",
    "LiabilityType",
    "GiftType",
    "ExemptionType",
    "Scenario",
    "ScenarioAssumption",
    "ScenarioResult",
    "ScenarioType",
    "ScenarioStatus",
    "UserPreference",
    "UserBehavior",
    "PersonalizedInsight",
    "PreferenceType",
    "ActionType",
    "InsightType",
]
