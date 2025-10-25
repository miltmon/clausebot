import { useState, useEffect } from 'react';
import { supabase } from '@/integrations/supabase/client';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';
import { Save, Loader2, RefreshCw } from 'lucide-react';

interface FunctionSetting {
  functionName: string;
  displayName: string;
  useKB: boolean;
  tokenLimit: number;
}

const DEFAULT_FUNCTIONS: FunctionSetting[] = [
  { functionName: 'ai-rag-example', displayName: 'AI RAG Example', useKB: true, tokenLimit: 200000 },
  { functionName: 'load-reference-documents', displayName: 'Document Loader', useKB: false, tokenLimit: 100000 },
];

export const AIFunctionSettings = () => {
  const [functions, setFunctions] = useState<FunctionSetting[]>(DEFAULT_FUNCTIONS);
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setSaving] = useState(false);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    setIsLoading(true);
    try {
      const { data, error } = await supabase
        .from('admin_settings')
        .select('key, value');

      if (error) throw error;

      if (data) {
        const updatedFunctions = functions.map(func => {
          const kbSetting = data.find(d => d.key === `${func.functionName}_use_kb`);
          const tokenSetting = data.find(d => d.key === `${func.functionName}_tokens`);
          
          return {
            ...func,
            useKB: kbSetting ? String(kbSetting.value) === 'true' : func.useKB,
            tokenLimit: tokenSetting ? parseInt(String(tokenSetting.value)) : func.tokenLimit,
          };
        });
        
        setFunctions(updatedFunctions);
      }
    } catch (error) {
      console.error('Error loading settings:', error);
      toast.error('Failed to load settings');
    } finally {
      setIsLoading(false);
    }
  };

  const saveSettings = async () => {
    setSaving(true);
    try {
      // Save all settings
      for (const func of functions) {
        // Save KB usage setting
        const { error: kbError } = await supabase
          .from('admin_settings')
          .upsert({
            key: `${func.functionName}_use_kb`,
            value: func.useKB.toString(),
          }, { onConflict: 'key' });

        if (kbError) throw kbError;

        // Save token limit setting
        const { error: tokenError } = await supabase
          .from('admin_settings')
          .upsert({
            key: `${func.functionName}_tokens`,
            value: func.tokenLimit.toString(),
          }, { onConflict: 'key' });

        if (tokenError) throw tokenError;
      }

      toast.success('Settings saved successfully');
    } catch (error) {
      console.error('Error saving settings:', error);
      toast.error('Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  const updateFunction = (index: number, updates: Partial<FunctionSetting>) => {
    setFunctions(prev => prev.map((func, i) => 
      i === index ? { ...func, ...updates } : func
    ));
  };

  if (isLoading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>AI Function Configuration</CardTitle>
            <CardDescription>
              Configure knowledge base usage and token limits for each AI function
            </CardDescription>
          </div>
          <Button
            variant="outline"
            size="icon"
            onClick={loadSettings}
            disabled={isLoading}
          >
            <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {functions.map((func, index) => (
          <div key={func.functionName} className="border rounded-lg p-4 space-y-4">
            <h3 className="font-semibold text-lg">{func.displayName}</h3>
            <p className="text-sm text-muted-foreground">Function: {func.functionName}</p>
            
            <div className="grid gap-4 md:grid-cols-2">
              <div className="flex items-center justify-between space-x-2">
                <Label htmlFor={`kb-${index}`} className="flex flex-col space-y-1">
                  <span>Use Knowledge Base</span>
                  <span className="font-normal text-xs text-muted-foreground">
                    Enable RAG context retrieval
                  </span>
                </Label>
                <Switch
                  id={`kb-${index}`}
                  checked={func.useKB}
                  onCheckedChange={(checked) => updateFunction(index, { useKB: checked })}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor={`tokens-${index}`}>
                  Max Tokens
                  <span className="text-xs text-muted-foreground ml-2">
                    (10K-500K for large docs)
                  </span>
                </Label>
                <Input
                  id={`tokens-${index}`}
                  type="number"
                  min="10000"
                  max="500000"
                  step="10000"
                  value={func.tokenLimit}
                  onChange={(e) => updateFunction(index, { 
                    tokenLimit: Math.max(10000, Math.min(500000, parseInt(e.target.value) || 200000))
                  })}
                />
                <p className="text-xs text-muted-foreground">
                  ~{Math.floor(func.tokenLimit / 3.5 / 500).toLocaleString()} pages at 500 words/page
                </p>
              </div>
            </div>
          </div>
        ))}

        <Button 
          onClick={saveSettings} 
          disabled={isSaving}
          className="w-full"
        >
          {isSaving ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Saving...
            </>
          ) : (
            <>
              <Save className="mr-2 h-4 w-4" />
              Save Settings
            </>
          )}
        </Button>
      </CardContent>
    </Card>
  );
};
