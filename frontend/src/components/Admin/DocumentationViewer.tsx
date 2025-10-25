import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { 
  FileText, 
  Book, 
  Code, 
  Rocket, 
  Map, 
  Wrench,
  Shield,
  BarChart3,
  Database,
  FileCode,
  ChevronRight
} from 'lucide-react';

interface Doc {
  id: string;
  title: string;
  description: string;
  icon: any;
  category: string;
  path: string;
}

const DOCUMENTATION: Doc[] = [
  {
    id: 'knowledge-base',
    title: 'Knowledge Base',
    description: 'Complete RAG system documentation and usage guide',
    icon: Database,
    category: 'Core Features',
    path: '/docs/KNOWLEDGE_BASE.md',
  },
  {
    id: 'large-documents',
    title: 'Large Document Handling',
    description: 'Guide for managing documents with thousands of pages',
    icon: FileText,
    category: 'Core Features',
    path: '/docs/LARGE_DOCUMENT_HANDLING.md',
  },
  {
    id: 'admin-ux',
    title: 'Admin UX Report',
    description: 'Admin dashboard analysis and improvements report',
    icon: BarChart3,
    category: 'Reports',
    path: '/docs/ADMIN_UX_REPORT.md',
  },
  {
    id: 'api',
    title: 'API Reference',
    description: 'API endpoints and integration documentation',
    icon: Code,
    category: 'Development',
    path: '/docs/API.md',
  },
  {
    id: 'architecture',
    title: 'Architecture',
    description: 'System architecture and design patterns',
    icon: FileCode,
    category: 'Development',
    path: '/docs/ARCHITECTURE.md',
  },
  {
    id: 'features',
    title: 'Features',
    description: 'Complete list of platform features',
    icon: Rocket,
    category: 'General',
    path: '/docs/FEATURES.md',
  },
  {
    id: 'roadmap',
    title: 'Roadmap',
    description: 'Future plans and development timeline',
    icon: Map,
    category: 'General',
    path: '/docs/ROADMAP.md',
  },
  {
    id: 'deployment',
    title: 'Deployment',
    description: 'Deployment guide and best practices',
    icon: Rocket,
    category: 'Development',
    path: '/docs/DEPLOYMENT.md',
  },
  {
    id: 'contributing',
    title: 'Contributing',
    description: 'Guidelines for contributing to the project',
    icon: Wrench,
    category: 'Development',
    path: '/docs/CONTRIBUTING.md',
  },
  {
    id: 'pwa',
    title: 'PWA Features',
    description: 'Progressive Web App implementation details',
    icon: Shield,
    category: 'General',
    path: '/docs/PWA.md',
  },
  {
    id: 'readme',
    title: 'README',
    description: 'Project overview and getting started',
    icon: Book,
    category: 'General',
    path: '/docs/README.md',
  },
];

export const DocumentationViewer = () => {
  const [selectedDoc, setSelectedDoc] = useState<Doc | null>(null);
  const [content, setContent] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);

  const loadDocument = async (doc: Doc) => {
    setIsLoading(true);
    setSelectedDoc(doc);
    
    try {
      // In a real implementation, you would fetch the actual file
      // For now, we'll show the doc info
      const mockContent = `# ${doc.title}

**Category:** ${doc.category}  
**Description:** ${doc.description}

---

*This documentation file is located at \`${doc.path}\`*

To view the full content:
1. Open the project in your code editor
2. Navigate to the docs folder
3. Open \`${doc.path.split('/').pop()}\`

## Quick Links

- [View in GitHub](#)
- [Download PDF](#)
- [Edit Documentation](#)

## Related Documentation

${DOCUMENTATION
  .filter(d => d.category === doc.category && d.id !== doc.id)
  .map(d => `- [${d.title}](${d.path})`)
  .join('\n')}

---

*For the most up-to-date documentation, please refer to the actual markdown files in the \`/docs\` directory.*`;

      setContent(mockContent);
    } catch (error) {
      console.error('Error loading document:', error);
      setContent('# Error\n\nFailed to load documentation.');
    } finally {
      setIsLoading(false);
    }
  };

  const categories = Array.from(new Set(DOCUMENTATION.map(d => d.category)));

  return (
    <div className="grid gap-6 lg:grid-cols-3">
      {/* Documentation List */}
      <Card className="lg:col-span-1">
        <CardHeader>
          <CardTitle>Documentation</CardTitle>
          <CardDescription>Browse all available documentation</CardDescription>
        </CardHeader>
        <CardContent>
          <ScrollArea className="h-[600px] pr-4">
            <div className="space-y-6">
              {categories.map(category => (
                <div key={category} className="space-y-2">
                  <h3 className="font-semibold text-sm text-muted-foreground px-2">
                    {category}
                  </h3>
                  <div className="space-y-1">
                    {DOCUMENTATION
                      .filter(doc => doc.category === category)
                      .map(doc => {
                        const Icon = doc.icon;
                        const isSelected = selectedDoc?.id === doc.id;
                        
                        return (
                          <Button
                            key={doc.id}
                            variant={isSelected ? "secondary" : "ghost"}
                            className="w-full justify-start"
                            onClick={() => loadDocument(doc)}
                          >
                            <Icon className="h-4 w-4 mr-2" />
                            <span className="flex-1 text-left truncate">
                              {doc.title}
                            </span>
                            <ChevronRight className="h-4 w-4 ml-2 opacity-50" />
                          </Button>
                        );
                      })}
                  </div>
                </div>
              ))}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>

      {/* Documentation Content */}
      <Card className="lg:col-span-2">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            {selectedDoc && <selectedDoc.icon className="h-5 w-5" />}
            {selectedDoc ? selectedDoc.title : 'Documentation Viewer'}
          </CardTitle>
          <CardDescription>
            {selectedDoc 
              ? selectedDoc.description 
              : 'Select a document from the list to view its contents'
            }
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex items-center justify-center h-[600px]">
              <div className="text-center space-y-2">
                <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent mx-auto" />
                <p className="text-sm text-muted-foreground">Loading documentation...</p>
              </div>
            </div>
          ) : selectedDoc ? (
            <ScrollArea className="h-[600px]">
              <div className="prose prose-sm max-w-none dark:prose-invert">
                <pre className="whitespace-pre-wrap text-sm bg-muted p-4 rounded-lg">
                  {content}
                </pre>
              </div>
            </ScrollArea>
          ) : (
            <div className="flex items-center justify-center h-[600px]">
              <div className="text-center space-y-4 max-w-md">
                <Book className="h-16 w-16 mx-auto text-muted-foreground opacity-50" />
                <div className="space-y-2">
                  <h3 className="font-semibold text-lg">No Document Selected</h3>
                  <p className="text-sm text-muted-foreground">
                    Choose a documentation file from the list on the left to view its contents.
                  </p>
                </div>
                <div className="grid grid-cols-2 gap-2 mt-6">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => loadDocument(DOCUMENTATION[0])}
                  >
                    Quick Start
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => loadDocument(DOCUMENTATION.find(d => d.id === 'knowledge-base')!)}
                  >
                    Knowledge Base
                  </Button>
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};
