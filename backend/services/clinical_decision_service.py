"""
Clinical Decision Support Service for ProCheck
Provides patient context integration, risk assessment, and contraindication checking
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from services.medical_knowledge_graph import medical_knowledge_graph

class RiskLevel(Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"

class ContraindicationSeverity(Enum):
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    CONTRAINDICATED = "contraindicated"

@dataclass
class PatientContext:
    age: Optional[int] = None
    gender: Optional[str] = None
    weight: Optional[float] = None  # in kg
    allergies: Optional[List[str]] = None
    medical_history: Optional[List[str]] = None
    current_medications: Optional[List[str]] = None
    pregnancy_status: Optional[str] = None
    setting: Optional[str] = None  # hospital, clinic, home, emergency

@dataclass
class RiskAssessment:
    overall_risk: RiskLevel
    risk_factors: List[str]
    recommendations: List[str]
    contraindications: List[Dict[str, Any]]
    dosage_adjustments: List[Dict[str, Any]]

class ClinicalDecisionService:
    def __init__(self):
        self.knowledge_graph = medical_knowledge_graph
        
        # Drug allergy patterns
        self.drug_allergy_patterns = {
            "penicillin": ["penicillin", "amoxicillin", "ampicillin", "benzylpenicillin"],
            "sulfa": ["sulfamethoxazole", "trimethoprim", "sulfasalazine", "sulfonamides"],
            "aspirin": ["aspirin", "acetylsalicylic acid", "nsaids", "ibuprofen"],
            "opioids": ["morphine", "fentanyl", "codeine", "oxycodone", "hydrocodone"],
            "contrast": ["iodinated contrast", "gadolinium", "contrast dye"]
        }
        
        # Age-based risk factors
        self.age_risk_factors = {
            "pediatric": {"min": 0, "max": 17, "risks": ["pediatric dosing", "growth considerations", "parental consent"]},
            "adult": {"min": 18, "max": 64, "risks": ["standard protocols"]},
            "geriatric": {"min": 65, "max": 150, "risks": ["reduced kidney function", "polypharmacy", "fall risk", "cognitive considerations"]}
        }
        
        # Medical condition interactions
        self.condition_interactions = {
            "diabetes": {
                "risk_factors": ["delayed wound healing", "infection risk", "cardiovascular complications"],
                "drug_adjustments": ["insulin requirements", "glucose monitoring"]
            },
            "hypertension": {
                "risk_factors": ["cardiovascular events", "stroke risk"],
                "drug_adjustments": ["blood pressure monitoring", "ace inhibitor considerations"]
            },
            "kidney_disease": {
                "risk_factors": ["drug clearance issues", "fluid balance"],
                "drug_adjustments": ["reduced dosing", "creatinine monitoring"]
            },
            "liver_disease": {
                "risk_factors": ["drug metabolism issues", "bleeding risk"],
                "drug_adjustments": ["hepatic dosing", "liver function monitoring"]
            },
            "pregnancy": {
                "risk_factors": ["fetal safety", "maternal complications"],
                "drug_adjustments": ["pregnancy category", "teratogenic risk"]
            }
        }

    def assess_patient_risk(self, patient_context: PatientContext, protocol_data: Dict[str, Any]) -> RiskAssessment:
        """Assess overall risk for a patient and protocol combination"""
        
        risk_factors = []
        recommendations = []
        contraindications = []
        dosage_adjustments = []
        
        # Age-based risk assessment
        if patient_context.age is not None:
            age_risk = self._assess_age_risk(patient_context.age)
            risk_factors.extend(age_risk["factors"])
            recommendations.extend(age_risk["recommendations"])
            dosage_adjustments.extend(age_risk["adjustments"])
        
        # Allergy assessment
        if patient_context.allergies:
            allergy_assessment = self._assess_allergies(patient_context.allergies, protocol_data)
            contraindications.extend(allergy_assessment["contraindications"])
            recommendations.extend(allergy_assessment["recommendations"])
        
        # Medical history assessment
        if patient_context.medical_history:
            history_assessment = self._assess_medical_history(patient_context.medical_history, protocol_data)
            risk_factors.extend(history_assessment["risk_factors"])
            recommendations.extend(history_assessment["recommendations"])
            dosage_adjustments.extend(history_assessment["adjustments"])
        
        # Current medications assessment
        if patient_context.current_medications:
            medication_assessment = self._assess_current_medications(patient_context.current_medications, protocol_data)
            contraindications.extend(medication_assessment["interactions"])
            recommendations.extend(medication_assessment["recommendations"])
        
        # Pregnancy assessment
        if patient_context.pregnancy_status:
            pregnancy_assessment = self._assess_pregnancy_risk(patient_context.pregnancy_status, protocol_data)
            risk_factors.extend(pregnancy_assessment["risk_factors"])
            recommendations.extend(pregnancy_assessment["recommendations"])
            contraindications.extend(pregnancy_assessment["contraindications"])
        
        # Determine overall risk level
        overall_risk = self._determine_overall_risk(risk_factors, contraindications)
        
        return RiskAssessment(
            overall_risk=overall_risk,
            risk_factors=risk_factors,
            recommendations=recommendations,
            contraindications=contraindications,
            dosage_adjustments=dosage_adjustments
        )

    def _assess_age_risk(self, age: int) -> Dict[str, List[str]]:
        """Assess age-related risks"""
        factors = []
        recommendations = []
        adjustments = []
        
        if age < 18:
            factors.append("Pediatric patient - specialized protocols required")
            recommendations.append("Use pediatric dosing guidelines")
            recommendations.append("Consider parental consent requirements")
            adjustments.append({"type": "pediatric_dosing", "description": "Adjust dosages based on weight and age"})
        elif age >= 65:
            factors.append("Geriatric patient - increased risk profile")
            factors.append("Potential for reduced kidney function")
            recommendations.append("Monitor kidney function")
            recommendations.append("Assess for polypharmacy interactions")
            recommendations.append("Consider fall risk and mobility issues")
            adjustments.append({"type": "renal_adjustment", "description": "Consider reduced dosing for renal clearance"})
        
        return {
            "factors": factors,
            "recommendations": recommendations,
            "adjustments": adjustments
        }

    def _assess_allergies(self, allergies: List[str], protocol_data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """Assess allergy-related contraindications"""
        contraindications = []
        recommendations = []
        
        # Check for drug allergies in protocol
        protocol_content = str(protocol_data.get("content", "")).lower()
        
        for allergy in allergies:
            allergy_lower = allergy.lower()
            
            # Check against known drug allergy patterns
            for drug_class, drugs in self.drug_allergy_patterns.items():
                if any(drug in allergy_lower for drug in drugs.split()):
                    # Check if protocol contains these drugs
                    for drug in drugs:
                        if drug in protocol_content:
                            contraindications.append({
                                "drug": drug,
                                "allergy": allergy,
                                "severity": ContraindicationSeverity.CONTRAINDICATED.value,
                                "recommendation": f"Avoid {drug} due to {allergy} allergy"
                            })
                            recommendations.append(f"Use alternative to {drug} due to {allergy} allergy")
        
        return {
            "contraindications": contraindications,
            "recommendations": recommendations
        }

    def _assess_medical_history(self, medical_history: List[str], protocol_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Assess medical history-related risks"""
        risk_factors = []
        recommendations = []
        adjustments = []
        
        protocol_content = str(protocol_data.get("content", "")).lower()
        
        for condition in medical_history:
            condition_lower = condition.lower()
            
            # Check for known condition interactions
            for medical_condition, interaction_data in self.condition_interactions.items():
                if medical_condition in condition_lower:
                    risk_factors.extend([f"{condition}: {risk}" for risk in interaction_data["risk_factors"]])
                    recommendations.extend([f"Monitor for {adjustment}" for adjustment in interaction_data["drug_adjustments"]])
                    adjustments.extend([{"type": "condition_based", "condition": condition, "adjustments": interaction_data["drug_adjustments"]}])
        
        return {
            "risk_factors": risk_factors,
            "recommendations": recommendations,
            "adjustments": adjustments
        }

    def _assess_current_medications(self, medications: List[str], protocol_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Assess drug interaction risks"""
        interactions = []
        recommendations = []
        
        # Common drug interactions
        interaction_patterns = {
            "warfarin": ["aspirin", "nsaids", "antibiotics"],
            "digoxin": ["diuretics", "calcium channel blockers"],
            "insulin": ["beta blockers", "thiazides"],
            "ace inhibitors": ["potassium supplements", "nsaids"],
            "beta blockers": ["insulin", "calcium channel blockers"]
        }
        
        protocol_content = str(protocol_data.get("content", "")).lower()
        
        for medication in medications:
            med_lower = medication.lower()
            
            # Check for interactions
            for drug, interacting_drugs in interaction_patterns.items():
                if drug in med_lower:
                    for interacting_drug in interacting_drugs:
                        if interacting_drug in protocol_content:
                            interactions.append({
                                "medication": medication,
                                "interacting_drug": interacting_drug,
                                "severity": "moderate",
                                "recommendation": f"Monitor for interaction between {medication} and {interacting_drug}"
                            })
                            recommendations.append(f"Monitor patient for drug interaction between {medication} and {interacting_drug}")
        
        return {
            "interactions": interactions,
            "recommendations": recommendations
        }

    def _assess_pregnancy_risk(self, pregnancy_status: str, protocol_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Assess pregnancy-related risks"""
        risk_factors = []
        recommendations = []
        contraindications = []
        
        if pregnancy_status.lower() in ["pregnant", "pregnancy", "expecting"]:
            risk_factors.append("Pregnant patient - fetal safety considerations")
            recommendations.append("Consider pregnancy category of all medications")
            recommendations.append("Assess teratogenic risk")
            recommendations.append("Consider fetal monitoring if applicable")
            
            # Check for contraindicated drugs in pregnancy
            contraindicated_drugs = ["warfarin", "ace inhibitors", "statins", "methotrexate", "isotretinoin"]
            protocol_content = str(protocol_data.get("content", "")).lower()
            
            for drug in contraindicated_drugs:
                if drug in protocol_content:
                    contraindications.append({
                        "drug": drug,
                        "reason": "pregnancy",
                        "severity": "severe",
                        "recommendation": f"Avoid {drug} in pregnancy due to teratogenic risk"
                    })
        
        return {
            "risk_factors": risk_factors,
            "recommendations": recommendations,
            "contraindications": contraindications
        }

    def _determine_overall_risk(self, risk_factors: List[str], contraindications: List[Dict[str, Any]]) -> RiskLevel:
        """Determine overall risk level based on factors and contraindications"""
        
        if any(contra.get("severity") == "contraindicated" for contra in contraindications):
            return RiskLevel.CRITICAL
        
        severe_contraindications = sum(1 for contra in contraindications if contra.get("severity") == "severe")
        if severe_contraindications > 0:
            return RiskLevel.HIGH
        
        if len(risk_factors) > 3 or len(contraindications) > 1:
            return RiskLevel.MODERATE
        
        return RiskLevel.LOW

    def get_patient_specific_recommendations(self, patient_context: PatientContext, query: str) -> Dict[str, Any]:
        """Get patient-specific recommendations based on context and query"""
        
        # Analyze the query for medical concepts
        query_analysis = self.knowledge_graph.get_medical_context([
            {"text": query.lower(), "type": "query"}
        ])
        
        recommendations = {
            "patient_context": {
                "age_group": self._get_age_group(patient_context.age),
                "risk_profile": "standard",
                "special_considerations": []
            },
            "protocol_modifications": [],
            "monitoring_requirements": [],
            "contraindication_warnings": []
        }
        
        # Age-specific recommendations
        if patient_context.age is not None:
            age_group = self._get_age_group(patient_context.age)
            if age_group == "pediatric":
                recommendations["patient_context"]["special_considerations"].append("Pediatric dosing required")
                recommendations["monitoring_requirements"].append("Weight-based dosing calculations")
            elif age_group == "geriatric":
                recommendations["patient_context"]["special_considerations"].append("Geriatric considerations")
                recommendations["monitoring_requirements"].append("Renal function monitoring")
        
        # Allergy-specific recommendations
        if patient_context.allergies:
            recommendations["contraindication_warnings"].extend([
                f"Check for {allergy} allergy" for allergy in patient_context.allergies
            ])
        
        return recommendations

    def _get_age_group(self, age: Optional[int]) -> str:
        """Get age group classification"""
        if age is None:
            return "unknown"
        elif age < 18:
            return "pediatric"
        elif age >= 65:
            return "geriatric"
        else:
            return "adult"

# Global instance
clinical_decision_service = ClinicalDecisionService()


