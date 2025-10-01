Feature 10.4: Personalization Engine
Feature Name: Adaptive Learning and Personalization System
User Story: As a user, I want the system to learn from my behavior, preferences, and feedback so that recommendations and advice become increasingly relevant and tailored to my specific situation over time.
Acceptance Criteria:
•	Learn from user interactions and behavior
•	Adapt recommendation style to user preferences
•	Track which recommendations users act on
•	Adjust priority and content based on success rates
•	Personalize communication frequency and channels
•	Adapt to user's financial literacy level
•	Remember user preferences across sessions
•	A/B test recommendation approaches
•	Provide transparency into personalization
Technical Requirements:
•	Machine learning models (collaborative filtering, content-based)
•	Behavioral tracking system
•	Feedback loop mechanism
•	A/B testing framework
•	Preference learning algorithms
•	User segmentation
•	Model retraining pipeline
•	Explainable AI for transparency
Constraints:
•	Must respect user privacy (GDPR/POPIA compliant)
•	Cannot make fully automated regulated financial decisions
•	Must allow user to override personalization
•	Model updates: Weekly retraining
•	Minimum data: 30 days of interactions before full personalization
•	Performance: Recommendations generated in <3 seconds
Implementation Approach:
SERVICE: PersonalizationEngine

# ===== USER PROFILE =====
FUNCTION build_user_profile(user_id: uuid) -> UserProfile:
  
  # Demographic factors
  demographics = {
    age: get_user_age(user_id),
    life_stage: determine_life_stage(user_id),
    country: get_primary_country(user_id),
    income_level: categorize_income_level(user_id),
    net_worth_level: categorize_net_worth(user_id)
  }
  
  # Behavioral factors
  behavior = {
    engagement_level: calculate_engagement_level(user_id),
    login_frequency: calculate_login_frequency(user_id),
    feature_usage: track_feature_usage(user_id),
    recommendation_interaction_rate: calculate_interaction_rate(user_id),
    goal_completion_rate: calculate_goal_completion_rate(user_id),
    average_session_duration: calculate_avg_session_duration(user_id)
  }
  
  # Preference factors
  preferences = {
    risk_tolerance: get_risk_tolerance(user_id),
    investment_style: infer_investment_style(user_id),
    communication_preference: get_communication_preference(user_id),
    detail_level_preference: infer_detail_preference(user_id),
    recommendation_categories_preferred: get_preferred_categories(user_id),
    notification_frequency: get_notification_frequency(user_id)
  }
  
  # Financial sophistication
  sophistication = {
    financial_literacy_score: assess_financial_literacy(user_id),
    complexity_comfortable_with: infer_complexity_level(user_id),
    terminology_familiarity: assess_terminology_knowledge(user_id),
    self_reported_expertise: get_self_reported_expertise(user_id)
  }
  
  # Historical performance
  history = {
    recommendations_accepted: get_accepted_recommendations(user_id),
    recommendations_dismissed: get_dismissed_recommendations(user_id),
    average_time_to_action: calculate_avg_time_to_action(user_id),
    most_successful_recommendation_types: identify_successful_types(user_id),
    abandoned_features: identify_abandoned_features(user_id)
  }
  
  RETURN {
    user_id: user_id,
    demographics: demographics,
    behavior: behavior,
    preferences: preferences,
    sophistication: sophistication,
    history: history,
    profile_completeness: calculate_profile_completeness(demographics, behavior, preferences),
    last_updated: NOW()
  }


# ===== BEHAVIORAL TRACKING =====
FUNCTION track_user_interaction(
  user_id: uuid,
  interaction: UserInteraction
) -> void:
  
  # Record interaction
  interaction_record = {
    user_id: user_id,
    interaction_type: interaction.type,
    target_id: interaction.target_id,
    target_type: interaction.target_type,
    action: interaction.action,
    context: interaction.context,
    timestamp: NOW()
  }
  
  store_interaction(interaction_record)
  
  # Update real-time profile elements
  MATCH interaction.type:
    CASE 'RECOMMENDATION_VIEWED':
      increment_metric(user_id, 'recommendations_viewed')
    
    CASE 'RECOMMENDATION_ACCEPTED':
      increment_metric(user_id, 'recommendations_accepted')
      record_successful_recommendation(
        user_id,
        interaction.target_id,
        interaction.recommendation_category
      )
    
    CASE 'RECOMMENDATION_DISMISSED':
      increment_metric(user_id, 'recommendations_dismissed')
      record_dismissal_reason(user_id, interaction.target_id, interaction.reason)
    
    CASE 'FEATURE_USED':
      record_feature_usage(user_id, interaction.feature_name)
    
    CASE 'GOAL_CREATED':
      record_goal_type_preference(user_id, interaction.goal_type)
    
    CASE 'CONTENT_READ':
      record_content_interest(user_id, interaction.content_topic)
    
    CASE 'TIME_SPENT':
      update_avg_session_duration(user_id, interaction.duration)
  
  # Trigger personalization update if threshold met
  IF should_update_personalization(user_id):
    async_update_user_personalization(user_id)


