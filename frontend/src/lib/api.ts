/**
 * API client for communicating with the backend.
 */

// Use environment variable for production, fallback to /api for local development (proxied via next.config.js)
const API_BASE = process.env.NEXT_PUBLIC_API_URL
  ? `${process.env.NEXT_PUBLIC_API_URL}/api`
  : '/api';

export interface Participant {
  id: string;
  participant_code: string;
  age?: number;
  gender?: string;
  education_level?: string;
  latin_square_row: number;
  condition_order: string[];
  created_at: string;
}

export interface ParticipantProgress {
  participant_id: string;
  participant_code: string;
  condition_order: string[];
  completed_conditions: string[];
  next_condition: string | null;
  sessions_completed: number;
  sessions_remaining: number;
}

export interface SessionResponse {
  id: string;
  participant_id: string;
  session_type: string;
  sequence_number: number;
  status: string;
  started_at: string;
  items_administered: number;
}

export interface TraitEstimate {
  theta: number;
  se: number;
  items_administered: number;
  completed: boolean;
}

export interface DOSEStartResponse {
  session_id: string;
  message: string;
  current_item: {
    number: number;
    text: string;
    trait: string;
  };
  current_estimates: Record<string, TraitEstimate>;
}

export interface DOSERespondResponse {
  session_id: string;
  action: 'present_item' | 'complete';
  next_item?: {
    number: number;
    text: string;
    trait: string;
  };
  current_estimates: Record<string, TraitEstimate>;
  progress: {
    items_administered: number;
    traits_completed: number;
    total_traits: number;
  };
  stopping_reason?: string;
}

export interface StaticStartResponse {
  session_id: string;
  message: string;
  current_item: number;
  item_text: string;
  total_items: number;
}

export interface StaticRespondResponse {
  session_id: string;
  is_complete: boolean;
  next_item_number: number | null;
  next_item_text: string | null;
  progress: string;
  message: string | null;
}

export interface NaturalStartResponse {
  session_id: string;
  message: string;
  conversation_id: string;
}

export interface NaturalMessageResponse {
  session_id: string;
  message: string;
  turn_count: number;
  can_analyze: boolean;
}

export interface TraitInference {
  score: number;
  confidence: number;
  evidence: string;
}

export interface NaturalAnalyzeResponse {
  session_id: string;
  inferred_traits: Record<string, TraitInference>;
  conversation_turns: number;
  analysis_model: string;
}

export interface SurveyItemsResponse {
  items: Array<{
    number: number;
    text: string;
    trait: string;
  }>;
}

export interface ParticipantResultsResponse {
  participant_id: string;
  participant_code: string;
  condition_order: string[];
  sessions_completed: number;
  sessions: Array<{
    session_id: string;
    session_type: string;
    sequence_number: number;
    scores: Record<string, number>;
    metrics: {
      total_items: number;
      duration_seconds: number;
      item_reduction_rate: number | null;
    };
  }>;
  comparisons_with_survey: Record<string, {
    pearson_r: number;
    mean_absolute_error: number;
    trait_differences: Record<string, number>;
  }> | null;
}

// Helper function for API requests
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE}${endpoint}`;

  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `API error: ${response.status}`);
  }

  return response.json();
}

// Participant endpoints
export async function registerParticipant(data: {
  age?: number;
  gender?: string;
  education_level?: string;
}): Promise<Participant> {
  return apiRequest('/participants/register', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function getParticipant(id: string): Promise<Participant> {
  return apiRequest(`/participants/${id}`);
}

export async function getParticipantProgress(id: string): Promise<ParticipantProgress> {
  return apiRequest(`/participants/${id}/progress`);
}

// Survey (G1) endpoints
export async function startSurvey(participantId: string): Promise<SessionResponse> {
  return apiRequest(`/survey/${participantId}/start`, { method: 'POST' });
}

export async function getSurveyItems(sessionId: string): Promise<SurveyItemsResponse> {
  return apiRequest(`/survey/${sessionId}/items`);
}

export async function submitSurvey(
  sessionId: string,
  responses: Array<{ item_number: number; value: number }>
) {
  return apiRequest(`/survey/${sessionId}/submit`, {
    method: 'POST',
    body: JSON.stringify({ responses }),
  });
}

// Static Chatbot (G2) endpoints
export async function startStaticChatbot(participantId: string): Promise<StaticStartResponse> {
  return apiRequest(`/static/${participantId}/start`, { method: 'POST' });
}

export async function respondStaticChatbot(sessionId: string, responseValue: number): Promise<StaticRespondResponse> {
  return apiRequest(`/static/${sessionId}/respond`, {
    method: 'POST',
    body: JSON.stringify({ response_value: responseValue }),
  });
}

// DOSE Chatbot (G3) endpoints
export async function startDOSEChatbot(participantId: string): Promise<DOSEStartResponse> {
  return apiRequest(`/dose/${participantId}/start`, { method: 'POST' });
}

export async function respondDOSEChatbot(
  sessionId: string,
  responseValue: number
): Promise<DOSERespondResponse> {
  return apiRequest(`/dose/${sessionId}/respond`, {
    method: 'POST',
    body: JSON.stringify({ response_value: responseValue }),
  });
}

export async function getDOSEState(sessionId: string) {
  return apiRequest(`/dose/${sessionId}/state`);
}

// Natural Chatbot (G4) endpoints
export async function startNaturalChatbot(participantId: string): Promise<NaturalStartResponse> {
  return apiRequest(`/natural/${participantId}/start`, { method: 'POST' });
}

export async function sendNaturalMessage(sessionId: string, content: string): Promise<NaturalMessageResponse> {
  return apiRequest(`/natural/${sessionId}/message`, {
    method: 'POST',
    body: JSON.stringify({ content }),
  });
}

export async function analyzeNaturalConversation(sessionId: string): Promise<NaturalAnalyzeResponse> {
  return apiRequest(`/natural/${sessionId}/analyze`, { method: 'POST' });
}

export async function getNaturalHistory(sessionId: string) {
  return apiRequest(`/natural/${sessionId}/history`);
}

// Results endpoints
export async function getSessionResults(sessionId: string) {
  return apiRequest(`/results/session/${sessionId}`);
}

export async function getParticipantResults(participantId: string): Promise<ParticipantResultsResponse> {
  return apiRequest(`/results/participant/${participantId}`);
}

// Satisfaction Survey interfaces
export interface SatisfactionSubmit {
  overall_rating: number;       // 1-5 stars
  preferred_method: 'survey' | 'dose';
  dose_ease_of_use: number;     // 1-7 Likert
  would_recommend: number;      // 1-7 Likert
  open_feedback?: string;
  language?: string;
}

export interface SatisfactionResponse {
  id: string;
  participant_id: string;
  overall_rating: number;
  preferred_method: string;
  dose_ease_of_use: number;
  would_recommend: number;
  open_feedback?: string;
  language?: string;
  created_at: string;
}

export interface SatisfactionStatus {
  participant_id: string;
  has_completed: boolean;
  survey?: SatisfactionResponse;
}

// Satisfaction Survey endpoints
export async function submitSatisfactionSurvey(
  participantId: string,
  data: SatisfactionSubmit
): Promise<SatisfactionResponse> {
  return apiRequest(`/satisfaction/${participantId}/submit`, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function getSatisfactionStatus(participantId: string): Promise<SatisfactionStatus> {
  return apiRequest(`/satisfaction/${participantId}/status`);
}

export async function getSatisfactionSurvey(participantId: string): Promise<SatisfactionResponse> {
  return apiRequest(`/satisfaction/${participantId}`);
}
