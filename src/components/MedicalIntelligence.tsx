import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { AlertTriangle, Microscope, Stethoscope, Shield, Info, BookOpen, Activity } from 'lucide-react';
import { MedicalIntelligence as MedicalIntelligenceType } from '@/types';
import KnowledgeGraphInsights from './KnowledgeGraphInsights';

interface MedicalIntelligenceProps {
  intelligence: MedicalIntelligenceType & {
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
  };
}

export default function MedicalIntelligence({ intelligence }: MedicalIntelligenceProps) {
  const getIntentIcon = (intent: string) => {
    switch (intent) {
      case 'emergency':
        return <AlertTriangle className="h-5 w-5 text-red-600" />;
      case 'symptom_based':
        return <Stethoscope className="h-5 w-5 text-blue-600" />;
      case 'procedure_based':
        return <Microscope className="h-5 w-5 text-purple-600" />;
      case 'drug_based':
        return <Shield className="h-5 w-5 text-green-600" />;
      default:
        return <Info className="h-5 w-5 text-slate-600" />;
    }
  };

  const getIntentColor = (intent: string) => {
    switch (intent) {
      case 'emergency':
        return 'bg-red-50 text-red-700 border-red-200';
      case 'symptom_based':
        return 'bg-blue-50 text-blue-700 border-blue-200';
      case 'procedure_based':
        return 'bg-purple-50 text-purple-700 border-purple-200';
      case 'drug_based':
        return 'bg-emerald-50 text-emerald-700 border-emerald-200';
      default:
        return 'bg-slate-50 text-slate-700 border-slate-200';
    }
  };

  const getIntentLabel = (intent: string) => {
    switch (intent) {
      case 'emergency':
        return 'Emergency Protocol';
      case 'symptom_based':
        return 'Symptom Analysis';
      case 'procedure_based':
        return 'Medical Procedure';
      case 'drug_based':
        return 'Drug Information';
      case 'condition_based':
        return 'Medical Condition';
      default:
        return 'General Medical Query';
    }
  };

  return (
    <div className="space-y-4">
      {/* Intent and Context */}
      <Card className="border-l-4 border-l-slate-300 shadow-sm">
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-3 text-lg font-semibold text-slate-800">
            <div className="p-2 bg-slate-100 rounded-lg">
              {getIntentIcon(intelligence.intent)}
            </div>
            <span>Clinical Intelligence Analysis</span>
            <Badge className={`${getIntentColor(intelligence.intent)} font-medium`}>
              {getIntentLabel(intelligence.intent)}
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-0">
          {/* Medical Context */}
          {Object.keys(intelligence.medicalContext).length > 0 && (
            <div className="mb-4">
              <h4 className="text-sm font-semibold text-slate-700 mb-3 flex items-center gap-2">
                <Activity className="h-4 w-4 text-slate-500" />
                Patient Context
              </h4>
              <div className="flex flex-wrap gap-2">
                {intelligence.medicalContext.age && (
                  <Badge variant="outline" className="text-xs border-slate-300 text-slate-600">
                    Age: {intelligence.medicalContext.age}
                  </Badge>
                )}
                {intelligence.medicalContext.gender && (
                  <Badge variant="outline" className="text-xs border-slate-300 text-slate-600">
                    {intelligence.medicalContext.gender}
                  </Badge>
                )}
                {intelligence.medicalContext.urgency && (
                  <Badge 
                    variant="outline" 
                    className={`text-xs ${
                      intelligence.medicalContext.urgency === 'high' ? 'border-red-300 text-red-700 bg-red-50' :
                      intelligence.medicalContext.urgency === 'medium' ? 'border-amber-300 text-amber-700 bg-amber-50' :
                      'border-emerald-300 text-emerald-700 bg-emerald-50'
                    }`}
                  >
                    {intelligence.medicalContext.urgency} urgency
                  </Badge>
                )}
                {intelligence.medicalContext.setting && (
                  <Badge variant="outline" className="text-xs border-slate-300 text-slate-600">
                    {intelligence.medicalContext.setting}
                  </Badge>
                )}
              </div>
            </div>
          )}

          {/* Extracted Entities */}
          {intelligence.entities.length > 0 && (
            <div className="mb-4">
              <h4 className="text-sm font-semibold text-slate-700 mb-3 flex items-center gap-2">
                <Microscope className="h-4 w-4 text-slate-500" />
                Identified Medical Terms
              </h4>
              <div className="flex flex-wrap gap-2">
                {intelligence.entities.map((entity, index) => (
                  <Badge 
                    key={index}
                    variant="secondary"
                    className="text-xs bg-slate-100 text-slate-700 border-slate-200"
                    title={`Confidence: ${(entity.confidence * 100).toFixed(0)}%`}
                  >
                    {entity.text} ({entity.type})
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Safety Alerts */}
      {intelligence.safetyAlerts.length > 0 && (
        <Card className="border-l-4 border-l-red-400 bg-red-50 shadow-sm">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-3 text-lg font-semibold text-red-800">
              <div className="p-2 bg-red-100 rounded-lg">
                <AlertTriangle className="h-5 w-5 text-red-600" />
              </div>
              Critical Safety Alerts
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            <ul className="space-y-3">
              {intelligence.safetyAlerts.map((alert, index) => (
                <li key={index} className="text-sm text-red-700 flex items-start gap-3 p-3 bg-white rounded-lg border border-red-200">
                  <div className="w-2 h-2 bg-red-500 rounded-full mt-2 flex-shrink-0"></div>
                  <span>{alert}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {/* Clinical Notes */}
      {intelligence.clinicalNotes.length > 0 && (
        <Card className="border-l-4 border-l-blue-400 bg-blue-50 shadow-sm">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-3 text-lg font-semibold text-blue-800">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Stethoscope className="h-5 w-5 text-blue-600" />
              </div>
              Clinical Assessment Notes
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            <ul className="space-y-3">
              {intelligence.clinicalNotes.map((note, index) => (
                <li key={index} className="text-sm text-blue-700 flex items-start gap-3 p-3 bg-white rounded-lg border border-blue-200">
                  <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
                  <span>{note}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {/* Suggestions */}
      {intelligence.suggestions.length > 0 && (
        <Card className="border-l-4 border-l-emerald-400 bg-emerald-50 shadow-sm">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-3 text-lg font-semibold text-emerald-800">
              <div className="p-2 bg-emerald-100 rounded-lg">
                <BookOpen className="h-5 w-5 text-emerald-600" />
              </div>
              Clinical Recommendations
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            <ul className="space-y-3">
              {intelligence.suggestions.map((suggestion, index) => (
                <li key={index} className="text-sm text-emerald-700 flex items-start gap-3 p-3 bg-white rounded-lg border border-emerald-200">
                  <div className="w-2 h-2 bg-emerald-500 rounded-full mt-2 flex-shrink-0"></div>
                  <span>{suggestion}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {/* Related Concepts */}
      {intelligence.relatedConcepts.length > 0 && (
        <Card className="border-l-4 border-l-purple-400 bg-purple-50 shadow-sm">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-3 text-lg font-semibold text-purple-800">
              <div className="p-2 bg-purple-100 rounded-lg">
                <Microscope className="h-5 w-5 text-purple-600" />
              </div>
              Related Medical Concepts
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            <div className="flex flex-wrap gap-2">
              {intelligence.relatedConcepts.map((concept, index) => (
                <Badge 
                  key={index}
                  variant="outline"
                  className="text-xs border-purple-300 text-purple-700 bg-white hover:bg-purple-50"
                >
                  {concept}
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Knowledge Graph Insights */}
      {intelligence.knowledge_graph && (
        <KnowledgeGraphInsights knowledgeGraph={intelligence.knowledge_graph} />
      )}
    </div>
  );
}