# ===== RECOMMENDATION PERSONALIZATION =====
FUNCTION personalize_recommendations(
  user_id: uuid,
  base_recommendations: array[Recommendation]
) -> array[PersonalizedRecommendation]:
  
  profile = build_user_profile(user_id)
  
  personalized = []
  
  FOR EACH rec IN base_recommendations:
    # Calculate personalization score
    personalization_score = calculate_personalization_score(rec, profile)
    
    # Adjust recommendation based on profile
    personalized_rec = {
      ...rec,
      personalization_score: personalization_score,
      
      # Adjust title based on sophistication
      title: adapt_title_to_sophistication(rec.title, profile.sophistication),
      
      # Adjust description detail level
      description: adapt_description_detail(rec.description, profile.preferences.detail_level_preference),
      
      # Adjust tone
      tone: adapt_tone(profile.demographics.age, profile.sophistication),
      
      # Add personalized reasoning
      personalized_reasoning: generate_personalized_reasoning(rec, profile),
      
      # Adjust estimated benefit format
      benefit_presentation: adapt_benefit_presentation(rec.estimated_benefit, profile),
      
      # Add relevant examples
      examples: generate_relevant_examples(rec, profile),
      
      # Adjust priority based on user history
      adjusted_priority: adjust_priority_for_user(rec.priority, rec.category, profile)
    }
    
    personalized.append(personalized_rec)
  
  # Re-rank based on personalization
  ranked = rank_by_personalization(personalized, profile)
  
  # Filter out recommendations user consistently dismisses
  filtered = filter_consistently_dismissed(ranked, profile)
  
  RETURN filtered


FUNCTION calculate_personalization_score(
  recommendation: Recommendation,
  profile: UserProfile
) -> decimal:
  
  score = 0.0
  
  # Category preference weight (40%)
  category_preference = profile.history.most_successful_recommendation_types[recommendation.category] OR 0.5
  score += category_preference * 0.40
  
  # Sophistication match (20%)
  sophistication_match = assess_sophistication_match(recommendation, profile.sophistication)
  score += sophistication_match * 0.20
  
  # Life stage relevance (20%)
  life_stage_relevance = assess_life_stage_relevance(recommendation, profile.demographics)
  score += life_stage_relevance * 0.20
  
  # Timing appropriateness (10%)
  timing_score = assess_timing(recommendation, profile.behavior)
  score += timing_score * 0.10
  
  # Recent interaction patterns (10%)
  recency_score = assess_recency_relevance(recommendation, profile.history)
  score += recency_score * 0.10
  
  RETURN score


FUNCTION adapt_description_detail(
  description: string,
  detail_preference: enum['CONCISE', 'MODERATE', 'DETAILED']
) -> string:
  
  MATCH detail_preference:
    CASE 'CONCISE':
      # Extract key sentence only
      RETURN extract_key_sentence(description) + " [Show more]"
    
    CASE 'MODERATE':
      # Keep 2-3 sentences
      RETURN extract_summary(description, sentences: 3)
    
    CASE 'DETAILED':
      # Full description plus additional context
      RETURN description + "\n\n" + generate_additional_context(description)


FUNCTION generate_personalized_reasoning(
  recommendation: Recommendation,
  profile: UserProfile
) -> array[string]:
  
  reasoning = []
  
  # Add life-stage specific reasoning
  MATCH profile.demographics.life_stage:
    CASE 'EARLY_CAREER':
      IF recommendation.category = 'RETIREMENT':
        reasoning.append("Starting early gives your investments decades to grow through compounding")
    
    CASE 'MID_CAREER':
      IF recommendation.category = 'PROTECTION':
        reasoning.append("At your stage, protecting your family's financial security is crucial")
    
    CASE 'PRE_RETIREMENT':
      IF recommendation.category = 'TAX':
        reasoning.append("Tax planning now can significantly impact your retirement income")
  
  # Add country-specific reasoning
  IF profile.demographics.country = 'UK':
    reasoning.append("This takes advantage of UK tax allowances and reliefs")
  ELSE IF profile.demographics.country = 'SA':
    reasoning.append("This optimizes for South African tax efficiency")
  
  # Add historical success reasoning
  IF profile.history.similar_recommendations_successful:
    reasoning.append("Similar recommendations have worked well for you in the past")
  
  RETURN reasoning


