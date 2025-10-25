import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { CheckCircle, Clock, Users, Zap, BookOpen, Shield, Target, Award } from "lucide-react";

const Professional = () => {
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
              <a href="/professional" className="text-foreground font-medium">Professional</a>
              <a href="/demo" className="text-muted-foreground hover:text-foreground transition-colors">Demo</a>
              <a href="/pricing" className="text-muted-foreground hover:text-foreground transition-colors">Pricing</a>
            </nav>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-12">
        {/* Hero Section */}
        <section className="text-center max-w-4xl mx-auto mb-16">
          <Badge variant="secondary" className="mb-6">
            <Zap className="w-4 h-4 mr-1" />
            Professional Welding Code Intelligence
          </Badge>
          
          <h1 className="text-4xl md:text-6xl font-bold bg-gradient-to-r from-primary to-primary/70 bg-clip-text text-transparent mb-6">
            AI-Powered Welding Code Intelligence
          </h1>
          
          <p className="text-xl text-muted-foreground mb-8 max-w-3xl mx-auto">
            Master AWS D1.1:2025, ASME IX, and API 1104 with confidence. ClauseBot and WeldTrack turn complex standards into clear, actionable guidance.
          </p>

          <div className="flex flex-wrap justify-center gap-4 mb-8">
            <Badge variant="outline" className="px-4 py-2">
              <BookOpen className="w-4 h-4 mr-1" />
              AWS D1.1:2025
            </Badge>
            <Badge variant="outline" className="px-4 py-2">
              <Shield className="w-4 h-4 mr-1" />
              ASME IX
            </Badge>
            <Badge variant="outline" className="px-4 py-2">
              <Target className="w-4 h-4 mr-1" />
              API 1104
            </Badge>
          </div>

          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Button size="lg" className="px-8">
              <Clock className="w-4 h-4 mr-2" />
              Start Free Trial
            </Button>
            <Button variant="outline" size="lg">
              See Live Demo
            </Button>
          </div>
          
          <p className="text-sm text-muted-foreground mt-4">
            7 days, no credit card required
          </p>
        </section>

        {/* Stats Section */}
        <section className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-16">
          {[
            { value: "90%", label: "fewer rework issues", subtitle: "catch violations early" },
            { value: "<1.2s", label: "answers", subtitle: "instant clause lookup" },
            { value: "2x", label: "faster CWI prep", subtitle: "guided practice, clause-linked" },
            { value: "5,000+", label: "pros", subtitle: "trained & onboard" }
          ].map((stat, index) => (
            <Card key={index} className="text-center">
              <CardContent className="pt-6">
                <div className="text-3xl font-bold text-primary mb-2">{stat.value}</div>
                <div className="font-semibold mb-1">{stat.label}</div>
                <div className="text-sm text-muted-foreground">{stat.subtitle}</div>
              </CardContent>
            </Card>
          ))}
        </section>

        {/* Learn • Practice • Apply • Certify Framework */}
        <section className="mb-16">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Learn • Practice • Apply • Certify</h2>
            <p className="text-lg text-muted-foreground">Complete welding code mastery in four powerful stages</p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              {
                icon: BookOpen,
                title: "Learn",
                description: "CWI exam prep, clause-cited answers, study assistant",
                color: "bg-blue-500"
              },
              {
                icon: Target,
                title: "Practice",
                description: "Interactive Practice Lab, quizzes, simulations",
                color: "bg-green-500"
              },
              {
                icon: Shield,
                title: "Apply",
                description: "Real-time compliance checker for WPS/PQR and inspections",
                color: "bg-orange-500"
              },
              {
                icon: Award,
                title: "Certify",
                description: "Proof Vault registry, portable records for employers",
                color: "bg-purple-500"
              }
            ].map((stage, index) => (
              <Card key={index} className="relative overflow-hidden group hover:scale-105 transition-transform duration-200">
                <div className={`absolute top-0 left-0 w-full h-1 ${stage.color}`} />
                <CardHeader>
                  <div className="flex items-center space-x-3">
                    <div className={`p-2 rounded-lg ${stage.color} text-white`}>
                      <stage.icon className="w-5 h-5" />
                    </div>
                    <CardTitle className="text-lg">{stage.title}</CardTitle>
                  </div>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-sm">{stage.description}</CardDescription>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>

        {/* Features Grid */}
        <section className="mb-16">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Why ClauseBot Pro</h2>
            <p className="text-lg text-muted-foreground">Trusted by welding professionals worldwide</p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              {
                icon: Zap,
                title: "Instant Code Intelligence",
                description: "Get clause-cited answers in under 1.2 seconds with full traceability to AWS D1.1, ASME IX, and API standards."
              },
              {
                icon: Users,
                title: "Professional Grade",
                description: "Built by 40-year AWS CWI for real welders. Trusted by 5,000+ professionals across industries."
              },
              {
                icon: CheckCircle,
                title: "Compliance Assurance",
                description: "Reduce rework by 90% with real-time violation detection and preventive guidance."
              },
              {
                icon: BookOpen,
                title: "CWI Exam Prep",
                description: "2x faster preparation with guided practice sessions and clause-linked study materials."
              },
              {
                icon: Shield,
                title: "WPS/PQR Verification",
                description: "Real-time compliance checking for welding procedures and qualification records."
              },
              {
                icon: Award,
                title: "Certification Tracking",
                description: "Integrated with MiltmonNDT Academy for complete certification management."
              }
            ].map((feature, index) => (
              <Card key={index} className="group hover:shadow-lg transition-shadow duration-200">
                <CardHeader>
                  <div className="flex items-center space-x-3">
                    <div className="p-2 bg-primary/10 rounded-lg group-hover:bg-primary/20 transition-colors">
                      <feature.icon className="w-5 h-5 text-primary" />
                    </div>
                    <CardTitle className="text-lg">{feature.title}</CardTitle>
                  </div>
                </CardHeader>
                <CardContent>
                  <CardDescription>{feature.description}</CardDescription>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>

        {/* CTA Section */}
        <section className="text-center bg-muted/50 rounded-2xl p-12">
          <h2 className="text-3xl font-bold mb-4">Ready to Transform Your Welding Practice?</h2>
          <p className="text-lg text-muted-foreground mb-8 max-w-2xl mx-auto">
            Join thousands of welding professionals who trust ClauseBot Pro for code intelligence and compliance.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Button size="lg" className="px-8">
              Start Free Trial
            </Button>
            <Button variant="outline" size="lg">
              Schedule Demo
            </Button>
          </div>
        </section>
      </main>
    </div>
  );
};

export default Professional;