import React, { useState, useEffect } from 'react';
import { Button, Alert } from 'internal-packages/ui';
import { authStorage } from '../../utils/auth';

/**
 * AlertsList - Financial alerts with filtering and actions
 *
 * Features:
 * - Auto-loads on component mount
 * - Filter by read/unread status
 * - Filter by urgency (High/Medium/Low)
 * - Color-coded urgency badges
 * - Mark as read / Dismiss actions
 * - Empty state handling
 */
export function AlertsList() {
  const [alerts, setAlerts] = useState([]);
  const [filteredAlerts, setFilteredAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filterUnread, setFilterUnread] = useState(false);
  const [filterUrgency, setFilterUrgency] = useState('All');
  const [actioningId, setActioningId] = useState(null);

  useEffect(() => {
    loadAlerts();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [alerts, filterUnread, filterUrgency]);

  const loadAlerts = async () => {
    setLoading(true);
    setError(null);

    try {
      const res = await fetch('/api/v1/ai/alerts', {
        headers: {
          Authorization: `Bearer ${authStorage.getAccessToken()}`,
        },
      });

      if (!res.ok) {
        if (res.status === 401) {
          authStorage.clear();
          window.location.href = '/login';
          return;
        }

        const errorData = await res.json();
        throw new Error(errorData.detail || 'Failed to load alerts.');
      }

      const data = await res.json();
      setAlerts(data.alerts || []);
    } catch (err) {
      setError(err.message || 'Failed to load alerts. Please try again.');
      console.error('Error loading alerts:', err);
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...alerts];

    // Filter by unread only
    if (filterUnread) {
      filtered = filtered.filter((alert) => !alert.read_at);
    }

    // Filter by urgency
    if (filterUrgency !== 'All') {
      filtered = filtered.filter((alert) => alert.urgency === filterUrgency);
    }

    // Sort by urgency (high first), then date (newest first)
    const urgencyOrder = { HIGH: 1, MEDIUM: 2, LOW: 3 };
    filtered.sort((a, b) => {
      const urgencyDiff = urgencyOrder[a.urgency] - urgencyOrder[b.urgency];
      if (urgencyDiff !== 0) return urgencyDiff;
      return new Date(b.created_at) - new Date(a.created_at);
    });

    setFilteredAlerts(filtered);
  };

  const handleMarkRead = async (id) => {
    setActioningId(id);

    try {
      const res = await fetch(`/api/v1/ai/alerts/${id}/read`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${authStorage.getAccessToken()}`,
        },
      });

      if (!res.ok) {
        throw new Error('Failed to mark alert as read');
      }

      // Update alert in state
      setAlerts((prev) =>
        prev.map((alert) =>
          alert.id === id ? { ...alert, read_at: new Date().toISOString() } : alert
        )
      );
    } catch (err) {
      alert('Failed to mark alert as read. Please try again.');
      console.error('Error marking alert as read:', err);
    } finally {
      setActioningId(null);
    }
  };

  const handleDismiss = async (id) => {
    if (!window.confirm('Are you sure you want to dismiss this alert?')) {
      return;
    }

    setActioningId(id);

    try {
      const res = await fetch(`/api/v1/ai/alerts/${id}/dismiss`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${authStorage.getAccessToken()}`,
        },
      });

      if (!res.ok) {
        throw new Error('Failed to dismiss alert');
      }

      // Remove from list
      setAlerts((prev) => prev.filter((alert) => alert.id !== id));
    } catch (err) {
      alert('Failed to dismiss alert. Please try again.');
      console.error('Error dismissing alert:', err);
    } finally {
      setActioningId(null);
    }
  };

  const getUrgencyBadgeStyle = (urgency) => {
    const styles = {
      HIGH: {
        backgroundColor: '#FEE2E2',
        borderColor: '#EF4444',
        color: '#991B1B',
      },
      MEDIUM: {
        backgroundColor: '#FEF3C7',
        borderColor: '#F59E0B',
        color: '#92400E',
      },
      LOW: {
        backgroundColor: '#EFF6FF',
        borderColor: '#3B82F6',
        color: '#1E40AF',
      },
    };
    return styles[urgency] || styles.LOW;
  };

  // Styles
  const containerStyle = {
    maxWidth: '900px',
    margin: '0 auto',
  };

  const narrativeSectionStyle = {
    padding: '32px',
    backgroundColor: '#FFFFFF',
    borderRadius: '12px',
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.06)',
    marginBottom: '24px',
    lineHeight: '1.7',
  };

  const headingStyle = {
    fontSize: '1.2rem',
    fontWeight: 600,
    color: '#0F172A',
    marginBottom: '16px',
  };

  const paragraphStyle = {
    color: '#475569',
    marginBottom: '16px',
    lineHeight: '1.7',
  };

  const filterContainerStyle = {
    display: 'flex',
    gap: '16px',
    marginBottom: '24px',
    flexWrap: 'wrap',
    alignItems: 'center',
  };

  const checkboxContainerStyle = {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
  };

  const selectStyle = {
    padding: '8px 12px',
    borderRadius: '8px',
    border: '1px solid #E2E8F0',
    fontSize: '0.875rem',
    color: '#0F172A',
    backgroundColor: '#FFFFFF',
    cursor: 'pointer',
  };

  const alertCardStyle = (isRead) => ({
    padding: '24px',
    backgroundColor: isRead ? '#F8FAFC' : '#FFFFFF',
    borderRadius: '12px',
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.06)',
    marginBottom: '16px',
    lineHeight: '1.7',
    position: 'relative',
    border: isRead ? '1px solid #E2E8F0' : '1px solid #BFDBFE',
  });

  const urgencyBadgeStyle = (urgency) => ({
    position: 'absolute',
    top: '16px',
    right: '16px',
    padding: '4px 12px',
    borderRadius: '9999px',
    fontSize: '0.75rem',
    fontWeight: 600,
    border: `1px solid ${getUrgencyBadgeStyle(urgency).borderColor}`,
    ...getUrgencyBadgeStyle(urgency),
  });

  const messageStyle = {
    color: '#0F172A',
    marginBottom: '16px',
    lineHeight: '1.7',
    fontSize: '1rem',
    marginRight: '120px', // Space for badge
  };

  const actionButtonsStyle = {
    display: 'flex',
    gap: '12px',
    marginTop: '16px',
  };

  const emptyStateStyle = {
    padding: '64px 32px',
    textAlign: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: '12px',
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.06)',
  };

  // Loading state
  if (loading) {
    return (
      <div style={containerStyle}>
        <div style={narrativeSectionStyle}>
          <h3 style={headingStyle}>Important Updates</h3>
          <p style={paragraphStyle}>Loading your alerts...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div style={containerStyle}>
        <Alert variant="error">
          <p style={{ fontWeight: 600 }}>Unable to Load Alerts</p>
          <p style={{ marginTop: '4px', fontSize: '0.95rem' }}>{error}</p>
        </Alert>
      </div>
    );
  }

  // Empty state - no alerts
  if (alerts.length === 0) {
    return (
      <div style={containerStyle}>
        <div style={emptyStateStyle}>
          <div style={{ fontSize: '4rem', marginBottom: '24px' }}>✓</div>
          <h3 style={{ fontSize: '1.5rem', fontWeight: 600, color: '#0F172A', marginBottom: '16px' }}>
            No alerts right now - you're all caught up!
          </h3>
          <p style={{ color: '#475569', lineHeight: '1.7', marginBottom: '24px', maxWidth: '600px', margin: '0 auto' }}>
            I'll notify you here when there are important updates about your finances, such as
            approaching tax year deadlines, allowance limits, or other time-sensitive opportunities.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div style={containerStyle}>
      {/* Introduction */}
      <div style={narrativeSectionStyle}>
        <h3 style={headingStyle}>Important Updates About Your Finances</h3>
        <p style={paragraphStyle}>
          You have {alerts.filter(a => !a.read_at).length} unread alert{alerts.filter(a => !a.read_at).length === 1 ? '' : 's'} out of {alerts.length} total.
        </p>

        {/* Filters */}
        <div style={filterContainerStyle}>
          <div style={checkboxContainerStyle}>
            <input
              type="checkbox"
              id="unread-filter"
              checked={filterUnread}
              onChange={(e) => setFilterUnread(e.target.checked)}
              style={{ cursor: 'pointer' }}
            />
            <label htmlFor="unread-filter" style={{ fontSize: '0.875rem', color: '#475569', cursor: 'pointer' }}>
              Unread only
            </label>
          </div>

          <div>
            <label htmlFor="urgency-filter" style={{ display: 'block', fontSize: '0.75rem', color: '#475569', marginBottom: '4px' }}>
              Urgency
            </label>
            <select
              id="urgency-filter"
              value={filterUrgency}
              onChange={(e) => setFilterUrgency(e.target.value)}
              style={selectStyle}
            >
              <option value="All">All Urgency Levels</option>
              <option value="HIGH">High Urgency</option>
              <option value="MEDIUM">Medium Urgency</option>
              <option value="LOW">Low Urgency</option>
            </select>
          </div>
        </div>
      </div>

      {/* Alerts List */}
      {filteredAlerts.length > 0 ? (
        filteredAlerts.map((alertItem) => (
          <div key={alertItem.id} style={alertCardStyle(!!alertItem.read_at)}>
            {/* Urgency Badge */}
            <div style={urgencyBadgeStyle(alertItem.urgency)}>
              {alertItem.urgency}
            </div>

            {/* Alert Message */}
            <p style={messageStyle}>{alertItem.message}</p>

            {/* Action Buttons */}
            <div style={actionButtonsStyle}>
              {!alertItem.read_at && (
                <Button
                  variant="outline"
                  onClick={() => handleMarkRead(alertItem.id)}
                  disabled={actioningId === alertItem.id}
                  size="small"
                >
                  {actioningId === alertItem.id ? 'Marking...' : 'Mark as Read'}
                </Button>
              )}

              {alertItem.action_url && (
                <Button
                  variant="primary"
                  onClick={() => (window.location.href = alertItem.action_url)}
                  size="small"
                >
                  Take Action
                </Button>
              )}

              <Button
                variant="ghost"
                onClick={() => handleDismiss(alertItem.id)}
                disabled={actioningId === alertItem.id}
                size="small"
              >
                {actioningId === alertItem.id ? 'Dismissing...' : 'Dismiss'}
              </Button>
            </div>
          </div>
        ))
      ) : (
        <div style={emptyStateStyle}>
          <p style={{ color: '#475569', lineHeight: '1.7' }}>
            No alerts match your current filters. Try adjusting the filters above.
          </p>
        </div>
      )}
    </div>
  );
}
