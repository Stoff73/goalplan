import { useState } from 'react';
import { api } from '../api/client';

function Home() {
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const checkHealth = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await api.get('/health');
      setHealth(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h1 style={styles.title}>GoalPlan</h1>
        <p style={styles.subtitle}>Dual-Country Financial Planning</p>
        <p style={styles.description}>
          Managing finances across the UK and South Africa
        </p>

        <div style={styles.section}>
          <button
            onClick={checkHealth}
            disabled={loading}
            style={styles.button}
          >
            {loading ? 'Checking...' : 'Check API Health'}
          </button>

          {health && (
            <div style={styles.healthInfo}>
              <h3>✓ API Status: {health.status}</h3>
              <p>Service: {health.service}</p>
              <p>Version: {health.version}</p>
              <p>Environment: {health.environment}</p>
              <p>Redis: {health.redis}</p>
            </div>
          )}

          {error && (
            <div style={styles.error}>
              <p>✗ Error: {error}</p>
            </div>
          )}
        </div>

        <div style={styles.footer}>
          <p>Phase 0: Project Setup Complete</p>
        </div>
      </div>
    </div>
  );
}

const styles = {
  container: {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '20px',
  },
  card: {
    background: 'white',
    borderRadius: '8px',
    padding: '40px',
    maxWidth: '600px',
    width: '100%',
    boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
  },
  title: {
    fontSize: '36px',
    fontWeight: 'bold',
    color: '#2563eb',
    marginBottom: '8px',
  },
  subtitle: {
    fontSize: '20px',
    color: '#64748b',
    marginBottom: '8px',
  },
  description: {
    color: '#94a3b8',
    marginBottom: '32px',
  },
  section: {
    marginTop: '24px',
  },
  button: {
    background: '#2563eb',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    padding: '12px 24px',
    fontSize: '16px',
    cursor: 'pointer',
    width: '100%',
  },
  healthInfo: {
    marginTop: '20px',
    padding: '16px',
    background: '#f0fdf4',
    borderRadius: '6px',
    border: '1px solid #86efac',
  },
  error: {
    marginTop: '20px',
    padding: '16px',
    background: '#fef2f2',
    borderRadius: '6px',
    border: '1px solid #fca5a5',
    color: '#dc2626',
  },
  footer: {
    marginTop: '32px',
    paddingTop: '16px',
    borderTop: '1px solid #e2e8f0',
    color: '#94a3b8',
    textAlign: 'center',
  },
};

export default Home;
