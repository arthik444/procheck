"""
Medical NLP Service for ProCheck
Provides medical entity recognition, intent classification, and query enhancement
"""

from typing import Dict, List, Any, Optional, Tuple
import re
import json
from dataclasses import dataclass
from enum import Enum

class MedicalIntent(Enum):
    SYMPTOM_BASED = "symptom_based"
    PROCEDURE_BASED = "procedure_based"
    DRUG_BASED = "drug_based"
    CONDITION_BASED = "condition_based"
    EMERGENCY = "emergency"
    GENERAL = "general"

@dataclass
class MedicalEntity:
    text: str
    entity_type: str
    confidence: float
    start_pos: int
    end_pos: int

@dataclass
class QueryAnalysis:
    original_query: str
    intent: MedicalIntent
    entities: List[MedicalEntity]
    enhanced_query: str
    suggestions: List[str]
    medical_context: Dict[str, Any]

class MedicalNLPService:
    def __init__(self):
        # Medical entity patterns
        self.symptom_patterns = [
            r'\b(chest pain|shortness of breath|difficulty breathing|wheezing|coughing|fever|headache|nausea|vomiting|dizziness|fatigue|weakness|pain|swelling|rash|bleeding|confusion|seizure|unconsciousness)\b',
            r'\b(acute|chronic|severe|mild|moderate|sudden|gradual)\s+(pain|symptoms?|condition)\b',
            r'\b(cannot|unable to|difficulty|trouble)\s+(breathe|walk|speak|swallow|see|hear)\b'
        ]
        
        self.condition_patterns = [
            r'\b(heart attack|myocardial infarction|stroke|cerebrovascular accident|pneumonia|asthma|diabetes|hypertension|sepsis|shock|cardiac arrest|respiratory failure|kidney failure|liver failure)\b',
            r'\b(covid-19|coronavirus|influenza|flu|tuberculosis|tb|hepatitis|hiv|aids|cancer|tumor|malignancy)\b',
            r'\b(emergency|critical|life-threatening|urgent|acute|chronic)\s+(condition|illness|disease)\b'
        ]
        
        self.procedure_patterns = [
            r'\b(cpr|cardiopulmonary resuscitation|intubation|ventilation|defibrillation|surgery|operation|procedure|treatment|therapy|medication|injection|iv|intravenous)\b',
            r'\b(how to|steps to|procedure for|treatment for|management of)\b',
            r'\b(emergency|urgent|immediate)\s+(treatment|care|intervention|response)\b'
        ]
        
        self.drug_patterns = [
            r'\b(aspirin|morphine|epinephrine|adrenaline|insulin|penicillin|amoxicillin|paracetamol|acetaminophen|ibuprofen|morphine|fentanyl|naloxone|atropine|lidocaine|epinephrine)\b',
            r'\b(medication|drug|medicine|prescription|dose|dosage|mg|mcg|ml|tablet|capsule|injection|iv|oral|topical)\b',
            r'\b(contraindication|allergy|adverse effect|side effect|interaction)\b'
        ]
        
        self.emergency_patterns = [
            r'\b(emergency|urgent|critical|life-threatening|immediate|stat|asap|emergency room|er|trauma|cardiac arrest|respiratory arrest|sepsis|shock|stroke|heart attack)\b',
            r'\b(911|emergency services|ambulance|paramedic|first aid|emergency response)\b'
        ]
        
        # Medical synonyms and expansions
        self.medical_synonyms = {
            'chest pain': ['chest discomfort', 'chest pressure', 'angina', 'cardiac pain'],
            'heart attack': ['myocardial infarction', 'mi', 'acute coronary syndrome', 'acs'],
            'stroke': ['cerebrovascular accident', 'cva', 'brain attack'],
            'cpr': ['cardiopulmonary resuscitation', 'chest compressions', 'rescue breathing'],
            'breathing': ['respiration', 'ventilation', 'respiratory'],
            'blood pressure': ['bp', 'hypertension', 'hypotension'],
            'diabetes': ['diabetes mellitus', 'dm', 'high blood sugar'],
            'covid': ['coronavirus', 'sars-cov-2', 'covid-19'],
            'flu': ['influenza', 'seasonal flu'],
            'tb': ['tuberculosis', 'pulmonary tuberculosis'],
            'hiv': ['human immunodeficiency virus', 'aids'],
            'cancer': ['malignancy', 'tumor', 'neoplasm'],
            'surgery': ['operation', 'procedure', 'surgical intervention'],
            'medication': ['drug', 'medicine', 'pharmaceutical'],
            'injection': ['shot', 'injection', 'parenteral administration'],
            'iv': ['intravenous', 'intravenous therapy', 'iv therapy']
        }
        
        # Medical context keywords
        self.context_keywords = {
            'age': ['age', 'years old', 'year-old', 'pediatric', 'adult', 'elderly', 'geriatric'],
            'gender': ['male', 'female', 'man', 'woman', 'boy', 'girl'],
            'urgency': ['emergency', 'urgent', 'critical', 'immediate', 'stat', 'asap'],
            'setting': ['hospital', 'clinic', 'emergency room', 'er', 'icu', 'outpatient', 'home'],
            'severity': ['mild', 'moderate', 'severe', 'critical', 'life-threatening']
        }

    def analyze_query(self, query: str) -> QueryAnalysis:
        """Analyze a medical query and extract entities, intent, and context"""
        query_lower = query.lower().strip()
        
        # Extract medical entities
        entities = self._extract_entities(query)
        
        # Classify intent
        intent = self._classify_intent(query_lower, entities)
        
        # Enhance query with synonyms and expansions
        enhanced_query = self._enhance_query(query_lower)
        
        # Generate suggestions
        suggestions = self._generate_suggestions(query_lower, entities, intent)
        
        # Extract medical context
        medical_context = self._extract_medical_context(query_lower)
        
        return QueryAnalysis(
            original_query=query,
            intent=intent,
            entities=entities,
            enhanced_query=enhanced_query,
            suggestions=suggestions,
            medical_context=medical_context
        )

    def _extract_entities(self, query: str) -> List[MedicalEntity]:
        """Extract medical entities from query"""
        entities = []
        query_lower = query.lower()
        
        # Extract symptoms
        for pattern in self.symptom_patterns:
            for match in re.finditer(pattern, query_lower):
                entities.append(MedicalEntity(
                    text=match.group(),
                    entity_type="symptom",
                    confidence=0.8,
                    start_pos=match.start(),
                    end_pos=match.end()
                ))
        
        # Extract conditions
        for pattern in self.condition_patterns:
            for match in re.finditer(pattern, query_lower):
                entities.append(MedicalEntity(
                    text=match.group(),
                    entity_type="condition",
                    confidence=0.9,
                    start_pos=match.start(),
                    end_pos=match.end()
                ))
        
        # Extract procedures
        for pattern in self.procedure_patterns:
            for match in re.finditer(pattern, query_lower):
                entities.append(MedicalEntity(
                    text=match.group(),
                    entity_type="procedure",
                    confidence=0.8,
                    start_pos=match.start(),
                    end_pos=match.end()
                ))
        
        # Extract drugs
        for pattern in self.drug_patterns:
            for match in re.finditer(pattern, query_lower):
                entities.append(MedicalEntity(
                    text=match.group(),
                    entity_type="drug",
                    confidence=0.8,
                    start_pos=match.start(),
                    end_pos=match.end()
                ))
        
        return entities

    def _classify_intent(self, query: str, entities: List[MedicalEntity]) -> MedicalIntent:
        """Classify the medical intent of the query"""
        # Check for emergency keywords
        if any(re.search(pattern, query) for pattern in self.emergency_patterns):
            return MedicalIntent.EMERGENCY
        
        # Check entity types to determine intent
        entity_types = [entity.entity_type for entity in entities]
        
        if 'symptom' in entity_types:
            return MedicalIntent.SYMPTOM_BASED
        elif 'procedure' in entity_types:
            return MedicalIntent.PROCEDURE_BASED
        elif 'drug' in entity_types:
            return MedicalIntent.DRUG_BASED
        elif 'condition' in entity_types:
            return MedicalIntent.CONDITION_BASED
        else:
            return MedicalIntent.GENERAL

    def _enhance_query(self, query: str) -> str:
        """Enhance query with medical synonyms and expansions"""
        enhanced = query
        
        # Replace with synonyms
        for term, synonyms in self.medical_synonyms.items():
            if term in enhanced:
                # Add synonyms to the query
                enhanced += " " + " ".join(synonyms[:2])  # Add top 2 synonyms
        
        return enhanced

    def _generate_suggestions(self, query: str, entities: List[MedicalEntity], intent: MedicalIntent) -> List[str]:
        """Generate related medical suggestions"""
        suggestions = []
        
        if intent == MedicalIntent.SYMPTOM_BASED:
            suggestions.extend([
                "Related conditions and differential diagnosis",
                "Emergency protocols for severe symptoms",
                "Diagnostic procedures and tests",
                "Treatment protocols and medications"
            ])
        elif intent == MedicalIntent.PROCEDURE_BASED:
            suggestions.extend([
                "Step-by-step procedure guide",
                "Required equipment and medications",
                "Contraindications and safety precautions",
                "Post-procedure care and monitoring"
            ])
        elif intent == MedicalIntent.EMERGENCY:
            suggestions.extend([
                "Immediate emergency response protocols",
                "Critical care procedures",
                "Emergency medications and dosages",
                "Trauma and resuscitation protocols"
            ])
        
        return suggestions[:4]  # Limit to 4 suggestions

    def _extract_medical_context(self, query: str) -> Dict[str, Any]:
        """Extract medical context from query"""
        context = {}
        
        # Extract age information
        age_match = re.search(r'(\d+)\s*(years? old|year-old)', query)
        if age_match:
            context['age'] = int(age_match.group(1))
        
        # Extract gender
        if any(gender in query for gender in ['male', 'man', 'boy']):
            context['gender'] = 'male'
        elif any(gender in query for gender in ['female', 'woman', 'girl']):
            context['gender'] = 'female'
        
        # Extract urgency
        if any(urgent in query for urgent in ['emergency', 'urgent', 'critical', 'immediate']):
            context['urgency'] = 'high'
        elif any(mild in query for mild in ['mild', 'routine', 'non-urgent']):
            context['urgency'] = 'low'
        else:
            context['urgency'] = 'medium'
        
        # Extract setting
        if any(setting in query for setting in ['hospital', 'emergency room', 'er', 'icu']):
            context['setting'] = 'hospital'
        elif any(setting in query for setting in ['clinic', 'outpatient', 'office']):
            context['setting'] = 'clinic'
        else:
            context['setting'] = 'general'
        
        return context

    def get_medical_synonyms(self, term: str) -> List[str]:
        """Get medical synonyms for a term"""
        return self.medical_synonyms.get(term.lower(), [])

    def expand_medical_terms(self, query: str) -> str:
        """Expand medical terms in query for better search"""
        expanded = query
        for term, synonyms in self.medical_synonyms.items():
            if term in expanded.lower():
                expanded += " " + " ".join(synonyms[:3])
        return expanded

# Global instance
medical_nlp_service = MedicalNLPService()


