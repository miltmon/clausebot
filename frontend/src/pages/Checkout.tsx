import { useEffect, useState } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { CheckCircle, Loader2, AlertCircle, ArrowLeft } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { usePageTitle } from "@/hooks/usePageTitle";
import { supabase } from "@/integrations/supabase/client";

const Checkout = () => {
  usePageTitle("Checkout");
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  
  // Get plan from URL params (e.g., /checkout?plan=pro)
  const plan = searchParams.get("plan") || "pro";
  
  // Plan configurations
  const planDetails: Record<string, { 
    name: string; 
    price: string; 
    priceId: string; 
    features: string[];
    popular?: boolean;
  }> = {
    basic: {
      name: "ClauseBot.Ai",
      price: "$49.00/month",
      priceId: "price_1SNmJlGX27lkbwbwhCjF2SX9", // Test price - ClauseBot Pro Subscription $19/month
      features: [
        "AWS D1.1:2025 compliance",
        "Real-time clause citations",
        "< 2 second response time",
        "99.7% accuracy guarantee",
        "Basic WPS checking",
        "Email support"
      ]
    },
    pro: {
      name: "ClauseBot Pro",
      price: "$19.00/month",
      priceId: "price_1SNmJlGX27lkbwbwhCjF2SX9", // Test price - ClauseBot Pro Subscription $19/month
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
      ]
    },
    enterprise: {
      name: "Enterprise",
      price: "Custom pricing",
      priceId: "", // Enterprise uses contact form
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
      ]
    }
  };

  const selectedPlan = planDetails[plan] || planDetails.pro;

  // Handle Stripe Checkout
  const handleCheckout = async () => {
    if (plan === "enterprise") {
      // Enterprise goes to contact form
      window.location.href = "mailto:sales@clausebot.pro?subject=Enterprise Inquiry";
      return;
    }

    setLoading(true);
    
    try {
      // Call Supabase Edge Function to create Stripe Checkout Session
      const { data, error } = await supabase.functions.invoke('create-checkout-session', {
        body: {
          priceId: selectedPlan.priceId,
          plan: plan,
          successUrl: `${window.location.origin}/checkout?success=true&plan=${plan}`,
          cancelUrl: `${window.location.origin}/pricing`,
        },
      });

      if (error) {
        throw error;
      }

      if (!data?.url) {
        throw new Error("No checkout URL returned");
      }
      
      // Redirect to Stripe Checkout
      window.location.href = data.url;
      
    } catch (error) {
      console.error("Checkout error:", error);
      toast({
        title: "Checkout Error",
        description: error instanceof Error ? error.message : "Failed to start checkout. Please try again or contact support.",
        variant: "destructive",
      });
      setLoading(false);
    }
  };

  // Handle success/cancel callbacks from Stripe
  useEffect(() => {
    const successParam = searchParams.get("success");
    if (successParam === "true") {
      setSuccess(true);
      toast({
        title: "Payment Successful! 🎉",
        description: `Welcome to ${selectedPlan.name}! Check your email for next steps.`,
      });
    }
  }, [searchParams, selectedPlan.name, toast]);

  // Success view after payment
  if (success) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-background to-muted flex items-center justify-center p-4">
        <Card className="max-w-2xl w-full">
          <CardHeader className="text-center">
            <div className="mx-auto w-16 h-16 bg-green-500/10 rounded-full flex items-center justify-center mb-4">
              <CheckCircle className="w-10 h-10 text-green-500" />
            </div>
            <CardTitle className="text-3xl">Payment Successful!</CardTitle>
            <CardDescription className="text-lg">
              Welcome to {selectedPlan.name}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="bg-muted/50 rounded-lg p-6 space-y-3">
              <h3 className="font-semibold">What happens next?</h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li className="flex items-start space-x-2">
                  <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                  <span>Check your email for your welcome message and account setup instructions</span>
                </li>
                <li className="flex items-start space-x-2">
                  <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                  <span>Your subscription is now active and you have full access to all features</span>
                </li>
                <li className="flex items-start space-x-2">
                  <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                  <span>You can manage your subscription anytime from your dashboard</span>
                </li>
              </ul>
            </div>
            
            <div className="flex flex-col sm:flex-row gap-3">
              <Button 
                className="flex-1" 
                size="lg"
                onClick={() => navigate("/dashboard")}
              >
                Go to Dashboard
              </Button>
              <Button 
                variant="outline" 
                className="flex-1"
                onClick={() => navigate("/academy")}
              >
                Explore Academy
              </Button>
            </div>
            
            <p className="text-center text-sm text-muted-foreground">
              Need help? Contact us at support@clausebot.pro
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Main checkout view
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
            <Button 
              variant="ghost" 
              onClick={() => navigate("/pricing")}
              className="flex items-center space-x-2"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Back to Pricing</span>
            </Button>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-12">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold mb-4">Complete Your Order</h1>
            <p className="text-lg text-muted-foreground">
              You're one step away from unlocking powerful compliance intelligence
            </p>
          </div>

          <div className="grid lg:grid-cols-2 gap-8">
            {/* Order Summary */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  Order Summary
                  {selectedPlan.popular && (
                    <Badge variant="default">Most Popular</Badge>
                  )}
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex items-center justify-between pb-4 border-b">
                  <div>
                    <h3 className="font-semibold text-lg">{selectedPlan.name}</h3>
                    <p className="text-sm text-muted-foreground">Billed monthly</p>
                  </div>
                  <div className="text-right">
                    <p className="text-2xl font-bold">{selectedPlan.price}</p>
                  </div>
                </div>

                <div>
                  <h4 className="font-semibold mb-3">Included Features:</h4>
                  <ul className="space-y-2">
                    {selectedPlan.features.map((feature, index) => (
                      <li key={index} className="flex items-start space-x-2">
                        <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                        <span className="text-sm">{feature}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="bg-muted/50 rounded-lg p-4 space-y-2">
                  <div className="flex items-center space-x-2 text-sm">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    <span>7-day free trial included</span>
                  </div>
                  <div className="flex items-center space-x-2 text-sm">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    <span>Cancel anytime, no commitment</span>
                  </div>
                  <div className="flex items-center space-x-2 text-sm">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    <span>Secure payment via Stripe</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Checkout Action */}
            <Card>
              <CardHeader>
                <CardTitle>Payment Details</CardTitle>
                <CardDescription>
                  Secure checkout powered by Stripe
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="bg-blue-50 dark:bg-blue-950/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 flex items-start space-x-3">
                  <AlertCircle className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
                  <div className="text-sm">
                    <p className="font-medium text-blue-900 dark:text-blue-100 mb-1">
                      Free Trial Information
                    </p>
                    <p className="text-blue-700 dark:text-blue-300">
                      You won't be charged during your 7-day trial period. Cancel anytime before the trial ends.
                    </p>
                  </div>
                </div>

                <Button 
                  className="w-full" 
                  size="lg"
                  onClick={handleCheckout}
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Processing...
                    </>
                  ) : (
                    <>
                      Continue to Payment
                    </>
                  )}
                </Button>

                <div className="space-y-3">
                  <p className="text-xs text-center text-muted-foreground">
                    By continuing, you agree to our Terms of Service and Privacy Policy
                  </p>
                  
                  <div className="flex items-center justify-center space-x-2 text-xs text-muted-foreground">
                    <span>🔒 Secured by Stripe</span>
                    <span>•</span>
                    <span>256-bit SSL encryption</span>
                  </div>
                </div>

                <div className="border-t pt-6 space-y-4">
                  <h4 className="font-semibold text-sm">Need help?</h4>
                  <div className="space-y-2 text-sm text-muted-foreground">
                    <p>
                      Questions about pricing or features? 
                      <a href="mailto:sales@clausebot.pro" className="text-primary hover:underline ml-1">
                        Contact our sales team
                      </a>
                    </p>
                    <p>
                      Looking for enterprise pricing?
                      <Button 
                        variant="link" 
                        className="h-auto p-0 ml-1"
                        onClick={() => navigate("/pricing")}
                      >
                        View enterprise options
                      </Button>
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Checkout;

