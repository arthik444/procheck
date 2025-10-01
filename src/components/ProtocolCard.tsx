import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { 
  Star, 
  Copy, 
  Download, 
  Share2, 
  ExternalLink,
  ChevronDown,
  ChevronUp,
  Save,
  FileText,
  Users,
  Calendar,
  MapPin,
  Building,
  AlertTriangle,
  Stethoscope,
  Shield,
  Activity,
  MessageCircle,
  Info
} from 'lucide-react';
import { ProtocolData } from '@/types';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';

interface ProtocolCardProps {
  protocolData: ProtocolData;
}

export default function ProtocolCard({ protocolData }: ProtocolCardProps) {
  const [isSaved, setIsSaved] = useState(false);
  const [isReferencesOpen, setIsReferencesOpen] = useState(false);
  const [savedSteps, setSavedSteps] = useState<number[]>([]);
  const [isAdditionalInfoOpen, setIsAdditionalInfoOpen] = useState(true);

  const handleSave = () => {
    setIsSaved(!isSaved);
  };

  const handleCopy = () => {
    const stepsText = protocolData.steps
      .map((step, index) => `${index + 1}. ${step.step}`)
      .join('\n');
    navigator.clipboard.writeText(stepsText);
  };

  const handleDownload = () => {
    // Placeholder for PDF generation
    console.log('Download PDF functionality would be implemented here');
  };

  const handleShare = () => {
    // Placeholder for sharing functionality
    console.log('Share functionality would be implemented here');
  };

  const handleSaveStep = (stepId: number) => {
    setSavedSteps(prev => 
      prev.includes(stepId) 
        ? prev.filter(id => id !== stepId)
        : [...prev, stepId]
    );
  };

  const handleCopyStep = (step: string) => {
    navigator.clipboard.writeText(step);
  };

  return (
    <Card className="bg-white border-slate-200 shadow-sm">
      {/* Header */}
      <CardHeader className="pb-4">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="text-xl text-slate-900 mb-2">
              {protocolData.title}
            </CardTitle>
            <div className="flex items-center space-x-2 mb-3">
              <Badge variant="secondary" className="bg-teal-100 text-teal-700">
                <MapPin className="h-3 w-3 mr-1" />
                {protocolData.region}
              </Badge>
              <Badge variant="secondary" className="bg-blue-100 text-blue-700">
                <Calendar className="h-3 w-3 mr-1" />
                {protocolData.year}
              </Badge>
              <Badge variant="secondary" className="bg-slate-100 text-slate-700">
                <Building className="h-3 w-3 mr-1" />
                {protocolData.organization}
              </Badge>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="icon"
              onClick={handleSave}
              className={isSaved ? 'bg-yellow-50 border-yellow-200' : ''}
            >
              <Star className={`h-4 w-4 ${isSaved ? 'text-yellow-500 fill-current' : 'text-slate-500'}`} />
            </Button>
            <Button variant="outline" size="icon" onClick={handleCopy}>
              <Copy className="h-4 w-4 text-slate-500" />
            </Button>
            <Button variant="outline" size="icon" onClick={handleDownload}>
              <Download className="h-4 w-4 text-slate-500" />
            </Button>
            <Button variant="outline" size="icon" onClick={handleShare}>
              <Share2 className="h-4 w-4 text-slate-500" />
            </Button>
          </div>
        </div>
      </CardHeader>

      {/* Protocol Steps */}
      <CardContent className="space-y-4">
        {/* Quick Context Banner - if available */}
        {protocolData.medicalIntelligence && (
          <div className="flex items-start gap-3 p-3 bg-slate-50 rounded-lg border border-slate-200">
            <Info className="h-5 w-5 text-slate-500 mt-0.5 flex-shrink-0" />
            <div className="flex-1">
              <div className="flex flex-wrap gap-2 mb-1">
                {protocolData.medicalIntelligence.medicalContext.age && (
                  <Badge variant="outline" className="text-xs border-slate-300 text-slate-600">
                    Age: {protocolData.medicalIntelligence.medicalContext.age}
                  </Badge>
                )}
                {protocolData.medicalIntelligence.medicalContext.urgency && (
                  <Badge 
                    variant="outline" 
                    className={`text-xs ${
                      protocolData.medicalIntelligence.medicalContext.urgency === 'high' ? 'border-red-300 text-red-700 bg-red-50' :
                      protocolData.medicalIntelligence.medicalContext.urgency === 'medium' ? 'border-amber-300 text-amber-700 bg-amber-50' :
                      'border-emerald-300 text-emerald-700 bg-emerald-50'
                    }`}
                  >
                    {protocolData.medicalIntelligence.medicalContext.urgency} urgency
                  </Badge>
                )}
                {protocolData.medicalIntelligence.medicalContext.setting && (
                  <Badge variant="outline" className="text-xs border-slate-300 text-slate-600">
                    {protocolData.medicalIntelligence.medicalContext.setting}
                  </Badge>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Protocol Steps */}
        <div className="space-y-3">
          {protocolData.steps.map((step) => (
            <Card key={step.id} className="bg-slate-50 border-slate-200">
              <CardContent className="p-4">
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-teal-600 text-white rounded-full flex items-center justify-center text-sm font-semibold">
                      {step.id}
                    </div>
                  </div>
                  <div className="flex-1">
                    <div className="flex items-start justify-between">
                      <p className="text-sm text-slate-900 leading-relaxed">
                        {step.step}
                        {step.citations.map((citationId) => (
                          <sup key={citationId} className="text-xs text-teal-600 font-semibold ml-1">
                            [{citationId}]
                          </sup>
                        ))}
                      </p>
                      <div className="flex items-center space-x-1 ml-2">
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleSaveStep(step.id)}
                          className={`h-6 w-6 ${savedSteps.includes(step.id) ? 'bg-yellow-50' : ''}`}
                        >
                          <Save className={`h-3 w-3 ${savedSteps.includes(step.id) ? 'text-yellow-500' : 'text-slate-400'}`} />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleCopyStep(step.step)}
                          className="h-6 w-6"
                        >
                          <Copy className="h-3 w-3 text-slate-400" />
                        </Button>
                      </div>
                    </div>
                    {step.isNew && (
                      <Badge variant="secondary" className="bg-green-100 text-green-700 mt-2 text-xs">
                        New in {protocolData.year}
                      </Badge>
                    )}
                    {step.changes && (
                      <p className="text-xs text-slate-600 mt-2 italic">
                        {step.changes}
                      </p>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Additional Clinical Information - Collapsible */}
        {protocolData.medicalIntelligence && (protocolData.medicalIntelligence.safetyAlerts.length > 0 || 
          protocolData.medicalIntelligence.clinicalNotes.length > 0 || 
          protocolData.clinicalDecisionSupport) && (
          <Collapsible open={isAdditionalInfoOpen} onOpenChange={setIsAdditionalInfoOpen}>
            <CollapsibleTrigger asChild>
              <Button variant="ghost" className="w-full justify-between p-3 h-auto bg-slate-50 hover:bg-slate-100 mt-2">
                <span className="text-sm font-medium text-slate-900 flex items-center gap-2">
                  <Activity className="h-4 w-4" />
                  Additional Clinical Information
                </span>
                {isAdditionalInfoOpen ? (
                  <ChevronUp className="h-4 w-4 text-slate-500" />
                ) : (
                  <ChevronDown className="h-4 w-4 text-slate-500" />
                )}
              </Button>
            </CollapsibleTrigger>
            <CollapsibleContent className="space-y-3 mt-3">
              {/* Safety Alerts - Always visible if present */}
              {protocolData.medicalIntelligence?.safetyAlerts && protocolData.medicalIntelligence.safetyAlerts.length > 0 && (
                <div className="p-4 bg-red-50 rounded-lg border border-red-200">
                  <div className="flex items-center gap-2 mb-3">
                    <AlertTriangle className="h-4 w-4 text-red-600" />
                    <h4 className="text-sm font-semibold text-red-800">Safety Alerts</h4>
                  </div>
                  <div className="space-y-2">
                    {protocolData.medicalIntelligence.safetyAlerts.map((alert, index) => (
                      <div key={index} className="flex items-start gap-2 text-sm text-red-700">
                        <div className="w-1.5 h-1.5 bg-red-500 rounded-full mt-2 flex-shrink-0"></div>
                        <span>{alert}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Clinical Notes */}
              {protocolData.medicalIntelligence?.clinicalNotes && protocolData.medicalIntelligence.clinicalNotes.length > 0 && (
                <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                  <div className="flex items-center gap-2 mb-3">
                    <Stethoscope className="h-4 w-4 text-blue-600" />
                    <h4 className="text-sm font-semibold text-blue-800">Clinical Notes</h4>
                  </div>
                  <div className="space-y-2">
                    {protocolData.medicalIntelligence.clinicalNotes.map((note, index) => (
                      <div key={index} className="flex items-start gap-2 text-sm text-blue-700">
                        <div className="w-1.5 h-1.5 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
                        <span>{note}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Risk Assessment - Compact */}
              {protocolData.clinicalDecisionSupport?.riskAssessment && (
                <div className="p-4 bg-slate-50 rounded-lg border border-slate-200">
                  <div className="flex items-center gap-2 mb-3">
                    <Shield className="h-4 w-4 text-slate-600" />
                    <h4 className="text-sm font-semibold text-slate-800">Risk Assessment</h4>
                    <Badge className={`ml-auto text-xs ${
                      protocolData.clinicalDecisionSupport.riskAssessment.overall_risk === 'high' ? 'bg-red-100 text-red-700 border-red-200' :
                      protocolData.clinicalDecisionSupport.riskAssessment.overall_risk === 'moderate' ? 'bg-amber-100 text-amber-700 border-amber-200' :
                      'bg-emerald-100 text-emerald-700 border-emerald-200'
                    }`}>
                      {protocolData.clinicalDecisionSupport.riskAssessment.overall_risk}
                    </Badge>
                  </div>
                  {protocolData.clinicalDecisionSupport.riskAssessment.risk_factors.length > 0 && (
                    <div className="space-y-1.5">
                      {protocolData.clinicalDecisionSupport.riskAssessment.risk_factors.slice(0, 3).map((factor: string, index: number) => (
                        <div key={index} className="flex items-start gap-2 text-xs text-slate-700">
                          <div className="w-1.5 h-1.5 bg-amber-500 rounded-full mt-1.5 flex-shrink-0"></div>
                          <span>{factor}</span>
                        </div>
                      ))}
                      {protocolData.clinicalDecisionSupport.riskAssessment.risk_factors.length > 3 && (
                        <div className="text-xs text-slate-500 italic ml-4">
                          +{protocolData.clinicalDecisionSupport.riskAssessment.risk_factors.length - 3} more
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}

              {/* Contraindications - Compact */}
              {protocolData.clinicalDecisionSupport?.riskAssessment?.contraindications && 
                protocolData.clinicalDecisionSupport.riskAssessment.contraindications.length > 0 && (
                <div className="p-4 bg-red-50 rounded-lg border border-red-200">
                  <div className="flex items-center gap-2 mb-3">
                    <AlertTriangle className="h-4 w-4 text-red-600" />
                    <h4 className="text-sm font-semibold text-red-800">Contraindications</h4>
                  </div>
                  <div className="space-y-2">
                    {protocolData.clinicalDecisionSupport.riskAssessment.contraindications.map((contra: any, index: number) => (
                      <div key={index} className="text-xs text-red-700">
                        <span className="font-medium">{contra.recommendation}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </CollapsibleContent>
          </Collapsible>
        )}

        {/* Follow-up Questions - Perplexity Style */}
        {protocolData.medicalIntelligence?.suggestions && protocolData.medicalIntelligence.suggestions.length > 0 && (
          <div className="pt-4 border-t border-slate-200">
            <div className="flex items-center gap-2 mb-3">
              <MessageCircle className="h-4 w-4 text-slate-600" />
              <h4 className="text-sm font-semibold text-slate-800">Related Questions</h4>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
              {protocolData.medicalIntelligence.suggestions.slice(0, 4).map((suggestion, index) => (
                <Button
                  key={index}
                  variant="outline"
                  className="h-auto py-3 px-4 text-left justify-start text-sm text-slate-700 hover:bg-slate-50 hover:text-teal-600 hover:border-teal-300 whitespace-normal"
                  onClick={() => console.log('Follow-up question:', suggestion)}
                >
                  <span className="line-clamp-2">{suggestion}</span>
                </Button>
              ))}
            </div>
          </div>
        )}

        {/* Follow-up Actions */}
        <div className="pt-4 border-t border-slate-200">
          <div className="flex flex-wrap gap-2">
            <Button variant="outline" size="sm" className="text-slate-600">
              <FileText className="h-4 w-4 mr-2" />
              Compare with last year
            </Button>
            <Button variant="outline" size="sm" className="text-slate-600">
              <Download className="h-4 w-4 mr-2" />
              Export as PDF
            </Button>
            <Button variant="outline" size="sm" className="text-slate-600">
              <Users className="h-4 w-4 mr-2" />
              Send to team
            </Button>
          </div>
        </div>

        {/* References Section */}
        <div className="pt-4 border-t border-slate-200">
          <Button
            variant="ghost"
            onClick={() => setIsReferencesOpen(!isReferencesOpen)}
            className="w-full justify-between p-0 h-auto"
          >
            <span className="text-sm font-medium text-slate-900">
              References ({protocolData.citations.length})
            </span>
            {isReferencesOpen ? (
              <ChevronUp className="h-4 w-4 text-slate-500" />
            ) : (
              <ChevronDown className="h-4 w-4 text-slate-500" />
            )}
          </Button>
          
          {isReferencesOpen && (
            <div className="mt-4 space-y-3">
              {protocolData.citations.map((citation) => (
                <Card key={citation.id} className="bg-slate-50 border-slate-200">
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <span className="text-sm font-semibold text-teal-600">
                            [{citation.id}]
                          </span>
                          <h4 className="text-sm font-medium text-slate-900">
                            {citation.source}
                          </h4>
                        </div>
                        <div className="flex items-center space-x-2 mb-2">
                          <Badge variant="secondary" className="bg-slate-200 text-slate-700 text-xs">
                            {citation.organization}
                          </Badge>
                          <Badge variant="secondary" className="bg-slate-200 text-slate-700 text-xs">
                            {citation.year}
                          </Badge>
                          <Badge variant="secondary" className="bg-slate-200 text-slate-700 text-xs">
                            {citation.region}
                          </Badge>
                        </div>
                        <p className="text-xs text-slate-600 leading-relaxed">
                          {citation.excerpt}
                        </p>
                      </div>
                      {citation.url && (
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => window.open(citation.url, '_blank')}
                          className="ml-2 h-6 w-6"
                        >
                          <ExternalLink className="h-3 w-3 text-slate-400" />
                        </Button>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
