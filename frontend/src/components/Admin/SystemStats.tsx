import { useEffect, useState } from 'react';
import { supabase } from '@/integrations/supabase/client';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Database, FileText, Users, Settings } from 'lucide-react';

interface Stats {
  documentCount: number;
  totalSize: number;
  settingsCount: number;
}

export const SystemStats = () => {
  const [stats, setStats] = useState<Stats>({
    documentCount: 0,
    totalSize: 0,
    settingsCount: 0,
  });
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      // Get document count and total size
      const { data: docs, error: docsError } = await supabase
        .from('reference_documents')
        .select('file_size');

      if (docsError) throw docsError;

      const documentCount = docs?.length || 0;
      const totalSize = docs?.reduce((sum, doc) => sum + (doc.file_size || 0), 0) || 0;

      // Get settings count
      const { data: settings, error: settingsError } = await supabase
        .from('admin_settings')
        .select('id', { count: 'exact' });

      if (settingsError) throw settingsError;

      setStats({
        documentCount,
        totalSize,
        settingsCount: settings?.length || 0,
      });
    } catch (error) {
      console.error('Error loading stats:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  const statCards = [
    {
      title: 'Total Documents',
      value: stats.documentCount,
      icon: FileText,
      description: 'Documents in knowledge base',
    },
    {
      title: 'Storage Used',
      value: formatBytes(stats.totalSize),
      icon: Database,
      description: 'Total file storage',
    },
    {
      title: 'Active Settings',
      value: stats.settingsCount,
      icon: Settings,
      description: 'Configuration entries',
    },
  ];

  return (
    <div className="grid gap-4 md:grid-cols-3">
      {statCards.map((stat) => (
        <Card key={stat.title}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              {stat.title}
            </CardTitle>
            <stat.icon className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {isLoading ? '...' : stat.value}
            </div>
            <p className="text-xs text-muted-foreground">
              {stat.description}
            </p>
          </CardContent>
        </Card>
      ))}
    </div>
  );
};
