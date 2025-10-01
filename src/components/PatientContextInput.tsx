import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { User, Plus, X, AlertTriangle } from 'lucide-react';

interface PatientContext {
  age?: number;
  gender?: string;
  weight?: number;
  allergies: string[];
  medicalHistory: string[];
  currentMedications: string[];
  pregnancyStatus?: string;
  setting?: string;
}

interface PatientContextInputProps {
  onContextUpdate: (context: PatientContext) => void;
  initialContext?: PatientContext;
}

export default function PatientContextInput({ onContextUpdate, initialContext }: PatientContextInputProps) {
  const [context, setContext] = useState<PatientContext>(
    initialContext || {
      allergies: [],
      medicalHistory: [],
      currentMedications: []
    }
  );

  const [newAllergy, setNewAllergy] = useState('');
  const [newMedicalHistory, setNewMedicalHistory] = useState('');
  const [newMedication, setNewMedication] = useState('');

  const updateContext = (updates: Partial<PatientContext>) => {
    const newContext = { ...context, ...updates };
    setContext(newContext);
    onContextUpdate(newContext);
  };

  const addItem = (type: 'allergies' | 'medicalHistory' | 'currentMedications', value: string, setter: (value: string) => void) => {
    if (value.trim() && !context[type].includes(value.trim())) {
      const newItems = [...context[type], value.trim()];
      updateContext({ [type]: newItems });
      setter('');
    }
  };

  const removeItem = (type: 'allergies' | 'medicalHistory' | 'currentMedications', index: number) => {
    const newItems = context[type].filter((_, i) => i !== index);
    updateContext({ [type]: newItems });
  };

  const getAgeGroup = (age?: number) => {
    if (!age) return 'Unknown';
    if (age < 18) return 'Pediatric';
    if (age >= 65) return 'Geriatric';
    return 'Adult';
  };

  const getRiskLevel = () => {
    let riskFactors = 0;
    
    if (context.age && context.age < 18) riskFactors++; // Pediatric
    if (context.age && context.age >= 65) riskFactors++; // Geriatric
    if (context.allergies.length > 0) riskFactors++;
    if (context.medicalHistory.length > 0) riskFactors++;
    if (context.currentMedications.length > 0) riskFactors++;
    if (context.pregnancyStatus === 'pregnant') riskFactors++;
    
    if (riskFactors === 0) return { level: 'low', color: 'bg-green-100 text-green-800' };
    if (riskFactors <= 2) return { level: 'moderate', color: 'bg-yellow-100 text-yellow-800' };
    if (riskFactors <= 4) return { level: 'high', color: 'bg-orange-100 text-orange-800' };
    return { level: 'critical', color: 'bg-red-100 text-red-800' };
  };

  const riskLevel = getRiskLevel();

  return (
    <Card className="w-full">
      <CardHeader className="pb-4">
        <CardTitle className="flex items-center gap-2">
          <User className="h-5 w-5 text-teal-600" />
          Patient Context
          <Badge className={riskLevel.color}>
            {riskLevel.level.toUpperCase()} RISK
          </Badge>
        </CardTitle>
        <p className="text-sm text-slate-600">
          Provide patient information for personalized protocol recommendations and risk assessment
        </p>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Basic Demographics */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">Age (years)</label>
            <Input
              type="number"
              placeholder="e.g., 45"
              value={context.age || ''}
              onChange={(e) => updateContext({ age: e.target.value ? parseInt(e.target.value) : undefined })}
              className="w-full"
            />
            {context.age && (
              <p className="text-xs text-slate-500 mt-1">
                {getAgeGroup(context.age)} patient
              </p>
            )}
          </div>
          
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">Gender</label>
            <select
              className="w-full px-3 py-2 border border-slate-300 rounded-md text-sm"
              value={context.gender || ''}
              onChange={(e) => updateContext({ gender: e.target.value || undefined })}
            >
              <option value="">Select gender</option>
              <option value="male">Male</option>
              <option value="female">Female</option>
              <option value="other">Other</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">Weight (kg)</label>
            <Input
              type="number"
              placeholder="e.g., 70"
              value={context.weight || ''}
              onChange={(e) => updateContext({ weight: e.target.value ? parseFloat(e.target.value) : undefined })}
              className="w-full"
            />
          </div>
        </div>

        {/* Allergies */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            Allergies {context.allergies.length > 0 && (
              <Badge variant="secondary" className="ml-2">
                {context.allergies.length}
              </Badge>
            )}
          </label>
          <div className="flex gap-2 mb-2">
            <Input
              placeholder="e.g., Penicillin, Aspirin"
              value={newAllergy}
              onChange={(e) => setNewAllergy(e.target.value)}
              className="flex-1"
            />
            <Button
              onClick={() => addItem('allergies', newAllergy, setNewAllergy)}
              size="sm"
              variant="outline"
            >
              <Plus className="h-4 w-4" />
            </Button>
          </div>
          <div className="flex flex-wrap gap-2">
            {context.allergies.map((allergy, index) => (
              <Badge
                key={index}
                variant="destructive"
                className="bg-red-100 text-red-800 border-red-200"
              >
                {allergy}
                <button
                  onClick={() => removeItem('allergies', index)}
                  className="ml-1 hover:bg-red-200 rounded-full p-0.5"
                >
                  <X className="h-3 w-3" />
                </button>
              </Badge>
            ))}
          </div>
        </div>

        {/* Medical History */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            Medical History {context.medicalHistory.length > 0 && (
              <Badge variant="secondary" className="ml-2">
                {context.medicalHistory.length}
              </Badge>
            )}
          </label>
          <div className="flex gap-2 mb-2">
            <Input
              placeholder="e.g., Diabetes, Hypertension"
              value={newMedicalHistory}
              onChange={(e) => setNewMedicalHistory(e.target.value)}
              className="flex-1"
            />
            <Button
              onClick={() => addItem('medicalHistory', newMedicalHistory, setNewMedicalHistory)}
              size="sm"
              variant="outline"
            >
              <Plus className="h-4 w-4" />
            </Button>
          </div>
          <div className="flex flex-wrap gap-2">
            {context.medicalHistory.map((condition, index) => (
              <Badge
                key={index}
                variant="secondary"
                className="bg-blue-100 text-blue-800 border-blue-200"
              >
                {condition}
                <button
                  onClick={() => removeItem('medicalHistory', index)}
                  className="ml-1 hover:bg-blue-200 rounded-full p-0.5"
                >
                  <X className="h-3 w-3" />
                </button>
              </Badge>
            ))}
          </div>
        </div>

        {/* Current Medications */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            Current Medications {context.currentMedications.length > 0 && (
              <Badge variant="secondary" className="ml-2">
                {context.currentMedications.length}
              </Badge>
            )}
          </label>
          <div className="flex gap-2 mb-2">
            <Input
              placeholder="e.g., Metformin, Lisinopril"
              value={newMedication}
              onChange={(e) => setNewMedication(e.target.value)}
              className="flex-1"
            />
            <Button
              onClick={() => addItem('currentMedications', newMedication, setNewMedication)}
              size="sm"
              variant="outline"
            >
              <Plus className="h-4 w-4" />
            </Button>
          </div>
          <div className="flex flex-wrap gap-2">
            {context.currentMedications.map((medication, index) => (
              <Badge
                key={index}
                variant="secondary"
                className="bg-purple-100 text-purple-800 border-purple-200"
              >
                {medication}
                <button
                  onClick={() => removeItem('currentMedications', index)}
                  className="ml-1 hover:bg-purple-200 rounded-full p-0.5"
                >
                  <X className="h-3 w-3" />
                </button>
              </Badge>
            ))}
          </div>
        </div>

        {/* Additional Context */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">Pregnancy Status</label>
            <select
              className="w-full px-3 py-2 border border-slate-300 rounded-md text-sm"
              value={context.pregnancyStatus || ''}
              onChange={(e) => updateContext({ pregnancyStatus: e.target.value || undefined })}
            >
              <option value="">Not applicable</option>
              <option value="pregnant">Pregnant</option>
              <option value="breastfeeding">Breastfeeding</option>
              <option value="not_pregnant">Not pregnant</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">Clinical Setting</label>
            <select
              className="w-full px-3 py-2 border border-slate-300 rounded-md text-sm"
              value={context.setting || ''}
              onChange={(e) => updateContext({ setting: e.target.value || undefined })}
            >
              <option value="">Select setting</option>
              <option value="hospital">Hospital</option>
              <option value="clinic">Clinic</option>
              <option value="emergency">Emergency Room</option>
              <option value="icu">ICU</option>
              <option value="home">Home Care</option>
            </select>
          </div>
        </div>

        {/* Risk Assessment Summary */}
        <Card className="bg-slate-50 border-slate-200">
          <CardContent className="p-4">
            <div className="flex items-center gap-2 mb-2">
              <AlertTriangle className="h-4 w-4 text-slate-600" />
              <span className="text-sm font-medium text-slate-700">Risk Assessment</span>
            </div>
            <div className="text-sm text-slate-600 space-y-1">
              <p>• Age Group: {getAgeGroup(context.age)}</p>
              {context.allergies.length > 0 && (
                <p>• {context.allergies.length} known allergies - check contraindications</p>
              )}
              {context.medicalHistory.length > 0 && (
                <p>• {context.medicalHistory.length} medical conditions - monitor interactions</p>
              )}
              {context.currentMedications.length > 0 && (
                <p>• {context.currentMedications.length} current medications - check drug interactions</p>
              )}
              {context.pregnancyStatus === 'pregnant' && (
                <p>• Pregnant patient - fetal safety considerations</p>
              )}
            </div>
          </CardContent>
        </Card>
      </CardContent>
    </Card>
  );
}
