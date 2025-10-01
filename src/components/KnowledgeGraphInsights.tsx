import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Microscope, TrendingUp, AlertTriangle, Stethoscope, Pill, Activity, Zap, Target } from 'lucide-react';

interface KnowledgeGraphInsightsProps {
  knowledgeGraph: {
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

export default function KnowledgeGraphInsights({ knowledgeGraph }: KnowledgeGraphInsightsProps) {
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-50 text-red-700 border-red-200';
      case 'high':
        return 'bg-amber-50 text-amber-700 border-amber-200';
      case 'medium':
        return 'bg-yellow-50 text-yellow-700 border-yellow-200';
      case 'low':
        return 'bg-emerald-50 text-emerald-700 border-emerald-200';
      default:
        return 'bg-slate-50 text-slate-700 border-slate-200';
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'cardiovascular':
        return <Activity className="h-4 w-4 text-red-600" />;
      case 'respiratory':
        return <Stethoscope className="h-4 w-4 text-blue-600" />;
      case 'emergency':
        return <Zap className="h-4 w-4 text-amber-600" />;
      case 'pain_management':
      case 'antibiotic':
        return <Pill className="h-4 w-4 text-purple-600" />;
      default:
        return <Microscope className="h-4 w-4 text-slate-600" />;
    }
  };

