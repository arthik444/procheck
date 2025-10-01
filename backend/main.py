"""
ProCheck Backend API
Medical Protocol Search and Generation Service
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from typing import List
from config.settings import settings
from models.protocol_models import (
    ProtocolSearchRequest,
    ProtocolSearchResponse,
    ProtocolSearchHit,
    ProtocolGenerateRequest,
    ProtocolGenerateResponse,
)
from models.conversation_models import (
    ConversationSaveRequest,
    ConversationResponse,
    ConversationListResponse,
    ConversationDetailResponse,
    ConversationTitleUpdateRequest,
)
from services.elasticsearch_service import (
    check_cluster_health,
    ensure_index,
    search_protocols,
    count_documents,
    get_sample_documents,
    search_with_filters,
)
from services.gemini_service import summarize_checklist
from services.firestore_service import FirestoreService
from services.enhanced_search_service import enhanced_search_service
from services.clinical_decision_service import clinical_decision_service
from services.intelligent_protocol_service import intelligent_protocol_service

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "message": f"{settings.APP_NAME} is running!",
        "status": "healthy",
        "version": settings.APP_VERSION
    }

@app.get("/health")
async def health_check():
    """Detailed health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.environment,
        "config_status": {
            "elasticsearch_configured": settings.elasticsearch_configured,
            "gemini_configured": settings.gemini_configured
        }
    }

@app.get("/test")
async def test_endpoint():
    """Test endpoint for basic functionality"""
    return {
        "message": "Test endpoint working!",
        "timestamp": "2024-01-01T00:00:00Z",
        "data": {
            "elasticsearch_configured": settings.elasticsearch_configured,
            "gemini_configured": settings.gemini_configured,
            "elasticsearch_url": settings.ELASTICSEARCH_URL,
            "environment": settings.environment
        }
    }

@app.get("/elasticsearch/health")
async def elasticsearch_health():
    if not settings.elasticsearch_configured:
        raise HTTPException(status_code=400, detail="Elasticsearch is not configured. Set ELASTICSEARCH_URL in env.")
    return check_cluster_health()

@app.post("/elasticsearch/ensure-index")
async def elasticsearch_ensure_index():
    if not settings.elasticsearch_configured:
        raise HTTPException(status_code=400, detail="Elasticsearch is not configured. Set ELASTICSEARCH_URL in env.")
    return ensure_index()

@app.get("/elasticsearch/search")
async def elasticsearch_search(q: str | None = None, size: int = 5):
    if not settings.elasticsearch_configured:
        raise HTTPException(status_code=400, detail="Elasticsearch is not configured. Set ELASTICSEARCH_URL in env.")
    return search_protocols(q, size=size)

@app.get("/elasticsearch/count")
async def elasticsearch_count():
    if not settings.elasticsearch_configured:
        raise HTTPException(status_code=400, detail="Elasticsearch is not configured. Set ELASTICSEARCH_URL in env.")
    return count_documents()

@app.get("/elasticsearch/sample")
async def elasticsearch_sample(size: int = 3):
    if not settings.elasticsearch_configured:
        raise HTTPException(status_code=400, detail="Elasticsearch is not configured. Set ELASTICSEARCH_URL in env.")
    return get_sample_documents(size=size)

@app.post("/protocols/search", response_model=ProtocolSearchResponse)
async def protocols_search(payload: ProtocolSearchRequest):
    if not settings.elasticsearch_configured:
        raise HTTPException(status_code=400, detail="Elasticsearch is not configured.")
    es_resp = search_with_filters(payload.model_dump())
    if "error" in es_resp:
        raise HTTPException(status_code=502, detail=es_resp)
    hits = []
    for h in es_resp.get("hits", {}).get("hits", []):
        hits.append(ProtocolSearchHit(
            id=h.get("_id"),
            score=h.get("_score"),
            source=h.get("_source", {}),
            highlight=h.get("highlight")
        ))
    total = es_resp.get("hits", {}).get("total", {}).get("value", 0)
    took = es_resp.get("took", 0)
    return ProtocolSearchResponse(total=total, hits=hits, took_ms=took)

