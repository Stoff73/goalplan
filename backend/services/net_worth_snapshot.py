"""
Net Worth Snapshot Service

Manages creation, retrieval, and analysis of historical net worth snapshots.

This service provides:
- Daily snapshot creation (manual and automated)
- Historical snapshot retrieval
- Trend data for charts (last 12 months)
- Change calculations (day-over-day, month-over-month, year-over-year)
- Cleanup of old snapshots (retention: 2 years)

Architecture:
- Integrates with DashboardAggregationService for current data
- Stores complete breakdown data for historical accuracy
- Optimized queries for trend analysis
- Background job support for automated snapshots
"""

import logging
from decimal import Decimal
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, delete, func
from sqlalchemy.exc import IntegrityError

from models.net_worth_snapshot import NetWorthSnapshot
from services.dashboard_aggregation import DashboardAggregationService

logger = logging.getLogger(__name__)


class NetWorthSnapshotService:
    """Service for managing net worth snapshots and historical trend analysis."""

    RETENTION_DAYS = 730  # 2 years
    DEFAULT_TREND_MONTHS = 12

    def __init__(self, db: AsyncSession):
        """
        Initialize net worth snapshot service.

        Args:
            db: Database session for queries
        """
        self.db = db
        self.aggregation_service = DashboardAggregationService(db)

    async def create_snapshot(
        self,
        user_id: UUID,
        base_currency: str = "GBP",
        snapshot_date: Optional[date] = None
    ) -> NetWorthSnapshot:
        """
        Create a net worth snapshot for the user.

        Uses DashboardAggregationService to get current net worth data
        and stores it as a historical snapshot.

        Args:
            user_id: User UUID
            base_currency: Currency for all amounts (GBP, ZAR, USD, EUR)
            snapshot_date: Date for snapshot (default: today)

        Returns:
            NetWorthSnapshot: Created snapshot

        Raises:
            ValueError: If snapshot already exists for this date
            Exception: If aggregation fails

        Example:
            >>> service = NetWorthSnapshotService(db)
            >>> snapshot = await service.create_snapshot(user_id, "GBP")
            >>> print(snapshot.net_worth)
        """
        snapshot_date = snapshot_date or date.today()

        logger.info(
            f"Creating net worth snapshot for user {user_id} "
            f"on {snapshot_date} in {base_currency}"
        )

        try:
            # Get current net worth summary from aggregation service
            # Use use_cache=False to ensure fresh data for snapshot
            summary = await self.aggregation_service.get_net_worth_summary(
                user_id=user_id,
                base_currency=base_currency,
                as_of_date=snapshot_date,
                use_cache=False
            )

            # Create snapshot record
            snapshot = NetWorthSnapshot(
                user_id=user_id,
                snapshot_date=snapshot_date,
                base_currency=base_currency,
                net_worth=Decimal(str(summary['net_worth'])),
                total_assets=Decimal(str(summary['total_assets'])),
                total_liabilities=Decimal(str(summary['total_liabilities'])),
                breakdown_by_country=summary['breakdown_by_country'],
                breakdown_by_asset_class=summary['breakdown_by_asset_class'],
                breakdown_by_currency=summary['breakdown_by_currency']
            )

            self.db.add(snapshot)
            await self.db.commit()
            await self.db.refresh(snapshot)

            logger.info(
                f"Created snapshot {snapshot.id} for user {user_id}: "
                f"net_worth={snapshot.net_worth} {base_currency}"
            )

            return snapshot

        except IntegrityError as e:
            await self.db.rollback()
            # Check if it's a duplicate snapshot
            if "unique_snapshot_per_user_per_day" in str(e):
                logger.warning(
                    f"Snapshot already exists for user {user_id} on {snapshot_date}"
                )
                raise ValueError(
                    f"Snapshot already exists for {snapshot_date}. "
                    f"Only one snapshot per user per day is allowed."
                ) from e
            raise

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to create snapshot for user {user_id}: {e}")
            raise

    async def get_snapshots(
        self,
        user_id: UUID,
        from_date: date,
        to_date: date,
        base_currency: Optional[str] = None
    ) -> List[NetWorthSnapshot]:
        """
        Retrieve historical snapshots for a user within a date range.

        Args:
            user_id: User UUID
            from_date: Start date (inclusive)
            to_date: End date (inclusive)
            base_currency: Optional filter by currency

        Returns:
            List[NetWorthSnapshot]: Snapshots ordered by date descending

        Example:
            >>> from_date = date(2024, 1, 1)
            >>> to_date = date(2024, 12, 31)
            >>> snapshots = await service.get_snapshots(user_id, from_date, to_date)
            >>> for snap in snapshots:
            ...     print(f"{snap.snapshot_date}: {snap.net_worth}")
        """
        logger.info(
            f"Retrieving snapshots for user {user_id} "
            f"from {from_date} to {to_date}"
        )

        query = select(NetWorthSnapshot).where(
            and_(
                NetWorthSnapshot.user_id == user_id,
                NetWorthSnapshot.snapshot_date >= from_date,
                NetWorthSnapshot.snapshot_date <= to_date
            )
        )

        # Optional currency filter
        if base_currency:
            query = query.where(NetWorthSnapshot.base_currency == base_currency)

        # Order by date descending (most recent first)
        query = query.order_by(NetWorthSnapshot.snapshot_date.desc())

        result = await self.db.execute(query)
        snapshots = result.scalars().all()

        logger.info(f"Retrieved {len(snapshots)} snapshots for user {user_id}")

        return list(snapshots)

    async def get_trend_data(
        self,
        user_id: UUID,
        base_currency: str = "GBP",
        months: int = 12
    ) -> List[Dict[str, Any]]:
        """
        Get monthly trend data for charts.

        Retrieves one snapshot per month (last day of month) for the specified
        number of months. Used for dashboard trend charts.

        Args:
            user_id: User UUID
            base_currency: Currency for amounts
            months: Number of months to retrieve (default: 12)

        Returns:
            List of dicts with structure:
            [
                {"date": "2024-01-31", "net_worth": 100000.00},
                {"date": "2024-02-29", "net_worth": 105000.00},
                ...
            ]

        Example:
            >>> trend_data = await service.get_trend_data(user_id, "GBP", months=12)
            >>> print(f"12-month trend: {len(trend_data)} data points")
        """
        logger.info(
            f"Retrieving {months}-month trend data for user {user_id} in {base_currency}"
        )

        # Calculate date range
        to_date = date.today()
        from_date = to_date - timedelta(days=months * 31)  # Approximate

        # Get all snapshots in range
        snapshots = await self.get_snapshots(
            user_id=user_id,
            from_date=from_date,
            to_date=to_date,
            base_currency=base_currency
        )

        if not snapshots:
            logger.info(f"No snapshots found for user {user_id}")
            return []

        # Group by month and take last snapshot of each month
        monthly_snapshots: Dict[str, NetWorthSnapshot] = {}

        for snapshot in snapshots:
            # Group by year-month (e.g., "2024-01")
            month_key = snapshot.snapshot_date.strftime("%Y-%m")

            # Keep the latest snapshot for each month
            if (month_key not in monthly_snapshots or
                snapshot.snapshot_date > monthly_snapshots[month_key].snapshot_date):
                monthly_snapshots[month_key] = snapshot

        # Build trend data
        trend_data = [
            {
                "date": snapshot.snapshot_date.isoformat(),
                "net_worth": float(snapshot.net_worth)
            }
            for snapshot in sorted(
                monthly_snapshots.values(),
                key=lambda s: s.snapshot_date
            )
        ]

        logger.info(f"Generated trend data with {len(trend_data)} monthly points")

        return trend_data

    async def calculate_changes(
        self,
        user_id: UUID,
        base_currency: str = "GBP"
    ) -> Dict[str, Dict[str, float]]:
        """
        Calculate net worth changes over different time periods.

        Compares current net worth to:
        - Day: 1 day ago
        - Month: 30 days ago
        - Year: 365 days ago

        Args:
            user_id: User UUID
            base_currency: Currency for calculations

        Returns:
            Dict with structure:
            {
                "day": {"amount": 1000.00, "percentage": 1.5},
                "month": {"amount": 5000.00, "percentage": 5.2},
                "year": {"amount": 20000.00, "percentage": 25.0}
            }

        Example:
            >>> changes = await service.calculate_changes(user_id, "GBP")
            >>> print(f"Monthly change: {changes['month']['percentage']:.1f}%")
        """
        logger.info(f"Calculating changes for user {user_id} in {base_currency}")

        today = date.today()
        periods = {
            "day": today - timedelta(days=1),
            "month": today - timedelta(days=30),
            "year": today - timedelta(days=365)
        }

        # Get today's snapshot (or most recent)
        current_snapshots = await self.get_snapshots(
            user_id=user_id,
            from_date=today - timedelta(days=7),  # Look back up to 7 days
            to_date=today,
            base_currency=base_currency
        )

        if not current_snapshots:
            logger.info(f"No recent snapshots for user {user_id}")
            return {
                "day": {"amount": 0.0, "percentage": 0.0},
                "month": {"amount": 0.0, "percentage": 0.0},
                "year": {"amount": 0.0, "percentage": 0.0}
            }

        current_snapshot = current_snapshots[0]  # Most recent
        current_net_worth = float(current_snapshot.net_worth)

        changes: Dict[str, Dict[str, float]] = {}

        for period_name, period_date in periods.items():
            # Get snapshot closest to period date
            period_snapshots = await self.get_snapshots(
                user_id=user_id,
                from_date=period_date - timedelta(days=7),
                to_date=period_date + timedelta(days=7),
                base_currency=base_currency
            )

            if period_snapshots:
                # Find closest snapshot to target date
                closest_snapshot = min(
                    period_snapshots,
                    key=lambda s: abs((s.snapshot_date - period_date).days)
                )

                period_net_worth = float(closest_snapshot.net_worth)

                # Calculate change
                amount_change = current_net_worth - period_net_worth
                percentage_change = (
                    (amount_change / period_net_worth * 100)
                    if period_net_worth != 0
                    else 0.0
                )

                changes[period_name] = {
                    "amount": round(amount_change, 2),
                    "percentage": round(percentage_change, 2)
                }

            else:
                # No comparison data available
                changes[period_name] = {
                    "amount": 0.0,
                    "percentage": 0.0
                }

        logger.info(f"Calculated changes for user {user_id}: {changes}")

        return changes

    async def cleanup_old_snapshots(self) -> int:
        """
        Delete snapshots older than retention period (2 years).

        This method should be called by a background job (e.g., daily cron).

        Returns:
            int: Number of snapshots deleted

        Example:
            >>> deleted_count = await service.cleanup_old_snapshots()
            >>> print(f"Deleted {deleted_count} old snapshots")
        """
        cutoff_date = date.today() - timedelta(days=self.RETENTION_DAYS)

        logger.info(f"Cleaning up snapshots older than {cutoff_date}")

        # Delete old snapshots
        stmt = delete(NetWorthSnapshot).where(
            NetWorthSnapshot.snapshot_date < cutoff_date
        )

        result = await self.db.execute(stmt)
        await self.db.commit()

        deleted_count = result.rowcount

        logger.info(f"Deleted {deleted_count} snapshots older than {cutoff_date}")

        return deleted_count

    async def get_latest_snapshot(
        self,
        user_id: UUID,
        base_currency: str = "GBP"
    ) -> Optional[NetWorthSnapshot]:
        """
        Get the most recent snapshot for a user.

        Args:
            user_id: User UUID
            base_currency: Optional filter by currency

        Returns:
            NetWorthSnapshot or None if no snapshots exist

        Example:
            >>> latest = await service.get_latest_snapshot(user_id)
            >>> if latest:
            ...     print(f"Latest snapshot: {latest.snapshot_date}")
        """
        query = select(NetWorthSnapshot).where(
            NetWorthSnapshot.user_id == user_id
        )

        if base_currency:
            query = query.where(NetWorthSnapshot.base_currency == base_currency)

        query = query.order_by(NetWorthSnapshot.snapshot_date.desc()).limit(1)

        result = await self.db.execute(query)
        snapshot = result.scalar_one_or_none()

        return snapshot

    async def snapshot_exists(
        self,
        user_id: UUID,
        snapshot_date: date,
        base_currency: Optional[str] = None
    ) -> bool:
        """
        Check if a snapshot exists for a given user and date.

        Args:
            user_id: User UUID
            snapshot_date: Date to check
            base_currency: Optional filter by currency

        Returns:
            bool: True if snapshot exists, False otherwise

        Example:
            >>> exists = await service.snapshot_exists(user_id, date.today())
            >>> if not exists:
            ...     await service.create_snapshot(user_id)
        """
        query = select(NetWorthSnapshot.id).where(
            and_(
                NetWorthSnapshot.user_id == user_id,
                NetWorthSnapshot.snapshot_date == snapshot_date
            )
        )

        if base_currency:
            query = query.where(NetWorthSnapshot.base_currency == base_currency)

        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None