  return (
    <div className="space-y-4">
      {/* Emergency Indicators */}
      {knowledgeGraph.emergency_indicators.length > 0 && (
        <Card className="border-l-4 border-l-red-400 bg-red-50 shadow-sm">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-3 text-lg font-semibold text-red-800">
              <div className="p-2 bg-red-100 rounded-lg">
                <AlertTriangle className="h-5 w-5 text-red-600" />
              </div>
              Emergency Indicators
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            <div className="flex flex-wrap gap-2">
              {knowledgeGraph.emergency_indicators.map((indicator, index) => (
                <Badge 
                  key={index}
                  className={`${getSeverityColor(indicator.severity)} font-medium border`}
                >
                  {indicator.name}
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Differential Diagnosis */}
      {knowledgeGraph.differential_diagnosis.length > 0 && (
        <Card className="border-l-4 border-l-blue-400 bg-blue-50 shadow-sm">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-3 text-lg font-semibold text-blue-800">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Target className="h-5 w-5 text-blue-600" />
              </div>
              Differential Diagnosis
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            <div className="space-y-3">
              {knowledgeGraph.differential_diagnosis.map((diagnosis, index) => (
                <div key={index} className="flex items-center justify-between p-4 bg-white rounded-lg border border-blue-200 shadow-sm">
                  <div className="flex items-center gap-3">
                    <Badge className={`${getSeverityColor(diagnosis.severity)} font-medium border`}>
                      {diagnosis.severity}
                    </Badge>
                    <span className="font-medium text-slate-800">{diagnosis.name}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <TrendingUp className="h-4 w-4 text-blue-600" />
                    <span className="text-sm font-semibold text-blue-700">
                      {(diagnosis.score * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Primary Conditions */}
      {knowledgeGraph.primary_conditions.length > 0 && (
        <Card className="border-l-4 border-l-purple-400 bg-purple-50 shadow-sm">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-3 text-lg font-semibold text-purple-800">
              <div className="p-2 bg-purple-100 rounded-lg">
                <Stethoscope className="h-5 w-5 text-purple-600" />
              </div>
              Medical Conditions
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            <div className="flex flex-wrap gap-3">
              {knowledgeGraph.primary_conditions.map((condition, index) => (
                <div key={index} className="flex items-center gap-3 p-3 bg-white rounded-lg border border-purple-200 shadow-sm">
                  <div className="p-1.5 bg-purple-50 rounded">
                    {getCategoryIcon(condition.category)}
                  </div>
                  <Badge className={`${getSeverityColor(condition.severity)} font-medium border`}>
                    {condition.name}
                  </Badge>
                  <span className="text-xs text-slate-600 capitalize font-medium">
                    {condition.category.replace('_', ' ')}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Symptoms */}
      {knowledgeGraph.symptoms.length > 0 && (
        <Card className="border-l-4 border-l-emerald-400 bg-emerald-50 shadow-sm">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-3 text-lg font-semibold text-emerald-800">
              <div className="p-2 bg-emerald-100 rounded-lg">
                <Activity className="h-5 w-5 text-emerald-600" />
              </div>
              Identified Symptoms
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            <div className="flex flex-wrap gap-3">
              {knowledgeGraph.symptoms.map((symptom, index) => (
                <div key={index} className="flex items-center gap-3 p-3 bg-white rounded-lg border border-emerald-200 shadow-sm">
                  <div className="p-1.5 bg-emerald-50 rounded">
                    {getCategoryIcon(symptom.category)}
                  </div>
                  <Badge className={`${getSeverityColor(symptom.severity)} font-medium border`}>
                    {symptom.name}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Treatments */}
      {knowledgeGraph.treatments.length > 0 && (
        <Card className="border-l-4 border-l-blue-400 bg-blue-50 shadow-sm">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-3 text-lg font-semibold text-blue-800">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Stethoscope className="h-5 w-5 text-blue-600" />
              </div>
              Recommended Treatments
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            <div className="flex flex-wrap gap-3">
              {knowledgeGraph.treatments.map((treatment, index) => (
                <div key={index} className="flex items-center gap-3 p-3 bg-white rounded-lg border border-blue-200 shadow-sm">
                  <div className="p-1.5 bg-blue-50 rounded">
                    {getCategoryIcon(treatment.category)}
                  </div>
                  <Badge className={`${getSeverityColor(treatment.severity)} font-medium border`}>
                    {treatment.name}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Drugs */}
      {knowledgeGraph.drugs.length > 0 && (
        <Card className="border-l-4 border-l-indigo-400 bg-indigo-50 shadow-sm">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-3 text-lg font-semibold text-indigo-800">
              <div className="p-2 bg-indigo-100 rounded-lg">
                <Pill className="h-5 w-5 text-indigo-600" />
              </div>
              Medications
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            <div className="flex flex-wrap gap-3">
              {knowledgeGraph.drugs.map((drug, index) => (
                <div key={index} className="flex items-center gap-3 p-3 bg-white rounded-lg border border-indigo-200 shadow-sm">
                  <div className="p-1.5 bg-indigo-50 rounded">
                    {getCategoryIcon(drug.category)}
                  </div>
                  <Badge className={`${getSeverityColor(drug.severity)} font-medium border`}>
                    {drug.name}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Contraindications */}
      {knowledgeGraph.contraindications.length > 0 && (
        <Card className="border-l-4 border-l-red-400 bg-red-50 shadow-sm">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-3 text-lg font-semibold text-red-800">
              <div className="p-2 bg-red-100 rounded-lg">
                <AlertTriangle className="h-5 w-5 text-red-600" />
              </div>
              Contraindications
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            <div className="flex flex-wrap gap-2">
              {knowledgeGraph.contraindications.map((contra, index) => (
                <Badge 
                  key={index}
                  className="bg-red-100 text-red-700 border border-red-200 font-medium"
                >
                  {contra.name}
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Related Conditions */}
      {knowledgeGraph.related_conditions.length > 0 && (
        <Card className="border-l-4 border-l-slate-400 bg-slate-50 shadow-sm">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-3 text-lg font-semibold text-slate-800">
              <div className="p-2 bg-slate-100 rounded-lg">
                <Microscope className="h-5 w-5 text-slate-600" />
              </div>
              Related Conditions
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            <div className="flex flex-wrap gap-3">
              {knowledgeGraph.related_conditions.map((condition, index) => (
                <div key={index} className="flex items-center gap-3 p-3 bg-white rounded-lg border border-slate-200 shadow-sm">
                  <div className="p-1.5 bg-slate-50 rounded">
                    {getCategoryIcon(condition.category)}
                  </div>
                  <Badge className={`${getSeverityColor(condition.severity)} font-medium border`}>
                    {condition.name}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
