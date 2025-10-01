import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { AlertTriangle, Shield, Activity, Pill, User, TrendingUp, AlertCircle } from 'lucide-react';

interface RiskAssessment {
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
}

interface PatientRecommendations {
  patient_context: {
    age_group: string;
    risk_profile: string;
    special_considerations: string[];
  };
  protocol_modifications: string[];
  monitoring_requirements: string[];
  contraindication_warnings: string[];
}

interface ClinicalDecisionSupportProps {
  riskAssessment?: RiskAssessment;
  patientRecommendations?: PatientRecommendations;
}

export default function ClinicalDecisionSupport({ riskAssessment, patientRecommendations }: ClinicalDecisionSupportProps) {
  const getRiskColor = (risk: string) => {
    switch (risk.toLowerCase()) {
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'high':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'moderate':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low':
        return 'bg-green-100 text-green-800 border-green-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'contraindicated':
      case 'severe':
        return <AlertTriangle className="h-4 w-4 text-red-500" />;
      case 'moderate':
        return <AlertCircle className="h-4 w-4 text-yellow-500" />;
      case 'mild':
        return <Shield className="h-4 w-4 text-blue-500" />;
      default:
        return <Activity className="h-4 w-4 text-gray-500" />;
    }
  };

  return (
    <div className="space-y-4">
      {/* Overall Risk Assessment */}
      {riskAssessment && (
        <Card className="border-l-4 border-l-blue-400 shadow-sm">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-3 text-lg font-semibold text-slate-800">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Shield className="h-5 w-5 text-blue-600" />
              </div>
              <span>Clinical Risk Assessment</span>
              <Badge className={`${getRiskColor(riskAssessment.overall_risk)} font-medium border`}>
                {riskAssessment.overall_risk.toUpperCase()} RISK
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-0 space-y-4">
            {/* Risk Factors */}
            {riskAssessment.risk_factors.length > 0 && (
              <div>
                <h4 className="text-sm font-semibold text-slate-700 mb-3 flex items-center gap-2">
                  <AlertTriangle className="h-4 w-4 text-amber-600" />
                  Identified Risk Factors
                </h4>
                <div className="space-y-3">
                  {riskAssessment.risk_factors.map((factor, index) => (
                    <div key={index} className="flex items-start gap-3 p-3 bg-white rounded-lg border border-slate-200 shadow-sm">
                      <div className="w-2 h-2 bg-amber-500 rounded-full mt-2 flex-shrink-0"></div>
                      <span className="text-sm text-slate-700">{factor}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Recommendations */}
            {riskAssessment.recommendations.length > 0 && (
              <div>
                <h4 className="text-sm font-semibold text-slate-700 mb-3 flex items-center gap-2">
                  <Activity className="h-4 w-4 text-emerald-600" />
                  Clinical Recommendations
                </h4>
                <div className="space-y-3">
                  {riskAssessment.recommendations.map((recommendation, index) => (
                    <div key={index} className="flex items-start gap-3 p-3 bg-white rounded-lg border border-emerald-200 shadow-sm">
                      <div className="w-2 h-2 bg-emerald-500 rounded-full mt-2 flex-shrink-0"></div>
                      <span className="text-sm text-slate-700">{recommendation}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Contraindications */}
      {riskAssessment?.contraindications && riskAssessment.contraindications.length > 0 && (
        <Card className="border-l-4 border-l-red-400 bg-red-50 shadow-sm">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-3 text-lg font-semibold text-red-800">
              <div className="p-2 bg-red-100 rounded-lg">
                <AlertTriangle className="h-5 w-5 text-red-600" />
              </div>
              Contraindications & Warnings
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            <div className="space-y-3">
              {riskAssessment.contraindications.map((contra, index) => (
                <div key={index} className="p-4 bg-white rounded-lg border border-red-200 shadow-sm">
                  <div className="flex items-center gap-3 mb-3">
                    <div className="p-1.5 bg-red-50 rounded">
                      {getSeverityIcon(contra.severity)}
                    </div>
                    <Badge className={`${getRiskColor(contra.severity)} font-medium border`}>
                      {contra.severity.toUpperCase()}
                    </Badge>
                  </div>
                  <p className="text-sm text-red-800 font-medium mb-2">{contra.recommendation}</p>
                  <p className="text-xs text-red-600 bg-red-50 p-2 rounded border border-red-200">
                    <span className="font-medium">Reason:</span> {contra.reason}
                  </p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Dosage Adjustments */}
      {riskAssessment?.dosage_adjustments && riskAssessment.dosage_adjustments.length > 0 && (
        <Card className="border-l-4 border-l-purple-400 bg-purple-50 shadow-sm">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-3 text-lg font-semibold text-purple-800">
              <div className="p-2 bg-purple-100 rounded-lg">
                <Pill className="h-5 w-5 text-purple-600" />
              </div>
              Dosage Adjustments
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            <div className="space-y-3">
              {riskAssessment.dosage_adjustments.map((adjustment, index) => (
                <div key={index} className="p-4 bg-white rounded-lg border border-purple-200 shadow-sm">
                  <div className="flex items-center gap-3 mb-3">
                    <div className="p-1.5 bg-purple-50 rounded">
                      <TrendingUp className="h-4 w-4 text-purple-600" />
                    </div>
                    <span className="text-sm font-semibold text-purple-800 capitalize">
                      {adjustment.type.replace('_', ' ')}
                    </span>
                  </div>
                  <p className="text-sm text-purple-700 mb-3">{adjustment.description}</p>
                  {adjustment.condition && (
                    <p className="text-xs text-purple-600 bg-purple-50 p-2 rounded border border-purple-200 mb-3">
                      <span className="font-medium">Condition:</span> {adjustment.condition}
                    </p>
                  )}
                  {adjustment.adjustments && adjustment.adjustments.length > 0 && (
                    <div className="mt-3">
                      <p className="text-xs font-medium text-purple-800 mb-2">Specific adjustments:</p>
                      <div className="space-y-2">
                        {adjustment.adjustments.map((adj, adjIndex) => (
                          <div key={adjIndex} className="flex items-start gap-2 text-xs text-purple-700">
                            <div className="w-1.5 h-1.5 bg-purple-400 rounded-full mt-1.5 flex-shrink-0"></div>
                            <span>{adj}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Patient-Specific Recommendations */}
      {patientRecommendations && (
        <Card className="border-l-4 border-l-emerald-400 bg-emerald-50 shadow-sm">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-3 text-lg font-semibold text-emerald-800">
              <div className="p-2 bg-emerald-100 rounded-lg">
                <User className="h-5 w-5 text-emerald-600" />
              </div>
              Patient-Specific Recommendations
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-0 space-y-4">
            {/* Patient Context */}
            <div>
              <h4 className="text-sm font-semibold text-emerald-800 mb-3 flex items-center gap-2">
                <User className="h-4 w-4 text-emerald-600" />
                Patient Profile
              </h4>
              <div className="flex flex-wrap gap-2 mb-3">
                <Badge variant="outline" className="border-emerald-300 text-emerald-700 bg-white">
                  {patientRecommendations.patient_context.age_group} Patient
                </Badge>
                <Badge variant="outline" className="border-emerald-300 text-emerald-700 bg-white">
                  {patientRecommendations.patient_context.risk_profile} Risk Profile
                </Badge>
              </div>
              {patientRecommendations.patient_context.special_considerations.length > 0 && (
                <div className="space-y-2">
                  <p className="text-xs font-medium text-emerald-800">Special Considerations:</p>
                  {patientRecommendations.patient_context.special_considerations.map((consideration, index) => (
                    <div key={index} className="flex items-start gap-2 text-xs text-emerald-700 p-2 bg-white rounded border border-emerald-200">
                      <div className="w-1.5 h-1.5 bg-emerald-400 rounded-full mt-1.5 flex-shrink-0"></div>
                      <span>{consideration}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Protocol Modifications */}
            {patientRecommendations.protocol_modifications.length > 0 && (
              <div>
                <h4 className="text-sm font-semibold text-emerald-800 mb-3 flex items-center gap-2">
                  <Activity className="h-4 w-4 text-emerald-600" />
                  Protocol Modifications
                </h4>
                <div className="space-y-2">
                  {patientRecommendations.protocol_modifications.map((modification, index) => (
                    <div key={index} className="flex items-start gap-3 text-sm text-emerald-700 p-3 bg-white rounded border border-emerald-200 shadow-sm">
                      <div className="w-2 h-2 bg-emerald-500 rounded-full mt-1.5 flex-shrink-0"></div>
                      <span>{modification}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Monitoring Requirements */}
            {patientRecommendations.monitoring_requirements.length > 0 && (
              <div>
                <h4 className="text-sm font-semibold text-emerald-800 mb-3 flex items-center gap-2">
                  <TrendingUp className="h-4 w-4 text-emerald-600" />
                  Monitoring Requirements
                </h4>
                <div className="space-y-2">
                  {patientRecommendations.monitoring_requirements.map((requirement, index) => (
                    <div key={index} className="flex items-start gap-3 text-sm text-emerald-700 p-3 bg-white rounded border border-emerald-200 shadow-sm">
                      <div className="w-2 h-2 bg-emerald-500 rounded-full mt-1.5 flex-shrink-0"></div>
                      <span>{requirement}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Contraindication Warnings */}
            {patientRecommendations.contraindication_warnings.length > 0 && (
              <div>
                <h4 className="text-sm font-semibold text-emerald-800 mb-3 flex items-center gap-2">
                  <AlertTriangle className="h-4 w-4 text-red-600" />
                  Contraindication Warnings
                </h4>
                <div className="space-y-2">
                  {patientRecommendations.contraindication_warnings.map((warning, index) => (
                    <div key={index} className="flex items-start gap-3 text-sm text-emerald-700 p-3 bg-white rounded border border-red-200 shadow-sm">
                      <AlertTriangle className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
                      <span>{warning}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
