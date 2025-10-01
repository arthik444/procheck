"""
Enhanced Search Service for ProCheck
Integrates medical NLP with Elasticsearch for intelligent medical search
"""

from typing import Dict, List, Any, Optional
import json
from services.elasticsearch_service import get_client, search_with_filters
from services.medical_nlp_service import medical_nlp_service, MedicalIntent
from services.medical_knowledge_graph import medical_knowledge_graph
from config.settings import settings

class EnhancedSearchService:
    def __init__(self):
        self.es_client = get_client()
        self.medical_nlp = medical_nlp_service
        self.knowledge_graph = medical_knowledge_graph

    def intelligent_search(self, query: str, filters: Optional[Dict[str, Any]] = None, size: int = 10) -> Dict[str, Any]:
        """Perform intelligent medical search with NLP analysis"""
        
        # Analyze the query
        analysis = self.medical_nlp.analyze_query(query)
        
        # Build enhanced search request
        search_request = {
            "query": analysis.enhanced_query,
            "size": size,
            "filters": filters or {},
            "medical_context": {
                "intent": analysis.intent.value,
                "entities": [
                    {
                        "text": entity.text,
                        "type": entity.entity_type,
                        "confidence": entity.confidence
                    }
                    for entity in analysis.entities
                ],
                "context": analysis.medical_context,
                "suggestions": analysis.suggestions
            }
        }
        
        # Perform search with medical context
        es_response = search_with_filters(search_request)
        
        if "error" in es_response:
            return es_response
        
        # Enhance results with medical intelligence
        enhanced_results = self._enhance_search_results(es_response, analysis)
        
        return enhanced_results

    def _enhance_search_results(self, es_response: Dict[str, Any], analysis) -> Dict[str, Any]:
        """Enhance search results with medical context and intelligence"""
        
        hits = es_response.get("hits", {}).get("hits", [])
        enhanced_hits = []
        
        for hit in hits:
            enhanced_hit = self._enhance_single_result(hit, analysis)
            enhanced_hits.append(enhanced_hit)
        
        # Get medical context from knowledge graph
        medical_context = self.knowledge_graph.get_medical_context([
            {"text": entity.text, "type": entity.entity_type}
            for entity in analysis.entities
        ])
        
        # Add medical intelligence metadata
        medical_intelligence = {
            "query_analysis": {
                "original_query": analysis.original_query,
                "intent": analysis.intent.value,
                "entities": [
                    {
                        "text": entity.text,
                        "type": entity.entity_type,
                        "confidence": entity.confidence
                    }
                    for entity in analysis.entities
                ],
                "enhanced_query": analysis.enhanced_query,
                "medical_context": analysis.medical_context
            },
            "search_suggestions": analysis.suggestions,
            "related_concepts": self._get_related_concepts(analysis),
            "safety_alerts": self._get_safety_alerts(analysis),
            "clinical_notes": self._get_clinical_notes(analysis),
            "knowledge_graph": {
                "primary_conditions": [{"name": c.name, "severity": c.severity, "category": c.category} for c in medical_context["primary_conditions"]],
                "symptoms": [{"name": c.name, "severity": c.severity, "category": c.category} for c in medical_context["symptoms"]],
                "treatments": [{"name": c.name, "severity": c.severity, "category": c.category} for c in medical_context["treatments"]],
                "drugs": [{"name": c.name, "severity": c.severity, "category": c.category} for c in medical_context["drugs"]],
                "emergency_indicators": [{"name": c.name, "severity": c.severity} for c in medical_context["emergency_indicators"]],
                "contraindications": [{"name": c.name, "type": c.concept_type} for c in medical_context["contraindications"]],
                "related_conditions": [{"name": c.name, "severity": c.severity, "category": c.category} for c in medical_context["related_conditions"]],
                "differential_diagnosis": [{"name": c.name, "score": score, "severity": c.severity} for c, score in medical_context["differential_diagnosis"][:3]]
            }
        }
        
        return {
            **es_response,
            "hits": {
                **es_response.get("hits", {}),
                "hits": enhanced_hits
            },
            "medical_intelligence": medical_intelligence
        }

    def _enhance_single_result(self, hit: Dict[str, Any], analysis) -> Dict[str, Any]:
        """Enhance a single search result with medical context"""
        
        source = hit.get("_source", {})
        score = hit.get("_score", 0)
        
        # Calculate medical relevance score
        medical_relevance = self._calculate_medical_relevance(source, analysis)
        
        # Add medical annotations
        medical_annotations = {
            "relevance_score": medical_relevance,
            "clinical_importance": self._assess_clinical_importance(source, analysis),
            "safety_level": self._assess_safety_level(source, analysis),
            "urgency_indicator": self._assess_urgency(source, analysis),
            "related_conditions": self._get_related_conditions(source, analysis),
            "contraindications": self._get_contraindications(source, analysis)
        }
        
        return {
            **hit,
            "medical_annotations": medical_annotations
        }

    def _calculate_medical_relevance(self, source: Dict[str, Any], analysis) -> float:
        """Calculate medical relevance score based on query analysis"""
        base_score = 0.5
        
        # Boost score based on intent matching
        if analysis.intent == MedicalIntent.EMERGENCY:
            if any(emergency_word in source.get("content", "").lower() for emergency_word in ["emergency", "urgent", "critical", "immediate"]):
                base_score += 0.3
        
        # Boost score based on entity matches
        for entity in analysis.entities:
            if entity.text.lower() in source.get("content", "").lower():
                base_score += 0.1
        
        # Boost score based on medical context
        if analysis.medical_context.get("urgency") == "high":
            base_score += 0.2
        
        return min(base_score, 1.0)

    def _assess_clinical_importance(self, source: Dict[str, Any], analysis) -> str:
        """Assess clinical importance of the result"""
        content = source.get("content", "").lower()
        
        if any(word in content for word in ["emergency", "critical", "life-threatening", "immediate"]):
            return "critical"
        elif any(word in content for word in ["urgent", "important", "priority", "serious"]):
            return "high"
        elif any(word in content for word in ["routine", "standard", "common"]):
            return "medium"
        else:
            return "low"

    def _assess_safety_level(self, source: Dict[str, Any], analysis) -> str:
        """Assess safety level of the result"""
        content = source.get("content", "").lower()
        
        if any(word in content for word in ["contraindication", "warning", "danger", "risk", "adverse"]):
            return "high-risk"
        elif any(word in content for word in ["caution", "careful", "monitor", "supervision"]):
            return "moderate-risk"
        else:
            return "low-risk"

    def _assess_urgency(self, source: Dict[str, Any], analysis) -> str:
        """Assess urgency level of the result"""
        content = source.get("content", "").lower()
        
        if any(word in content for word in ["immediate", "stat", "emergency", "critical"]):
            return "immediate"
        elif any(word in content for word in ["urgent", "asap", "priority"]):
            return "urgent"
        elif any(word in content for word in ["routine", "scheduled", "planned"]):
            return "routine"
        else:
            return "standard"

    def _get_related_conditions(self, source: Dict[str, Any], analysis) -> List[str]:
        """Get related medical conditions"""
        # This would typically come from a medical knowledge graph
        # For now, return some common related conditions
        content = source.get("content", "").lower()
        
        related = []
        if "cardiac" in content or "heart" in content:
            related.extend(["myocardial infarction", "cardiac arrest", "heart failure"])
        if "respiratory" in content or "breathing" in content:
            related.extend(["pneumonia", "asthma", "respiratory failure"])
        if "diabetes" in content:
            related.extend(["diabetic ketoacidosis", "hypoglycemia", "diabetic complications"])
        
        return related[:3]

    def _get_contraindications(self, source: Dict[str, Any], analysis) -> List[str]:
        """Get contraindications and warnings"""
        content = source.get("content", "").lower()
        
        contraindications = []
        if "penicillin" in content and "allergy" in analysis.original_query.lower():
            contraindications.append("Penicillin allergy contraindication")
        if "pregnancy" in content and analysis.medical_context.get("gender") == "female":
            contraindications.append("Pregnancy considerations")
        if "pediatric" in content and analysis.medical_context.get("age", 0) > 18:
            contraindications.append("Adult patient - pediatric protocol")
        
        return contraindications

    def _get_related_concepts(self, analysis) -> List[str]:
        """Get related medical concepts based on query analysis"""
        related = []
        
        if analysis.intent == MedicalIntent.SYMPTOM_BASED:
            related.extend(["differential diagnosis", "diagnostic tests", "treatment protocols"])
        elif analysis.intent == MedicalIntent.PROCEDURE_BASED:
            related.extend(["equipment requirements", "safety precautions", "post-procedure care"])
        elif analysis.intent == MedicalIntent.EMERGENCY:
            related.extend(["emergency response", "critical care", "resuscitation protocols"])
        
        return related

    def _get_safety_alerts(self, analysis) -> List[str]:
        """Get safety alerts based on query analysis"""
        alerts = []
        
        if analysis.intent == MedicalIntent.EMERGENCY:
            alerts.append("Emergency protocol - ensure immediate medical attention")
        
        if analysis.medical_context.get("urgency") == "high":
            alerts.append("High urgency case - prioritize immediate care")
        
        if any(entity.entity_type == "drug" for entity in analysis.entities):
            alerts.append("Drug-related query - check for allergies and interactions")
        
        return alerts

    def _get_clinical_notes(self, analysis) -> List[str]:
        """Get clinical notes and recommendations"""
        notes = []
        
        if analysis.medical_context.get("age", 0) < 18:
            notes.append("Pediatric patient - consider age-appropriate protocols")
        elif analysis.medical_context.get("age", 0) > 65:
            notes.append("Geriatric patient - consider age-related considerations")
        
        if analysis.medical_context.get("setting") == "hospital":
            notes.append("Hospital setting - full resources available")
        elif analysis.medical_context.get("setting") == "clinic":
            notes.append("Clinic setting - limited resources, consider referral")
        
        return notes

    def get_medical_suggestions(self, query: str) -> Dict[str, Any]:
        """Get medical suggestions based on query analysis"""
        analysis = self.medical_nlp.analyze_query(query)
        
        return {
            "query_analysis": {
                "intent": analysis.intent.value,
                "entities": [{"text": e.text, "type": e.entity_type} for e in analysis.entities],
                "medical_context": analysis.medical_context
            },
            "suggestions": analysis.suggestions,
            "enhanced_query": analysis.enhanced_query,
            "related_concepts": self._get_related_concepts(analysis)
        }

# Global instance
enhanced_search_service = EnhancedSearchService()
