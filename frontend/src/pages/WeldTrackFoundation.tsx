import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { 
  BookOpen, 
  Play, 
  CheckCircle, 
  Clock, 
  Users, 
  Award,
  FileText,
  Video,
  Brain,
  Target
} from "lucide-react";

const WeldTrackFoundation = () => {
  const modules = [
    {
      id: 1,
      title: "AWS D1.1 Fundamentals",
      description: "Introduction to structural welding code basics",
      lessons: 8,
      duration: "2 hours",
      completed: true,
      type: "video"
    },
    {
      id: 2,
      title: "Material Requirements",
      description: "Base metals, filler metals, and qualification",
      lessons: 6,
      duration: "1.5 hours",
      completed: true,
      type: "interactive"
    },
    {
      id: 3,
      title: "Welding Procedure Specifications",
      description: "WPS development and qualification requirements",
      lessons: 10,
      duration: "3 hours",
      completed: false,
      current: true,
      type: "hands-on"
    },
    {
      id: 4,
      title: "Visual Inspection Techniques",
      description: "Acceptance criteria and inspection methods",
      lessons: 12,
      duration: "2.5 hours",
      completed: false,
      type: "practical"
    },
    {
      id: 5,
      title: "CWI Exam Preparation",
      description: "Practice tests and exam strategies",
      lessons: 15,
      duration: "4 hours",
      completed: false,
      type: "assessment"
    }
  ];

  const getModuleIcon = (type: string) => {
    switch (type) {
      case 'video': return Video;
      case 'interactive': return Brain;
      case 'hands-on': return Target;
      case 'practical': return FileText;
      case 'assessment': return Award;
      default: return BookOpen;
    }
  };

  const completedModules = modules.filter(m => m.completed).length;
  const progressPercentage = (completedModules / modules.length) * 100;

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
              <span className="font-semibold text-xl">WeldTrack Foundation</span>
            </div>
            <nav className="hidden md:flex items-center space-x-6">
              <a href="/academy" className="text-muted-foreground hover:text-foreground transition-colors">← Back to Academy</a>
              <Badge variant="outline">In Progress</Badge>
            </nav>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-12">
        {/* Course Header */}
        <section className="mb-12">
          <div className="grid lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2">
              <Badge variant="secondary" className="mb-4">
                <BookOpen className="w-4 h-4 mr-1" />
                AWS D1.1:2025 Foundation Course
              </Badge>
              
              <h1 className="text-4xl font-bold mb-4">WeldTrack Foundation</h1>
              <p className="text-xl text-muted-foreground mb-6">
                Master AWS D1.1:2025 fundamentals with interactive lessons, practice exercises, and real-world applications. 
                Built by industry experts for aspiring CWIs and welding professionals.
              </p>

              <div className="flex flex-wrap gap-4 mb-6">
                <div className="flex items-center space-x-2 text-sm">
                  <Clock className="w-4 h-4 text-muted-foreground" />
                  <span>8-12 weeks</span>
                </div>
                <div className="flex items-center space-x-2 text-sm">
                  <Users className="w-4 h-4 text-muted-foreground" />
                  <span>2,400+ students</span>
                </div>
                <div className="flex items-center space-x-2 text-sm">
                  <Award className="w-4 h-4 text-muted-foreground" />
                  <span>Certificate included</span>
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span>Course Progress</span>
                  <span>{completedModules} of {modules.length} modules completed</span>
                </div>
                <Progress value={progressPercentage} className="h-2" />
              </div>
            </div>

            <div className="lg:col-span-1">
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">ClauseBot Integration</CardTitle>
                  <CardDescription>AI-powered learning assistant</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="bg-muted/50 rounded-lg p-4 border-2 border-dashed border-muted-foreground/20">
                    <div className="text-center">
                      <Brain className="w-8 h-8 text-primary mx-auto mb-2" />
                      <h3 className="font-semibold mb-1">Ask ClauseBot</h3>
                      <p className="text-sm text-muted-foreground mb-3">
                        Get instant answers to AWS D1.1 questions with clause citations
                      </p>
                      <Button size="sm" className="w-full">
                        Launch ClauseBot
                      </Button>
                    </div>
                  </div>
                  <div className="text-xs text-muted-foreground text-center">
                    Available 24/7 throughout your learning journey
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </section>

        {/* Course Modules */}
        <section className="mb-12">
          <div className="flex items-center justify-between mb-8">
            <h2 className="text-2xl font-bold">Course Modules</h2>
            <Button variant="outline">
              <Play className="w-4 h-4 mr-2" />
              Continue Learning
            </Button>
          </div>

          <div className="space-y-4">
            {modules.map((module, index) => {
              const ModuleIcon = getModuleIcon(module.type);
              
              return (
                <Card 
                  key={module.id} 
                  className={`transition-all duration-200 hover:shadow-md ${
                    module.current ? 'ring-2 ring-primary' : ''
                  } ${module.completed ? 'bg-muted/30' : ''}`}
                >
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <div className={`p-3 rounded-lg ${
                          module.completed 
                            ? 'bg-green-100 text-green-600' 
                            : module.current
                            ? 'bg-primary/10 text-primary'
                            : 'bg-muted text-muted-foreground'
                        }`}>
                          {module.completed ? (
                            <CheckCircle className="w-6 h-6" />
                          ) : (
                            <ModuleIcon className="w-6 h-6" />
                          )}
                        </div>
                        
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-1">
                            <h3 className="text-lg font-semibold">{module.title}</h3>
                            {module.current && (
                              <Badge variant="default" className="text-xs">Current</Badge>
                            )}
                            {module.completed && (
                              <Badge variant="secondary" className="text-xs">Complete</Badge>
                            )}
                          </div>
                          <p className="text-muted-foreground mb-2">{module.description}</p>
                          <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                            <span>{module.lessons} lessons</span>
                            <span>•</span>
                            <span>{module.duration}</span>
                            <span>•</span>
                            <span className="capitalize">{module.type}</span>
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center space-x-2">
                        {module.completed ? (
                          <Button variant="outline" size="sm">
                            Review
                          </Button>
                        ) : module.current ? (
                          <Button size="sm">
                            Continue
                          </Button>
                        ) : (
                          <Button variant="ghost" size="sm" disabled>
                            Locked
                          </Button>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </section>

        {/* Course Stats */}
        <section className="grid md:grid-cols-4 gap-6 mb-12">
          {[
            { label: "Completion Rate", value: "95%", icon: Award },
            { label: "Avg. Study Time", value: "6 weeks", icon: Clock },
            { label: "Pass Rate", value: "89%", icon: Target },
            { label: "Student Rating", value: "4.8/5", icon: Users }
          ].map((stat, index) => (
            <Card key={index} className="text-center">
              <CardContent className="pt-6">
                <stat.icon className="w-8 h-8 text-primary mx-auto mb-2" />
                <div className="text-2xl font-bold text-primary mb-1">{stat.value}</div>
                <div className="text-sm text-muted-foreground">{stat.label}</div>
              </CardContent>
            </Card>
          ))}
        </section>

        {/* Learning Resources */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-6">Additional Resources</h2>
          <div className="grid md:grid-cols-3 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center space-x-2">
                  <FileText className="w-5 h-5" />
                  <span>Study Guides</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground mb-4">
                  Comprehensive PDF guides covering all module topics with quick reference charts.
                </p>
                <Button variant="outline" size="sm">Download All</Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center space-x-2">
                  <Brain className="w-5 h-5" />
                  <span>Practice Tests</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground mb-4">
                  Interactive quizzes and mock CWI exams to test your knowledge and readiness.
                </p>
                <Button variant="outline" size="sm">Start Quiz</Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center space-x-2">
                  <Users className="w-5 h-5" />
                  <span>Community</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground mb-4">
                  Connect with fellow students and instructors in our dedicated discussion forums.
                </p>
                <Button variant="outline" size="sm">Join Discussion</Button>
              </CardContent>
            </Card>
          </div>
        </section>

        {/* CTA Section */}
        <section className="text-center bg-muted/50 rounded-2xl p-12">
          <h2 className="text-3xl font-bold mb-4">Ready to Continue Your Journey?</h2>
          <p className="text-lg text-muted-foreground mb-8 max-w-2xl mx-auto">
            Master AWS D1.1:2025 with expert guidance and practical applications. Join thousands of successful welding professionals.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Button size="lg" className="px-8">
              <Play className="w-4 h-4 mr-2" />
              Continue Module 3
            </Button>
            <Button variant="outline" size="lg">
              View All Courses
            </Button>
          </div>
        </section>
      </main>
    </div>
  );
};

export default WeldTrackFoundation;