# ===== COLLABORATIVE FILTERING =====
FUNCTION get_collaborative_recommendations(user_id: uuid) -> array[Recommendation]:
  
  # Find similar users
  similar_users = find_similar_users(user_id, count: 20)
  
  # Get recommendations that similar users accepted
  collaborative_recommendations = []
  
  FOR EACH similar_user IN similar_users:
    accepted_recs = get_accepted_recommendations(similar_user.user_id)
    
    FOR EACH rec IN accepted_recs:
      # Check if this user hasn't seen this recommendation type yet
      IF NOT user_has_seen_recommendation_type(user_id, rec.type):
        
        # Calculate relevance score
        relevance = calculate_collaborative_relevance(
          recommendation: rec,
          target_user_id: user_id,
          source_user_similarity: similar_user.similarity_score
        )
        
        collaborative_recommendations.append({
          recommendation: rec,
          relevance_score: relevance,
          source: 'COLLABORATIVE_FILTERING',
          similar_user_count: COUNT(similar_users WHERE accepted this rec)
        })
  
  # Rank and return top recommendations
  ranked = SORT(collaborative_recommendations, BY relevance_score DESC)
  
  RETURN ranked[0:5]  # Top 5


FUNCTION find_similar_users(target_user_id: uuid, count: integer) -> array[SimilarUser]:
  
  target_profile = build_user_profile(target_user_id)
  all_users = get_all_active_users()
  
  similarities = []
  
  FOR EACH user IN all_users:
    IF user.id = target_user_id:
      CONTINUE  # Skip self
    
    user_profile = build_user_profile(user.id)
    
    # Calculate similarity score
    similarity = calculate_profile_similarity(target_profile, user_profile)
    
    IF similarity > 0.5:  # Threshold
      similarities.append({
        user_id: user.id,
        similarity_score: similarity,
        common_attributes: identify_common_attributes(target_profile, user_profile)
      })
  
  # Sort by similarity
  sorted_similar = SORT(similarities, BY similarity_score DESC)
  
  RETURN sorted_similar[0:count]


FUNCTION calculate_profile_similarity(
  profile_a: UserProfile,
  profile_b: UserProfile
) -> decimal:
  
  # Weighted similarity across dimensions
  
  # Demographic similarity (30%)
  demo_similarity = (
    age_similarity(profile_a.demographics.age, profile_b.demographics.age) * 0.4 +
    (profile_a.demographics.life_stage = profile_b.demographics.life_stage ? 1.0 : 0.0) * 0.3 +
    income_similarity(profile_a.demographics.income_level, profile_b.demographics.income_level) * 0.3
  )
  
  # Behavioral similarity (30%)
  behavior_similarity = (
    engagement_similarity(profile_a.behavior.engagement_level, profile_b.behavior.engagement_level) * 0.5 +
    feature_usage_overlap(profile_a.behavior.feature_usage, profile_b.behavior.feature_usage) * 0.5
  )
  
  # Preference similarity (20%)
  pref_similarity = (
    (profile_a.preferences.risk_tolerance = profile_b.preferences.risk_tolerance ? 1.0 : 0.5) * 0.5 +
    category_preference_overlap(profile_a.preferences, profile_b.preferences) * 0.5
  )
  
  # Financial sophistication similarity (20%)
  soph_similarity = ABS(profile_a.sophistication.financial_literacy_score - 
                        profile_b.sophistication.financial_literacy_score) / 10.0
  soph_similarity = 1.0 - soph_similarity  # Invert so closer = higher score
  
  # Weighted total
  total_similarity = (
    demo_similarity * 0.30 +
    behavior_similarity * 0.30 +
    pref_similarity * 0.20 +
    soph_similarity * 0.20
  )
  
  RETURN total_similarity


