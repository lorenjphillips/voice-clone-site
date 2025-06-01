import { useState, useEffect } from 'react';
import { Mic, Play, Download } from 'lucide-react';
import ThemeToggle from '../components/ThemeToggle';
import VoiceSettings from '../components/VoiceSettings';
import FileUploadComponent from '../components/FileUpload';
import TipsSection from '../components/TipsSection';
import { TTSApi, TTSRequest } from '../lib/api';

const Index = () => {
  const [text, setText] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [voiceSettings, setVoiceSettings] = useState({
    exaggeration: 0.5,
    temperature: 0.8,
    cfgPace: 0.5,
    seed: 0,
  });
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [generatedAudio, setGeneratedAudio] = useState<{
    audioData: string;
    sampleRate: number;
  } | null>(null);
  const [apiHealth, setApiHealth] = useState<string>('checking...');

  const characterLimit = 300;

  // Check API health on component mount
  useEffect(() => {
    const checkHealth = async () => {
      try {
        await TTSApi.healthCheck();
        setApiHealth('Local Backend Server Running ✅ ');
        setError(null);
      } catch (err) {
        setApiHealth('API Disconnected');
        setError('Error: Cannot connect to TTS API. Make sure the backend server is running.');
      }
    };

    checkHealth();
    // Check health every 30 seconds
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleGenerate = async () => {
    if (!text.trim()) {
      alert('Please enter some text to generate speech');
      return;
    }

    setIsGenerating(true);
    setError(null);
    setGeneratedAudio(null);

    try {
      const request: TTSRequest = {
        text: text.trim(),
        exaggeration: voiceSettings.exaggeration,
        temperature: voiceSettings.temperature,
        cfg_weight: voiceSettings.cfgPace,
        seed: voiceSettings.seed,
      };

      let response;
      if (selectedFile) {
        response = await TTSApi.generateTTSWithVoice(request, selectedFile);
      } else {
        response = await TTSApi.generateTTS(request);
      }

      setGeneratedAudio({
        audioData: response.audio_base64,
        sampleRate: response.sample_rate,
      });

      setError(null);
    } catch (err) {
      console.error('TTS Generation Error:', err);
      setError(err instanceof Error ? err.message : 'Failed to generate speech');
    } finally {
      setIsGenerating(false);
    }
  };

  const playAudio = () => {
    if (!generatedAudio) return;

    try {
      // Create audio element and play the base64 audio
      const audio = new Audio(`data:audio/wav;base64,${generatedAudio.audioData}`);
      audio.play().catch(console.error);
    } catch (err) {
      console.error('Audio playback error:', err);
      setError('Failed to play audio');
    }
  };

  const downloadAudio = () => {
    if (!generatedAudio) return;

    try {
      // Create download link for the audio
      const link = document.createElement('a');
      link.href = `data:audio/wav;base64,${generatedAudio.audioData}`;
      link.download = `chatterbox_tts_${Date.now()}.wav`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (err) {
      console.error('Audio download error:', err);
      setError('Failed to download audio');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-dark text-foreground">
      {/* Background Pattern */}
      <div className="fixed inset-0 opacity-5">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(220,38,38,0.3),transparent_50%)]"></div>
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_80%_20%,rgba(234,88,12,0.2),transparent_50%)]"></div>
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_20%_80%,rgba(249,115,22,0.2),transparent_50%)]"></div>
      </div>

      <div className="relative container mx-auto px-4 py-6 max-w-7xl">
        {/* Header */}
        <header className="flex justify-between items-center mb-8">
          <div className="text-center flex-1">
            <h1 className="text-3xl md:text-4xl font-bold bg-gradient-red-orange bg-clip-text text-transparent mb-2">
              Imprint AI
            </h1>
            <p className="text-lg text-muted-foreground">
              Voice Cloning and Agent Creation Sandbox
            </p>
            <p className="text-sm text-muted-foreground mt-1">
              API Status: {apiHealth}
            </p>
          </div>
          <ThemeToggle />
        </header>

        {/* Main Horizontal Flow */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          {/* Text Input Section */}
          <div className="glass-card p-4 space-y-3">
            <h3 className="text-lg font-semibold text-foreground">
              Text to Speech
            </h3>
            
            <div className="space-y-2">
              <label className="block text-sm font-medium text-foreground">
                Enter your text (max {characterLimit} characters):
              </label>
              <textarea
                value={text}
                onChange={(e) => setText(e.target.value.slice(0, characterLimit))}
                placeholder="Type your message here..."
                className="w-full h-24 px-3 py-2 bg-background/50 border border-border rounded-lg resize-none focus:ring-2 focus:ring-red-500 focus:border-transparent transition-all duration-300 text-sm"
                maxLength={characterLimit}
              />
              <div className="flex justify-between items-center">
                <span className="text-xs text-muted-foreground">
                  {text.length} / {characterLimit}
                </span>
                {text.length > 100 && (
                  <span className="text-xs text-orange-400">
                    Shorter texts often produce better quality
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Voice Cloning Section */}
          <FileUploadComponent onFileSelect={setSelectedFile} />

          {/* Voice Settings */}
          <VoiceSettings onSettingsChange={setVoiceSettings} />
        </div>

        {/* Generate Button */}
        <div className="text-center mb-6">
          <button
            onClick={handleGenerate}
            disabled={isGenerating || !text.trim()}
            className={`glow-button px-8 py-3 text-lg font-semibold rounded-xl transition-all duration-300 ${
              isGenerating || !text.trim()
                ? 'opacity-50 cursor-not-allowed'
                : 'hover:scale-105'
            }`}
          >
            <Mic className="inline-block w-5 h-5 mr-2" />
            {isGenerating ? 'Generating...' : 'Generate Speech'}
          </button>
        </div>

        {/* Error Display */}
        {error && (
          <div className="glass-card p-4 border-l-4 border-red-500 mb-6">
            <p className="text-red-400 font-medium">{error}</p>
          </div>
        )}

        {/* Audio Player Section */}
        {generatedAudio && (
          <div className="glass-card p-6 space-y-4 mb-6">
            <h3 className="text-xl font-semibold text-foreground text-center">
              Generated Audio
            </h3>
            <div className="flex gap-4 justify-center">
              <button
                onClick={playAudio}
                className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg flex items-center gap-2 transition-colors"
              >
                <Play className="w-4 h-4" />
                Play Audio
              </button>
              <button
                onClick={downloadAudio}
                className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg flex items-center gap-2 transition-colors"
              >
                <Download className="w-4 h-4" />
                Download
              </button>
            </div>
            <p className="text-sm text-muted-foreground text-center">
              Sample Rate: {generatedAudio.sampleRate} Hz
            </p>
          </div>
        )}

        {/* Tips Section - Compressed */}
        <TipsSection />

        {/* Footer */}
        <footer className="mt-8 text-center">
          <div className="glass-card p-4">
            <p className="text-sm text-muted-foreground mb-1">
              Zero-shot voice cloning • Ultra-low latency • Built-in watermarking
            </p>
            <p className="text-xs text-muted-foreground">
              Powered by Chatterbox • MIT Licensed Open Source
            </p>
          </div>
        </footer>
      </div>
    </div>
  );
};

export default Index;
