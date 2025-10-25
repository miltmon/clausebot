import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { CheckCircle, ArrowLeft, ArrowRight, User, Target, BookOpen } from "lucide-react";

const AcademyOnboarding = () => {
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState({
    firstName: "",
    lastName: "",
    email: "",
    experience: "",
    goals: "",
    certifications: []
  });

  const steps = [
    { id: 1, title: "Profile Setup", icon: User },
    { id: 2, title: "Experience Level", icon: BookOpen },
    { id: 3, title: "Learning Goals", icon: Target }
  ];

  const handleNext = () => {
    if (currentStep < steps.length) {
      setCurrentStep(currentStep + 1);
    } else {
      // Route to appropriate learning path
      if (formData.goals === "weldtrack") {
        window.location.href = "/academy/weldtrack-foundation";
      } else if (formData.goals === "spli") {
        window.location.href = "/academy/spli-foundation";
      } else {
        window.location.href = "/academy";
      }
    }
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    } else {
      window.location.href = "/academy";
    }
  };

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
              <span className="font-semibold text-xl">ClauseBot Pro Academy</span>
            </div>
            <Badge variant="outline">Onboarding</Badge>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-12">
        <div className="max-w-2xl mx-auto">
          {/* Progress Steps */}
          <div className="flex items-center justify-center mb-8">
            {steps.map((step, index) => (
              <div key={step.id} className="flex items-center">
                <div className={`flex items-center space-x-2 ${
                  currentStep >= step.id ? 'text-primary' : 'text-muted-foreground'
                }`}>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center border-2 ${
                  currentStep >= step.id 
                    ? 'bg-primary border-primary text-primary-foreground' 
                    : 'border-muted-foreground'
                }`}>
                    {currentStep > step.id ? (
                      <CheckCircle className="w-4 h-4" />
                    ) : (
                      <step.icon className="w-4 h-4" />
                    )}
                  </div>
                  <span className="font-medium text-sm hidden sm:block">{step.title}</span>
                </div>
                {index < steps.length - 1 && (
                  <div className={`w-12 h-0.5 mx-4 ${
                    currentStep > step.id ? 'bg-primary' : 'bg-muted-foreground/20'
                  }`} />
                )}
              </div>
            ))}
          </div>

          {/* Step Content */}
          <Card className="mb-8">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                {(() => {
                  const CurrentIcon = steps[currentStep - 1].icon;
                  return <CurrentIcon className="w-5 h-5" />;
                })()}
                <span>{steps[currentStep - 1].title}</span>
              </CardTitle>
              <CardDescription>
                {currentStep === 1 && "Let's get to know you and set up your learning profile."}
                {currentStep === 2 && "Help us understand your current experience level."}
                {currentStep === 3 && "What would you like to focus on first?"}
              </CardDescription>
            </CardHeader>

            <CardContent className="space-y-6">
              {/* Step 1: Profile Setup */}
              {currentStep === 1 && (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="firstName">First Name</Label>
                      <Input
                        id="firstName"
                        placeholder="Enter your first name"
                        value={formData.firstName}
                        onChange={(e) => setFormData({...formData, firstName: e.target.value})}
                      />
                    </div>
                    <div>
                      <Label htmlFor="lastName">Last Name</Label>
                      <Input
                        id="lastName"
                        placeholder="Enter your last name"
                        value={formData.lastName}
                        onChange={(e) => setFormData({...formData, lastName: e.target.value})}
                      />
                    </div>
                  </div>
                  <div>
                    <Label htmlFor="email">Email Address</Label>
                    <Input
                      id="email"
                      type="email"
                      placeholder="your.email@example.com"
                      value={formData.email}
                      onChange={(e) => setFormData({...formData, email: e.target.value})}
                    />
                  </div>
                </div>
              )}

              {/* Step 2: Experience Level */}
              {currentStep === 2 && (
                <div className="space-y-4">
                  <Label>What's your current welding experience level?</Label>
                  <RadioGroup 
                    value={formData.experience} 
                    onValueChange={(value) => setFormData({...formData, experience: value})}
                  >
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="beginner" id="beginner" />
                      <Label htmlFor="beginner" className="cursor-pointer">
                        <div>
                          <div className="font-medium">Beginner</div>
                          <div className="text-sm text-muted-foreground">New to welding or just starting out</div>
                        </div>
                      </Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="intermediate" id="intermediate" />
                      <Label htmlFor="intermediate" className="cursor-pointer">
                        <div>
                          <div className="font-medium">Intermediate</div>
                          <div className="text-sm text-muted-foreground">Some welding experience, want to improve</div>
                        </div>
                      </Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="advanced" id="advanced" />
                      <Label htmlFor="advanced" className="cursor-pointer">
                        <div>
                          <div className="font-medium">Advanced</div>
                          <div className="text-sm text-muted-foreground">Experienced welder looking for certification</div>
                        </div>
                      </Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="professional" id="professional" />
                      <Label htmlFor="professional" className="cursor-pointer">
                        <div>
                          <div className="font-medium">Professional</div>
                          <div className="text-sm text-muted-foreground">CWI or inspector seeking continued education</div>
                        </div>
                      </Label>
                    </div>
                  </RadioGroup>
                </div>
              )}

              {/* Step 3: Learning Goals */}
              {currentStep === 3 && (
                <div className="space-y-4">
                  <Label>Which learning path interests you most?</Label>
                  <RadioGroup 
                    value={formData.goals} 
                    onValueChange={(value) => setFormData({...formData, goals: value})}
                  >
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="weldtrack" id="weldtrack" />
                      <Label htmlFor="weldtrack" className="cursor-pointer">
                        <div>
                          <div className="font-medium">WeldTrack Foundation</div>
                          <div className="text-sm text-muted-foreground">AWS D1.1:2025 fundamentals and CWI preparation</div>
                        </div>
                      </Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="spli" id="spli" />
                      <Label htmlFor="spli" className="cursor-pointer">
                        <div>
                          <div className="font-medium">SPLI Foundation</div>
                          <div className="text-sm text-muted-foreground">Structural plate inspection fundamentals</div>
                        </div>
                      </Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="explore" id="explore" />
                      <Label htmlFor="explore" className="cursor-pointer">
                        <div>
                          <div className="font-medium">Let me explore first</div>
                          <div className="text-sm text-muted-foreground">I want to browse all available courses</div>
                        </div>
                      </Label>
                    </div>
                  </RadioGroup>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Navigation */}
            <div className="flex items-center justify-between">
            <Button 
              variant="outline" 
              onClick={handleBack}
              className="flex items-center space-x-2"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Back</span>
            </Button>

            <div className="text-sm text-muted-foreground">
              Step {currentStep} of {steps.length}
            </div>

            <Button 
              onClick={handleNext}
              className="flex items-center space-x-2"
              disabled={
                (currentStep === 1 && (!formData.firstName || !formData.lastName || !formData.email)) ||
                (currentStep === 2 && !formData.experience) ||
                (currentStep === 3 && !formData.goals)
              }
            >
              <span>{currentStep === steps.length ? 'Get Started' : 'Next'}</span>
              <ArrowRight className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </main>
    </div>
  );
};

export default AcademyOnboarding;