# ===== A/B TESTING FRAMEWORK =====
FUNCTION assign_ab_test_variant(
  user_id: uuid,
  test_name: string
) -> string:
  
  # Check if user already assigned to this test
  existing_assignment = get_ab_test_assignment(user_id, test_name)
  
  IF existing_assignment:
    RETURN existing_assignment.variant
  
  # Get test configuration
  test_config = get_ab_test_config(test_name)
  
  IF NOT test_config.active:
    RETURN 'CONTROL'  # Default if test not active
  
  # Assign variant based on consistent hash
  hash = consistent_hash(user_id + test_name)
  variant_index = hash MOD 100
  
  cumulative = 0
  FOR EACH variant IN test_config.variants:
    cumulative += variant.traffic_percentage
    IF variant_index < cumulative:
      selected_variant = variant.name
      BREAK
  
  # Record assignment
  record_ab_test_assignment(user_id, test_name, selected_variant)
  
  RETURN selected_variant


FUNCTION apply_ab_test_personalization(
  recommendation: Recommendation,
  user_id: uuid
) -> Recommendation:
  
  # Example tests
  
  # Test 1: Benefit emphasis
  benefit_test_variant = assign_ab_test_variant(user_id, 'BENEFIT_EMPHASIS')
  
  MATCH benefit_test_variant:
    CASE 'CONTROL':
      # Standard benefit presentation
      PASS
    
    CASE 'MONETARY_FOCUS':
      # Emphasize monetary benefits
      IF recommendation.estimated_benefit.amount:
        recommendation.title = "Save £{amount}: " + recommendation.title
    
    CASE 'PERCENTAGE_FOCUS':
      # Emphasize percentage improvements
      IF recommendation.estimated_benefit.percentage:
        recommendation.title = "Improve by {percentage}%: " + recommendation.title
  
  # Test 2: Urgency framing
  urgency_test_variant = assign_ab_test_variant(user_id, 'URGENCY_FRAMING')
  
  MATCH urgency_test_variant:
    CASE 'CONTROL':
      PASS
    
    CASE 'HIGH_URGENCY':
      IF recommendation.deadline:
        days_remaining = calculate_days_until(recommendation.deadline)
        recommendation.description = "⚠️ Only {days} days left! " + recommendation.description
    
    CASE 'LOW_PRESSURE':
      # Remove urgency language
      recommendation.description = remove_urgency_words(recommendation.description)
  
  # Test 3: Social proof
  social_proof_variant = assign_ab_test_variant(user_id, 'SOCIAL_PROOF')
  
  MATCH social_proof_variant:
    CASE 'CONTROL':
      PASS
    
    CASE 'SOCIAL_PROOF':
      # Add social proof element
      similar_users_count = count_similar_users_who_accepted(recommendation)
      IF similar_users_count > 10:
        recommendation.description += "\n\n✓ {count} users in similar situations have acted on this."
  
  RETURN recommendation


FUNCTION record_ab_test_outcome(
  user_id: uuid,
  test_name: string,
  recommendation_id: uuid,
  outcome: enum['VIEWED', 'ACCEPTED', 'DISMISSED', 'IGNORED']
) -> void:
  
  variant = get_ab_test_assignment(user_id, test_name).variant
  
  outcome_record = {
    test_name: test_name,
    variant: variant,
    user_id: user_id,
    recommendation_id: recommendation_id,
    outcome: outcome,
    timestamp: NOW()
  }
  
  store_ab_test_outcome(outcome_record)


FUNCTION analyze_ab_test_results(test_name: string) -> ABTestAnalysis:
  
  test_config = get_ab_test_config(test_name)
  
  variant_performance = []
  
  FOR EACH variant IN test_config.variants:
    outcomes = get_ab_test_outcomes(test_name, variant.name)
    
    total = outcomes.count
    accepted = COUNT(outcomes WHERE outcome = 'ACCEPTED')
    dismissed = COUNT(outcomes WHERE outcome = 'DISMISSED')
    viewed = COUNT(outcomes WHERE outcome = 'VIEWED')
    
    acceptance_rate = (accepted / total) * 100
    dismissal_rate = (dismissed / total) * 100
    engagement_rate = ((viewed + accepted) / total) * 100
    
    variant_performance.append({
      variant_name: variant.name,
      sample_size: total,
      acceptance_rate: acceptance_rate,
      dismissal_rate: dismissal_rate,
      engagement_rate: engagement_rate,
      statistical_significance: calculate_statistical_significance(
        variant,
        test_config.variants[0],  # Compare to control
        outcomes
      )
    })
  
  # Determine winner
  winner = MAX(variant_performance, BY acceptance_rate)
  
  # Calculate lift over control
  control_performance = FIRST(variant_performance WHERE variant_name = 'CONTROL')
  lift = ((winner.acceptance_rate - control_performance.acceptance_rate) / 
          control_performance.acceptance_rate) * 100
  
  RETURN {
    test_name: test_name,
    variant_performance: variant_performance,
    winner: winner.variant_name,
    lift_over_control: lift,
    recommendation: IF lift > 10 AND winner.statistical_significance > 0.95 THEN
                      "Roll out winning variant to all users"
                   ELSE
                      "Continue testing or refine hypothesis"
  }


