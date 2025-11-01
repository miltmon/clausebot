import { useEffect, useState } from 'react';
import { useSupabase } from '../hooks/useSupabase';
import WeldingSymbolsExplorer from './WeldingSymbolsExplorer';

export default function ProGatedWeldingSymbols() {
  const { user, loading } = useSupabase();
  const [hasPro, setHasPro] = useState(false);
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    async function checkPro() {
      if (!user) {
        setChecking(false);
        return;
      }
      
      try {
        const { data } = await supabase
          .from('subscribers')
          .select('has_pro_access')
          .eq('user_id', user.id)
          .single();
        
        setHasPro(data?.has_pro_access || false);
      } catch (error) {
        console.error('Error checking Pro access:', error);
        setHasPro(false);
      } finally {
        setChecking(false);
      }
    }
    
    checkPro();
  }, [user]);

  if (loading || checking) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-sky-600"></div>
        <span className="ml-3 text-gray-600">Loading...</span>
      </div>
    );
  }
  
  if (!user) {
    return (
      <div className="p-8 text-center bg-gradient-to-br from-slate-50 to-sky-50 rounded-xl border">
        <div className="max-w-md mx-auto">
          <div className="w-16 h-16 mx-auto mb-4 bg-sky-100 rounded-full flex items-center justify-center">
            <svg className="w-8 h-8 text-sky-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Sign In Required</h2>
          <p className="text-gray-600 mb-6">
            Please sign in to access welding symbols and CWI resources
          </p>
          <button 
            onClick={() => window.location.href = '/auth/signin'}
            className="px-6 py-3 bg-sky-600 text-white rounded-lg hover:bg-sky-700 transition-colors font-medium"
          >
            Sign In
          </button>
        </div>
      </div>
    );
  }

  if (!hasPro) {
    return (
      <div className="p-8 text-center bg-gradient-to-br from-amber-50 to-orange-50 rounded-xl border border-amber-200">
        <div className="max-w-md mx-auto">
          <div className="w-16 h-16 mx-auto mb-4 bg-amber-100 rounded-full flex items-center justify-center">
            <svg className="w-8 h-8 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">🔒 Pro Feature</h2>
          <p className="text-gray-600 mb-2">
            Unlock 25+ welding symbol references and CWI resources
          </p>
          <p className="text-sm text-gray-500 mb-6">
            Get instant access to technical articles, symbol guides, and professional welding resources
          </p>
          
          <div className="bg-white rounded-lg p-4 mb-6 border border-amber-200">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">Pro Access</span>
              <span className="font-bold text-2xl text-gray-900">$49.99</span>
            </div>
            <div className="text-xs text-gray-500 mt-1">per month</div>
          </div>
          
          <button 
            onClick={() => window.location.href = '/upgrade'}
            className="w-full px-6 py-3 bg-gradient-to-r from-sky-600 to-blue-600 text-white rounded-lg hover:from-sky-700 hover:to-blue-700 transition-all duration-200 font-medium shadow-lg"
          >
            Upgrade to Pro
          </button>
          
          <p className="text-xs text-gray-500 mt-3">
            Cancel anytime • 7-day free trial
          </p>
        </div>
      </div>
    );
  }

  return <WeldingSymbolsExplorer />;
}
