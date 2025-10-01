"""
Medical Knowledge Graph Service for ProCheck
Builds relationships between medical concepts for intelligent search and recommendations
"""

from typing import Dict, List, Any, Optional, Set, Tuple
import json
from dataclasses import dataclass
from enum import Enum

class RelationshipType(Enum):
    SYMPTOM_TO_CONDITION = "symptom_to_condition"
    CONDITION_TO_TREATMENT = "condition_to_treatment"
    DRUG_TO_CONDITION = "drug_to_condition"
    DRUG_TO_SIDE_EFFECT = "drug_to_side_effect"
    PROCEDURE_TO_CONDITION = "procedure_to_condition"
    CONTRAINDICATION = "contraindication"
    RELATED_CONDITION = "related_condition"
    EMERGENCY_PROTOCOL = "emergency_protocol"

@dataclass
class MedicalConcept:
    id: str
    name: str
    concept_type: str
    description: Optional[str] = None
    aliases: Optional[List[str]] = None
    severity: Optional[str] = None  # low, medium, high, critical
    category: Optional[str] = None  # cardiovascular, respiratory, neurological, etc.

@dataclass
class MedicalRelationship:
    source: str
    target: str
    relationship_type: RelationshipType
    strength: float  # 0.0 to 1.0
    evidence_level: str  # high, medium, low
    description: Optional[str] = None

