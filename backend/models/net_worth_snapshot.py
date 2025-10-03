"""
Net Worth Snapshot models for historical tracking of user financial positions.

This module provides SQLAlchemy models for:
- Daily snapshots of user net worth
- Complete breakdown data (by country, asset class, currency)
- Historical trend tracking
- Change calculations (day-over-day, month-over-month, year-over-year)

Business logic:
- One snapshot per user per day (unique constraint)
- Retention period: 2 years
- Automated daily snapshot creation
- Manual snapshot creation on-demand
"""

import uuid
from datetime import datetime, date
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Column, String, ForeignKey, Numeric, DateTime,
    Date, CheckConstraint, UniqueConstraint, Index, JSON
)
from sqlalchemy.orm import relationship

from database import Base
from models.user import GUID  # Use platform-independent GUID type


class NetWorthSnapshot(Base):
    """
    Daily snapshot of user net worth with complete breakdown data.

    Captures point-in-time financial position including:
    - Total net worth, assets, and liabilities
    - Breakdown by country (UK, SA, Offshore)
    - Breakdown by asset class (Cash, Investments, Property, Pensions, etc.)
    - Breakdown by currency (original currency exposure)
    - Base currency for conversions

    Used for:
    - Historical trend charts
    - Change calculations (day/month/year)
    - Performance tracking
    """

    __tablename__ = 'net_worth_snapshots'

    # Primary Key
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(
        GUID,
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Snapshot Date and Currency
    snapshot_date = Column(Date, nullable=False, index=True)
    base_currency = Column(String(3), nullable=False)  # GBP, ZAR, USD, EUR

    # Net Worth Summary
    net_worth = Column(Numeric(15, 2), nullable=False)
    total_assets = Column(Numeric(15, 2), nullable=False)
    total_liabilities = Column(Numeric(15, 2), nullable=False)

    # Breakdown Data (stored as JSONB for flexibility)
    # Format matches dashboard_aggregation.py output structure
    breakdown_by_country = Column(JSON, nullable=True)
    """
    Example structure:
    [
        {"country": "UK", "assets": 100000.00, "liabilities": 50000.00, "net": 50000.00, "percentage": 50.0},
        {"country": "SA", "assets": 50000.00, "liabilities": 0.00, "net": 50000.00, "percentage": 50.0}
    ]
    """

    breakdown_by_asset_class = Column(JSON, nullable=True)
    """
    Example structure:
    [
        {"category": "Cash", "assets": 25000.00, "liabilities": 0.00, "net": 25000.00, "percentage": 25.0},
        {"category": "Investments", "assets": 75000.00, "liabilities": 0.00, "net": 75000.00, "percentage": 75.0}
    ]
    """

    breakdown_by_currency = Column(JSON, nullable=True)
    """
    Example structure:
    [
        {"currency": "GBP", "amount": 75000.00, "percentage": 75.0},
        {"currency": "ZAR", "amount": 25000.00, "percentage": 25.0}
    ]
    """

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", backref="net_worth_snapshots")

    # Table Constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'snapshot_date', name='unique_snapshot_per_user_per_day'),
        CheckConstraint('total_assets >= 0', name='check_non_negative_assets'),
        CheckConstraint('total_liabilities >= 0', name='check_non_negative_liabilities'),
        Index('idx_snapshot_user_date_desc', 'user_id', 'snapshot_date', postgresql_ops={'snapshot_date': 'DESC'}),
        Index('idx_snapshot_date_cleanup', 'snapshot_date'),  # For cleanup job
    )

    def __repr__(self) -> str:
        return (
            f"<NetWorthSnapshot(id={self.id}, user_id={self.user_id}, "
            f"date={self.snapshot_date}, net_worth={self.net_worth} {self.base_currency})>"
        )

    def to_dict(self) -> dict:
        """
        Convert snapshot to dictionary for API responses.

        Returns:
            dict: Snapshot data with all fields
        """
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'snapshot_date': self.snapshot_date.isoformat(),
            'base_currency': self.base_currency,
            'net_worth': float(self.net_worth),
            'total_assets': float(self.total_assets),
            'total_liabilities': float(self.total_liabilities),
            'breakdown_by_country': self.breakdown_by_country,
            'breakdown_by_asset_class': self.breakdown_by_asset_class,
            'breakdown_by_currency': self.breakdown_by_currency,
            'created_at': self.created_at.isoformat()
        }
