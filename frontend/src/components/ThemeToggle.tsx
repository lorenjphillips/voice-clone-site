
import { useState, useEffect } from 'react';
import { Lightbulb, LightbulbOff } from 'lucide-react';

const ThemeToggle = () => {
  const [isDark, setIsDark] = useState(true); // Default to dark theme

  useEffect(() => {
    // Set dark theme by default on initial load
    document.documentElement.classList.add('dark');
  }, []);

  const toggleTheme = () => {
    const newTheme = !isDark;
    setIsDark(newTheme);
    
    if (newTheme) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  };

  return (
    <button
      onClick={toggleTheme}
      className="p-3 rounded-full glass-card hover:bg-white/20 dark:hover:bg-white/10 transition-all duration-300 group"
      aria-label="Toggle theme"
    >
      {isDark ? (
        <Lightbulb className="w-5 h-5 text-orange-400 group-hover:animate-pulse" />
      ) : (
        <LightbulbOff className="w-5 h-5 text-gray-600 group-hover:animate-pulse" />
      )}
    </button>
  );
};

export default ThemeToggle;