@app.post("/protocols/intelligent-search")
async def protocols_intelligent_search(payload: ProtocolSearchRequest):
    """Enhanced search with medical NLP and intelligence"""
    if not settings.elasticsearch_configured:
        raise HTTPException(status_code=400, detail="Elasticsearch is not configured.")
    
    try:
        # Use enhanced search service
        result = enhanced_search_service.intelligent_search(
            query=payload.query or "",
            filters=payload.filters,
            size=payload.size or 10
        )
        
        if "error" in result:
            raise HTTPException(status_code=502, detail=result)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": "intelligent_search_error", "details": str(e)})

@app.post("/protocols/medical-suggestions")
async def get_medical_suggestions(query: str):
    """Get medical suggestions and query analysis"""
    try:
        suggestions = enhanced_search_service.get_medical_suggestions(query)
        return suggestions
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": "suggestions_error", "details": str(e)})

@app.post("/protocols/generate-intelligent")
async def generate_intelligent_protocol(query: str, size: int = 8):
    """Generate comprehensive medical protocol using intelligent search + LLM generation"""
    if not settings.elasticsearch_configured:
        raise HTTPException(status_code=400, detail="Elasticsearch is not configured.")
    if not settings.gemini_configured:
        raise HTTPException(status_code=400, detail="Gemini AI is not configured.")
    
    try:
        result = intelligent_protocol_service.generate_intelligent_protocol(query, size)
        
        if "error" in result:
            raise HTTPException(status_code=502, detail=result)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": "intelligent_protocol_error", "details": str(e)})

