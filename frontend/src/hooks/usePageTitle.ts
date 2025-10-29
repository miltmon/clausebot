import { useEffect } from 'react';

/**
 * Custom hook to dynamically set page title
 * @param title - The page title to set
 * @param suffix - Optional suffix (defaults to "| ClauseBot Pro")
 */
export const usePageTitle = (title: string, suffix: string = "| ClauseBot Pro") => {
  useEffect(() => {
    const fullTitle = suffix ? `${title} ${suffix}` : title;
    document.title = fullTitle;
    
    // Cleanup: reset to default title on unmount
    return () => {
      document.title = "ClauseBot Pro – Clause-Cited Compliance Intelligence";
    };
  }, [title, suffix]);
};

