import { createRoot } from 'react-dom/client'
import App from './App.tsx'
import './index.css'
import { initGA } from './ga'
import ErrorBoundary from './components/ErrorBoundary'

// Initialize Google Analytics - only in production with explicit flag
try {
  if (import.meta.env.VITE_ENABLE_GA === 'true') {
    initGA(import.meta.env.VITE_GA_ID || '');
  }
} catch (e) {
  // Silent failure - don't block mount
  (window as any).__gaInitError = true;
  console.warn('GA init failed (non-blocking):', e);
}

// Track successful mount for monitoring
const trackMount = () => {
  try {
    if (typeof window !== 'undefined' && (window as any).gtag) {
      (window as any).gtag('event', 'frontend_mount_ok', {
        timestamp: new Date().toISOString(),
      });
    }
  } catch {}
};

// Render with error boundary
createRoot(document.getElementById("root")!).render(
  <ErrorBoundary>
    <App />
  </ErrorBoundary>
);

// Track mount success after render
setTimeout(trackMount, 1000);
