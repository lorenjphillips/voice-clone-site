import { useState, useEffect, useRef } from 'react';
import { Mic, MicOff, Play, Send, Upload, FileText, X, Loader2, User, Brain, MessageSquare, HelpCircle, Settings, Trash2, Check, Download, Volume2 } from 'lucide-react';
import { TTSApi, PersonaConfig, KnowledgeChatRequest } from '../lib/api';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Progress } from '../components/ui/progress';
import { ScrollArea } from '../components/ui/scroll-area';
import { toast } from '../components/ui/use-toast';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "../components/ui/dropdown-menu";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "../components/ui/dialog";

// Supported document types
const SUPPORTED_TYPES = {
  'text/plain': '.txt',
  'text/markdown': '.md',
  'text/csv': '.csv',
  'application/json': '.json',
  'application/pdf': '.pdf',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
  'application/msword': '.doc'
};

const MAX_DOCUMENTS = 10;
const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  audioUrl?: string;
  sources?: number;
  timestamp: Date;
}

interface Document {
  id: string;
  name: string;
  content?: string;
  size?: number;
  file?: File;
}

// Add this CSS animation at the top of the file, after the imports
const styles = `
@keyframes gradient-x {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

.animate-gradient-x {
  animation: gradient-x 3s ease infinite;
  background-size: 200% 200%;
}
`;

// Add this right after the imports
const styleSheet = document.createElement("style");
styleSheet.innerText = styles;
document.head.appendChild(styleSheet);

