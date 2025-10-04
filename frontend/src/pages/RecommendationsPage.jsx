import React from 'react';
import { Layout } from '../components/Layout';
import { RecommendationsList } from '../components/recommendations/RecommendationsList';

export default function RecommendationsPage() {
  return (
    <Layout showHeader={true} containerWidth="xl">
      <RecommendationsList />
    </Layout>
  );
}
