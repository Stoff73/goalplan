import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Layout } from '../components/Layout';
import { Alert } from 'internal-packages/ui';
import { PersonalInformationSection } from '../components/profile/PersonalInformationSection';
import { ChangePasswordSection } from '../components/profile/ChangePasswordSection';
import { ChangeEmailSection } from '../components/profile/ChangeEmailSection';
import { DeleteAccountSection } from '../components/profile/DeleteAccountSection';
import { profileEndpoints } from '../utils/api';
import { authStorage } from '../utils/auth';

export default function ProfilePage() {
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    // Check authentication
    if (!authStorage.isAuthenticated()) {
      navigate('/login');
      return;
    }

    loadProfile();
  }, [navigate]);

  async function loadProfile() {
    setLoading(true);
    setError('');

    try {
      const data = await profileEndpoints.getProfile();
      setProfile(data);
    } catch (err) {
      setError(err.message || 'Failed to load profile. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  function handleProfileUpdate(updatedProfile) {
    setProfile(updatedProfile);

    // Also update user in localStorage
    const currentUser = authStorage.getUser();
    if (currentUser) {
      authStorage.setUser({
        ...currentUser,
        firstName: updatedProfile.firstName,
        lastName: updatedProfile.lastName,
      });
    }
  }

  if (loading) {
    return (
      <Layout>
        <div style={{ textAlign: 'center', padding: '64px 0' }}>
          <p style={{ color: '#475569', fontSize: '1rem' }}>Loading your profile...</p>
        </div>
      </Layout>
    );
  }

  return (
    <Layout containerWidth="lg">
      {/* Page Header */}
      <div style={{ marginBottom: '48px' }}>
        <h1
          style={{
            fontSize: '2rem',
            fontWeight: 700,
            color: '#0F172A',
            marginBottom: '8px',
          }}
        >
          Your profile settings
        </h1>
        <p style={{ color: '#475569', fontSize: '1rem', lineHeight: '1.7' }}>
          Manage your personal information, security settings, and account preferences.
        </p>
      </div>

      {/* Global Error */}
      {error && (
        <Alert type="error" style={{ marginBottom: '24px' }}>
          {error}
        </Alert>
      )}

      {/* Profile Sections */}
      <div style={{ display: 'grid', gap: '48px' }}>
        {/* Personal Information */}
        <PersonalInformationSection profile={profile} onProfileUpdate={handleProfileUpdate} />

        {/* Change Password */}
        <ChangePasswordSection />

        {/* Change Email */}
        <ChangeEmailSection currentEmail={profile?.email} />

        {/* Danger Zone - Delete Account */}
        <div>
          <div
            style={{
              borderTop: '2px solid #E2E8F0',
              paddingTop: '48px',
            }}
          >
            <div style={{ marginBottom: '24px' }}>
              <h2
                style={{
                  fontSize: '1.5rem',
                  fontWeight: 700,
                  color: '#991B1B',
                  marginBottom: '8px',
                }}
              >
                Danger zone
              </h2>
              <p style={{ color: '#7F1D1D', fontSize: '0.95rem', lineHeight: '1.7' }}>
                Irreversible actions that will permanently affect your account.
              </p>
            </div>

            <DeleteAccountSection />
          </div>
        </div>
      </div>
    </Layout>
  );
}
