import { createRoot } from 'react-dom/client'
import App from './App.tsx'
import './index.css'
import { initGA } from './ga'

// Initialize Google Analytics
initGA()

createRoot(document.getElementById("root")!).render(<App />);