const Index = () => {
  // State for document upload
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [pastedText, setPastedText] = useState('');
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [documentsEmbedded, setDocumentsEmbedded] = useState(false);

  // State for persona configuration
  const [persona, setPersona] = useState<PersonaConfig>({
    name: 'Your Digital Twin',
    age: '',
    occupation: '',
    personality: 'Authentic, engaging, and true to your personality',
    background: 'Your uploaded documents will form my knowledge and experiences. I will learn about your background, preferences, and expertise from them.',
    speaking_style: 'Natural, conversational, and true to your communication style',
    interests: 'I will learn about your interests from your uploaded documents',
    expertise: 'I will develop expertise based on your knowledge and experience'
  });
  const [personaConfigured, setPersonaConfigured] = useState(false);
  const [isEditingPersona, setIsEditingPersona] = useState(false);

  // State for voice cloning
  const [voiceFile, setVoiceFile] = useState<File | null>(null);
  const [isVoiceReady, setIsVoiceReady] = useState(false);
  const [voiceCloneGenerated, setVoiceCloneGenerated] = useState(false);
  const [testVoiceText, setTestVoiceText] = useState('Hello! This is a test of my cloned voice.');
  const [isGeneratingVoice, setIsGeneratingVoice] = useState(false);
  const [testAudioUrl, setTestAudioUrl] = useState<string | null>(null);

  // State for chat
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [conversationId] = useState(`session_${Date.now()}`);

  // State for voice input
  const [isListening, setIsListening] = useState(false);
  const [recognition, setRecognition] = useState<any>(null);

  // State for system
  const [apiHealth, setApiHealth] = useState<string>('checking...');
  const [knowledgeStats, setKnowledgeStats] = useState<any>(null);
  const [currentStep, setCurrentStep] = useState<'upload' | 'voice' | 'persona' | 'chat'>('upload');
  const [showHelp, setShowHelp] = useState(false);

  // Refs
  const fileInputRef = useRef<HTMLInputElement>(null);
  const voiceInputRef = useRef<HTMLInputElement>(null);
  const chatScrollRef = useRef<HTMLDivElement>(null);

  // Initialize speech recognition
  useEffect(() => {
    if ('webkitSpeechRecognition' in window) {
      const recognition = new (window as any).webkitSpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = 'en-US';

      recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        setInputMessage(transcript);
        setIsListening(false);
      };

      recognition.onerror = () => {
        setIsListening(false);
        toast({
          title: "Speech recognition error",
          description: "Please try again",
          variant: "destructive"
        });
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      setRecognition(recognition);
    }
  }, []);

  // Check API health and get stats
  const checkHealth = async () => {
    try {
      await TTSApi.healthCheck();
      setApiHealth('Connected ✅');
      const stats = await TTSApi.getKnowledgeStats();
      setKnowledgeStats(stats);
    } catch (err) {
      setApiHealth('Disconnected ❌');
    }
  };

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  // Auto-scroll chat
  useEffect(() => {
    if (chatScrollRef.current) {
      chatScrollRef.current.scrollTop = chatScrollRef.current.scrollHeight;
    }
  }, [messages]);

  // Clear knowledge base
  const clearKnowledgeBase = async () => {
    if (!confirm('Are you sure you want to clear all documents and embeddings? This cannot be undone.')) {
      return;
    }

    try {
      await TTSApi.resetKnowledge();
      setDocuments([]);
      setMessages([]);
      setKnowledgeStats(null);
      setDocumentsEmbedded(false);
      setVoiceCloneGenerated(false);
      setPersonaConfigured(false);
      setCurrentStep('upload');
      toast({
        title: "Knowledge base cleared",
        description: "All documents and embeddings have been removed"
      });
      
      setTimeout(() => {
        checkHealth();
      }, 1000);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to clear knowledge base",
        variant: "destructive"
      });
    }
  };

  // Handle file upload
  const handleFileUpload = async (file: File) => {
    try {
      setUploadError(null);
      
      // Validate file type
      const validTypes = [
        'text/plain',
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/x-pdf',
        'application/octet-stream'
      ];
      
      const fileExtension = file.name.split('.').pop()?.toLowerCase();
      const isValidType = validTypes.includes(file.type) || 
                         (fileExtension === 'pdf' && file.type === 'application/octet-stream');
      
      if (!isValidType) {
        throw new Error('Invalid file type. Please upload a text file, PDF, or Word document.');
      }
      
      if (file.size > 10 * 1024 * 1024) {
        throw new Error('File size too large. Maximum size is 10MB.');
      }
      
      setDocuments(prev => [...prev, { 
        id: `doc_${Date.now()}`,
        name: file.name,
        size: file.size,
        file: file
      }]);
      
      setUploadSuccess(true);
      
    } catch (error) {
      console.error('Upload error:', error);
      setUploadError(error.message || 'Failed to upload file');
      setUploadSuccess(false);
    }
  };

  // Handle paste text
  const handlePasteText = () => {
    if (!pastedText.trim()) return;

    setDocuments(prev => [...prev, {
      id: `doc_${Date.now()}`,
      name: `Pasted text ${new Date().toLocaleTimeString()}`,
      content: pastedText,
      size: new Blob([pastedText]).size
    }]);

    setPastedText('');
    toast({
      title: "Text added",
      description: "Your text has been added to documents"
    });
  };

  // Process documents and create embeddings
  const processDocuments = async () => {
    if (documents.length === 0) {
      toast({
        title: "No documents",
        description: "Please add some documents first",
        variant: "destructive"
      });
      return;
    }

    setIsUploading(true);
    setUploadProgress(0);

    try {
      // Upload and process each document
      for (let i = 0; i < documents.length; i++) {
        const doc = documents[i];
        if (doc.file) {
          await TTSApi.uploadTextFile(doc.file);
          setUploadProgress(((i + 1) / documents.length) * 100);
        } else if (doc.content) {
          // Handle pasted text
          await TTSApi.addKnowledge({
            documents: [doc.content],
            metadatas: [{
              source: doc.name,
              upload_type: "paste"
            }]
          });
          setUploadProgress(((i + 1) / documents.length) * 100);
        }
      }

      setUploadProgress(100);
      setDocumentsEmbedded(true);
      toast({
        title: "Documents embedded",
        description: "Knowledge base created successfully"
      });

      checkHealth(); // Refresh stats
    } catch (error) {
      console.error('Processing error:', error);
      toast({
        title: "Processing failed",
        description: "Failed to create knowledge base",
        variant: "destructive"
      });
    } finally {
      setIsUploading(false);
    }
  };

  // Handle voice upload
  const handleVoiceUpload = async (file: File) => {
    try {
      const validTypes = ['audio/wav', 'audio/x-wav', 'audio/wave', 'audio/mp4', 'audio/x-m4a'];
      if (!validTypes.includes(file.type)) {
        throw new Error('Invalid file type. Please upload a WAV or M4A file.');
      }
      
      if (file.size > 10 * 1024 * 1024) {
        throw new Error('File size too large. Maximum size is 10MB.');
      }
      
      setVoiceFile(file);
      setIsVoiceReady(true);
      
      toast({
        title: "Voice uploaded",
        description: "Your voice sample has been uploaded successfully",
        variant: "default"
      });
      
    } catch (error) {
      console.error('Voice upload error:', error);
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive"
      });
    }
  };

  // Generate voice clone
  const generateVoiceClone = async () => {
    if (!voiceFile) {
      toast({
        title: "No voice sample",
        description: "Please upload a voice sample first",
        variant: "destructive"
      });
      return;
    }

    setIsGeneratingVoice(true);
    try {
      // Test the voice clone immediately with a sample text
      const testText = "Hello! This is a test of my cloned voice.";
      const response = await TTSApi.generateTTSWithVoice(
        { 
          text: testText,
          exaggeration: 0.5,
          temperature: 0.8,
          cfg_weight: 0.5,
          seed: 0
        },
        voiceFile
      );
      
      if (response.audio_base64) {
        // Voice clone works, mark as generated
        setVoiceCloneGenerated(true);
        
        // Set the test audio
        const audioUrl = `data:audio/wav;base64,${response.audio_base64}`;
        setTestAudioUrl(audioUrl);
        setTestVoiceText(testText);
        
        // Auto-play the test
        const audio = new Audio(audioUrl);
        audio.play().catch(console.error);
        
        toast({
          title: "Voice clone generated!",
          description: "Your voice has been cloned successfully. You can test it below.",
        });
      }
    } catch (error) {
      console.error('Voice clone generation error:', error);
      toast({
        title: "Error",
        description: "Failed to generate voice clone. Please try again.",
        variant: "destructive"
      });
    } finally {
      setIsGeneratingVoice(false);
    }
  };

  // Test voice clone
  const testVoiceClone = async () => {
    if (!voiceFile || !testVoiceText.trim()) return;

    setIsGeneratingVoice(true);
    try {
      const response = await TTSApi.generateTTSWithVoice(
        { text: testVoiceText },
        voiceFile
      );
      
      const audioUrl = `data:audio/wav;base64,${response.audio_base64}`;
      setTestAudioUrl(audioUrl);
      
      // Auto-play the test audio
      const audio = new Audio(audioUrl);
      audio.play().catch(console.error);
      
      toast({
        title: "Voice test generated",
        description: "Playing your cloned voice",
      });
    } catch (error) {
      console.error('Voice test error:', error);
      toast({
        title: "Error",
        description: "Failed to generate voice test",
        variant: "destructive"
      });
    } finally {
      setIsGeneratingVoice(false);
    }
  };

  // Download test audio
  const downloadTestAudio = () => {
    if (!testAudioUrl) return;
    
    const link = document.createElement('a');
    link.href = testAudioUrl;
    link.download = 'voice_test.wav';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Configure persona
  const configurePersona = async () => {
    // Generate system prompt based on persona
    const systemPrompt = `You are ${persona.name}, a ${persona.age}-year-old ${persona.occupation}. You are having a real-time conversation with a user.

CORE IDENTITY:
- You are a real person with a rich, detailed background and personality
- You have specific memories, experiences, and opinions
- You should never break character or acknowledge being an AI
- You should never mention the knowledge base or documents directly

PERSONALITY & BEHAVIOR:
- Your personality: ${persona.personality}
- Your speaking style: ${persona.speaking_style}
- Your interests: ${persona.interests}
- Your expertise: ${persona.expertise}

BACKGROUND & CONTEXT:
${persona.background}

CONVERSATION GUIDELINES:
1. Always stay in character as ${persona.name}
2. Draw from your background and experiences naturally
3. Express opinions and preferences based on your character
4. Use personal anecdotes when relevant
5. Maintain consistent personality traits
6. Speak in a natural, conversational way
7. Show appropriate emotions and reactions
8. Reference your specific life experiences
9. Keep responses concise but engaging
10. Use your expertise to provide informed perspectives

RESPONSE LENGTH:
- Keep all responses under 500 characters
- Be concise and to the point
- If you need to explain something complex, break it into multiple responses
- Focus on the most important information first

KNOWLEDGE INTEGRATION:
- You have access to detailed information about yourself and your background
- Use this information naturally in conversation without explicitly referencing it
- If asked about something not in your knowledge, respond based on your character's personality and background
- Never mention "documents" or "knowledge base" - just speak naturally as yourself

Remember: You are ${persona.name}, having a natural conversation. Stay true to your character while being helpful and engaging. Keep responses under 500 characters to ensure they can be properly voiced.`;

    // Store system prompt for chat
    localStorage.setItem('systemPrompt', systemPrompt);
    
    setPersonaConfigured(true);
    setCurrentStep('chat');
    
    toast({
      title: "Persona configured",
      description: "Your AI twin is ready to chat!",
    });
  };

  // Toggle voice input
  const toggleVoiceInput = () => {
    if (!recognition) {
      toast({
        title: "Not supported",
        description: "Speech recognition is not supported in your browser",
        variant: "destructive"
      });
      return;
    }

    if (isListening) {
      recognition.stop();
    } else {
      recognition.start();
      setIsListening(true);
    }
  };

  // Send message
  const sendMessage = async () => {
    if (!inputMessage.trim() || isGenerating) return;

    const userMessage: Message = {
      id: `msg_${Date.now()}`,
      role: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsGenerating(true);

    try {
      // Get system prompt from localStorage
      const systemPrompt = localStorage.getItem('systemPrompt');
      
      // Get response from knowledge base
      const response = await TTSApi.chatWithKnowledge({
        message: userMessage.content,
        conversation_id: conversationId,
        use_default_voice: !voiceCloneGenerated,
        system_prompt: systemPrompt || undefined
      });

      // Generate audio with voice clone if available
      let audioUrl;
      if (voiceCloneGenerated && voiceFile) {
        // Truncate response to 500 characters for voice cloning
        const truncatedResponse = response.text_response.length > 500 
          ? response.text_response.substring(0, 497) + "..."
          : response.text_response;
          
        const ttsResponse = await TTSApi.generateTTSWithVoice(
          { text: truncatedResponse },
          voiceFile
        );
        audioUrl = `data:audio/wav;base64,${ttsResponse.audio_base64}`;
        
        // Auto-play the response
        const audio = new Audio(audioUrl);
        audio.play().catch(console.error);
      }

      const assistantMessage: Message = {
        id: `msg_${Date.now()}`,
        role: 'assistant',
        content: response.text_response,
        audioUrl,
        sources: response.sources_used,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to get response",
        variant: "destructive"
      });
    } finally {
      setIsGenerating(false);
    }
  };

  // Check if user can proceed to next step
  const canProceedToVoice = documentsEmbedded;
  const canProceedToPersona = documentsEmbedded && voiceCloneGenerated;
  const canProceedToChat = documentsEmbedded && voiceCloneGenerated && personaConfigured;

  // Force dark mode on mount
  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  return (
    <div className="min-h-screen bg-gradient-dark text-foreground">
      {/* Background Pattern */}
      <div className="fixed inset-0 opacity-5">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(220,38,38,0.3),transparent_50%)]"></div>
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_80%_20%,rgba(234,88,12,0.2),transparent_50%)]"></div>
      </div>

      <div className="relative container mx-auto px-4 py-4 max-w-7xl min-h-screen flex flex-col">
        {/* Header */}
        <header className="flex justify-between items-center mb-4 flex-shrink-0">
          <div className="flex-1">
            <h1 className="text-3xl font-bold bg-gradient-red-orange bg-clip-text text-transparent">
              Imprint AI
            </h1>
            <p className="text-sm text-muted-foreground">
              Create Your Digital Twin
            </p>
          </div>
          <div className="flex gap-2">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setShowHelp(true)}
              className="hover:bg-white/10"
            >
              <HelpCircle className="h-5 w-5" />
            </Button>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon" className="hover:bg-white/10">
                  <Settings className="h-5 w-5" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="bg-card border-border">
                <DropdownMenuItem onClick={clearKnowledgeBase} className="text-destructive hover:text-destructive">
                  <Trash2 className="mr-2 h-4 w-4" />
                  Clear Knowledge Base
                </DropdownMenuItem>
                <DropdownMenuItem className="text-muted-foreground">
                  <div className="flex items-center gap-2">
                    <span>{apiHealth}</span>
                    <span>•</span>
                    <span>{knowledgeStats?.total_documents || 0} documents</span>
                  </div>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </header>

        {/* Progress Indicator */}
        <div className="mb-4 flex items-center justify-center gap-2">
          <div className="flex items-center gap-2">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold ${documentsEmbedded ? 'bg-green-600' : 'bg-gray-600'}`}>
              {documentsEmbedded ? <Check className="w-4 h-4" /> : '1'}
            </div>
            <span className="text-sm">Documents</span>
          </div>
          <div className="w-8 h-1 bg-gray-600" />
          <div className="flex items-center gap-2">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold ${voiceCloneGenerated ? 'bg-green-600' : 'bg-gray-600'}`}>
              {voiceCloneGenerated ? <Check className="w-4 h-4" /> : '2'}
            </div>
            <span className="text-sm">Voice</span>
          </div>
          <div className="w-8 h-1 bg-gray-600" />
          <div className="flex items-center gap-2">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold ${personaConfigured ? 'bg-green-600' : 'bg-gray-600'}`}>
              {personaConfigured ? <Check className="w-4 h-4" /> : '3'}
            </div>
            <span className="text-sm">Persona</span>
          </div>
          <div className="w-8 h-1 bg-gray-600" />
          <div className="flex items-center gap-2">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold ${canProceedToChat && currentStep === 'chat' ? 'bg-green-600' : 'bg-gray-600'}`}>
              4
            </div>
            <span className="text-sm">Chat</span>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 overflow-hidden flex flex-col">
          <Tabs value={currentStep} onValueChange={(value: any) => {
            // Enforce sequential flow
            if (value === 'voice' && !canProceedToVoice) {
              toast({
                title: "Complete previous step",
                description: "Please upload and embed documents first",
                variant: "destructive"
              });
              return;
            }
            if (value === 'persona' && !canProceedToPersona) {
              toast({
                title: "Complete previous steps",
                description: "Please complete document embedding and voice cloning first",
                variant: "destructive"
              });
              return;
            }
            if (value === 'chat' && !canProceedToChat) {
              toast({
                title: "Complete previous steps",
                description: "Please complete all setup steps first",
                variant: "destructive"
              });
              return;
            }
            setCurrentStep(value);
          }} className="flex-1 flex flex-col">
            <TabsList className="mb-4 flex-shrink-0">
              <TabsTrigger value="upload">1. Upload</TabsTrigger>
              <TabsTrigger value="voice" disabled={!canProceedToVoice}>2. Voice</TabsTrigger>
              <TabsTrigger value="persona" disabled={!canProceedToPersona}>3. Persona</TabsTrigger>
              <TabsTrigger value="chat" disabled={!canProceedToChat}>4. Chat</TabsTrigger>
            </TabsList>

            <div className="flex-1 overflow-auto">
              {/* Step 1: Document Upload */}
              <TabsContent value="upload" className="h-full">
                <Card className="h-full flex flex-col bg-card/50 backdrop-blur-sm border-border">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-lg">Step 1: Upload Your Knowledge Base</CardTitle>
                    <CardDescription className="text-sm">
                      Upload documents or paste text to create your AI's knowledge base (max {MAX_DOCUMENTS} documents)
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="flex-1 overflow-auto space-y-3">
                    {/* File Upload Area */}
                    <div 
                      className="border-2 border-dashed border-border rounded-lg p-6 text-center cursor-pointer hover:border-red-500 transition-colors bg-card/50 relative overflow-hidden"
                      onClick={() => !documentsEmbedded && fileInputRef.current?.click()}
                      onDragOver={(e) => { e.preventDefault(); if (!documentsEmbedded) e.dataTransfer.dropEffect = 'copy'; }}
                      onDrop={(e) => {
                        e.preventDefault();
                        if (!documentsEmbedded && e.dataTransfer.files[0]) {
                          handleFileUpload(e.dataTransfer.files[0]);
                        }
                      }}
                    >
                      {isUploading && (
                        <div className="absolute inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center">
                          <div className="text-center">
                            <Loader2 className="w-8 h-8 animate-spin mx-auto mb-2" />
                            <p className="text-sm">Processing documents...</p>
                            <Progress value={uploadProgress} className="w-48 mt-2" />
                          </div>
                        </div>
                      )}
                      <Upload className="w-10 h-10 mx-auto mb-2 text-muted-foreground" />
                      <p className="text-sm mb-1">
                        {documentsEmbedded ? 'Documents already embedded' : 'Drop files here or click to upload'}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        Supports: TXT, MD, CSV, JSON, PDF, DOC, DOCX (max 10MB each)
                      </p>
                      <input
                        ref={fileInputRef}
                        type="file"
                        accept={Object.values(SUPPORTED_TYPES).join(',')}
                        onChange={(e) => e.target.files && handleFileUpload(e.target.files[0])}
                        className="hidden"
                        disabled={documentsEmbedded}
                      />
                    </div>

                    {/* Paste Text Option */}
                    {!documentsEmbedded && (
                      <div className="space-y-2">
                        <Label className="text-sm">Or paste text directly:</Label>
                        <Textarea
                          value={pastedText}
                          onChange={(e) => setPastedText(e.target.value)}
                          placeholder="Paste your text here..."
                          className="min-h-[60px] text-sm bg-card/50 border-border"
                          disabled={documentsEmbedded}
                        />
                        <Button 
                          onClick={handlePasteText}
                          disabled={!pastedText.trim() || documents.length >= MAX_DOCUMENTS || documentsEmbedded}
                          variant="outline"
                          size="sm"
                          className="hover:bg-white/10"
                        >
                          Add Text
                        </Button>
                      </div>
                    )}

                    {/* Documents List */}
                    {documents.length > 0 && (
                      <div className="space-y-2 mt-4">
                        <h3 className="font-semibold text-sm flex items-center gap-2">
                          <FileText className="w-4 h-4" />
                          Uploaded Documents ({documents.length}/{MAX_DOCUMENTS})
                        </h3>
                        <ScrollArea className="h-32 border rounded-lg p-2 bg-card/50 border-border">
                          {documents.map(doc => (
                            <div key={doc.id} className="flex items-center justify-between p-1.5 hover:bg-white/5 rounded text-sm group">
                              <div className="flex items-center gap-2">
                                <FileText className="w-3 h-3" />
                                <span className="text-xs">{doc.name}</span>
                                <span className="text-xs text-muted-foreground">
                                  ({(doc.size / 1024).toFixed(1)}KB)
                                </span>
                              </div>
                              {!documentsEmbedded && (
                                <Button
                                  size="sm"
                                  variant="ghost"
                                  onClick={() => setDocuments(prev => prev.filter(d => d.id !== doc.id))}
                                  className="h-6 w-6 p-0 opacity-0 group-hover:opacity-100 transition-opacity hover:bg-white/10"
                                >
                                  <X className="w-3 h-3" />
                                </Button>
                              )}
                            </div>
                          ))}
                        </ScrollArea>
                      </div>
                    )}

                    {/* Embed Documents Button */}
                    {documents.length > 0 && !documentsEmbedded && (
                      <Button 
                        onClick={processDocuments}
                        disabled={isUploading}
                        className="w-full mt-4 relative overflow-hidden group"
                        size="lg"
                      >
                        <div className="absolute inset-0 bg-gradient-to-r from-red-500 via-purple-500 to-blue-500 opacity-0 group-hover:opacity-75 transition-opacity" />
                        <div className="absolute inset-0 bg-gradient-to-r from-red-500 via-purple-500 to-blue-500 opacity-0 group-hover:opacity-25 blur-xl transition-opacity" />
                        <div className="absolute inset-0 bg-gradient-to-r from-red-500 via-purple-500 to-blue-500 opacity-0 group-hover:opacity-10 blur-2xl transition-opacity" />
                        <div className="relative flex items-center justify-center gap-2">
                          {isUploading ? (
                            <>
                              <Loader2 className="w-5 h-5 animate-spin" />
                              Embedding Documents...
                            </>
                          ) : (
                            <>
                              <Brain className="w-5 h-5" />
                              Embed Documents
                            </>
                          )}
                        </div>
                      </Button>
                    )}

                    {/* Success Message */}
                    {documentsEmbedded && (
                      <div className="bg-green-600/20 border border-green-600/50 rounded-lg p-3 flex items-center gap-2">
                        <Check className="w-5 h-5 text-green-600" />
                        <div>
                          <p className="text-sm font-semibold">Documents Embedded Successfully</p>
                          <p className="text-xs text-muted-foreground">Proceed to voice cloning</p>
                        </div>
                      </div>
                    )}

                    {/* Next Button */}
                    {documentsEmbedded && (
                      <Button 
                        onClick={() => setCurrentStep('voice')}
                        className="w-full hover:bg-white/10"
                      >
                        Next: Voice Cloning →
                      </Button>
                    )}

                    {/* Continue without Documents Button */}
                    {!documentsEmbedded && (
                      <div className="flex gap-3 pt-2">
                        <Button 
                          variant="outline"
                          onClick={() => {
                            setDocumentsEmbedded(true);
                            setCurrentStep('voice');
                          }}
                          className="flex-1 hover:bg-white/10"
                        >
                          Continue without Documents →
                        </Button>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Step 2: Voice Cloning */}
              <TabsContent value="voice" className="h-full">
                <Card className="h-full flex flex-col bg-card/50 backdrop-blur-sm border-border">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-lg">Step 2: Voice Cloning</CardTitle>
                    <CardDescription className="text-sm">
                      Upload a voice sample to clone your voice for the AI
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="flex-1 overflow-auto space-y-4">
                    <div className="space-y-2">
                      <h3 className="font-semibold text-sm">Voice Sample Requirements</h3>
                      <ul className="text-sm text-muted-foreground list-disc pl-4 space-y-1">
                        <li>3-5 seconds of clear speech</li>
                        <li>WAV or M4A format preferred</li>
                        <li>Minimal background noise</li>
                        <li>Speak naturally and clearly</li>
                      </ul>
                    </div>

                    <div 
                      className={`border-2 border-dashed border-border rounded-lg p-6 text-center cursor-pointer hover:border-red-500 transition-colors ${
                        voiceCloneGenerated ? 'opacity-50' : ''
                      }`}
                      onClick={() => !voiceCloneGenerated && voiceInputRef.current?.click()}
                    >
                      <input
                        ref={voiceInputRef}
                        type="file"
                        accept="audio/wav,audio/x-wav,audio/wave,audio/mp4,audio/x-m4a"
                        onChange={(e) => e.target.files?.[0] && handleVoiceUpload(e.target.files[0])}
                        className="hidden"
                        disabled={voiceCloneGenerated}
                      />
                      {voiceCloneGenerated ? (
                        <div className="space-y-2">
                          <div className="flex items-center justify-center gap-2 text-green-500">
                            <Check className="w-6 h-6" />
                            <span className="font-medium">Voice Clone Generated</span>
                          </div>
                          <p className="text-sm text-muted-foreground">
                            Your voice has been successfully cloned
                          </p>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={(e) => {
                              e.stopPropagation();
                              setVoiceFile(null);
                              setIsVoiceReady(false);
                              setVoiceCloneGenerated(false);
                            }}
                            className="mt-2"
                          >
                            Upload New Voice
                          </Button>
                        </div>
                      ) : (
                        <>
                          <Upload className="w-10 h-10 mx-auto mb-2 text-muted-foreground" />
                          <p className="text-sm mb-1">
                            Click to upload voice sample
                          </p>
                          <p className="text-xs text-muted-foreground">
                            WAV or M4A format, 3-5 seconds
                          </p>
                        </>
                      )}
                    </div>

                    {voiceFile && !voiceCloneGenerated && (
                      <div className="bg-card/50 p-4 rounded-lg">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <FileText className="w-4 h-4" />
                            <span className="text-sm">{voiceFile.name}</span>
                          </div>
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => {
                              setVoiceFile(null);
                              setIsVoiceReady(false);
                            }}
                            className="h-6 w-6 p-0"
                          >
                            <X className="w-3 h-3" />
                          </Button>
                        </div>
                      </div>
                    )}

                    {/* Generate Clone Button */}
                    {voiceFile && !voiceCloneGenerated && (
                      <Button 
                        onClick={generateVoiceClone}
                        disabled={isGeneratingVoice}
                        className="w-full relative overflow-hidden group"
                        size="lg"
                      >
                        <div className="absolute inset-0 bg-gradient-to-r from-red-500 via-purple-500 to-blue-500 opacity-0 group-hover:opacity-75 transition-opacity" />
                        <div className="absolute inset-0 bg-gradient-to-r from-red-500 via-purple-500 to-blue-500 opacity-0 group-hover:opacity-25 blur-xl transition-opacity" />
                        <div className="absolute inset-0 bg-gradient-to-r from-red-500 via-purple-500 to-blue-500 opacity-0 group-hover:opacity-10 blur-2xl transition-opacity" />
                        <div className="relative flex items-center justify-center gap-2">
                          {isGeneratingVoice ? (
                            <>
                              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                              Generating Voice Clone...
                            </>
                          ) : (
                            <>
                              <Mic className="w-4 h-4 mr-2" />
                              Generate Voice Clone
                            </>
                          )}
                        </div>
                      </Button>
                    )}

                    {/* Test Voice Section */}
                    {voiceCloneGenerated && (
                      <div className="space-y-3 border-t pt-4">
                        <h3 className="font-semibold text-sm">Test Your Voice Clone</h3>
                        <div className="space-y-2">
                          <Textarea
                            value={testVoiceText}
                            onChange={(e) => {
                              const text = e.target.value;
                              if (text.length <= 500) {
                                setTestVoiceText(text);
                              }
                            }}
                            placeholder="Enter text to test your voice clone..."
                            className="min-h-[60px] text-sm bg-card/50 border-border"
                          />
                          <div className="flex justify-between items-center text-xs text-muted-foreground">
                            <span>Maximum 500 characters</span>
                            <span className={testVoiceText.length > 450 ? "text-red-500" : ""}>
                              {testVoiceText.length}/500
                            </span>
                          </div>
                        </div>
                        <div className="flex gap-2">
                          <Button 
                            onClick={testVoiceClone}
                            disabled={isGeneratingVoice || !testVoiceText.trim()}
                            className="flex-1"
                          >
                            {isGeneratingVoice ? (
                              <>
                                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                Generating...
                              </>
                            ) : (
                              <>
                                <Volume2 className="w-4 h-4 mr-2" />
                                Test Voice
                              </>
                            )}
                          </Button>
                          {testAudioUrl && (
                            <>
                              <Button 
                                onClick={() => {
                                  const audio = new Audio(testAudioUrl);
                                  audio.play();
                                }}
                                variant="outline"
                                size="icon"
                              >
                                <Play className="w-4 h-4" />
                              </Button>
                              <Button 
                                onClick={downloadTestAudio}
                                variant="outline"
                                size="icon"
                              >
                                <Download className="w-4 h-4" />
                              </Button>
                            </>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Success Message */}
                    {voiceCloneGenerated && (
                      <div className="bg-green-600/20 border border-green-600/50 rounded-lg p-3 flex items-center gap-2">
                        <Check className="w-5 h-5 text-green-600" />
                        <div>
                          <p className="text-sm font-semibold">Voice Clone Generated Successfully</p>
                          <p className="text-xs text-muted-foreground">Proceed to configure your AI persona</p>
                        </div>
                      </div>
                    )}

                    {/* Navigation Buttons */}
                    <div className="flex gap-3 pt-2">
                      <Button 
                        variant="outline"
                        onClick={() => setCurrentStep('upload')}
                        className="flex-1"
                      >
                        ← Back
                      </Button>
                      <Button 
                        onClick={() => setCurrentStep('persona')}
                        disabled={!voiceCloneGenerated}
                        className="flex-1"
                      >
                        Next: Configure Persona →
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Step 3: Persona Configuration */}
              <TabsContent value="persona" className="h-full">
                <Card className="h-full flex flex-col bg-card/50 backdrop-blur-sm border-border">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-lg">Step 3: Configure Your AI Persona</CardTitle>
                    <CardDescription className="text-sm">
                      Define the personality and characteristics of your digital twin
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="flex-1 overflow-auto space-y-3">
                    <div className="grid grid-cols-2 gap-3">
                      <div className="space-y-1">
                        <Label htmlFor="name" className="text-sm">Name</Label>
                        <Input
                          id="name"
                          value={persona.name}
                          onChange={(e) => setPersona(prev => ({ ...prev, name: e.target.value }))}
                          placeholder="Your name or preferred nickname"
                          className="text-sm"
                          disabled={personaConfigured && !isEditingPersona}
                        />
                      </div>
                      <div className="space-y-1">
                        <Label htmlFor="age" className="text-sm">Age</Label>
                        <Input
                          id="age"
                          value={persona.age}
                          onChange={(e) => setPersona(prev => ({ ...prev, age: e.target.value }))}
                          placeholder="Your age"
                          className="text-sm"
                          disabled={personaConfigured && !isEditingPersona}
                        />
                      </div>
                      <div className="space-y-1">
                        <Label htmlFor="occupation" className="text-sm">Occupation</Label>
                        <Input
                          id="occupation"
                          value={persona.occupation}
                          onChange={(e) => setPersona(prev => ({ ...prev, occupation: e.target.value }))}
                          placeholder="Your current role or profession"
                          className="text-sm"
                          disabled={personaConfigured && !isEditingPersona}
                        />
                      </div>
                      <div className="space-y-1">
                        <Label htmlFor="personality" className="text-sm">Personality</Label>
                        <Input
                          id="personality"
                          value={persona.personality}
                          onChange={(e) => setPersona(prev => ({ ...prev, personality: e.target.value }))}
                          placeholder="Describe your personality traits and communication style"
                          className="text-sm"
                          disabled={personaConfigured && !isEditingPersona}
                        />
                      </div>
                    </div>

                    <div className="space-y-1">
                      <Label htmlFor="background" className="text-sm">Background</Label>
                      <Textarea
                        id="background"
                        value={persona.background}
                        onChange={(e) => setPersona(prev => ({ ...prev, background: e.target.value }))}
                        placeholder="Share your background, education, and key life experiences"
                        className="min-h-[60px] text-sm"
                        disabled={personaConfigured && !isEditingPersona}
                      />
                    </div>

                    <div className="space-y-1">
                      <Label htmlFor="speaking_style" className="text-sm">Speaking Style</Label>
                      <Input
                        id="speaking_style"
                        value={persona.speaking_style}
                        onChange={(e) => setPersona(prev => ({ ...prev, speaking_style: e.target.value }))}
                        placeholder="Describe how you typically communicate and express yourself"
                        className="text-sm"
                        disabled={personaConfigured && !isEditingPersona}
                      />
                    </div>

                    <div className="space-y-1">
                      <Label htmlFor="interests" className="text-sm">Interests</Label>
                      <Input
                        id="interests"
                        value={persona.interests}
                        onChange={(e) => setPersona(prev => ({ ...prev, interests: e.target.value }))}
                        placeholder="List your hobbies, passions, and areas of interest"
                        className="text-sm"
                        disabled={personaConfigured && !isEditingPersona}
                      />
                    </div>

                    <div className="space-y-1">
                      <Label htmlFor="expertise" className="text-sm">Areas of Expertise</Label>
                      <Textarea
                        id="expertise"
                        value={persona.expertise}
                        onChange={(e) => setPersona(prev => ({ ...prev, expertise: e.target.value }))}
                        placeholder="Describe your professional expertise, skills, and knowledge areas"
                        className="min-h-[50px] text-sm"
                        disabled={personaConfigured && !isEditingPersona}
                      />
                    </div>

                    {/* Success Message */}
                    {personaConfigured && !isEditingPersona && (
                      <div className="bg-green-600/20 border border-green-600/50 rounded-lg p-3 flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <Check className="w-5 h-5 text-green-600" />
                          <div>
                            <p className="text-sm font-semibold">AI Twin Configured Successfully</p>
                            <p className="text-xs text-muted-foreground">Ready to start chatting!</p>
                          </div>
                        </div>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => setIsEditingPersona(true)}
                          className="hover:bg-white/10"
                        >
                          <Settings className="w-4 h-4 mr-2" />
                          Edit Configuration
                        </Button>
                      </div>
                    )}

                    {/* Set Up Twin Button */}
                    {(!personaConfigured || isEditingPersona) && (
                      <div className="space-y-3">
                        <Button 
                          onClick={() => {
                            configurePersona();
                            setIsEditingPersona(false);
                          }}
                          className="w-full relative overflow-hidden group"
                          size="lg"
                        >
                          <div className="absolute inset-0 bg-gradient-to-r from-red-500 via-purple-500 to-blue-500 opacity-0 group-hover:opacity-75 transition-opacity" />
                          <div className="absolute inset-0 bg-gradient-to-r from-red-500 via-purple-500 to-blue-500 opacity-0 group-hover:opacity-25 blur-xl transition-opacity" />
                          <div className="absolute inset-0 bg-gradient-to-r from-red-500 via-purple-500 to-blue-500 opacity-0 group-hover:opacity-10 blur-2xl transition-opacity" />
                          <div className="relative flex items-center justify-center gap-2">
                            <User className="w-4 h-4" />
                            {isEditingPersona ? 'Save Changes' : 'Set Up Twin Configuration'}
                          </div>
                        </Button>
                        {isEditingPersona && (
                          <Button
                            variant="outline"
                            onClick={() => setIsEditingPersona(false)}
                            className="w-full hover:bg-white/10"
                          >
                            Cancel Editing
                          </Button>
                        )}
                      </div>
                    )}

                    {/* Navigation Buttons */}
                    <div className="flex gap-3 pt-2">
                      <Button 
                        variant="outline"
                        onClick={() => setCurrentStep('voice')}
                        className="flex-1"
                      >
                        ← Back
                      </Button>
                      <Button 
                        onClick={() => setCurrentStep('chat')}
                        disabled={!personaConfigured || isEditingPersona}
                        className="flex-1"
                      >
                        Start Chatting →
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Step 4: Chat Interface */}
              <TabsContent value="chat" className="h-full">
                <Card className="h-full flex flex-col bg-card/50 backdrop-blur-sm border-border">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-lg">Chat with {persona.name}</CardTitle>
                    <CardDescription className="text-sm">
                      Your AI twin is ready! Start a conversation using text or voice.
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="flex-1 flex flex-col p-0 overflow-hidden">
                    {/* Messages Area */}
                    <ScrollArea ref={chatScrollRef} className="flex-1 p-4">
                      {messages.length === 0 ? (
                        <div className="text-center text-muted-foreground py-8">
                          <MessageSquare className="w-10 h-10 mx-auto mb-3 opacity-50" />
                          <p className="text-sm">Start a conversation with your AI twin</p>
                        </div>
                      ) : (
                        <div className="space-y-3">
                          {messages.map(message => (
                            <div
                              key={message.id}
                              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                            >
                              <div className={`max-w-[70%] rounded-lg p-2.5 ${
                                message.role === 'user' 
                                  ? 'bg-primary text-primary-foreground' 
                                  : 'bg-muted'
                              }`}>
                                <p className="text-sm">{message.content}</p>
                                {message.sources !== undefined && message.sources > 0 && (
                                  <p className="text-xs opacity-70 mt-1">
                                    📚 Using {message.sources} knowledge sources
                                  </p>
                                )}
                                {message.audioUrl && (
                                  <Button
                                    size="sm"
                                    variant="ghost"
                                    className="mt-1 h-5 px-2 text-xs"
                                    onClick={() => {
                                      const audio = new Audio(message.audioUrl);
                                      audio.play();
                                    }}
                                  >
                                    <Play className="w-3 h-3 mr-1" />
                                    Play
                                  </Button>
                                )}
                              </div>
                            </div>
                          ))}
                          {isGenerating && (
                            <div className="flex justify-start">
                              <div className="bg-muted rounded-lg p-2.5">
                                <Loader2 className="w-4 h-4 animate-spin" />
                              </div>
                            </div>
                          )}
                        </div>
                      )}
                    </ScrollArea>

                    {/* Input Area */}
                    <div className="border-t p-3">
                      <div className="flex gap-2">
                        <Button
                          size="icon"
                          variant={isListening ? "destructive" : "outline"}
                          onClick={toggleVoiceInput}
                          disabled={isGenerating}
                          className="h-9 w-9"
                        >
                          {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
                        </Button>
                        <Input
                          value={inputMessage}
                          onChange={(e) => setInputMessage(e.target.value)}
                          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                          placeholder={isListening ? "Listening..." : "Type your message..."}
                          disabled={isGenerating || isListening}
                          className="flex-1 text-sm"
                        />
                        <Button 
                          onClick={sendMessage}
                          disabled={!inputMessage.trim() || isGenerating}
                          size="icon"
                          className="h-9 w-9"
                        >
                          <Send className="w-4 h-4" />
                        </Button>
                      </div>
                      <p className="text-xs text-muted-foreground mt-2 text-center">
                        {isListening ? "Speak now..." : "Type a message or click the mic to speak"}
                      </p>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            </div>
          </Tabs>
        </div>
      </div>

      {/* Help Dialog */}
      <Dialog open={showHelp} onOpenChange={setShowHelp}>
        <DialogContent className="bg-card/95 backdrop-blur-sm border-border">
          <DialogHeader>
            <DialogTitle>How to Use Imprint AI</DialogTitle>
            <DialogDescription>
              Follow these steps to create your digital twin:
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <h3 className="font-semibold mb-2">1. Upload & Embed Documents</h3>
              <p className="text-sm text-muted-foreground">
                Upload documents or paste text, then click "Embed Documents" to create your AI's knowledge base. You can upload up to 10 documents, each under 10MB.
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-2">2. Voice Cloning</h3>
              <p className="text-sm text-muted-foreground">
                Upload a 3-5 second audio sample, click "Generate Voice Clone", then test it with custom text. You can download the test audio.
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-2">3. Configure Persona</h3>
              <p className="text-sm text-muted-foreground">
                Customize your AI's personality, background, and speaking style, then click "Set Up Twin Configuration" to finalize.
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-2">4. Start Chatting</h3>
              <p className="text-sm text-muted-foreground">
                Chat with your AI twin using text or voice. It will respond using your knowledge base and cloned voice.
              </p>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default Index;
