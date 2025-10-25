// GA4 initialization helper - avoids Vite template string issues
export function initGA() {
  const id = import.meta.env.VITE_GA_ID;
  if (!id || id === 'G-XXXXXXXX') return; // Skip if not configured

  const script1 = document.createElement('script');
  script1.async = true;
  script1.src = `https://www.googletagmanager.com/gtag/js?id={id}`;
  document.head.appendChild(script1);

  const script2 = document.createElement('script');
  script2.innerHTML = `
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', '{id}');
  `;
  document.head.appendChild(script2);
}
