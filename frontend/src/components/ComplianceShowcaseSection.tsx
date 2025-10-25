
import React, { useRef, useEffect } from "react";

const ComplianceShowcaseSection = () => {
  const sectionRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Simple animation when the section comes into view
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("opacity-100", "translate-y-0");
            entry.target.classList.remove("opacity-0", "translate-y-10");
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.2 }
    );
    
    if (sectionRef.current) {
      observer.observe(sectionRef.current);
    }
    
    return () => {
      if (sectionRef.current) {
        observer.unobserve(sectionRef.current);
      }
    };
  }, []);

  return (
    <section ref={sectionRef} className="w-full py-20 bg-gray-100" id="compliance-showcase">
      <div className="container px-6 lg:px-8 mx-auto">
        <div className="flex flex-col items-center opacity-0 translate-y-10 transition-all duration-1000">
          <div className="mb-12 text-center">
            <div className="pulse-chip mb-4">
              <span className="inline-flex items-center justify-center w-5 h-5 rounded-full bg-pulse-500 text-white mr-2">03</span>
              <span>Compliance Engine</span>
            </div>
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-display font-bold mb-4">
              Production-Ready AI Platform with <span className="text-[#FC4D0A]">Enterprise Architecture</span>
            </h2>
            <p className="text-lg text-gray-600 max-w-3xl mx-auto">
              Built with multi-model AI routing, RAG pipeline architecture, real-time monitoring, and enterprise security. 
              Featuring advanced vector search, intelligent caching, audit-grade compliance, and production-ready infrastructure.
            </p>
          </div>
          
          <div className="relative w-full max-w-4xl overflow-hidden rounded-3xl shadow-2xl">
            <img 
              src="/clausebot-badge.png" 
              alt="ClauseBot.Ai enterprise architecture showing AI compliance with decision-ready indicators" 
              className="w-full object-cover"
            />
            <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent p-8">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-white text-xl font-semibold">Enterprise AI Architecture</h3>
                  <p className="text-white/80">Multi-model routing with production monitoring</p>
                </div>
                <button className="px-6 py-3 bg-pulse-500 hover:bg-pulse-600 text-white font-medium rounded-full transition-colors duration-300">
                  Learn More
                </button>
              </div>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
            <div className="bg-white p-6 rounded-xl shadow-elegant hover:shadow-elegant-hover transition-all duration-300">
              <div className="w-12 h-12 bg-pulse-100 rounded-full flex items-center justify-center mb-4">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 16V12M12 8H12.01M22 12C22 17.5228 17.5228 22 12 22C6.47715 22 2 17.5228 2 12C2 6.47715 6.47715 2 12 2C17.5228 2 22 6.47715 22 12Z" stroke="#FC4D0A" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
              <h4 className="text-lg font-semibold mb-2">AI Model Routing</h4>
              <p className="text-gray-600">Advanced multi-provider architecture with GPT-4o, Claude, Gemini, and DeepSeek routing based on query complexity and cost optimization.</p>
            </div>
            
            <div className="bg-white p-6 rounded-xl shadow-elegant hover:shadow-elegant-hover transition-all duration-300">
              <div className="w-12 h-12 bg-pulse-100 rounded-full flex items-center justify-center mb-4">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M9.5 14.5L5.5 18.5M9.5 14.5L11.5 16.5L14.5 13.5M9.5 14.5L6.5 11.5M14.5 13.5L18.5 9.5M14.5 13.5L17.5 16.5M18.5 9.5L17.086 8.086M18.5 9.5L19.914 10.914" stroke="#FC4D0A" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
              <h4 className="text-lg font-semibold mb-2">Production Infrastructure</h4>
              <p className="text-gray-600">Enterprise-grade monitoring, feature flags, instant rollback capabilities, rate limiting, and comprehensive audit logging for production reliability.</p>
            </div>
            
            <div className="bg-white p-6 rounded-xl shadow-elegant hover:shadow-elegant-hover transition-all duration-300">
              <div className="w-12 h-12 bg-pulse-100 rounded-full flex items-center justify-center mb-4">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M21 8V16M21 12H17M7 8V16M7 12H3M12 3V21M12 16L16 12M12 16L8 12" stroke="#FC4D0A" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
              <h4 className="text-lg font-semibold mb-2">Enterprise Integration</h4>
              <p className="text-gray-600">API-first design with enterprise SSO, audit logging, and seamless integration into existing business systems and workflows.</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default ComplianceShowcaseSection;
