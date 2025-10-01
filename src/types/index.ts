export interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: string;
  protocolData?: ProtocolData;
}

export interface ProtocolStep {
  id: number;
  step: string;
  citations: number[];
  isNew?: boolean;
  changes?: string;
}

export interface Citation {
  id: number;
  source: string;
  organization: string;
  year: string;
  region: string;
  url?: string;
  excerpt: string;
}

export interface MedicalIntelligence {
  intent: string;
  entities: Array<{
    text: string;
    type: string;
    confidence: number;
  }>;
  medicalContext: Record<string, any>;
  suggestions: string[];
  safetyAlerts: string[];
  clinicalNotes: string[];
  relatedConcepts: string[];
  knowledge_graph?: {
    primary_conditions: Array<{
      name: string;
      severity: string;
      category: string;
    }>;
    symptoms: Array<{
      name: string;
      severity: string;
      category: string;
    }>;
    treatments: Array<{
      name: string;
      severity: string;
      category: string;
    }>;
    drugs: Array<{
      name: string;
      severity: string;
      category: string;
    }>;
    emergency_indicators: Array<{
      name: string;
      severity: string;
    }>;
    contraindications: Array<{
      name: string;
      type: string;
    }>;
    related_conditions: Array<{
      name: string;
      severity: string;
      category: string;
    }>;
    differential_diagnosis: Array<{
      name: string;
      score: number;
      severity: string;
    }>;
  };
}

export interface ClinicalDecisionSupport {
  riskAssessment?: {
    overall_risk: string;
    risk_factors: string[];
    recommendations: string[];
    contraindications: Array<{
      drug?: string;
      allergy?: string;
      reason: string;
      severity: string;
      recommendation: string;
    }>;
    dosage_adjustments: Array<{
      type: string;
      description: string;
      condition?: string;
      adjustments?: string[];
    }>;
  };
  patientRecommendations?: {
    patient_context: {
      age_group: string;
      risk_profile: string;
      special_considerations: string[];
    };
    protocol_modifications: string[];
    monitoring_requirements: string[];
    contraindication_warnings: string[];
  };
}

export interface ProtocolData {
  title: string;
  region: string;
  year: string;
  organization: string;
  steps: ProtocolStep[];
  citations: Citation[];
  lastUpdated?: string;
  medicalIntelligence?: MedicalIntelligence;
  clinicalDecisionSupport?: ClinicalDecisionSupport;
}

export interface RecentSearch {
  id: string;
  query: string;
  timestamp: string;
  region: string;
  year: string;
}

export interface SavedProtocol {
  id: string;
  title: string;
  organization: string;
  savedDate: string;
  region: string;
  year: string;
}

export type Region = 'Mumbai' | 'Delhi' | 'Bangalore' | 'Chennai' | 'Global' | 'WHO' | 'India' | 'US' | 'UK';
export type Year = '2024' | '2023' | '2022' | '2021' | '2020';

export const regions: Region[] = ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Global', 'WHO', 'India', 'US', 'UK'];
export const years: Year[] = ['2024', '2023', '2022', '2021', '2020'];
