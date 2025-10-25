import React from "react";

interface ClauseBotLogoProps {
  variant?: "full" | "icon";
  className?: string;
}

const ClauseBotLogo = ({ variant = "full", className = "" }: ClauseBotLogoProps) => {
  if (variant === "icon") {
    return (
      <svg 
        width="56" 
        height="56" 
        viewBox="0 0 56 56" 
        fill="none" 
        xmlns="http://www.w3.org/2000/svg"
        className={className}
      >
        {/* Clause "C" */}
        <path 
          d="M36 12 A20 20 0 1 0 36 44"
          stroke="#38BDF8" 
          strokeWidth="5" 
          strokeLinecap="round" 
          fill="none"
        />
        {/* Compliance check */}
        <path 
          d="M26 30 L34 38 L52 20" 
          stroke="#22C55E" 
          strokeWidth="5"
          strokeLinecap="round" 
          strokeLinejoin="round"
        />
      </svg>
    );
  }

  return (
    <svg 
      width="320" 
      height="72" 
      viewBox="0 0 320 72" 
      fill="none" 
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      {/* Icon */}
      <g transform="translate(8,8)">
        {/* Clause "C" */}
        <path 
          d="M40 12 A20 20 0 1 0 40 52"
          stroke="#38BDF8" 
          strokeWidth="6" 
          strokeLinecap="round" 
          fill="none"
        />
        {/* Compliance check */}
        <path 
          d="M30 36 L38 44 L56 26" 
          stroke="#22C55E" 
          strokeWidth="6"
          strokeLinecap="round" 
          strokeLinejoin="round"
        />
      </g>

      {/* Wordmark */}
      <g fontFamily="Inter, system-ui, -apple-system, Segoe UI" fontWeight="700">
        <text x="88" y="42" fontSize="28" fill="#0D1B2A" letterSpacing="1.2">
          CLAUSEBOT
        </text>
        {/* Tagline */}
        <text x="88" y="60" fontSize="14" fill="#475569" letterSpacing="0.4">
          Clause-cited. Decision-ready.
        </text>
      </g>
    </svg>
  );
};

export default ClauseBotLogo;