# ⚠️ DEPRECATED FRONTEND

## Notice: This frontend has been deprecated

The original HTML/CSS/JavaScript frontend (`index.html.deprecated`) has been **deprecated** and replaced with a modern React TypeScript application.

## 🆕 New Frontend

The new frontend is located in the `/frontend` directory and offers:

- ⚛️ **React + TypeScript** - Modern, type-safe development
- 🎨 **Tailwind CSS** - Beautiful, responsive design
- 🎭 **Shadcn/ui** - High-quality component library
- 🌙 **Dark/Light mode** - Theme switching support
- 📱 **Mobile responsive** - Works on all devices
- 🔄 **Real-time API integration** - Direct connection to the TTS backend
- 🎵 **Built-in audio player** - Play and download generated audio
- ✨ **Better UX** - Improved user experience and error handling

## 🚀 How to Use the New Frontend

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Start development:**
   ```bash
   # From project root
   python start_dev.py
   ```
   This starts both the backend API and frontend development server.

3. **Open in browser:**
   ```
   http://localhost:5173
   ```

## 🔄 Migration Benefits

- **Better maintainability** - Modular component architecture
- **Type safety** - TypeScript prevents runtime errors
- **Modern tooling** - Vite for fast development and building
- **Component reusability** - Shared UI components
- **Better state management** - React hooks for cleaner code
- **Improved performance** - Optimized React rendering

## 📂 File Structure

```
frontend/
├── src/
│   ├── components/        # Reusable UI components
│   ├── pages/            # Page components
│   ├── lib/              # Utilities and API client
│   └── hooks/            # Custom React hooks
├── public/               # Static assets
└── package.json          # Dependencies and scripts
```

## 🗂️ What was moved to legacy

- `index.html` → `legacy/index.html.deprecated`
- All inline CSS and JavaScript was converted to React components
- API integration was improved with proper TypeScript interfaces

---

**Note:** The legacy frontend may still work but is no longer maintained. Please use the new React frontend for the best experience. 