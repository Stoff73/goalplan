import React from 'react';
import { Card, Tabs, TabsList, TabsTrigger, TabsContent } from 'internal-packages/ui';
import { RetirementAgeScenario } from './RetirementAgeScenario';
import { CareerChangeScenario } from './CareerChangeScenario';
import { PropertyScenario } from './PropertyScenario';
import { MonteCarloScenario } from './MonteCarloScenario';
import { ScenarioComparison } from './ScenarioComparison';

/**
 * ScenarioDashboard - Main scenario analysis interface
 *
 * Follows STYLEGUIDE.md narrative storytelling:
 * - Tabbed interface for different scenario types
 * - Each tab has narrative intro
 * - Clean, intuitive navigation
 * - Consistent spacing and styling
 */
export function ScenarioDashboard() {
  return (
    <div style={{ padding: '24px', maxWidth: '1400px', margin: '0 auto' }}>
      {/* Page Header */}
      <div style={{ marginBottom: '32px' }}>
        <h1 style={{
          fontSize: '2rem',
          fontWeight: 700,
          color: '#0F172A',
          marginBottom: '12px'
        }}>
          Scenario Analysis
        </h1>
        <p style={{
          fontSize: '1.1rem',
          color: '#475569',
          lineHeight: '1.7',
          maxWidth: '800px'
        }}>
          Model different life decisions and see their financial impact. Try changing your
          retirement age, exploring a career move, or analyzing a property purchase.
        </p>
      </div>

      {/* Tabbed Interface */}
      <Tabs defaultValue="retirement-age">
        <TabsList>
          <TabsTrigger value="retirement-age">
            Retirement Age
          </TabsTrigger>
          <TabsTrigger value="career-change">
            Career Change
          </TabsTrigger>
          <TabsTrigger value="property">
            Property Purchase
          </TabsTrigger>
          <TabsTrigger value="monte-carlo">
            Monte Carlo
          </TabsTrigger>
          <TabsTrigger value="compare">
            Compare Scenarios
          </TabsTrigger>
        </TabsList>

        <TabsContent value="retirement-age">
          <RetirementAgeScenario />
        </TabsContent>

        <TabsContent value="career-change">
          <CareerChangeScenario />
        </TabsContent>

        <TabsContent value="property">
          <PropertyScenario />
        </TabsContent>

        <TabsContent value="monte-carlo">
          <MonteCarloScenario />
        </TabsContent>

        <TabsContent value="compare">
          <ScenarioComparison />
        </TabsContent>
      </Tabs>
    </div>
  );
}
