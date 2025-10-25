import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Play, MessageSquare, BookOpen, Search, Clock, CheckCircle } from "lucide-react";

const Demo = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-background to-muted">
      {/* Header */}
      <header className="border-b bg-background/95 backdrop-blur">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="h-8 w-8 bg-primary rounded-lg flex items-center justify-center">
                <span className="text-primary-foreground font-bold text-sm">CB</span>
              </div>
              <span className="font-semibold text-xl">ClauseBot Pro</span>
            </div>
            <nav className="hidden md:flex items-center space-x-6">
              <a href="/" className="text-muted-foreground hover:text-foreground transition-colors">Home</a>
              <a href="/academy" className="text-muted-foreground hover:text-foreground transition-colors">Academy</a>
              <a href="/professional" className="text-muted-foreground hover:text-foreground transition-colors">Professional</a>
              <a href="/demo" className="text-foreground font-medium">Demo</a>
              <a href="/pricing" className="text-muted-foreground hover:text-foreground transition-colors">Pricing</a>
            </nav>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-12">
        {/* Hero Section */}
        <section className="text-center max-w-4xl mx-auto mb-16">
          <Badge variant="secondary" className="mb-6">
            <Play className="w-4 h-4 mr-1" />
            Interactive Demo
          </Badge>
          
          <h1 className="text-4xl md:text-6xl font-bold bg-gradient-to-r from-primary to-primary/70 bg-clip-text text-transparent mb-6">
            See ClauseBot Pro in Action
          </h1>
          
          <p className="text-xl text-muted-foreground mb-8 max-w-3xl mx-auto">
            Experience real-time welding code intelligence with our interactive demos. See how ClauseBot Pro transforms complex standards into instant, actionable answers.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Button size="lg" className="px-8">
              <Play className="w-4 h-4 mr-2" />
              Launch Live Demo
            </Button>
            <Button variant="outline" size="lg">
              Schedule Personal Demo
            </Button>
          </div>
        </section>

        {/* Demo Options */}
        <section className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-16">
          {[
            {
              icon: MessageSquare,
              title: "Sarah's CWI Prep Session",
              description: "Follow Sarah, a welding student, as she prepares for her CWI exam using ClauseBot's AI-powered study assistant.",
              demo_url: "https://app.miltmonndt.com/clausebot/demo/sarah",
              duration: "5 min",
              difficulty: "Beginner"
            },
            {
              icon: Search,
              title: "Code Lookup Demo",
              description: "Watch real-time clause lookups for AWS D1.1:2025, ASME IX, and API 1104 with instant citations.",
              demo_url: "#",
              duration: "3 min",
              difficulty: "Intermediate"
            },
            {
              icon: CheckCircle,
              title: "WPS Compliance Check",
              description: "See how ClauseBot validates welding procedure specifications against current code requirements.",
              demo_url: "#",
              duration: "7 min",
              difficulty: "Advanced"
            }
          ].map((demo, index) => (
            <Card key={index} className="group hover:shadow-lg transition-all duration-200 hover:scale-105">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="p-2 bg-primary/10 rounded-lg group-hover:bg-primary/20 transition-colors">
                      <demo.icon className="w-5 h-5 text-primary" />
                    </div>
                    <div>
                      <CardTitle className="text-lg">{demo.title}</CardTitle>
                      <div className="flex items-center space-x-2 mt-1">
                        <Badge variant="outline" className="text-xs">
                          <Clock className="w-3 h-3 mr-1" />
                          {demo.duration}
                        </Badge>
                        <Badge variant="secondary" className="text-xs">
                          {demo.difficulty}
                        </Badge>
                      </div>
                    </div>
                  </div>
                  <Play className="w-6 h-6 text-muted-foreground group-hover:text-primary transition-colors" />
                </div>
              </CardHeader>
              <CardContent>
                <CardDescription className="mb-4">{demo.description}</CardDescription>
                <Button 
                  className="w-full" 
                  onClick={() => window.open(demo.demo_url, '_blank')}
                >
                  Launch Demo
                </Button>
              </CardContent>
            </Card>
          ))}
        </section>

        {/* What You'll See */}
        <section className="mb-16">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">What You'll Experience</h2>
            <p className="text-lg text-muted-foreground">See ClauseBot Pro's key features in action</p>
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            <div className="space-y-6">
              <div className="flex items-start space-x-4">
                <div className="p-2 bg-green-100 rounded-lg flex-shrink-0">
                  <CheckCircle className="w-5 h-5 text-green-600" />
                </div>
                <div>
                  <h3 className="font-semibold mb-2">Instant Clause Citations</h3>
                  <p className="text-muted-foreground">Watch ClauseBot provide exact clause references from AWS D1.1, ASME IX, and API 1104 in under 1.2 seconds.</p>
                </div>
              </div>

              <div className="flex items-start space-x-4">
                <div className="p-2 bg-blue-100 rounded-lg flex-shrink-0">
                  <MessageSquare className="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <h3 className="font-semibold mb-2">Natural Language Queries</h3>
                  <p className="text-muted-foreground">Ask questions in plain English and get precise, technical answers with full code backing.</p>
                </div>
              </div>

              <div className="flex items-start space-x-4">
                <div className="p-2 bg-purple-100 rounded-lg flex-shrink-0">
                  <BookOpen className="w-5 h-5 text-purple-600" />
                </div>
                <div>
                  <h3 className="font-semibold mb-2">Interactive Learning</h3>
                  <p className="text-muted-foreground">Experience guided practice sessions that adapt to your knowledge level and certification goals.</p>
                </div>
              </div>
            </div>

            <div className="bg-muted/50 rounded-xl p-8 flex items-center justify-center">
              <div className="text-center">
                <div className="w-24 h-24 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Play className="w-12 h-12 text-primary" />
                </div>
                <h3 className="text-lg font-semibold mb-2">Ready to See It Live?</h3>
                <p className="text-muted-foreground mb-4">
                  Launch our most popular demo to see ClauseBot Pro in action.
                </p>
                <Button>
                  Start Sarah's Demo
                </Button>
              </div>
            </div>
          </div>
        </section>

        {/* Demo Features */}
        <section className="mb-16">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Demo Features</h2>
            <p className="text-lg text-muted-foreground">Explore all the capabilities of ClauseBot Pro</p>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            {[
              "Real-time code intelligence",
              "Clause-cited accuracy",
              "Multi-standard support",
              "Interactive Q&A",
              "WPS/PQR validation",
              "CWI exam preparation",
              "Compliance checking",
              "Study progress tracking",
              "Professional workflows"
            ].map((feature, index) => (
              <div key={index} className="flex items-center space-x-3 p-4 bg-background rounded-lg border">
                <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0" />
                <span className="font-medium">{feature}</span>
              </div>
            ))}
          </div>
        </section>

        {/* CTA Section */}
        <section className="text-center bg-muted/50 rounded-2xl p-12">
          <h2 className="text-3xl font-bold mb-4">Ready to Get Started?</h2>
          <p className="text-lg text-muted-foreground mb-8 max-w-2xl mx-auto">
            Experience the power of AI-driven welding code intelligence with your free trial.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Button size="lg" className="px-8">
              Start Free Trial
            </Button>
            <Button variant="outline" size="lg">
              Contact Sales
            </Button>
          </div>
          <p className="text-sm text-muted-foreground mt-4">
            7 days free • No credit card required • Full access
          </p>
        </section>
      </main>
    </div>
  );
};

export default Demo;