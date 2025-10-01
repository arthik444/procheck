"""
Intelligent Protocol Generation Service
Combines medical NLP, Elasticsearch search, and LLM generation for comprehensive medical protocols
"""

from typing import Dict, List, Any, Optional
import json
from services.enhanced_search_service import enhanced_search_service
from services.gemini_service import summarize_checklist
from services.medical_nlp_service import medical_nlp_service

class IntelligentProtocolService:
    def __init__(self):
        self.enhanced_search = enhanced_search_service
        self.medical_nlp = medical_nlp_service

    def generate_intelligent_protocol(self, query: str, size: int = 8) -> Dict[str, Any]:
        """
        Generate a comprehensive medical protocol using intelligent search and LLM generation
        """
        
        # Step 1: Perform intelligent search with medical NLP
        search_result = self.enhanced_search.intelligent_search(
            query=query,
            filters=None,
            size=size
        )
        
        if "error" in search_result:
            return {"error": "search_error", "details": search_result.get("error")}
        
        # Step 2: Extract medical intelligence
        medical_intelligence = search_result.get("medical_intelligence", {})
        query_analysis = medical_intelligence.get("query_analysis", {})
        
        # Step 3: Prepare context for LLM
        search_hits = search_result.get("hits", {}).get("hits", [])
        context_snippets = self._prepare_context_snippets(query, search_hits)
        
        # Step 4: Create enhanced prompt with medical intelligence
        enhanced_instructions = self._create_enhanced_instructions(
            query, query_analysis, medical_intelligence
        )
        
        # Step 5: Generate protocol using Gemini with medical context
        protocol_result = summarize_checklist(
            title=query,
            context_snippets=context_snippets,
            instructions=enhanced_instructions,
            region=None,
            year=None
        )
        
        if "error" in protocol_result:
            return {"error": "protocol_generation_error", "details": protocol_result.get("error")}
        
        # Step 6: Combine results with medical intelligence
        combined_result = self._combine_results(
            query, search_result, protocol_result, medical_intelligence
        )
        
        return combined_result

    def _prepare_context_snippets(self, query: str, search_hits: List[Dict]) -> List[str]:
        """Prepare context snippets from search results"""
        snippets = []
        
        for hit in search_hits[:5]:  # Use top 5 results
            source = hit.get("_source", {})
            content = source.get("content", "")
            title = source.get("title", "")
            
            # Create informative snippet
            snippet = f"Title: {title}\nContent: {content[:500]}..."
            snippets.append(snippet)
        
        # If no search results, provide generic medical context based on query
        if not snippets:
            query_lower = query.lower()
            if any(word in query_lower for word in ["chest pain", "heart", "cardiac"]):
                snippets.append("Title: Cardiac Emergency Protocol\nContent: Immediate assessment of vital signs, ECG monitoring, oxygen administration, and emergency medication protocols for cardiac conditions.")
            elif any(word in query_lower for word in ["breathing", "respiratory", "asthma"]):
                snippets.append("Title: Respiratory Emergency Protocol\nContent: Airway assessment, oxygen therapy, bronchodilator administration, and respiratory monitoring protocols.")
            elif any(word in query_lower for word in ["emergency", "urgent", "critical"]):
                snippets.append("Title: Emergency Response Protocol\nContent: Immediate assessment, vital signs monitoring, airway management, and emergency intervention protocols.")
            else:
                snippets.append("Title: General Medical Assessment Protocol\nContent: Patient assessment, vital signs monitoring, symptom evaluation, and treatment planning protocols.")
        
        return snippets

    def _create_enhanced_instructions(self, query: str, query_analysis: Dict, medical_intelligence: Dict) -> str:
        """Create enhanced instructions for LLM based on medical intelligence"""
        
        base_instructions = f"""
Analyze the provided medical context and generate a comprehensive, actionable medical protocol checklist for: "{query}"

MEDICAL INTELLIGENCE CONTEXT:
- Intent: {query_analysis.get('intent', 'general')}
- Entities: {json.dumps(query_analysis.get('entities', []), indent=2)}
- Medical Context: {json.dumps(query_analysis.get('medical_context', {}), indent=2)}
- Enhanced Query: {query_analysis.get('enhanced_query', query)}

SAFETY CONSIDERATIONS:
"""
        
        # Add safety alerts
        safety_alerts = medical_intelligence.get("safety_alerts", [])
        if safety_alerts:
            base_instructions += "\n- CRITICAL SAFETY ALERTS:\n"
            for alert in safety_alerts:
                base_instructions += f"  • {alert}\n"
        
        # Add clinical notes
        clinical_notes = medical_intelligence.get("clinical_notes", [])
        if clinical_notes:
            base_instructions += "\n- CLINICAL NOTES:\n"
            for note in clinical_notes:
                base_instructions += f"  • {note}\n"
        
        # Add related concepts
        related_concepts = medical_intelligence.get("related_concepts", [])
        if related_concepts:
            base_instructions += f"\n- RELATED MEDICAL CONCEPTS: {', '.join(related_concepts)}\n"
        
        # Add intent-specific instructions
        intent = query_analysis.get('intent', 'general')
        if intent == 'emergency':
            base_instructions += """
EMERGENCY PROTOCOL REQUIREMENTS:
- Prioritize immediate life-saving interventions
- Include critical time-sensitive steps
- Highlight emergency medications and dosages
- Include emergency contact procedures
- Emphasize safety and contraindications
"""
        elif intent == 'symptom_based':
            # Check if it's an infectious disease query
            if any(term in query.lower() for term in ['dengue', 'malaria', 'typhoid', 'fever', 'infection']):
                base_instructions += """
INFECTIOUS DISEASE PROTOCOL REQUIREMENTS:
- Include comprehensive warning signs and red flags
- Provide specific diagnostic tests (CBC, serology, antigen tests)
- Include treatment protocols based on severity (mild, moderate, severe)
- Add specific monitoring parameters (vital signs, hematocrit, platelet count, organ function)
- Include fluid management protocols (oral, IV crystalloids)
- Add specific contraindications (NSAIDs for dengue, etc.)
- Include hospitalization criteria and discharge planning
- Provide patient/family education on warning signs
- Add follow-up monitoring schedules
- Include complication management protocols
"""
            else:
                base_instructions += """
SYMPTOM-BASED PROTOCOL REQUIREMENTS:
- Include differential diagnosis considerations
- Provide diagnostic steps and tests
- Include treatment protocols based on severity
- Add monitoring and follow-up instructions
"""
        elif intent == 'procedure_based':
            base_instructions += """
PROCEDURE-BASED PROTOCOL REQUIREMENTS:
- Provide step-by-step procedure instructions
- Include equipment and medication requirements
- Add safety precautions and contraindications
- Include post-procedure care instructions
"""
        elif intent == 'drug_based':
            base_instructions += """
DRUG-BASED PROTOCOL REQUIREMENTS:
- Include dosage calculations and administration
- Add contraindications and drug interactions
- Include monitoring requirements
- Add allergy and adverse reaction considerations
"""
        
        base_instructions += """
PROTOCOL GENERATION REQUIREMENTS:
- Generate concise, actionable checklist items based on the provided context
- DO NOT copy the context snippets directly - create new protocol steps
- Each step should be a clear, actionable medical instruction
- Prioritize safety and clinical accuracy
- Focus on the most critical and evidence-based steps
- Ensure protocol is appropriate for the medical context
- Include any relevant contraindications or warnings
- Generate 3-8 specific protocol steps based on the context provided
"""
        
        return base_instructions

    def _combine_results(self, query: str, search_result: Dict, protocol_result: Dict, medical_intelligence: Dict) -> Dict[str, Any]:
        """Combine search results, protocol generation, and medical intelligence"""
        
        # Extract protocol data
        checklist = protocol_result.get("checklist", [])
        citations = protocol_result.get("citations", [])
        
        # Create enhanced protocol data
        protocol_data = {
            "title": self._generate_protocol_title(query, medical_intelligence),
            "region": "Global",  # Could be enhanced with location detection
            "year": "2024",
            "organization": "ProCheck Medical Intelligence",
            "steps": self._format_protocol_steps(checklist),
            "citations": self._format_citations(citations, search_result),
            "lastUpdated": self._get_current_timestamp(),
            "medicalIntelligence": self._format_medical_intelligence(medical_intelligence)
        }
        
        # Create response content
        response_content = self._generate_response_content(query, medical_intelligence)
        
        return {
            "success": True,
            "query": query,
            "response_content": response_content,
            "protocol_data": protocol_data,
            "search_results": {
                "total": search_result.get("hits", {}).get("total", {}).get("value", 0),
                "hits": search_result.get("hits", {}).get("hits", []),
                "took_ms": search_result.get("took", 0)
            },
            "medical_intelligence": medical_intelligence
        }

    def _generate_protocol_title(self, query: str, medical_intelligence: Dict) -> str:
        """Generate an appropriate protocol title based on query and medical intelligence"""
        query_analysis = medical_intelligence.get("query_analysis", {})
        intent = query_analysis.get("intent", "general")
        
        if intent == "emergency":
            return f"Emergency Protocol: {query}"
        elif intent == "symptom_based":
            return f"Symptom-Based Protocol: {query}"
        elif intent == "procedure_based":
            return f"Medical Procedure: {query}"
        elif intent == "drug_based":
            return f"Medication Protocol: {query}"
        else:
            return f"Medical Protocol: {query}"

    def _format_protocol_steps(self, checklist: List[Any]) -> List[Dict[str, Any]]:
        """Format checklist into protocol steps"""
        formatted_steps = []
        
        for i, step in enumerate(checklist, 1):
            # Handle both string and object formats from LLM
            if isinstance(step, dict):
                step_text = step.get("text", str(step))
            else:
                step_text = str(step)
            
            formatted_steps.append({
                "id": i,
                "step": step_text,
                "citations": [1],  # Default citation
                "isNew": False,
                "changes": None
            })
        
        return formatted_steps

    def _format_citations(self, citations: List[str], search_result: Dict) -> List[Dict[str, Any]]:
        """Format citations from search results"""
        formatted_citations = []
        search_hits = search_result.get("hits", {}).get("hits", [])
        
        # Use search results as citations
        for i, hit in enumerate(search_hits[:5], 1):
            source = hit.get("_source", {})
            formatted_citations.append({
                "id": i,
                "source": source.get("title", "Medical Reference"),
                "organization": source.get("organization", "Medical Authority"),
                "year": str(source.get("year", "2024")),
                "region": source.get("region", "Global"),
                "url": source.get("source_url", ""),
                "excerpt": source.get("content", "")[:200] + "..." if len(source.get("content", "")) > 200 else source.get("content", "")
            })
        
        return formatted_citations

    def _format_medical_intelligence(self, medical_intelligence: Dict) -> Dict[str, Any]:
        """Format medical intelligence for frontend"""
        query_analysis = medical_intelligence.get("query_analysis", {})
        
        return {
            "intent": query_analysis.get("intent", "general"),
            "entities": query_analysis.get("entities", []),
            "medicalContext": query_analysis.get("medical_context", {}),
            "suggestions": medical_intelligence.get("search_suggestions", []),
            "safetyAlerts": medical_intelligence.get("safety_alerts", []),
            "clinicalNotes": medical_intelligence.get("clinical_notes", []),
            "relatedConcepts": medical_intelligence.get("related_concepts", []),
            "knowledgeGraph": medical_intelligence.get("knowledge_graph", {})
        }

    def _generate_response_content(self, query: str, medical_intelligence: Dict) -> str:
        """Generate response content based on medical intelligence"""
        query_analysis = medical_intelligence.get("query_analysis", {})
        intent = query_analysis.get("intent", "general")
        safety_alerts = medical_intelligence.get("safety_alerts", [])
        clinical_notes = medical_intelligence.get("clinical_notes", [])
        
        # Base response based on intent
        if intent == "emergency":
            response = "🚨 **EMERGENCY PROTOCOL** - Here's the immediate response protocol:"
        elif intent == "symptom_based":
            response = "🔍 **SYMPTOM-BASED ANALYSIS** - Here's the diagnostic and treatment protocol:"
        elif intent == "procedure_based":
            response = "⚕️ **PROCEDURE PROTOCOL** - Here's the step-by-step medical procedure:"
        elif intent == "drug_based":
            response = "💊 **MEDICATION PROTOCOL** - Here's the medication management protocol:"
        else:
            response = "📋 **MEDICAL PROTOCOL** - Here's the comprehensive protocol:"
        
        # Add safety alerts
        if safety_alerts:
            response += f"\n\n⚠️ **SAFETY ALERTS:**\n{safety_alerts[0]}"  # Show first alert
            if len(safety_alerts) > 1:
                response += f"\n({len(safety_alerts) - 1} additional alerts in medical intelligence)"
        
        # Add clinical notes
        if clinical_notes:
            response += f"\n\n📋 **CLINICAL NOTES:**\n{clinical_notes[0]}"  # Show first note
            if len(clinical_notes) > 1:
                response += f"\n({len(clinical_notes) - 1} additional notes in medical intelligence)"
        
        return response

    def _get_current_timestamp(self) -> str:
        """Get current timestamp in the required format"""
        from datetime import datetime
        return datetime.now().isoformat() + "Z"

# Global instance
intelligent_protocol_service = IntelligentProtocolService()
