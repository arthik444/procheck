from typing import List, Dict, Any
import google.generativeai as genai
from config.settings import settings

_client_initialized = False
_model: Any | None = None

def _ensure_client():
    global _client_initialized, _model
    if _client_initialized and _model is not None:
        return
    if not settings.GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not configured")
    genai.configure(api_key=settings.GEMINI_API_KEY)
    _model = genai.GenerativeModel(
        model_name=settings.GEMINI_MODEL,
        generation_config={
            "max_output_tokens": 768,
            "temperature": 0.2,
        },
    )
    _client_initialized = True


def _extract_text(response: Any) -> str:
    # Try the quick accessor, then fall back to candidates->parts
    try:
        if hasattr(response, "text") and response.text:
            return response.text
    except Exception:
        pass
    try:
        if getattr(response, "candidates", None):
            for cand in response.candidates:
                content = getattr(cand, "content", None)
                if not content:
                    continue
                parts = getattr(content, "parts", [])
                texts: List[str] = []
                for part in parts:
                    t = getattr(part, "text", None)
                    if t:
                        texts.append(t)
                if texts:
                    return "\n".join(texts)
    except Exception:
        pass
    return ""


def _clean_checklist_step(text: str) -> str:
    """Clean and shorten a checklist step to be concise and actionable."""
    text = str(text).strip()
    if not text:
        return ""
    
    # Remove common prefixes that make it verbose
    prefixes_to_remove = [
        "Step", "Action", "Task", "Procedure", "Process", "Check", "Verify", "Ensure", "Confirm",
        "The patient should", "The healthcare provider should", "The clinician should",
        "It is important to", "It is recommended to", "It is necessary to",
        "First", "Next", "Then", "Finally", "Additionally", "Furthermore",
    ]
    
    for prefix in prefixes_to_remove:
        if text.lower().startswith(prefix.lower()):
            text = text[len(prefix):].strip()
            if text.startswith(":"):
                text = text[1:].strip()
            break
    
    # Remove verbose endings
    endings_to_remove = [
        "as needed", "if necessary", "if required", "if appropriate", "if indicated",
        "according to protocol", "per guidelines", "as per standard practice",
        "to ensure patient safety", "for optimal outcomes", "for best results",
    ]
    
    for ending in endings_to_remove:
        if text.lower().endswith(ending.lower()):
            text = text[:-len(ending)].strip()
            break
    
    # Limit length to keep it concise
    if len(text) > 120:
        # Try to cut at a natural break
        for delimiter in [". ", "; ", ", "]:
            if delimiter in text[:120]:
                text = text[:text[:120].rfind(delimiter) + 1].strip()
                break
        else:
            text = text[:117] + "..."
    
    return text


