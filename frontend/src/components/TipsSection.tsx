
const TipsSection = () => {
  const tips = [
    {
      title: "Audio Quality Guidelines",
      content: "Use clear, high-quality audio samples (5-30 seconds) for voice cloning"
    },
    {
      title: "Parameter Usage Instructions",
      content: "Higher exaggeration values create more expressive and emotional speech"
    },
    {
      title: "Temperature Controls",
      content: "Lower temperature for consistent voice, higher for natural variation"
    },
    {
      title: "CFG/Pace Effects",
      content: "CFG/Pace affects speed and emphasis - experiment to find the perfect setting"
    },
    {
      title: "Seed Usage",
      content: "Use seed values >0 for identical result reproduction across sessions"
    },
    {
      title: "Content Optimization",
      content: "Shorter texts (under 100 characters) often produce better quality results"
    }
  ];

  return (
    <div className="glass-card p-6 space-y-4">
      <h3 className="text-xl font-semibold text-foreground flex items-center gap-2">
        💡 Tips for Better Results
      </h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {tips.map((tip, index) => (
          <div
            key={index}
            className="p-4 bg-gradient-to-br from-red-600/10 to-orange-600/10 rounded-lg border border-red-600/20 hover:border-red-500/40 transition-all duration-300"
          >
            <h4 className="font-medium text-foreground mb-2">{tip.title}</h4>
            <p className="text-sm text-muted-foreground">{tip.content}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TipsSection;
