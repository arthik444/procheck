import { useState, useRef, useEffect } from 'react';
import { Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Menu, X, Stethoscope } from 'lucide-react';
import LandingScreen from '@/components/LandingScreen';
import Sidebar from '@/components/Sidebar';
import ChatInput from '@/components/ChatInput';
import ChatMessage from '@/components/ChatMessage';
import LoginPage from '@/components/auth/LoginPage';
import SignupPage from '@/components/auth/SignupPage';
import ForgotPasswordPage from '@/components/auth/ForgotPasswordPage';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import { Message, ProtocolData } from '@/types';
import { useAuth } from '@/contexts/AuthContext';
import { generateIntelligentProtocol, saveConversation, ConversationMessage } from '@/lib/api';

function App() {
  const { currentUser } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentConversationId, setCurrentConversationId] = useState<string>(() =>
    `conv_${Date.now()}`
  );
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleStartSearch = () => {
    if (currentUser) {
      navigate('/dashboard');
      setIsSidebarOpen(true);
    } else {
      navigate('/login');
    }
  };

  const handleSampleQuery = (query: string) => {
    if (currentUser) {
      navigate('/dashboard');
      setIsSidebarOpen(true);
      setTimeout(() => {
        handleSendMessage(query);
      }, 100);
    } else {
      navigate('/login');
    }
  };




  // Helper function to get user's local timestamp in backend format
  const getUserTimestamp = () => {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');
    const ms = String(now.getMilliseconds()).padStart(3, '0');

    return `${year}-${month}-${day}T${hours}:${minutes}:${seconds}.${ms}`;
  };

  // Helper function to save conversation
  const saveCurrentConversation = async (updatedMessages: Message[], lastQuery: string) => {
    if (!currentUser) return;

    try {
      const conversationMessages: ConversationMessage[] = updatedMessages.map(msg => ({
        id: msg.id,
        type: msg.type as 'user' | 'assistant',
        content: msg.content,
        timestamp: msg.timestamp, // Preserve original message timestamp
        protocol_data: msg.protocolData || undefined,
      }));

      // Use the first message timestamp as conversation created_at
      const firstMessageTimestamp = updatedMessages.length > 0 ? updatedMessages[0].timestamp : getUserTimestamp();

      await saveConversation(currentUser.uid, {
        id: currentConversationId,
        title: lastQuery.length > 50 ? lastQuery.substring(0, 50) + '...' : lastQuery,
        messages: conversationMessages,
        last_query: lastQuery,
        tags: ['medical-protocol'],
        created_at: firstMessageTimestamp,
      });
    } catch (error) {
      console.error('Failed to save conversation:', error);
    }
  };

  const handleSendMessage = async (content: string) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content,
      timestamp: getUserTimestamp(),
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Use the new intelligent protocol generation service
      const result = await generateIntelligentProtocol(content, 8);

      if (result.error) {
        throw new Error(result.details || result.error);
      }

      // Extract the generated protocol data
      const protocolData: ProtocolData = result.protocol_data;
      const responseContent = result.response_content;

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: responseContent,
        timestamp: getUserTimestamp(),
        protocolData,
      };

      setMessages(prev => {
        const newMessages = [...prev, assistantMessage];
        // Save conversation asynchronously
        saveCurrentConversation(newMessages, content);
        return newMessages;
      });
    } catch (err: any) {
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: `Sorry, I couldn't process that request. ${err?.message || ''}`.trim(),
        timestamp: getUserTimestamp(),
      };
      setMessages(prev => {
        const newMessages = [...prev, assistantMessage];
        // Save conversation even on error
        saveCurrentConversation(newMessages, content);
        return newMessages;
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewSearch = () => {
    setMessages([]);
    setCurrentConversationId(`conv_${Date.now()}`); // Generate new conversation ID
  };

  const handleRecentSearch = (query: string) => {
    handleSendMessage(query);
  };

  const handleSavedProtocol = (protocolId: string) => {
    console.log('Loading saved protocol:', protocolId);
  };

  const handleAuthSuccess = () => {
    const from = location.state?.from?.pathname || '/dashboard';
    navigate(from, { replace: true });
  };

  const Dashboard = () => (
    <div className="h-screen flex bg-slate-50">
      {isSidebarOpen && (
        <>
          <div 
            className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
            onClick={() => setIsSidebarOpen(false)}
          />
          <div className="fixed lg:relative lg:translate-x-0 inset-y-0 left-0 z-50 lg:z-auto">
            <Sidebar
              onNewSearch={handleNewSearch}
              onRecentSearch={handleRecentSearch}
              onSavedProtocol={handleSavedProtocol}
            />
          </div>
        </>
      )}
      <div className="flex-1 flex flex-col h-full">
        <header className="bg-white border-b border-slate-200 px-4 py-3 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="lg:hidden"
            >
              {isSidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </Button>
            <h1 className="text-lg font-semibold text-slate-900">ProCheck Protocol Assistant</h1>
          </div>
          <Button
            variant="outline"
            onClick={() => navigate('/')}
            className="text-slate-600"
          >
            Back to Home
          </Button>
        </header>
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 && (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <div className="w-20 h-20 bg-teal-100 rounded-full flex items-center justify-center mx-auto mb-6">
                  <Stethoscope className="h-10 w-10 text-teal-600" />
                </div>
                <h2 className="text-2xl font-semibold text-slate-900 mb-2">
                  Welcome to ProCheck
                </h2>
                <p className="text-slate-600 mb-6 max-w-md">
                  Ask me about any medical protocol, procedure, or treatment guideline. 
                  I'll provide you with comprehensive, clinically cited information.
                </p>
                <div className="flex flex-wrap gap-2 justify-center">
                  <Button
                    variant="outline"
                    onClick={() => handleSampleQuery("Checklist for pediatric asthma, Mumbai 2024")}
                    className="text-sm"
                  >
                    Pediatric Asthma Protocol
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => handleSampleQuery("Dengue fever protocol Delhi guidelines")}
                    className="text-sm"
                  >
                    Dengue Fever Protocol
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => handleSampleQuery("COVID-19 treatment WHO protocol 2024")}
                    className="text-sm"
                  >
                    COVID-19 Treatment
                  </Button>
                </div>
              </div>
            </div>
          )}
          {messages.map((message) => (
            <ChatMessage key={message.id} message={message} />
          ))}
          {isLoading && (
            <div className="flex justify-start">
              <div className="max-w-[90%]">
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0">
                    <div className="w-10 h-10 bg-slate-100 rounded-full flex items-center justify-center">
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-teal-600"></div>
                    </div>
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <h4 className="font-semibold text-slate-900">ProCheck Protocol Assistant</h4>
                    </div>
                    <div className="bg-slate-50 border border-slate-200 rounded-lg p-4">
                      <p className="text-sm text-slate-600">
                        Analyzing medical guidelines and synthesizing protocol...
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
        <ChatInput 
          onSendMessage={handleSendMessage}
          isLoading={isLoading}
        />
      </div>
    </div>
  );

  return (
    <Routes>
      <Route path="/" element={<LandingScreen onStartSearch={handleStartSearch} onSampleQuery={handleSampleQuery} />} />
      <Route path="/login" element={<LoginPage onLoginSuccess={handleAuthSuccess} />} />
      <Route path="/signup" element={<SignupPage onSignupSuccess={handleAuthSuccess} />} />
      <Route path="/forgot-password" element={<ForgotPasswordPage />} />
      <Route path="/dashboard" element={
        <ProtectedRoute>
          <Dashboard />
        </ProtectedRoute>
      } />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
