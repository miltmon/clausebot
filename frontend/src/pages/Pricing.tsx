import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { CheckCircle, X, Zap, Building2, Users, Crown } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { usePageTitle } from "@/hooks/usePageTitle";

const Pricing = () => {
  usePageTitle("Pricing");
  const navigate = useNavigate();
  
  const plans = [
    {
      name: "ClauseBot.Ai",
      description: "Perfect for individual welders",
      price: "$49.00",
      period: "per month",
      planId: "basic",
      icon: Zap,
      popular: false,
      features: [
        "AWS D1.1:2025 compliance",
        "Real-time clause citations",
        "< 2 second response time",
        "99.7% accuracy guarantee",
        "Basic WPS checking",
        "Email support"
      ],
      limitations: [
        "Limited to welding standards",
        "No API access",
        "No team features"
      ],
      cta: "Start Free Trial",
      link: "https://clausebotai.lovable.app"
    },
    {
      name: "ClauseBot Pro",
      description: "Multi-craft platform for professionals",
      price: "$99",
      period: "per month",
      planId: "pro",
      icon: Building2,
      popular: true,
      features: [
        "All ClauseBot.Ai features",
        "Multi-craft modules (WeldTrack™, VoltTrack™, MediTrack™)",
        "ASME IX, API 1104, NEC, FDA standards",
        "Advanced WPS/PQR validation",
        "Audit trail & compliance docs",
        "SOC 2 & GDPR compliance",
        "Priority support",
        "Academy access"
      ],
      limitations: [
        "Single user license",
        "Limited API calls"
      ],
      cta: "Upgrade to Pro",
      link: "/checkout?plan=pro"
    },
    {
      name: "Enterprise",
      description: "Custom solutions for organizations",
      price: "Custom",
      period: "pricing",
      planId: "enterprise",
      icon: Crown,
      popular: false,
      features: [
        "All Pro features",
        "Unlimited users",
        "ClauseOS API access",
        "Custom integrations",
        "White-label options",
        "Dedicated support",
        "Custom standards",
        "On-premise deployment",
        "Training & onboarding",
        "SLA guarantees"
      ],
      limitations: [],
      cta: "Contact Sales",
      link: "mailto:sales@clausebot.pro?subject=Enterprise Inquiry"
    }
  ];

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
              <a href="/demo" className="text-muted-foreground hover:text-foreground transition-colors">Demo</a>
              <a href="/pricing" className="text-foreground font-medium">Pricing</a>
            </nav>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-12">
        {/* Hero Section */}
        <section className="text-center max-w-4xl mx-auto mb-16">
          <h1 className="text-4xl md:text-6xl font-bold bg-gradient-to-r from-primary to-primary/70 bg-clip-text text-transparent mb-6">
            Choose Your Plan
          </h1>
          
          <p className="text-xl text-muted-foreground mb-8 max-w-3xl mx-auto">
            From individual welders to enterprise organizations, we have the right solution for your compliance and code intelligence needs.
          </p>

          <div className="flex items-center justify-center space-x-2 mb-8">
            <Badge variant="secondary" className="px-4 py-2">
              <CheckCircle className="w-4 h-4 mr-1" />
              7-day free trial on all plans
            </Badge>
            <Badge variant="outline" className="px-4 py-2">
              No credit card required
            </Badge>
          </div>
        </section>

        {/* Pricing Cards */}
        <section className="grid lg:grid-cols-3 gap-8 mb-16">
          {plans.map((plan, index) => (
            <Card 
              key={index} 
              className={`relative overflow-hidden transition-all duration-200 hover:scale-105 ${
                plan.popular ? 'ring-2 ring-primary shadow-xl' : 'hover:shadow-lg'
              }`}
            >
              {plan.popular && (
                <div className="absolute top-0 left-0 right-0 bg-primary text-primary-foreground text-center py-2 text-sm font-medium">
                  Most Popular
                </div>
              )}
              
              <CardHeader className={plan.popular ? "pt-12" : ""}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className={`p-2 rounded-lg ${plan.popular ? 'bg-primary text-primary-foreground' : 'bg-primary/10 text-primary'}`}>
                      <plan.icon className="w-5 h-5" />
                    </div>
                    <div>
                      <CardTitle className="text-xl">{plan.name}</CardTitle>
                      <CardDescription>{plan.description}</CardDescription>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-baseline space-x-2 mt-6">
                  <span className="text-4xl font-bold">{plan.price}</span>
                  <span className="text-muted-foreground">/{plan.period}</span>
                </div>
              </CardHeader>

              <CardContent className="space-y-6">
                {/* Features */}
                <div>
                  <h4 className="font-semibold mb-3 text-green-700">Included Features</h4>
                  <ul className="space-y-2">
                    {plan.features.map((feature, featureIndex) => (
                      <li key={featureIndex} className="flex items-start space-x-2">
                        <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                        <span className="text-sm">{feature}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Limitations */}
                {plan.limitations.length > 0 && (
                  <div>
                    <h4 className="font-semibold mb-3 text-muted-foreground">Limitations</h4>
                    <ul className="space-y-2">
                      {plan.limitations.map((limitation, limitationIndex) => (
                        <li key={limitationIndex} className="flex items-start space-x-2">
                          <X className="w-4 h-4 text-muted-foreground mt-0.5 flex-shrink-0" />
                          <span className="text-sm text-muted-foreground">{limitation}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                <Button 
                  className={`w-full ${plan.popular ? '' : 'variant-outline'}`}
                  size="lg"
                  onClick={() => {
                    if (plan.name === "ClauseBot.Ai") {
                      window.open(plan.link, '_blank');
                    } else if (plan.planId) {
                      navigate(`/checkout?plan=${plan.planId}`);
                    } else {
                      window.location.href = plan.link;
                    }
                  }}
                >
                  {plan.cta}
                </Button>
              </CardContent>
            </Card>
          ))}
        </section>

        {/* Feature Comparison */}
        <section className="mb-16">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Feature Comparison</h2>
            <p className="text-lg text-muted-foreground">See what's included in each plan</p>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full border border-border rounded-lg overflow-hidden">
              <thead className="bg-muted">
                <tr>
                  <th className="text-left p-4 font-semibold">Features</th>
                  <th className="text-center p-4 font-semibold">ClauseBot.Ai</th>
                  <th className="text-center p-4 font-semibold">ClauseBot Pro</th>
                  <th className="text-center p-4 font-semibold">Enterprise</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {[
                  ["AWS D1.1:2025 Support", true, true, true],
                  ["Multi-craft Modules", false, true, true],
                  ["API Access", false, false, true],
                  ["Team Features", false, false, true],
                  ["Custom Standards", false, false, true],
                  ["White-label Options", false, false, true],
                  ["On-premise Deployment", false, false, true],
                  ["Dedicated Support", false, false, true]
                ].map(([feature, clausebotAI, clausebotPro, enterprise], index) => (
                  <tr key={index} className="hover:bg-muted/50">
                    <td className="p-4 font-medium">{feature}</td>
                    <td className="p-4 text-center">
                      {clausebotAI ? (
                        <CheckCircle className="w-5 h-5 text-green-500 mx-auto" />
                      ) : (
                        <X className="w-5 h-5 text-muted-foreground mx-auto" />
                      )}
                    </td>
                    <td className="p-4 text-center">
                      {clausebotPro ? (
                        <CheckCircle className="w-5 h-5 text-green-500 mx-auto" />
                      ) : (
                        <X className="w-5 h-5 text-muted-foreground mx-auto" />
                      )}
                    </td>
                    <td className="p-4 text-center">
                      {enterprise ? (
                        <CheckCircle className="w-5 h-5 text-green-500 mx-auto" />
                      ) : (
                        <X className="w-5 h-5 text-muted-foreground mx-auto" />
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        {/* FAQ Section */}
        <section className="mb-16">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Frequently Asked Questions</h2>
            <p className="text-lg text-muted-foreground">Everything you need to know about our pricing</p>
          </div>

          <div className="max-w-3xl mx-auto space-y-6">
            {[
              {
                question: "Can I switch plans anytime?",
                answer: "Yes, you can upgrade or downgrade your plan at any time. Changes take effect immediately, and we'll prorate any billing differences."
              },
              {
                question: "What's included in the free trial?",
                answer: "All plans include a 7-day free trial with full access to features. No credit card required to start."
              },
              {
                question: "Do you offer discounts for educational institutions?",
                answer: "Yes, we offer special pricing for educational institutions and students. Contact our sales team for more information."
              },
              {
                question: "What payment methods do you accept?",
                answer: "We accept all major credit cards, PayPal, and can arrange invoicing for enterprise customers."
              }
            ].map((faq, index) => (
              <Card key={index}>
                <CardHeader>
                  <CardTitle className="text-lg">{faq.question}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground">{faq.answer}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>

        {/* CTA Section */}
        <section className="text-center bg-muted/50 rounded-2xl p-12">
          <h2 className="text-3xl font-bold mb-4">Ready to Get Started?</h2>
          <p className="text-lg text-muted-foreground mb-8 max-w-2xl mx-auto">
            Join thousands of welding professionals who trust ClauseBot Pro for code intelligence and compliance.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Button size="lg" className="px-8" onClick={() => navigate('/checkout?plan=pro')}>
              Start Free Trial
            </Button>
            <Button variant="outline" size="lg" onClick={() => window.location.href = 'mailto:sales@clausebot.pro?subject=Sales Inquiry'}>
              Contact Sales
            </Button>
          </div>
          <p className="text-sm text-muted-foreground mt-4">
            Questions? Contact our team at sales@clausebot.pro
          </p>
        </section>
      </main>
    </div>
  );
};

export default Pricing;