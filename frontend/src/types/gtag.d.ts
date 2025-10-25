declare global {
  interface Window {
    gtag?: (...args: any[]) => void;
  }
  
  const gtag: (...args: any[]) => void;
}

export {};