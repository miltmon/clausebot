import { useState } from 'react';
import { FLAGS } from '@/lib/flags';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Lock, Info, Send } from 'lucide-react';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import { Helmet } from 'react-helmet';

const ClauseBot = () => {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState<string | null>(null);
  const [isAsking, setIsAsking] = useState(false);

  const handleAsk = () => {
    setIsAsking(true);
    // Simulate processing delay
    setTimeout(() => {
      setResponse(
        "Preview mode — Clause intelligence is currently disabled. This is a UI preview only.\n\n" +
        "The full ClauseBot system includes:\n" +
        "• Code clause parsing and indexing\n" +
        "• WPS/PQR validation against standards\n" +
        "• Multi-code crosswalk (AWS D1.1, ASME IX, API 1104, NBBI)\n" +
        "• Citation-linked responses\n\n" +
        "These capabilities are in private testing."
      );
      setIsAsking(false);
    }, 800);
  };

  if (!FLAGS.CLAUSEBOT_PUBLIC) {
    return (
      <>
        <Helmet>
          <title>ClauseBot Intelligence - Private Testing</title>
          <meta name="robots" content="noindex,nofollow" />
        </Helmet>
        <Navbar />
        <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-background via-background/95 to-primary/5">
          <Card className="max-w-2xl w-full border-2">
            <CardHeader className="text-center space-y-4">
              <div className="mx-auto w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center">
                <Lock className="h-8 w-8 text-primary" />
              </div>
              <div>
                <CardTitle className="text-3xl">ClauseBot Intelligence</CardTitle>
                <CardDescription className="text-base mt-2">
                  Currently in Private Testing
                </CardDescription>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <Alert>
                <Info className="h-4 w-4" />
                <AlertDescription>
                  <strong>Preview Only:</strong> The UI is ready, but clause intelligence, code parsing, 
                  and WPS validation are gated for private testing.
                </AlertDescription>
              </Alert>
              
              <div className="space-y-3">
                <h3 className="font-semibold">Capabilities in Development:</h3>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li className="flex items-start gap-2">
                    <Badge variant="outline" className="mt-0.5">AWS D1.1</Badge>
                    <span>Structural Welding Code - Steel (2025 Edition)</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <Badge variant="outline" className="mt-0.5">ASME IX</Badge>
                    <span>Welding and Brazing Qualifications</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <Badge variant="outline" className="mt-0.5">API 1104</Badge>
                    <span>Welding of Pipelines and Related Facilities</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <Badge variant="outline" className="mt-0.5">NBBI</Badge>
                    <span>National Board Inspection Code</span>
                  </li>
                </ul>
              </div>
            </CardContent>
            <CardFooter className="flex-col space-y-3">
              <p className="text-sm text-center text-muted-foreground">
                Interested in early access? Contact us to request testing privileges.
              </p>
              <Button variant="outline" className="w-full" onClick={() => window.location.href = '/pricing'}>
                Learn More About ClauseBot
              </Button>
            </CardFooter>
          </Card>
        </div>
        <Footer />
      </>
    );
  }

  return (
    <>
      <Helmet>
        <title>Ask ClauseBot - Preview Mode</title>
        <meta name="robots" content="noindex,nofollow" />
      </Helmet>
      <Navbar />
      <div className="min-h-screen p-4 md:p-8 bg-gradient-to-br from-background via-background/95 to-primary/5">
        <div className="max-w-4xl mx-auto space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-2xl">Ask ClauseBot</CardTitle>
                  <CardDescription>
                    Query welding code clauses, requirements, and qualifications
                  </CardDescription>
                </div>
                <Badge variant="secondary">Preview Mode</Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Textarea
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Ask about AWS D1.1 preheat requirements, ASME IX PQR variables, API 1104 acceptance criteria, or any code clause..."
                  className="min-h-[120px] resize-none"
                  disabled={isAsking}
                />
                <Button 
                  onClick={handleAsk} 
                  disabled={!query.trim() || isAsking}
                  className="w-full sm:w-auto"
                >
                  <Send className="h-4 w-4 mr-2" />
                  {isAsking ? 'Processing...' : 'Ask ClauseBot'}
                </Button>
              </div>

              {response && (
                <Alert className="border-2">
                  <Info className="h-4 w-4" />
                  <AlertDescription className="whitespace-pre-line">
                    {response}
                  </AlertDescription>
                </Alert>
              )}

              <div className="pt-4 border-t">
                <p className="text-xs text-muted-foreground text-center">
                  <strong>Preview Only:</strong> Code clause parsing, WPS validation, and citation-linked 
                  responses are disabled. Full intelligence capabilities are in private testing.
                </p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Available Code Standards</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-3 sm:grid-cols-2">
                {[
                  { id: 'aws_d1_1', title: 'AWS D1.1', subtitle: 'Structural Welding - Steel (2025)' },
                  { id: 'asme_ix', title: 'ASME IX', subtitle: 'Welding Qualifications (2023)' },
                  { id: 'api_1104', title: 'API 1104', subtitle: 'Pipeline Welding (2021)' },
                  { id: 'nbb_i', title: 'NBBI', subtitle: 'Inspection Code (2023)' },
                ].map((code) => (
                  <div key={code.id} className="p-3 border rounded-lg space-y-1">
                    <p className="font-medium">{code.title}</p>
                    <p className="text-sm text-muted-foreground">{code.subtitle}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
      <Footer />
    </>
  );
};

export default ClauseBot;
