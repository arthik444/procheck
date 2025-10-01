import { Card, CardContent } from '@/components/ui/card';
import { Stethoscope, User, Microscope, Activity, AlertTriangle, Shield, Clock, CheckCircle, Info } from 'lucide-react';
import { Message } from '@/types';
import ProtocolCard from './ProtocolCard';

interface ChatMessageProps {
  message: Message;
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const getIntentIcon = (intent: string) => {
    switch (intent) {
      case 'emergency': return <AlertTriangle className="h-5 w-5" />;
      case 'symptom_based': return <Activity className="h-5 w-5" />;
      case 'procedure_based': return <Stethoscope className="h-5 w-5" />;
      case 'drug_based': return <Shield className="h-5 w-5" />;
      default: return <Info className="h-5 w-5" />;
    }
  };

  const getIntentColor = (intent: string) => {
    switch (intent) {
      case 'emergency': return 'text-red-700 bg-red-50 border-red-200';
      case 'symptom_based': return 'text-blue-700 bg-blue-50 border-blue-200';
      case 'procedure_based': return 'text-purple-700 bg-purple-50 border-purple-200';
      case 'drug_based': return 'text-emerald-700 bg-emerald-50 border-emerald-200';
      default: return 'text-slate-700 bg-slate-50 border-slate-200';
    }
  };

  const getIntentLabel = (intent: string) => {
    switch (intent) {
      case 'emergency': return 'Emergency Protocol';
      case 'symptom_based': return 'Symptom-Based Analysis';
      case 'procedure_based': return 'Medical Procedure';
      case 'drug_based': return 'Medication Protocol';
      default: return 'Medical Protocol';
    }
  };

  if (message.type === 'user') {
    return (
      <div className="flex justify-end mb-6">
        <div className="max-w-[80%]">
          <div className="flex items-end space-x-2">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-teal-600 rounded-full flex items-center justify-center">
                <User className="h-4 w-4 text-white" />
              </div>
            </div>
            <Card className="bg-teal-600 text-white border-teal-600">
              <CardContent className="p-4">
                <p className="text-sm whitespace-pre-wrap">{message.content}</p>
              </CardContent>
            </Card>
          </div>
          <p className="text-xs text-slate-500 mt-1 text-right">
            {formatTime(message.timestamp)}
          </p>
        </div>
      </div>
    );
  }

  const medicalIntelligence = message.protocolData?.medicalIntelligence;
  const intent = medicalIntelligence?.intent || 'general';

  return (
    <div className="flex justify-start mb-6">
      <div className="max-w-[90%]">
        <div className="flex items-start space-x-3">
          <div className="flex-shrink-0">
            <div className="w-10 h-10 rounded-full flex items-center justify-center bg-white border-2 border-slate-200 shadow-sm">
              <div className={getIntentColor(intent).split(' ')[0]}>
                {getIntentIcon(intent)}
              </div>
            </div>
          </div>
          <div className="flex-1">
            <div className="flex items-center space-x-2 mb-3">
              <div className="flex items-center space-x-2">
                <h4 className="font-semibold text-slate-900">ProCheck Medical Assistant</h4>
                <div className={`px-2 py-1 rounded-full text-xs font-medium border ${getIntentColor(intent)}`}>
                  {getIntentLabel(intent)}
                </div>
              </div>
              <span className="text-xs text-slate-500">{formatTime(message.timestamp)}</span>
            </div>
            
            {message.content && (
              <Card className={`mb-4 shadow-sm border-l-4 ${getIntentColor(intent).includes('red') ? 'border-l-red-400' : 
                getIntentColor(intent).includes('blue') ? 'border-l-blue-400' :
                getIntentColor(intent).includes('purple') ? 'border-l-purple-400' :
                getIntentColor(intent).includes('emerald') ? 'border-l-emerald-400' : 'border-l-slate-400'}`}>
                <CardContent className="p-4">
                  <div className="flex items-start space-x-3">
                    <div className="p-2 bg-slate-100 rounded-lg flex-shrink-0">
                      <Info className="h-4 w-4 text-slate-600" />
                    </div>
                    <div className="flex-1">
                      <p className="text-sm text-slate-700 whitespace-pre-wrap leading-relaxed">
                        {message.content}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
            
            {message.protocolData && (
              <ProtocolCard protocolData={message.protocolData} />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
