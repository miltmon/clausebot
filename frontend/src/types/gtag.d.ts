type GtagCommand = 'config' | 'event' | 'set' | 'consent';
type GtagParams = Record<string, string | number | boolean | undefined>;

declare global {
  interface Window {
    gtag?: (command: GtagCommand, targetId: string, params?: GtagParams) => void;
  }
  
  const gtag: (command: GtagCommand, targetId: string, params?: GtagParams) => void;
}

export {};