# ===== FEEDBACK LOOP =====
FUNCTION process_user_feedback(
  user_id: uuid,
  feedback: Feedback
) -> void:
  
  # Store feedback
  store_feedback(feedback)
  
  # Update personalization based on feedback
  MATCH feedback.type:
    CASE 'RECOMMENDATION_RATING':
      # User rated a recommendation (1-5 stars)
      update_recommendation_type_preference(
        user_id,
        feedback.recommendation_category,
        feedback.rating
      )
    
    CASE 'FEATURE_RATING':
      # User rated a feature
      update_feature_preference(
        user_id,
        feedback.feature_name,
        feedback.rating
      )
    
    CASE 'CONTENT_PREFERENCE':
      # User indicated preference for content style
      update_content_style_preference(
        user_id,
        feedback.preferred_style
      )
    
    CASE 'NOTIFICATION_PREFERENCE':
      # User adjusted notification settings
      update_notification_preferences(
        user_id,
        feedback.notification_settings
      )
    
    CASE 'GENERAL_FEEDBACK':
      # Qualitative feedback - analyze sentiment
      sentiment = analyze_sentiment(feedback.text)
      update_satisfaction_score(user_id, sentiment)
  
  # Trigger model retraining if significant feedback accumulated
  IF should_retrain_model(user_id):
    schedule_model_retraining(user_id)


# ===== MODEL RETRAINING =====
FUNCTION retrain_personalization_models() -> void:
  
  # Run weekly (scheduled job)
  
  # Get all users with sufficient interaction history
  eligible_users = get_users_with_min_interactions(min_interactions: 50)
  
  FOR EACH user IN eligible_users:
    # Extract features
    features = extract_user_features(user.id)
    
    # Extract labels (successful recommendations)
    labels = extract_recommendation_outcomes(user.id)
    
    # Train user-specific model
    model = train_recommendation_model(features, labels)
    
    # Evaluate model
    performance = evaluate_model(model, validation_data)
    
    # Store model if performance acceptable
    IF performance.accuracy > 0.70:
      store_user_model(user.id, model, performance)
  
  # Train global collaborative filtering model
  global_cf_model = train_collaborative_filtering_model(all_user_interactions)
  store_global_model('COLLABORATIVE_FILTERING', global_cf_model)
  
  # Log retraining metrics
  log_model_retraining_metrics({
    users_retrained: eligible_users.count,
    average_accuracy: AVERAGE(all_models.accuracy),
    timestamp: NOW()
  })


# ===== EXPLAINABILITY =====
FUNCTION explain_personalization(
  user_id: uuid,
  recommendation_id: uuid
) -> PersonalizationExplanation:
  
  recommendation = get_recommendation(recommendation_id)
  profile = build_user_profile(user_id)
  
  # Explain why this recommendation was shown
  explanation = {
    primary_reasons: [],
    contributing_factors: [],
    how_to_improve_relevance: []
  }
  
  # Analyze recommendation selection
  IF recommendation.category IN profile.history.most_successful_recommendation_types:
    explanation.primary_reasons.append(
      "You've successfully acted on similar {category} recommendations before"
    )
  
  IF recommendation matches profile.demographics.life_stage:
    explanation.primary_reasons.append(
      "This is particularly relevant for your current life stage"
    )
  
  IF recommendation.estimated_benefit.amount > profile.typical_benefit_threshold:
    explanation.primary_reasons.append(
      "The potential benefit (£{amount}) is significant for your situation"
    )
  
  # Contributing factors
  IF recommendation selected via collaborative filtering:
    similar_count = count_similar_users_who_accepted(recommendation_id)
    explanation.contributing_factors.append(
      "{count} users with similar profiles have benefited from this"
    )
  
  IF recommendation.urgency_score > 80:
    explanation.contributing_factors.append(
      "This is time-sensitive and requires prompt action"
    )
  
  # How to improve relevance
  explanation.how_to_improve_relevance = [
    "Rate recommendations to help us understand your preferences",
    "Complete your financial goals for more targeted advice",
    "Provide feedback on what types of recommendations you find most valuable"
  ]
  
  RETURN explanation