@app.post("/clinical/risk-assessment")
async def clinical_risk_assessment(patient_data: dict, protocol_data: dict):
    """Get clinical risk assessment and patient-specific recommendations"""
    try:
        # Create patient context from request data
        patient_context = PatientContext(
            age=patient_data.get("age"),
            gender=patient_data.get("gender"),
            weight=patient_data.get("weight"),
            allergies=patient_data.get("allergies", []),
            medical_history=patient_data.get("medical_history", []),
            current_medications=patient_data.get("current_medications", []),
            pregnancy_status=patient_data.get("pregnancy_status"),
            setting=patient_data.get("setting")
        )
        
        # Perform risk assessment
        risk_assessment = clinical_decision_service.assess_patient_risk(patient_context, protocol_data)
        
        # Get patient-specific recommendations
        recommendations = clinical_decision_service.get_patient_specific_recommendations(
            patient_context, 
            protocol_data.get("query", "")
        )
        
        return {
            "risk_assessment": {
                "overall_risk": risk_assessment.overall_risk.value,
                "risk_factors": risk_assessment.risk_factors,
                "recommendations": risk_assessment.recommendations,
                "contraindications": risk_assessment.contraindications,
                "dosage_adjustments": risk_assessment.dosage_adjustments
            },
            "patient_recommendations": recommendations
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": "risk_assessment_error", "details": str(e)})

@app.post("/clinical/knowledge-graph")
async def get_knowledge_graph_data(entities: List[str]):
    """Get medical knowledge graph data for given entities"""
    try:
        from services.medical_knowledge_graph import medical_knowledge_graph
        
        result = {
            "entities": {},
            "relationships": {},
            "differential_diagnosis": [],
            "treatment_recommendations": [],
            "contraindications": []
        }
        
        for entity in entities:
            concept = medical_knowledge_graph.find_concept(entity)
            if concept:
                result["entities"][entity] = {
                    "name": concept.name,
                    "type": concept.concept_type,
                    "severity": concept.severity,
                    "category": concept.category,
                    "aliases": concept.aliases
                }
                
                # Get related concepts
                related = medical_knowledge_graph.get_related_concepts(concept.id)
                result["relationships"][entity] = [
                    {
                        "target": target.name,
                        "type": rel.relationship_type.value,
                        "strength": rel.strength,
                        "evidence": rel.evidence_level
                    }
                    for target, rel in related[:5]
                ]
                
                # Get differential diagnosis if it's a symptom
                if concept.concept_type == "symptom":
                    differential = medical_knowledge_graph.get_differential_diagnosis([entity])
                    result["differential_diagnosis"].extend([
                        {"condition": cond.name, "score": score, "severity": cond.severity}
                        for cond, score in differential[:3]
                    ])
                
                # Get treatment recommendations if it's a condition
                if concept.concept_type == "condition":
                    treatments = medical_knowledge_graph.get_treatment_recommendations(entity)
                    result["treatment_recommendations"].extend([
                        {"treatment": treat.name, "type": rel.relationship_type.value, "strength": rel.strength}
                        for treat, rel in treatments[:3]
                    ])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": "knowledge_graph_error", "details": str(e)})

@app.post("/protocols/generate", response_model=ProtocolGenerateResponse)
async def protocols_generate(payload: ProtocolGenerateRequest):
    if not settings.GEMINI_API_KEY:
        raise HTTPException(status_code=400, detail="GEMINI_API_KEY is not configured.")
    try:
        result = summarize_checklist(
            title=payload.title,
            context_snippets=payload.context_snippets,
            instructions=payload.instructions,
            region=payload.region,
            year=payload.year,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail={"error": "gemini_error", "details": str(e)})

    checklist_items = [
        {"step": item.get("step", idx + 1), "text": item.get("text", "")} 
        for idx, item in enumerate(result.get("checklist", []))
    ]
    return ProtocolGenerateResponse(
        title=result.get("title", payload.title),
        checklist=checklist_items,
        citations=result.get("citations", []),
    )

# Conversation management endpoints
@app.post("/conversations/save", response_model=ConversationResponse)
async def save_conversation(user_id: str, payload: ConversationSaveRequest):
    """Save or update a conversation for a user"""
    if not user_id or not user_id.strip():
        raise HTTPException(status_code=400, detail="user_id is required")

    result = FirestoreService.save_conversation(user_id, payload.model_dump())

    if not result.get("success"):
        status_code = 502 if result.get("error") == "firestore_error" else 500
        raise HTTPException(status_code=status_code, detail=result)

    return ConversationResponse(**result)

@app.get("/conversations/{user_id}", response_model=ConversationListResponse)
async def get_user_conversations(user_id: str, limit: int = 20):
    """Get all conversations for a user"""
    if not user_id or not user_id.strip():
        raise HTTPException(status_code=400, detail="user_id is required")

    result = FirestoreService.get_user_conversations(user_id, limit)

    if not result.get("success"):
        status_code = 502 if result.get("error") == "firestore_error" else 500
        raise HTTPException(status_code=status_code, detail=result)

    return ConversationListResponse(**result)

@app.get("/conversations/{user_id}/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation(user_id: str, conversation_id: str):
    """Get a specific conversation for a user"""
    if not user_id or not user_id.strip():
        raise HTTPException(status_code=400, detail="user_id is required")
    if not conversation_id or not conversation_id.strip():
        raise HTTPException(status_code=400, detail="conversation_id is required")

    result = FirestoreService.get_conversation(user_id, conversation_id)

    if not result.get("success"):
        if result.get("error") == "not_found":
            raise HTTPException(status_code=404, detail="Conversation not found")
        status_code = 502 if result.get("error") == "firestore_error" else 500
        raise HTTPException(status_code=status_code, detail=result)

    return ConversationDetailResponse(**result)

@app.delete("/conversations/{user_id}/{conversation_id}")
async def delete_conversation(user_id: str, conversation_id: str):
    """Delete a conversation for a user"""
    if not user_id or not user_id.strip():
        raise HTTPException(status_code=400, detail="user_id is required")
    if not conversation_id or not conversation_id.strip():
        raise HTTPException(status_code=400, detail="conversation_id is required")

    result = FirestoreService.delete_conversation(user_id, conversation_id)

    if not result.get("success"):
        if result.get("error") == "not_found":
            raise HTTPException(status_code=404, detail="Conversation not found")
        status_code = 502 if result.get("error") == "firestore_error" else 500
        raise HTTPException(status_code=status_code, detail=result)

    return {"success": True, "message": "Conversation deleted successfully"}

@app.put("/conversations/{user_id}/{conversation_id}/title")
async def update_conversation_title(user_id: str, conversation_id: str, payload: ConversationTitleUpdateRequest):
    """Update conversation title"""
    if not user_id or not user_id.strip():
        raise HTTPException(status_code=400, detail="user_id is required")
    if not conversation_id or not conversation_id.strip():
        raise HTTPException(status_code=400, detail="conversation_id is required")

    result = FirestoreService.update_conversation_title(user_id, conversation_id, payload.title)

    if not result.get("success"):
        if result.get("error") == "not_found":
            raise HTTPException(status_code=404, detail="Conversation not found")
        status_code = 502 if result.get("error") == "firestore_error" else 500
        raise HTTPException(status_code=status_code, detail=result)

    return {"success": True, "message": "Title updated successfully"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )
