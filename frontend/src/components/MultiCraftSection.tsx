import React from "react";

const MultiCraftSection = () => {
  const tracks = [
    {
      name: "WeldTrack™",
      description: "AWS D1.1, ASME Section IX, API 1104 compliance with clause-cited precision for welding professionals",
      icon: "🔥",
      color: "bg-orange-50 border-orange-200",
      iconBg: "bg-orange-100"
    },
    {
      name: "VoltTrack™",
      description: "NEC, NFPA, IEEE electrical code compliance with standard-anchored guidance and safety protocols",
      icon: "⚡",
      color: "bg-blue-50 border-blue-200",
      iconBg: "bg-blue-100"
    },
    {
      name: "MediTrack™",
      description: "FDA, ISO 13485, IEC 62304 medical device standards with regulatory citation engine and audit trails",
      icon: "🏥",
      color: "bg-green-50 border-green-200",
      iconBg: "bg-green-100"
    },
    {
      name: "BuildTrack™",
      description: "OSHA, AISC, ACI construction and building codes with integrated safety and structural compliance",
      icon: "🏗️",
      color: "bg-purple-50 border-purple-200",
      iconBg: "bg-purple-100"
    }
  ];

  return (
    <section className="w-full py-20 bg-white" id="multi-craft">
      <div className="container px-6 lg:px-8 mx-auto">
        <div className="text-center mb-16 animate-on-scroll">
          <div className="pulse-chip mb-4">
            <span className="inline-flex items-center justify-center w-5 h-5 rounded-full bg-pulse-500 text-white mr-2">04</span>
            <span>Product Modules</span>
          </div>
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-display font-bold mb-4">
            One Platform, <span className="text-[#FC4D0A]">Multiple Industries</span>
          </h2>
          <p className="text-lg text-gray-600 max-w-3xl mx-auto">
            ClauseBot.Ai's modular architecture powers specialized compliance engines across diverse industries. 
            Same enterprise-grade infrastructure, same audit-ready precision, tailored for each domain.
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 animate-on-scroll">
          {tracks.map((track, index) => (
            <div 
              key={index}
              className={`p-6 rounded-xl border-2 hover:shadow-elegant-hover transition-all duration-300 ${track.color}`}
            >
              <div className={`w-12 h-12 rounded-full flex items-center justify-center mb-4 text-2xl ${track.iconBg}`}>
                {track.icon}
              </div>
              <h3 className="text-xl font-display font-semibold mb-3">{track.name}</h3>
              <p className="text-gray-600 text-sm leading-relaxed">{track.description}</p>
            </div>
          ))}
        </div>
        
        <div className="mt-16 text-center animate-on-scroll">
          <div className="bg-gray-50 p-8 rounded-2xl max-w-4xl mx-auto">
            <h3 className="text-2xl font-display font-semibold mb-4">The ClauseBot.Ai Platform Vision</h3>
            <p className="text-gray-700 leading-relaxed">
              Beyond individual modules, ClauseBot.Ai represents a <strong>unified compliance platform</strong>—with 
              enterprise APIs, multi-tenant licensing, and industry committee recognition. 
              From prototype to production, one platform scales across all standard-driven industries with audit-ready precision.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
};

export default MultiCraftSection;