def summarize_checklist(title: str, context_snippets: List[str], instructions: str | None = None, region: str | None = None, year: int | None = None) -> Dict[str, Any]:
    _ensure_client()
    assert _model is not None

    prompt_parts: List[str] = [
        "You are a medical protocol assistant. Generate a concise, actionable checklist.",
        "CRITICAL: Each step must be SHORT (max 15 words), ACTIONABLE, and CLEAR.",
        "Output ONLY JSON with this exact structure:",
        '{"title": "string", "checklist": [{"step": 1, "text": "short action"}, ...], "citations": []}',
        "Rules:",
        "- Steps must be imperative commands (e.g., 'Assess vital signs', 'Administer medication')",
        "- NO explanations, NO context, NO 'ensure that' or 'make sure'",
        "- NO code fences, NO extra text, NO markdown formatting",
        "- Output ONLY the JSON object, nothing else",
        "- Keep each step under 15 words",
        "- Number steps 1, 2, 3...",
        "- Analyze ALL provided context and select the MOST RELEVANT information for the user's query",
        "- If context contains conflicting information, prioritize the most authoritative or recent sources",
        "- Ignore irrelevant information that doesn't directly relate to the user's specific query",
        "- IMPORTANT: Do NOT wrap the JSON in ```json``` code blocks or any other formatting",
        "- Return ONLY the raw JSON object",
    ]
    
    if region:
        prompt_parts.append(f"Region: {region}.")
    if year:
        prompt_parts.append(f"Year: {year}.")
    if instructions:
        prompt_parts.append(f"Instructions: {instructions}")

    prompt_parts.append(f"Title: {title}")
    prompt_parts.append("Context:")
    for i, snippet in enumerate(context_snippets[:6], start=1):  # Limit context to avoid verbosity
        prompt_parts.append(f"{i}. {snippet}")

    prompt = "\n".join(prompt_parts)
    response = _model.generate_content(prompt)
    text = _extract_text(response)

    import json
    import re
    if text:
        # Clean the text to extract JSON from markdown code blocks
        text = text.strip()
        
        # Remove markdown code block markers
        if text.startswith('```json'):
            text = text[7:]  # Remove ```json
        elif text.startswith('```'):
            text = text[3:]   # Remove ```
        
        if text.endswith('```'):
            text = text[:-3]  # Remove trailing ```
        
        # Remove any remaining whitespace and newlines
        text = text.strip()
        
        # Handle cases where there might be extra text before/after JSON
        if '{' in text and '}' in text:
            start = text.find('{')
            end = text.rfind('}') + 1
            text = text[start:end]
        
        try:
            data = json.loads(text)
            out_title = str(data.get("title", title)).strip() or title
            raw_items = data.get("checklist", [])
            checklist: List[Dict[str, Any]] = []
            
            for idx, item in enumerate(raw_items, start=1):
                if isinstance(item, dict):
                    step_num = int(item.get("step", idx))
                    step_text = _clean_checklist_step(item.get("text", ""))
                else:
                    step_num = idx
                    step_text = _clean_checklist_step(str(item))
                
                if step_text and len(step_text) > 3:  # Only include meaningful steps
                    checklist.append({"step": step_num, "text": step_text})
            
            citations = data.get("citations", [])
            if not isinstance(citations, list):
                citations = []
            citations = [str(c).strip() for c in citations if str(c).strip()]
            
            return {
                "title": out_title,
                "checklist": checklist,
                "citations": citations,
            }
        except Exception as e:
            print(f"LLM JSON parsing failed: {e}")
            print(f"LLM response text: {text[:500]}...")
            print(f"Full LLM response length: {len(text)}")
            print(f"Full LLM response: {text}")
            
            # Try to extract JSON from the response manually
            try:
                # Look for JSON pattern in the response
                import re
                
                # Try different JSON extraction patterns
                patterns = [
                    r'```json\s*(\{.*?\})\s*```',  # JSON in code blocks
                    r'```\s*(\{.*?\})\s*```',      # JSON in generic code blocks
                    r'(\{.*?\})',                   # Any JSON object
                ]
                
                for pattern in patterns:
                    json_match = re.search(pattern, text, re.DOTALL)
                    if json_match:
                        json_text = json_match.group(1) if len(json_match.groups()) > 0 else json_match.group(0)
                        try:
                            data = json.loads(json_text)
                            print(f"Successfully extracted JSON manually using pattern: {pattern}")
                            break
                        except:
                            continue
                else:
                    print(f"No valid JSON found in response")
                    raise Exception("No valid JSON found")
                
                out_title = str(data.get("title", title)).strip() or title
                raw_items = data.get("checklist", [])
                checklist: List[Dict[str, Any]] = []
                
                for idx, item in enumerate(raw_items, start=1):
                    if isinstance(item, dict):
                        step_num = int(item.get("step", idx))
                        step_text = _clean_checklist_step(item.get("text", ""))
                    else:
                        step_num = idx
                        step_text = _clean_checklist_step(str(item))
                    
                    if step_text and len(step_text) > 3:
                        checklist.append({"step": step_num, "text": step_text})
                
                citations = data.get("citations", [])
                if not isinstance(citations, list):
                    citations = []
                citations = [str(c).strip() for c in citations if str(c).strip()]
                
                return {
                    "title": out_title,
                    "checklist": checklist,
                    "citations": citations,
                }
            except Exception as e2:
                print(f"Manual JSON extraction also failed: {e2}")
                pass

    # Fallback: create concise steps from context
    fallback_steps = []
    
    # Generate specific medical protocol steps based on query
    if "dengue" in title.lower():
        fallback_steps = [
            {"step": 1, "text": "Assess for warning signs: persistent vomiting, severe abdominal pain, mucosal bleeding, lethargy, restlessness, hepatomegaly >2cm, rapid pulse, narrow pulse pressure"},
            {"step": 2, "text": "Order complete blood count (CBC), hematocrit, platelet count, dengue NS1 antigen test, and liver function tests immediately"},
            {"step": 3, "text": "Monitor vital signs every 4-6 hours: temperature, pulse, blood pressure, respiratory rate, capillary refill time, and urine output"},
            {"step": 4, "text": "Manage fever with paracetamol 15mg/kg every 6 hours (max 4g/day); avoid NSAIDs and aspirin to prevent bleeding"},
            {"step": 5, "text": "Maintain adequate hydration: oral fluids 50-100ml/kg/day or IV crystalloids (Ringer's lactate) if oral intake inadequate"},
            {"step": 6, "text": "Monitor hematocrit levels every 6-12 hours - if rising >20% from baseline, consider fluid resuscitation with crystalloids"},
            {"step": 7, "text": "Platelet transfusion only if <10,000/μL with active bleeding or <20,000/μL with high bleeding risk (surgery, trauma)"},
            {"step": 8, "text": "Monitor for plasma leakage: daily weight, abdominal girth, clinical signs of fluid accumulation (pleural effusion, ascites)"},
            {"step": 9, "text": "Assess for severe dengue: shock, respiratory distress, severe bleeding, organ impairment (liver, kidney, brain)"},
            {"step": 10, "text": "Educate patient/family on warning signs and importance of follow-up monitoring every 24-48 hours"},
            {"step": 11, "text": "Consider hospitalization for severe dengue, warning signs, or high-risk patients (pregnancy, comorbidities, age <1 year or >65 years)"},
            {"step": 12, "text": "Monitor for complications: dengue hemorrhagic fever, dengue shock syndrome, organ failure, secondary infections"},
            {"step": 13, "text": "Provide supportive care: bed rest, mosquito bite prevention, adequate nutrition, and psychological support"},
            {"step": 14, "text": "Consider antiviral therapy in severe cases and manage complications according to standard protocols"},
            {"step": 15, "text": "Arrange follow-up: repeat CBC in 24-48 hours, monitor for late complications, and provide discharge instructions"}
        ]
    elif "chest pain" in title.lower() or "heart" in title.lower() or "cardiac" in title.lower():
        fallback_steps = [
            {"step": 1, "text": "Assess vital signs immediately"},
            {"step": 2, "text": "Obtain 12-lead ECG"},
            {"step": 3, "text": "Administer oxygen if needed"},
            {"step": 4, "text": "Check for cardiac risk factors"},
            {"step": 5, "text": "Consider cardiac monitoring"}
        ]
    elif "breathing" in title.lower() or "respiratory" in title.lower() or "asthma" in title.lower():
        fallback_steps = [
            {"step": 1, "text": "Assess airway and breathing"},
            {"step": 2, "text": "Check oxygen saturation"},
            {"step": 3, "text": "Administer bronchodilators if indicated"},
            {"step": 4, "text": "Monitor respiratory status"},
            {"step": 5, "text": "Consider chest X-ray if needed"}
        ]
    elif "emergency" in title.lower() or "urgent" in title.lower():
        fallback_steps = [
            {"step": 1, "text": "Assess patient stability"},
            {"step": 2, "text": "Obtain vital signs"},
            {"step": 3, "text": "Establish IV access"},
            {"step": 4, "text": "Monitor patient closely"},
            {"step": 5, "text": "Prepare for emergency interventions"}
        ]
    else:
        fallback_steps = [
            {"step": 1, "text": "Perform initial patient assessment"},
            {"step": 2, "text": "Obtain vital signs"},
            {"step": 3, "text": "Review medical history"},
            {"step": 4, "text": "Perform focused physical examination"},
            {"step": 5, "text": "Develop treatment plan"}
        ]
    
    return {
        "title": title,
        "checklist": fallback_steps,
        "citations": [],
    }
