
import React from "react";

const SpecsSection = () => {
  return (
    <section className="w-full py-6 sm:py-10 bg-blue-600" id="specifications" 
      style={{
        backgroundImage: 'url("data:image/svg+xml,%3Csvg width="40" height="40" viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg"%3E%3Cg fill="rgba(255,255,255,0.1)" fill-opacity="1" fill-rule="evenodd"%3E%3Cpath d="m0 40l40-40h-40v40zm40 0v-40h-40l40 40z"/%3E%3C/g%3E%3C/svg%3E")',
        backgroundSize: '40px 40px'
      }}
    >
      <div className="container px-4 sm:px-6 lg:px-8 mx-auto">
        {/* Header with badge and line */}
        <div className="flex items-center gap-4 mb-8 sm:mb-16">
          <div className="flex items-center gap-4">
            <div className="pulse-chip bg-white/20 text-white border-white/30">
              <span className="inline-flex items-center justify-center w-5 h-5 rounded-full bg-white text-blue-600 mr-2 font-semibold">3</span>
              <span>Specs</span>
            </div>
          </div>
          <div className="flex-1 h-[1px] bg-white/30"></div>
        </div>
        
        {/* Main content with text mask image - responsive text sizing */}
        <div className="max-w-5xl pl-4 sm:pl-8">
          <h2 className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl xl:text-6xl font-display leading-tight mb-8 sm:mb-12">
            <span className="block text-white font-bold">
              Built with production-grade architecture: Multi-model AI routing (GPT-4o, Claude, Gemini), RAG pipeline with vector search, enterprise security, real-time monitoring, and audit-ready citation engines. Enterprise-grade precision with production reliability.
            </span>
          </h2>
        </div>
      </div>
    </section>
  );
};

export default SpecsSection;