API Endpoints:
# Profile Management
GET /api/v1/personalization/profile/{userId}
PUT /api/v1/personalization/profile/{userId}/preferences
POST /api/v1/personalization/profile/{userId}/refresh

# Interaction Tracking
POST /api/v1/personalization/track-interaction
POST /api/v1/personalization/track-event

# Feedback
POST /api/v1/personalization/feedback
GET /api/v1/personalization/feedback/{userId}/history

# A/B Testing
GET /api/v1/personalization/ab-test/{testName}/variant
POST /api/v1/personalization/ab-test/{testName}/outcome

# Explainability
GET /api/v1/personalization/explain/{recommendationId}
GET /api/v1/personalization/why-seeing-this

# Admin (for monitoring)
GET /api/v1/personalization/model-performance
POST /api/v1/personalization/retrain-models
GET /api/v1/personalization/ab-test/{testName}/results
Data Models:
TABLE: user_personalization_profiles
- user_id: UUID (PK, FK to users)
- engagement_level: ENUM('LOW', 'MEDIUM', 'HIGH')
- financial_literacy_score: INTEGER (1-10)
- risk_tolerance: ENUM('LOW', 'MEDIUM', 'HIGH')
- detail_preference: ENUM('CONCISE', 'MODERATE', 'DETAILED')
- preferred_categories: JSON (array)
- dismissed_categories: JSON (array)
- communication_style: VARCHAR(50)
- notification_frequency: ENUM('REAL_TIME', 'DAILY', 'WEEKLY', 'MONTHLY')
- preferred_channels: JSON (array: 'EMAIL', 'IN_APP', 'SMS')
- profile_completeness: DECIMAL(5,2)
- last_updated: TIMESTAMP
- created_at: TIMESTAMP

TABLE: user_interactions
- id: UUID (PK)
- user_id: UUID (FK to users)
- interaction_type: ENUM('RECOMMENDATION_VIEWED', 'RECOMMENDATION_ACCEPTED', 
                        'RECOMMENDATION_DISMISSED', 'FEATURE_USED', 'GOAL_CREATED',
                        'CONTENT_READ', 'TIME_SPENT', 'SEARCH_PERFORMED')
- target_id: UUID
- target_type: VARCHAR(50)
- action: VARCHAR(100)
- context: JSON
- session_id: UUID
- timestamp: TIMESTAMP
- device_type: VARCHAR(50)

TABLE: recommendation_feedback
- id: UUID (PK)
- recommendation_id: UUID (FK to ai_recommendations)
- user_id: UUID (FK to users)
- feedback_type: ENUM('RATING', 'HELPFUL', 'NOT_HELPFUL', 'ALREADY_DONE', 'NOT_RELEVANT')
- rating: INTEGER (1-5, nullable)
- feedback_text: TEXT
- timestamp: TIMESTAMP

TABLE: recommendation_outcomes
- id: UUID (PK)
- recommendation_id: UUID (FK to ai_recommendations)
- user_id: UUID (FK to users)
- outcome: ENUM('ACCEPTED', 'PARTIALLY_ACCEPTED', 'DISMISSED', 'IGNORED', 'EXPIRED')
- outcome_date: TIMESTAMP
- time_to_action_days: INTEGER
- actual_benefit_realized: DECIMAL(15,2) (measured post-action)
- notes: TEXT

TABLE: category_preferences
- user_id: UUID (FK to users)
- category: VARCHAR(100)
- preference_score: DECIMAL(5,2) (0-1 scale)
- acceptance_count: INTEGER
- dismissal_count: INTEGER
- total_shown: INTEGER
- last_interaction: TIMESTAMP
- PRIMARY KEY (user_id, category)

TABLE: similar_user_mappings
- user_id: UUID (FK to users)
- similar_user_id: UUID (FK to users)
- similarity_score: DECIMAL(5,4)
- common_attributes: JSON
- calculated_at: TIMESTAMP
- PRIMARY KEY (user_id, similar_user_id)

TABLE: ab_test_configurations
- test_name: VARCHAR(100) (PK)
- description: TEXT
- hypothesis: TEXT
- start_date: DATE
- end_date: DATE
- active: BOOLEAN
- variants: JSON (array of {name, description, traffic_percentage})
- success_metric: VARCHAR(100)
- minimum_sample_size: INTEGER
- created_by: UUID (FK to users - admin)
- created_at: TIMESTAMP

TABLE: ab_test_assignments
- id: UUID (PK)
- user_id: UUID (FK to users)
- test_name: VARCHAR(100) (FK to ab_test_configurations)
- variant: VARCHAR(50)
- assigned_at: TIMESTAMP
- UNIQUE (user_id, test_name)

TABLE: ab_test_outcomes
- id: UUID (PK)
- test_name: VARCHAR(100) (FK to ab_test_configurations)
- variant: VARCHAR(50)
- user_id: UUID (FK to users)
- recommendation_id: UUID (FK to ai_recommendations)
- outcome: ENUM('VIEWED', 'ACCEPTED', 'DISMISSED', 'IGNORED', 'COMPLETED')
- timestamp: TIMESTAMP
- context: JSON

TABLE: personalization_models
- user_id: UUID (PK, FK to users)
- model_type: ENUM('RECOMMENDATION_RANKING', 'CONTENT_PREFERENCE', 'TIMING_OPTIMIZATION')
- model_data: BYTEA (serialized model)
- model_version: VARCHAR(20)
- training_date: TIMESTAMP
- performance_metrics: JSON
- feature_importance: JSON
- active: BOOLEAN DEFAULT TRUE

TABLE: user_feature_vectors
- user_id: UUID (PK, FK to users)
- features: JSON (feature vector for ML models)
- calculated_at: TIMESTAMP

TABLE: personalization_events_log
- id: UUID (PK)
- user_id: UUID (FK to users)
- event_type: VARCHAR(100)
- event_data: JSON
- timestamp: TIMESTAMP
- processing_status: ENUM('PENDING', 'PROCESSED', 'FAILED')

INDEX on user_interactions(user_id, timestamp DESC)
INDEX on user_interactions(interaction_type, timestamp DESC)
INDEX on recommendation_outcomes(user_id, outcome, outcome_date)
INDEX on ab_test_outcomes(test_name, variant, outcome)
INDEX on category_preferences(user_id, preference_score DESC)
INDEX on personalization_events_log(processing_status, timestamp)
Error Handling:
ERROR CASES:
1. Insufficient interaction data for personalization
   - Response: 200 OK
   - Behavior: Fall back to general recommendations
   - Message: "Building your personalized profile. Complete more actions for tailored advice"
   
2. Model training failure
   - Response: 500 Internal Server Error (logged internally)
   - Behavior: Use previous model version or fallback
   - User impact: None (transparent failover)
   
3. A/B test assignment conflict
   - Response: 200 OK
   - Behavior: Use existing assignment
   - Log: Warning for investigation
   
4. Feature extraction failure
   - Response: 200 OK
   - Behavior: Use partial features or defaults
   - Log: Error for debugging
   
5. User opts out of personalization
   - Response: 200 OK
   - Behavior: Disable personalization, use standard recommendations
   - Store: User preference permanently

EDGE CASES:
- New user: Use demographic-based recommendations until sufficient data
- Inactive user returning: Check for stale profile, update before personalizing
- User behavior changes dramatically: Detect concept drift, retrain model
- Privacy mode: Limit tracking, use aggregated patterns only
- Multiple devices: Merge interaction data across sessions
- Shared account: Detect multiple user patterns, suggest separate profiles
- Extreme outlier user: Fall back to robust general recommendations
- Testing environment: Separate A/B test assignments from production
Performance Considerations:
•	Profile building: Cache for 1 hour, recalculate on significant events
•	Interaction tracking: Async processing via message queue
•	Model inference: <100ms for recommendation scoring
•	Similarity calculation: Pre-compute weekly for active users
•	A/B test assignment: Hash-based, deterministic, <5ms
•	Feature extraction: Batch process daily, cache results
•	Model retraining: Weekly batch job, off-peak hours
•	Expected interactions per user: 10-100 per session
•	Collaborative filtering: Use approximate nearest neighbors for scale
•	Real-time personalization: Hot path <200ms end-to-end
 