class MedicalKnowledgeGraph:
    def __init__(self):
        self.concepts: Dict[str, MedicalConcept] = {}
        self.relationships: List[MedicalRelationship] = []
        self._build_knowledge_base()

    def _build_knowledge_base(self):
        """Build the medical knowledge base with concepts and relationships"""
        
        # Define medical concepts
        concepts_data = [
            # Cardiovascular
            {"id": "chest_pain", "name": "chest pain", "type": "symptom", "severity": "high", "category": "cardiovascular", "aliases": ["chest discomfort", "chest pressure", "angina"]},
            {"id": "shortness_of_breath", "name": "shortness of breath", "type": "symptom", "severity": "high", "category": "respiratory", "aliases": ["dyspnea", "difficulty breathing", "breathlessness"]},
            {"id": "heart_attack", "name": "heart attack", "type": "condition", "severity": "critical", "category": "cardiovascular", "aliases": ["myocardial infarction", "MI", "acute coronary syndrome"]},
            {"id": "cardiac_arrest", "name": "cardiac arrest", "type": "condition", "severity": "critical", "category": "cardiovascular", "aliases": ["sudden cardiac arrest", "SCA"]},
            {"id": "hypertension", "name": "hypertension", "type": "condition", "severity": "medium", "category": "cardiovascular", "aliases": ["high blood pressure", "HTN"]},
            
            # Respiratory
            {"id": "asthma", "name": "asthma", "type": "condition", "severity": "medium", "category": "respiratory", "aliases": ["bronchial asthma", "reactive airway disease"]},
            {"id": "pneumonia", "name": "pneumonia", "type": "condition", "severity": "high", "category": "respiratory", "aliases": ["lung infection", "pulmonary infection"]},
            {"id": "respiratory_failure", "name": "respiratory failure", "type": "condition", "severity": "critical", "category": "respiratory", "aliases": ["respiratory arrest", "breathing failure"]},
            
            # Emergency/Procedures
            {"id": "cpr", "name": "CPR", "type": "procedure", "severity": "critical", "category": "emergency", "aliases": ["cardiopulmonary resuscitation", "chest compressions"]},
            {"id": "defibrillation", "name": "defibrillation", "type": "procedure", "severity": "critical", "category": "emergency", "aliases": ["defibrillator", "shock therapy"]},
            {"id": "intubation", "name": "intubation", "type": "procedure", "severity": "high", "category": "respiratory", "aliases": ["endotracheal intubation", "ET tube"]},
            
            # Drugs
            {"id": "aspirin", "name": "aspirin", "type": "drug", "severity": "medium", "category": "cardiovascular", "aliases": ["acetylsalicylic acid", "ASA"]},
            {"id": "epinephrine", "name": "epinephrine", "type": "drug", "severity": "high", "category": "emergency", "aliases": ["adrenaline", "EpiPen"]},
            {"id": "morphine", "name": "morphine", "type": "drug", "severity": "high", "category": "pain_management", "aliases": ["morphine sulfate", "opioid"]},
            {"id": "penicillin", "name": "penicillin", "type": "drug", "severity": "medium", "category": "antibiotic", "aliases": ["penicillin G", "benzylpenicillin"]},
            
            # General
            {"id": "fever", "name": "fever", "type": "symptom", "severity": "medium", "category": "general", "aliases": ["pyrexia", "elevated temperature"]},
            {"id": "diabetes", "name": "diabetes", "type": "condition", "severity": "high", "category": "endocrine", "aliases": ["diabetes mellitus", "DM", "high blood sugar"]},
            {"id": "sepsis", "name": "sepsis", "type": "condition", "severity": "critical", "category": "infectious", "aliases": ["blood infection", "systemic infection"]},
            {"id": "stroke", "name": "stroke", "type": "condition", "severity": "critical", "category": "neurological", "aliases": ["cerebrovascular accident", "CVA", "brain attack"]},
        ]
        
        # Create concept objects
        for concept_data in concepts_data:
            concept = MedicalConcept(
                id=concept_data["id"],
                name=concept_data["name"],
                concept_type=concept_data["type"],
                description=None,
                aliases=concept_data.get("aliases", []),
                severity=concept_data.get("severity"),
                category=concept_data.get("category")
            )
            self.concepts[concept.id] = concept
        
        # Define relationships
        relationships_data = [
            # Symptom to Condition relationships
            {"source": "chest_pain", "target": "heart_attack", "type": "symptom_to_condition", "strength": 0.9, "evidence": "high"},
            {"source": "chest_pain", "target": "asthma", "type": "symptom_to_condition", "strength": 0.6, "evidence": "medium"},
            {"source": "shortness_of_breath", "target": "heart_attack", "type": "symptom_to_condition", "strength": 0.8, "evidence": "high"},
            {"source": "shortness_of_breath", "target": "asthma", "type": "symptom_to_condition", "strength": 0.9, "evidence": "high"},
            {"source": "shortness_of_breath", "target": "pneumonia", "type": "symptom_to_condition", "strength": 0.8, "evidence": "high"},
            {"source": "fever", "target": "pneumonia", "type": "symptom_to_condition", "strength": 0.7, "evidence": "medium"},
            {"source": "fever", "target": "sepsis", "type": "symptom_to_condition", "strength": 0.8, "evidence": "high"},
            
            # Condition to Treatment relationships
            {"source": "heart_attack", "target": "aspirin", "type": "condition_to_treatment", "strength": 0.9, "evidence": "high"},
            {"source": "cardiac_arrest", "target": "cpr", "type": "condition_to_treatment", "strength": 1.0, "evidence": "high"},
            {"source": "cardiac_arrest", "target": "defibrillation", "type": "condition_to_treatment", "strength": 0.9, "evidence": "high"},
            {"source": "asthma", "target": "epinephrine", "type": "condition_to_treatment", "strength": 0.8, "evidence": "high"},
            {"source": "respiratory_failure", "target": "intubation", "type": "condition_to_treatment", "strength": 0.9, "evidence": "high"},
            
            # Drug relationships
            {"source": "aspirin", "target": "heart_attack", "type": "drug_to_condition", "strength": 0.9, "evidence": "high"},
            {"source": "epinephrine", "target": "cardiac_arrest", "type": "drug_to_condition", "strength": 0.8, "evidence": "high"},
            {"source": "morphine", "target": "chest_pain", "type": "drug_to_condition", "strength": 0.7, "evidence": "medium"},
            
            # Contraindications
            {"source": "penicillin", "target": "penicillin_allergy", "type": "contraindication", "strength": 1.0, "evidence": "high"},
            {"source": "aspirin", "target": "bleeding_disorder", "type": "contraindication", "strength": 0.8, "evidence": "high"},
            
            # Related conditions
            {"source": "heart_attack", "target": "cardiac_arrest", "type": "related_condition", "strength": 0.7, "evidence": "medium"},
            {"source": "hypertension", "target": "heart_attack", "type": "related_condition", "strength": 0.6, "evidence": "medium"},
            {"source": "diabetes", "target": "heart_attack", "type": "related_condition", "strength": 0.5, "evidence": "medium"},
            
            # Emergency protocols
            {"source": "cardiac_arrest", "target": "emergency_protocol", "type": "emergency_protocol", "strength": 1.0, "evidence": "high"},
            {"source": "stroke", "target": "emergency_protocol", "type": "emergency_protocol", "strength": 1.0, "evidence": "high"},
            {"source": "sepsis", "target": "emergency_protocol", "type": "emergency_protocol", "strength": 1.0, "evidence": "high"},
        ]
        
        # Create relationship objects
        for rel_data in relationships_data:
            relationship = MedicalRelationship(
                source=rel_data["source"],
                target=rel_data["target"],
                relationship_type=RelationshipType(rel_data["type"]),
                strength=rel_data["strength"],
                evidence_level=rel_data["evidence"]
            )
            self.relationships.append(relationship)

    def find_concept(self, name: str) -> Optional[MedicalConcept]:
        """Find a medical concept by name or alias"""
        name_lower = name.lower().strip()
        
        # Direct name match
        for concept in self.concepts.values():
            if concept.name.lower() == name_lower:
                return concept
            # Check aliases
            if concept.aliases:
                for alias in concept.aliases:
                    if alias.lower() == name_lower:
                        return concept
        
        return None

    def get_related_concepts(self, concept_id: str, relationship_types: Optional[List[RelationshipType]] = None, min_strength: float = 0.5) -> List[Tuple[MedicalConcept, MedicalRelationship]]:
        """Get concepts related to the given concept"""
        related = []
        
        for relationship in self.relationships:
            if relationship.strength < min_strength:
                continue
            
            if relationship_types and relationship.relationship_type not in relationship_types:
                continue
            
            if relationship.source == concept_id:
                target_concept = self.concepts.get(relationship.target)
                if target_concept:
                    related.append((target_concept, relationship))
            elif relationship.target == concept_id:
                source_concept = self.concepts.get(relationship.source)
                if source_concept:
                    related.append((source_concept, relationship))
        
        # Sort by relationship strength
        related.sort(key=lambda x: x[1].strength, reverse=True)
        return related

    def get_differential_diagnosis(self, symptoms: List[str]) -> List[Tuple[MedicalConcept, float]]:
        """Get differential diagnosis based on symptoms"""
        diagnosis_scores = {}
        
        for symptom in symptoms:
            concept = self.find_concept(symptom)
            if not concept:
                continue
            
            # Find conditions related to this symptom
            related = self.get_related_concepts(
                concept.id, 
                [RelationshipType.SYMPTOM_TO_CONDITION]
            )
            
            for condition, relationship in related:
                if condition.concept_type == "condition":
                    score = relationship.strength
                    if condition.id in diagnosis_scores:
                        diagnosis_scores[condition.id] += score
                    else:
                        diagnosis_scores[condition.id] = score
        
        # Convert to list and sort by score
        diagnoses = []
        for condition_id, score in diagnosis_scores.items():
            condition = self.concepts.get(condition_id)
            if condition:
                diagnoses.append((condition, score))
        
        diagnoses.sort(key=lambda x: x[1], reverse=True)
        return diagnoses

    def get_treatment_recommendations(self, condition: str) -> List[Tuple[MedicalConcept, MedicalRelationship]]:
        """Get treatment recommendations for a condition"""
        concept = self.find_concept(condition)
        if not concept:
            return []
        
        return self.get_related_concepts(
            concept.id,
            [RelationshipType.CONDITION_TO_TREATMENT, RelationshipType.DRUG_TO_CONDITION]
        )

    def get_contraindications(self, drug: str) -> List[Tuple[MedicalConcept, MedicalRelationship]]:
        """Get contraindications for a drug"""
        concept = self.find_concept(drug)
        if not concept:
            return []
        
        return self.get_related_concepts(
            concept.id,
            [RelationshipType.CONTRAINDICATION]
        )

    def is_emergency(self, condition: str) -> bool:
        """Check if a condition requires emergency protocols"""
        concept = self.find_concept(condition)
        if not concept:
            return False
        
        # Check if it's marked as critical severity
        if concept.severity == "critical":
            return True
        
        # Check if it has emergency protocol relationships
        related = self.get_related_concepts(
            concept.id,
            [RelationshipType.EMERGENCY_PROTOCOL]
        )
        
        return len(related) > 0

    def get_medical_context(self, query_entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get medical context based on query entities"""
        context = {
            "primary_conditions": [],
            "symptoms": [],
            "treatments": [],
            "drugs": [],
            "emergency_indicators": [],
            "contraindications": [],
            "related_conditions": [],
            "differential_diagnosis": []
        }
        
        entity_texts = [entity.get("text", "").lower() for entity in query_entities]
        
        for entity_text in entity_texts:
            concept = self.find_concept(entity_text)
            if not concept:
                continue
            
            # Categorize the concept
            if concept.concept_type == "symptom":
                context["symptoms"].append(concept)
            elif concept.concept_type == "condition":
                context["primary_conditions"].append(concept)
                if self.is_emergency(concept.id):
                    context["emergency_indicators"].append(concept)
            elif concept.concept_type == "drug":
                context["drugs"].append(concept)
                # Check for contraindications
                contraindications = self.get_contraindications(concept.id)
                context["contraindications"].extend([c[0] for c in contraindications])
            elif concept.concept_type == "procedure":
                context["treatments"].append(concept)
        
        # Get differential diagnosis if symptoms are present
        if context["symptoms"]:
            symptoms = [s.name for s in context["symptoms"]]
            differential = self.get_differential_diagnosis(symptoms)
            context["differential_diagnosis"] = differential[:5]  # Top 5
        
        # Get related conditions
        for condition in context["primary_conditions"]:
            related = self.get_related_concepts(
                condition.id,
                [RelationshipType.RELATED_CONDITION]
            )
            context["related_conditions"].extend([c[0] for c in related[:3]])
        
        return context

# Global instance
medical_knowledge_graph = MedicalKnowledgeGraph()


