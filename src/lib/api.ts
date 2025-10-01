export type BackendSearchFilters = {
  region?: string[];
  year?: number[];
  authority?: string[];
  specialty?: string[];
  urgency?: string[];
  tags?: string[];
};

export type BackendSearchRequest = {
  query?: string;
  size?: number;
  filters?: BackendSearchFilters;
};

export type BackendSearchHit = {
  id: string;
  score?: number;
  source: Record<string, any>;
  highlight?: Record<string, any> | null;
};

export type BackendSearchResponse = {
  total: number;
  hits: BackendSearchHit[];
  took_ms: number;
  medical_context?: Record<string, any>;
};

export type BackendGenerateRequest = {
  title: string;
  context_snippets: string[];
  instructions?: string | null;
  region?: string | null;
  year?: number | null;
  medical_context?: Record<string, any>;
};

export type BackendChecklistItem = {
  step: number;
  text: string;
  priority?: string;
  rationale?: string;
};

export type BackendGenerateResponse = {
  title: string;
  checklist: BackendChecklistItem[];
  citations: string[];
  safety_notes?: string[];
  context?: Record<string, any>;
};

// Conversation types
export type ConversationMessage = {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: string;
  protocol_data?: any;
};

export type ConversationSaveRequest = {
  id?: string;
  title?: string;
  messages: ConversationMessage[];
  protocol_data?: any;
  last_query?: string;
  tags?: string[];
  created_at?: string;
};

export type ConversationResponse = {
  success: boolean;
  conversation_id?: string;
  document_id?: string;
  error?: string;
  details?: string;
  message?: string;
};

export type ConversationListItem = {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
  last_query: string;
};

export type ConversationListResponse = {
  success: boolean;
  conversations: ConversationListItem[];
  total: number;
  error?: string;
  details?: string;
};

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

export async function searchProtocols(req: BackendSearchRequest): Promise<BackendSearchResponse> {
  const res = await fetch(`${API_BASE}/protocols/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Search failed: ${res.status} ${text}`);
  }
  return res.json();
}

export async function intelligentSearchProtocols(req: BackendSearchRequest): Promise<any> {
  const res = await fetch(`${API_BASE}/protocols/intelligent-search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Intelligent search failed: ${res.status} ${text}`);
  }
  return res.json();
}

export async function getMedicalSuggestions(query: string): Promise<any> {
  const res = await fetch(`${API_BASE}/protocols/medical-suggestions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query }),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Medical suggestions failed: ${res.status} ${text}`);
  }
  return res.json();
}

export async function generateProtocol(req: BackendGenerateRequest): Promise<BackendGenerateResponse> {
  const res = await fetch(`${API_BASE}/protocols/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Generate failed: ${res.status} ${text}`);
  }
  return res.json();
}

export async function generateIntelligentProtocol(query: string, size: number = 8): Promise<any> {
  const res = await fetch(`${API_BASE}/protocols/generate-intelligent?query=${encodeURIComponent(query)}&size=${size}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Intelligent protocol generation failed: ${res.status} ${text}`);
  }
  return res.json();
}

// Conversation API functions
export async function saveConversation(userId: string, conversation: ConversationSaveRequest): Promise<ConversationResponse> {
  const res = await fetch(`${API_BASE}/conversations/save?user_id=${encodeURIComponent(userId)}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(conversation),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Save conversation failed: ${res.status} ${text}`);
  }
  return res.json();
}

export async function getUserConversations(userId: string, limit: number = 20): Promise<ConversationListResponse> {
  const res = await fetch(`${API_BASE}/conversations/${encodeURIComponent(userId)}?limit=${limit}`);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Get conversations failed: ${res.status} ${text}`);
  }
  return res.json();
}

export async function getConversation(userId: string, conversationId: string): Promise<any> {
  const res = await fetch(`${API_BASE}/conversations/${encodeURIComponent(userId)}/${encodeURIComponent(conversationId)}`);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Get conversation failed: ${res.status} ${text}`);
  }
  return res.json();
}

export async function deleteConversation(userId: string, conversationId: string): Promise<{ success: boolean; message: string }> {
  const res = await fetch(`${API_BASE}/conversations/${encodeURIComponent(userId)}/${encodeURIComponent(conversationId)}`, {
    method: 'DELETE',
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Delete conversation failed: ${res.status} ${text}`);
  }
  return res.json();
}
