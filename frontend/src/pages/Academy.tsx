import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { BookOpen, Users, Award, Target, Clock, ArrowRight } from "lucide-react";

const Academy = () => {
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
            <nav className="hidden md:flex items-center space-x-6">
              <a href="/" className="text-muted-foreground hover:text-foreground transition-colors">Home</a>
              <a href="/academy" className="text-foreground font-medium">Academy</a>
              <a href="/professional" className="text-muted-foreground hover:text-foreground transition-colors">Professional</a>
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
            <BookOpen className="w-4 h-4 mr-1" />
            MiltmonNDT Academy
          </Badge>
          
          <h1 className="text-4xl md:text-6xl font-bold bg-gradient-to-r from-primary to-primary/70 bg-clip-text text-transparent mb-6">
            Master Welding Standards
          </h1>
          
          <p className="text-xl text-muted-foreground mb-8 max-w-3xl mx-auto">
            Built by a 40-year AWS CWI for real welders. From fundamentals to certification, learn at your own pace with AI-powered guidance and practical applications.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Button size="lg" className="px-8" onClick={() => window.location.href = '/academy/onboarding'}>
              <ArrowRight className="w-4 h-4 mr-2" />
              Begin Your Journey
            </Button>
            <Button variant="outline" size="lg">
              Browse Tracks
            </Button>
          </div>
        </section>

        {/* Learning Paths */}
        <section className="mb-16">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Learning Paths</h2>
            <p className="text-lg text-muted-foreground">Choose your certification journey</p>
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            <Card className="group hover:shadow-lg transition-all duration-200 hover:scale-105">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="p-3 bg-blue-500/10 rounded-lg group-hover:bg-blue-500/20 transition-colors">
                      <BookOpen className="w-6 h-6 text-blue-600" />
                    </div>
                    <div>
                      <CardTitle className="text-xl">WeldTrack Foundation</CardTitle>
                      <CardDescription>AWS D1.1 fundamentals and CWI prep</CardDescription>
                    </div>
                  </div>
                  <Badge variant="outline">Most Popular</Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                  <Clock className="w-4 h-4" />
                  <span>8-12 weeks</span>
                  <Users className="w-4 h-4 ml-4" />
                  <span>2,400+ students</span>
                </div>
                <p className="text-muted-foreground">
                  Master AWS D1.1:2025 with interactive lessons, practice quizzes, and real-world applications. Perfect for aspiring CWIs and welding professionals.
                </p>
                <div className="space-y-2">
                  <h4 className="font-semibold text-sm">What you'll learn:</h4>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    <li>• AWS D1.1 code fundamentals</li>
                    <li>• WPS and PQR requirements</li>
                    <li>• Visual inspection techniques</li>
                    <li>• CWI exam preparation</li>
                  </ul>
                </div>
                <Button className="w-full" onClick={() => window.location.href = '/academy/weldtrack-foundation'}>
                  Start WeldTrack
                </Button>
              </CardContent>
            </Card>

            <Card className="group hover:shadow-lg transition-all duration-200 hover:scale-105">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="p-3 bg-green-500/10 rounded-lg group-hover:bg-green-500/20 transition-colors">
                      <Target className="w-6 h-6 text-green-600" />
                    </div>
                    <div>
                      <CardTitle className="text-xl">SPLI Foundation</CardTitle>
                      <CardDescription>Structural plate inspection basics</CardDescription>
                    </div>
                  </div>
                  <Badge variant="secondary">New</Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                  <Clock className="w-4 h-4" />
                  <span>4-6 weeks</span>
                  <Users className="w-4 h-4 ml-4" />
                  <span>New track</span>
                </div>
                <p className="text-muted-foreground">
                  Learn structural plate inspection fundamentals with hands-on exercises and industry best practices. Ideal for inspectors and quality professionals.
                </p>
                <div className="space-y-2">
                  <h4 className="font-semibold text-sm">What you'll learn:</h4>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    <li>• Structural plate basics</li>
                    <li>• Inspection methodologies</li>
                    <li>• Quality assurance protocols</li>
                    <li>• Documentation standards</li>
                  </ul>
                </div>
                <Button className="w-full" variant="outline">
                  Coming Soon
                </Button>
              </CardContent>
            </Card>
          </div>
        </section>

        {/* Academy Stats */}
        <section className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-16">
          {[
            { value: "2,400+", label: "Active Students", icon: Users },
            { value: "95%", label: "Pass Rate", icon: Award },
            { value: "40+", label: "Years Experience", icon: Clock },
            { value: "AWS", label: "CWI Built", icon: BookOpen }
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

        {/* Integration with MiltmonNDT */}
        <section className="mb-16">
          <Card className="bg-muted/50 border-2 border-dashed border-muted-foreground/20">
            <CardContent className="p-8 text-center">
              <div className="flex items-center justify-center space-x-4 mb-6">
                <div className="h-12 w-12 bg-primary rounded-lg flex items-center justify-center">
                  <span className="text-primary-foreground font-bold">CB</span>
                </div>
                <div className="text-2xl font-bold text-muted-foreground">+</div>
                <div className="h-12 w-12 bg-green-500 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-sm">NDT</span>
                </div>
              </div>
              <h3 className="text-xl font-bold mb-2">Integrated with MiltmonNDT</h3>
              <p className="text-muted-foreground mb-6 max-w-2xl mx-auto">
                Your learning progress automatically syncs with your MiltmonNDT certification vault. 
                Complete courses, earn certificates, and maintain your professional record in one place.
              </p>
              <Button variant="outline" onClick={() => window.open('https://www.miltmonndt.com/academy', '_blank')}>
                Visit MiltmonNDT Academy
              </Button>
            </CardContent>
          </Card>
        </section>

        {/* CTA Section */}
        <section className="text-center bg-muted/50 rounded-2xl p-12">
          <h2 className="text-3xl font-bold mb-4">Ready to Start Learning?</h2>
          <p className="text-lg text-muted-foreground mb-8 max-w-2xl mx-auto">
            Join thousands of welding professionals advancing their careers through structured, expert-led education.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Button size="lg" className="px-8" onClick={() => window.location.href = '/academy/onboarding'}>
              Begin Onboarding
            </Button>
            <Button variant="outline" size="lg">
              Learn More
            </Button>
          </div>
        </section>
      </main>
    </div>
  );
};

export default Academy;