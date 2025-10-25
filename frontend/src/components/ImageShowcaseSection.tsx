
import React from "react";

const ImageShowcaseSection = () => {
  return (
    <section className="w-full pt-0 pb-8 sm:pb-12 bg-white" id="showcase">
      <div className="container px-4 sm:px-6 lg:px-8 mx-auto">
        <div className="max-w-3xl mx-auto text-center mb-8 sm:mb-12 animate-on-scroll">
          <h2 className="text-3xl sm:text-4xl font-display font-bold tracking-tight text-gray-900 mb-3 sm:mb-4">
            Proven in Production
          </h2>
          <p className="text-base sm:text-lg text-gray-600">
            ClauseBot.Ai leads the way as our first specialized implementation—delivering AWS compliance for welders at $49.00/month, powered by the ClauseBot Pro engine.
          </p>
        </div>
        
        <div className="rounded-2xl sm:rounded-3xl overflow-hidden shadow-elegant mx-auto max-w-4xl animate-on-scroll">
          <div className="w-full">
            <img 
              src="/clausebot-badge.png" 
              alt="ClauseBot.Ai interface showing clause-cited compliance with decision-ready status" 
              className="w-full h-auto object-cover"
            />
          </div>
          <div className="bg-white p-4 sm:p-8">
            <div className="flex items-center justify-between mb-3 sm:mb-4">
              <h3 className="text-xl sm:text-2xl font-display font-semibold">ClauseBot.Ai</h3>
              <div className="flex items-center gap-2">
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  LIVE
                </span>
                <a 
                  href="https://www.clausebot.ai" 
                  target="_blank" 
                  rel="noopener noreferrer" 
                  className="text-pulse-500 hover:text-pulse-600 text-sm font-medium transition-colors"
                >
                  Visit Site →
                </a>
              </div>
            </div>
            <p className="text-gray-700 text-sm sm:text-base">
              Our first specialized craft module in production. ClauseBot.Ai delivers AWS welding compliance 
              at $49.00/month, proving the platform's capability to scale from enterprise infrastructure down to 
              focused, affordable solutions for specific trades.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
};

export default ImageShowcaseSection;
