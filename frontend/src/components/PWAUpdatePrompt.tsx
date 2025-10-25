import React, { useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';

interface BeforeInstallPromptEvent extends Event {
  readonly platforms: string[];
  readonly userChoice: Promise<{
    outcome: 'accepted' | 'dismissed';
    platform: string;
  }>;
  prompt(): Promise<void>;
}

const PWAUpdatePrompt = () => {
  const [needRefresh, setNeedRefresh] = useState(false);
  const [offlineReady, setOfflineReady] = useState(false);
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [deferredPrompt, setDeferredPrompt] = useState<BeforeInstallPromptEvent | null>(null);
  const [showInstallPrompt, setShowInstallPrompt] = useState(false);

  useEffect(() => {
    const handleBeforeInstallPrompt = (e: Event) => {
      e.preventDefault();
      setDeferredPrompt(e as BeforeInstallPromptEvent);
      setShowInstallPrompt(true);
    };

    const handleAppInstalled = () => {
      setDeferredPrompt(null);
      setShowInstallPrompt(false);
      toast.success('ClauseBot.Ai installed successfully!');
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    window.addEventListener('appinstalled', handleAppInstalled);

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
      window.removeEventListener('appinstalled', handleAppInstalled);
    };
  }, []);

  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      toast.success('Connection restored! Syncing data...');
    };

    const handleOffline = () => {
      setIsOnline(false);
      toast.warning('You\'re offline. ClauseBot.Ai will continue working with cached data.');
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Check for service worker registration and show offline ready message
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.ready.then(() => {
        setOfflineReady(true);
        toast.success('ClauseBot.Ai is ready to work offline!', {
          description: 'All essential features are cached and available without internet.',
          duration: 5000,
        });
      });
    }

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  const handleInstallClick = async () => {
    if (!deferredPrompt) return;

    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;
    
    if (outcome === 'accepted') {
      toast.success('Installing ClauseBot.Ai...');
    }
    
    setDeferredPrompt(null);
    setShowInstallPrompt(false);
  };

  return (
    <div>
      {/* Offline indicator */}
      {!isOnline && (
        <div className="fixed top-0 left-0 right-0 bg-yellow-600 text-white text-center py-2 px-4 text-sm z-50">
          <span className="font-medium">Offline Mode</span> - Working with cached data
        </div>
      )}

      {/* Install prompt for PWA */}
      {showInstallPrompt && (
        <div className="fixed bottom-4 left-4 bg-[#0B1220] text-white p-4 rounded-lg shadow-lg border border-gray-700 max-w-sm z-50">
          <div className="flex flex-col gap-3">
            <p className="text-sm font-medium">Install ClauseBot.Ai</p>
            <p className="text-xs text-gray-300">
              Install the app for faster access and offline capability - perfect for construction sites!
            </p>
            <div className="flex gap-2">
              <Button 
                onClick={handleInstallClick}
                size="sm"
                className="bg-[#0D47A1] hover:bg-[#0A3A85]"
              >
                Install App
              </Button>
              <Button 
                onClick={() => setShowInstallPrompt(false)}
                variant="outline"
                size="sm"
                className="border-gray-600 text-gray-300"
              >
                Not Now
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PWAUpdatePrompt;