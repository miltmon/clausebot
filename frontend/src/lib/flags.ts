// Feature flags for gating functionality
export const FLAGS = {
  CLAUSEBOT_PUBLIC: (import.meta.env.VITE_FEATURE_CLAUSEBOT_PUBLIC ?? 'false') === 'true',
  CLAUSE_INTELLIGENCE: (import.meta.env.VITE_FEATURE_CLAUSE_INTELLIGENCE ?? 'false') === 'true',
  WPS_VALIDATION: (import.meta.env.VITE_FEATURE_WPS_VALIDATION ?? 'false') === 'true',
} as const;

export type FeatureFlag = keyof typeof FLAGS;
