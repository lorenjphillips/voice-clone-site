import { useState } from 'react';

interface VoiceSettingsProps {
  onSettingsChange: (settings: {
    exaggeration: number;
    temperature: number;
    cfgPace: number;
    seed: number;
  }) => void;
}

const VoiceSettings = ({ onSettingsChange }: VoiceSettingsProps) => {
  const [exaggeration, setExaggeration] = useState(0.5);
  const [temperature, setTemperature] = useState(0.8);
  const [cfgPace, setCfgPace] = useState(0.5);
  const [seed, setSeed] = useState(0);

  const handleSettingChange = (
    setter: (value: number) => void,
    value: number,
    settingName: string
  ) => {
    setter(value);
    const newSettings = {
      exaggeration: settingName === 'exaggeration' ? value : exaggeration,
      temperature: settingName === 'temperature' ? value : temperature,
      cfgPace: settingName === 'cfgPace' ? value : cfgPace,
      seed: settingName === 'seed' ? value : seed,
    };
    onSettingsChange(newSettings);
  };

  return (
    <div className="glass-card p-6 space-y-6">
      <h3 className="text-xl font-semibold text-foreground flex items-center gap-2">
        🎛️ Voice Settings
      </h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Exaggeration Control */}
        <div className="space-y-3">
          <label className="block text-sm font-medium text-foreground">
            Exaggeration: {exaggeration.toFixed(1)}
          </label>
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={exaggeration}
            onChange={(e) => handleSettingChange(setExaggeration, parseFloat(e.target.value), 'exaggeration')}
            className="w-full h-2 bg-gradient-to-r from-red-600 to-orange-500 rounded-lg appearance-none cursor-pointer slider"
          />
          <p className="text-xs text-muted-foreground">
            0.0 (neutral) to 1.0 (very expressive)
          </p>
        </div>

        {/* Temperature Control */}
        <div className="space-y-3">
          <label className="block text-sm font-medium text-foreground">
            Temperature: {temperature.toFixed(1)}
          </label>
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={temperature}
            onChange={(e) => handleSettingChange(setTemperature, parseFloat(e.target.value), 'temperature')}
            className="w-full h-2 bg-gradient-to-r from-red-600 to-orange-500 rounded-lg appearance-none cursor-pointer slider"
          />
          <p className="text-xs text-muted-foreground">
            0.0 (monotone) to 1.0 (varied)
          </p>
        </div>

        {/* CFG/Pace Control */}
        <div className="space-y-3">
          <label className="block text-sm font-medium text-foreground">
            CFG/Pace: {cfgPace.toFixed(1)}
          </label>
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={cfgPace}
            onChange={(e) => handleSettingChange(setCfgPace, parseFloat(e.target.value), 'cfgPace')}
            className="w-full h-2 bg-gradient-to-r from-red-600 to-orange-500 rounded-lg appearance-none cursor-pointer slider"
          />
          <p className="text-xs text-muted-foreground">
            0.0 (fast) to 1.0 (slow)
          </p>
        </div>

        {/* Seed Control */}
        <div className="space-y-3">
          <label className="block text-sm font-medium text-foreground">
            Seed: {seed}
          </label>
          <input
            type="number"
            min="0"
            value={seed}
            onChange={(e) => handleSettingChange(setSeed, parseInt(e.target.value) || 0, 'seed')}
            className="w-full px-3 py-2 bg-background/50 border border-border rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
            placeholder="0 for random"
          />
          <p className="text-xs text-muted-foreground">
            0 = random, &gt;0 = reproducible results
          </p>
        </div>
      </div>
    </div>
  );
};

export default VoiceSettings;
