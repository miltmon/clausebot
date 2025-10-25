import React from "react";

const PlatformOverviewSection = () => {
  const keyAttributes = [
    {
      title: "Continuous Standards Alignment",
      description: "All modules and programs are meticulously updated to reflect the most current, widely recognized industry standards and best practices.",
      icon: "📋"
    },
    {
      title: "AI-Driven Clause Interpretation",
      description: "Integrated AI tools empower users to translate complex regulatory language—across legal, technical, and compliance domains—into clear, actionable insights.",
      icon: "🤖"
    },
    {
      title: "Personalized Learning Tracks",
      description: "The platform guides users step by step through structured career and certification pathways, supporting everyone from beginners to advanced professionals.",
      icon: "🎯"
    },
    {
      title: "Credibility & Expertise",
      description: "Programs are built and validated by certified professionals, ensuring the curriculum is trusted by individuals, companies, and authorities seeking rigorous, audit-ready training.",
      icon: "⭐"
    },
    {
      title: "Logbooks & Practical Resources",
      description: "Beyond theoretical knowledge, learners gain practical logbooks, real-world scenarios, and problem-solving exercises connected to industry protocols and compliance requirements.",
      icon: "📚"
    },
    {
      title: "Real-Time Support",
      description: "Direct access to certified experts and comprehensive support fosters confidence and successful advancement through qualification milestones.",
      icon: "🎧"
    },
    {
      title: "Career and Credential Advancement",
      description: "Its ecosystem is designed not just to educate but to qualify, certify, and enable professional growth in highly regulated, standards-driven environments.",
      icon: "🚀"
    }
  ];

  return (
    <section className="w-full py-20 bg-white" id="platform-overview">
      <div className="container px-6 lg:px-8 mx-auto">
        <div className="text-center mb-16 animate-on-scroll">
          <div className="pulse-chip mb-4">
            <span>Platform Overview</span>
          </div>
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-display font-bold mb-6">
            Advanced Digital <span className="text-[#FC4D0A]">Compliance & Professional Development</span>
          </h2>
          <p className="text-lg text-gray-700 max-w-4xl mx-auto leading-relaxed">
            The platform stands out as an advanced digital compliance and professional development environment, 
            built for multi-domain training, credentialing, and adherence to standards—without being limited to any specific technical field.
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-16 animate-on-scroll">
          {keyAttributes.map((attribute, index) => (
            <div 
              key={index}
              className="p-6 rounded-xl border border-gray-200 hover:shadow-elegant-hover transition-all duration-300 bg-white"
            >
              <div className="w-12 h-12 rounded-full flex items-center justify-center mb-4 text-2xl bg-blue-50">
                {attribute.icon}
              </div>
              <h3 className="text-lg font-display font-semibold mb-3 text-gray-900">{attribute.title}</h3>
              <p className="text-gray-600 text-sm leading-relaxed">{attribute.description}</p>
            </div>
          ))}
        </div>
        
        <div className="text-center animate-on-scroll">
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-8 rounded-2xl max-w-5xl mx-auto border border-blue-100">
            <h3 className="text-2xl font-display font-semibold mb-4 text-gray-900">
              Next-Gen Standards-Based Professional Development
            </h3>
            <p className="text-gray-700 leading-relaxed text-lg">
              This platform is a <strong>next-generation, standards-based professional development and compliance solution</strong>—leveraging 
              the latest technology to turn complex codes, laws, and best practices into accessible pathways for upskilling, 
              certification, and career advancement across multiple domains.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
};

export default PlatformOverviewSection;