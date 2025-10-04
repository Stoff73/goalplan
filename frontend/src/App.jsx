import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import RegisterPage from './pages/RegisterPage';
import LoginPage from './pages/LoginPage';
import VerifyEmailPage from './pages/VerifyEmailPage';
import Setup2FAPage from './pages/Setup2FAPage';
import DashboardPage from './pages/DashboardPage';
import ProfilePage from './pages/ProfilePage';
import TaxStatusPage from './pages/TaxStatusPage';
import IncomePage from './pages/IncomePage';
import SavingsPage from './pages/SavingsPage';
import ProtectionPage from './pages/ProtectionPage';
import InvestmentPage from './pages/InvestmentPage';
import { GoalsPage } from './pages/GoalsPage';
import AIAdvisorPage from './pages/AIAdvisorPage';
import RetirementPage from './pages/RetirementPage';
import { IHTPage } from './pages/IHTPage';
import { PersonalizedDashboard } from './components/personalization/PersonalizedDashboard';
import { PersonalizationSettings } from './components/personalization/PersonalizationSettings';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Default route redirects to login */}
        <Route path="/" element={<Navigate to="/login" replace />} />

        {/* Authentication routes */}
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/verify-email" element={<VerifyEmailPage />} />
        <Route path="/setup-2fa" element={<Setup2FAPage />} />

        {/* Protected routes */}
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/tax-status" element={<TaxStatusPage />} />
        <Route path="/income" element={<IncomePage />} />
        <Route path="/savings" element={<SavingsPage />} />
        <Route path="/protection" element={<ProtectionPage />} />
        <Route path="/investments" element={<InvestmentPage />} />
        <Route path="/investments/dashboard" element={<InvestmentPage />} />
        <Route path="/investments/holdings" element={<InvestmentPage />} />
        <Route path="/investments/allocation" element={<InvestmentPage />} />
        <Route path="/retirement" element={<RetirementPage />} />
        <Route path="/iht" element={<IHTPage />} />
        <Route path="/goals" element={<GoalsPage />} />
        <Route path="/ai-advisor" element={<AIAdvisorPage />} />

        {/* Personalization routes */}
        <Route path="/personalized-dashboard" element={<PersonalizedDashboard />} />
        <Route path="/settings/personalization" element={<PersonalizationSettings />} />

        {/* Catch all - redirect to login */}
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
