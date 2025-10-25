
import React, { useState } from "react";
import { ArrowRight, Brain } from "lucide-react";
import { QuizModal } from "./QuizModal";

const Hero = () => {
  const [isQuizOpen, setIsQuizOpen] = useState(false);

  return (
    <section className="bg-[#0B1220] text-white" id="hero">
      <div className="max-w-6xl mx-auto px-6 py-16">
        <div className="flex items-center gap-3 mb-4">
          <div className="h-8 w-8 rounded-lg bg-[#0D47A1] flex items-center justify-center">
            <span className="font-bold text-sm">CB</span>
          </div>
          <h1 className="text-2xl md:text-3xl font-semibold">ClauseBot.Ai</h1>
        </div>

        <p className="text-3xl md:text-5xl font-semibold tracking-tight">
          Clause-cited. Decision-ready.
        </p>

        <p className="mt-4 max-w-2xl text-white/80">
          The compliance OS for standards-driven work. Instant, clause-referenced answers for AWS D1.1:2025, ASME IX, API 1104—and beyond.
        </p>

        <div className="mt-8 flex flex-col sm:flex-row gap-3">
          <a 
            href="/auth" 
            className="px-5 py-3 rounded-lg bg-[#0D47A1] hover:bg-[#0A3A85] transition-colors duration-200 flex items-center justify-center gap-2"
          >
            Get Started Free
            <ArrowRight className="w-4 h-4" />
          </a>
          <button 
            onClick={() => setIsQuizOpen(true)}
            className="px-5 py-3 rounded-lg border border-white/20 hover:bg-white/10 transition-colors duration-200 flex items-center justify-center gap-2"
          >
            <Brain className="w-4 h-4" />
            Start ClauseBot Quiz
          </button>
        </div>

        <blockquote className="mt-8 text-white/70 italic">
          "ClauseBot was never about replacing welders. It was about honoring them—
          by giving them a colleague who never sleeps, never forgets, and never compromises on SAFETY."
          <span className="not-italic"> — "Miltmon"</span>
        </blockquote>
      </div>

      <QuizModal 
        isOpen={isQuizOpen} 
        onClose={() => setIsQuizOpen(false)}
        category="Structural Welding"
      />
    </section>
  );

};

export default Hero;
