// GA4 initialization helper - SSR-safe, idempotent
let gaBooted = false;

export function initGA(id?: string) {
  if (typeof window === "undefined") return;           // SSR guard
  
  const gaId = id || import.meta.env.VITE_GA_ID;
  if (!gaId || gaId === 'G-XXXXXXXX') return;         // no ID, no GA
  if (gaBooted || (window as any).__gaBooted) return; // idempotent
  
  (window as any).__gaBooted = true;
  gaBooted = true;

  try {
    // Load gtag.js
    const script1 = document.createElement("script");
    script1.async = true;
    script1.src = `https://www.googletagmanager.com/gtag/js?id=${encodeURIComponent(gaId)}`;
    document.head.appendChild(script1);

    // Initialize dataLayer + gtag
    (window as any).dataLayer = (window as any).dataLayer || [];
    function gtag(...args: any[]) { 
      (window as any).dataLayer.push(args); 
    }
    (window as any).gtag = gtag;

    gtag("js", new Date());
    gtag("config", gaId); // <-- pass the variable, not '${id}'
  } catch (error) {
    console.error('GA initialization failed:', error);
    // Never block React mount if GA fails
  }
}
