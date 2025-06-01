
import { useState } from 'react';
import { Mic } from 'lucide-react';
import ThemeToggle from '../components/ThemeToggle';
import VoiceSettings from '../components/VoiceSettings';
import FileUploadComponent from '../components/FileUpload';
import TipsSection from '../components/TipsSection';

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
  const [error, setError] = useState('❌ Error: Failed to load TTS model');

  const characterLimit = 300;

  const handleGenerate = async () => {
    if (!text.trim()) {
      alert('Please enter some text to generate speech');
      return;
    }

    setIsGenerating(true);
    // Simulate API call
    setTimeout(() => {
      setIsGenerating(false);
      alert('Speech generation would happen here!');
    }, 2000);
  };

  return (
    <div className="min-h-screen bg-gradient-dark text-foreground">
      {/* Background Pattern */}
      <div className="fixed inset-0 opacity-5">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(220,38,38,0.3),transparent_50%)]"></div>
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_80%_20%,rgba(234,88,12,0.2),transparent_50%)]"></div>
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_20%_80%,rgba(249,115,22,0.2),transparent_50%)]"></div>
      </div>

      <div className="relative container mx-auto px-4 py-8 max-w-6xl">
        {/* Header */}
        <header className="flex justify-between items-center mb-12">
          <div className="text-center flex-1">
            <h1 className="text-4xl md:text-6xl font-bold bg-gradient-red-orange bg-clip-text text-transparent mb-4">
              🎙️ Chatterbox TTS
            </h1>
            <p className="text-xl text-muted-foreground">
              Advanced Text-to-Speech with Voice Cloning
            </p>
          </div>
          <ThemeToggle />
        </header>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Left Column */}
          <div className="space-y-8">
            {/* Text Input Section */}
            <div className="glass-card p-6 space-y-4">
              <h3 className="text-xl font-semibold text-foreground flex items-center gap-2">
                📝 Text to Speech
              </h3>
              
              <div className="space-y-2">
                <label className="block text-sm font-medium text-foreground">
                  Enter your text (max {characterLimit} characters):
                </label>
                <textarea
                  value={text}
                  onChange={(e) => setText(e.target.value.slice(0, characterLimit))}
                  placeholder="Type your message here..."
                  className="w-full h-32 px-4 py-3 bg-background/50 border border-border rounded-lg resize-none focus:ring-2 focus:ring-red-500 focus:border-transparent transition-all duration-300"
                  maxLength={characterLimit}
                />
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">
                    {text.length} / {characterLimit}
                  </span>
                  {text.length > 100 && (
                    <span className="text-xs text-orange-400">
                      💡 Shorter texts often produce better quality
                    </span>
                  )}
                </div>
              </div>
            </div>

            {/* Voice Cloning Section */}
            <FileUploadComponent onFileSelect={setSelectedFile} />

            {/* Generate Button */}
            <div className="text-center">
              <button
                onClick={handleGenerate}
                disabled={isGenerating || !text.trim()}
                className={`glow-button px-8 py-4 text-lg font-semibold rounded-xl transition-all duration-300 ${
                  isGenerating || !text.trim()
                    ? 'opacity-50 cursor-not-allowed'
                    : 'hover:scale-105'
                }`}
              >
                <Mic className="inline-block w-5 h-5 mr-2" />
                {isGenerating ? 'Generating...' : '🎙️ Generate Speech'}
              </button>
            </div>

            {/* Error Display */}
            {error && (
              <div className="glass-card p-4 border-l-4 border-red-500">
                <p className="text-red-400 font-medium">{error}</p>
              </div>
            )}
          </div>

          {/* Right Column */}
          <div className="space-y-8">
            {/* Voice Settings */}
            <VoiceSettings onSettingsChange={setVoiceSettings} />
          </div>
        </div>

        {/* Tips Section */}
        <TipsSection />

        {/* Footer */}
        <footer className="mt-12 text-center">
          <div className="glass-card p-6">
            <p className="text-sm text-muted-foreground mb-2">
              🚀 Zero-shot voice cloning • ⚡ Ultra-low latency • 🔒 Built-in watermarking
            </p>
            <p className="text-xs text-muted-foreground">
              Powered by advanced AI technology • MIT Licensed Open Source
            </p>
          </div>
        </footer>
      </div>
    </div>
  );
};

export default Index;
