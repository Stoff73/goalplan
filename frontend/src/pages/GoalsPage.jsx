import React, { useState } from 'react';
import { Layout } from '../components/Layout';
import { GoalsDashboard } from '../components/goals/GoalsDashboard';
import { GoalForm } from '../components/goals/GoalForm';
import { GoalDetails } from '../components/goals/GoalDetails';

/**
 * GoalsPage - Main page for financial goals management
 *
 * Manages view state between:
 * - Dashboard view (list of goals)
 * - Create/Edit form view
 * - Goal details view
 *
 * Follows React 19 patterns - no forwardRef, simple state management
 */
export function GoalsPage() {
  const [currentView, setCurrentView] = useState('dashboard'); // 'dashboard' | 'form' | 'details'
  const [selectedGoalId, setSelectedGoalId] = useState(null);
  const [editingGoal, setEditingGoal] = useState(null);

  const handleCreateGoal = () => {
    setEditingGoal(null);
    setCurrentView('form');
  };

  const handleEditGoal = (goal) => {
    setEditingGoal(goal);
    setCurrentView('form');
  };

  const handleGoalSelect = (goalId) => {
    setSelectedGoalId(goalId);
    setCurrentView('details');
  };

  const handleFormSuccess = (result) => {
    // After creating/editing, go to details view
    setSelectedGoalId(result.id);
    setCurrentView('details');
  };

  const handleFormCancel = () => {
    setEditingGoal(null);
    setCurrentView('dashboard');
  };

  const handleDeleteSuccess = () => {
    setSelectedGoalId(null);
    setCurrentView('dashboard');
  };

  const handleBackToDashboard = () => {
    setSelectedGoalId(null);
    setEditingGoal(null);
    setCurrentView('dashboard');
  };

  return (
    <Layout showHeader={true} containerWidth="xl">
      {currentView === 'dashboard' && (
        <GoalsDashboard
          onGoalSelect={handleGoalSelect}
          onCreateGoal={handleCreateGoal}
        />
      )}

      {currentView === 'form' && (
        <GoalForm
          goalId={editingGoal?.id || null}
          initialData={editingGoal}
          onSuccess={handleFormSuccess}
          onCancel={handleFormCancel}
        />
      )}

      {currentView === 'details' && selectedGoalId && (
        <GoalDetails
          goalId={selectedGoalId}
          onEdit={handleEditGoal}
          onDelete={handleDeleteSuccess}
          onBack={handleBackToDashboard}
        />
      )}
    </Layout>
  );
}
