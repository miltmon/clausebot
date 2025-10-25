import React from "react";

const ComplianceDocumentation = () => {
  const sections = [
    {
      id: "data-awareness",
      title: "Data Awareness & Real-Time Accuracy",
      icon: "🧠",
      content: [
        {
          subtitle: "What ClauseBot Knows:",
          items: [
            "Live Database Schema - Real-time awareness of all Airtable bases, tables, and fields",
            "Sync Health Status - Knows which data is fresh, stale, or has drift issues", 
            "Field Relationships - Understands lookup fields, linked records, and data lineage",
            "Interface Mapping - Knows which interfaces use which tables and for what purpose"
          ]
        },
        {
          subtitle: "Critical Limitations:",
          items: [
            "Read-Only Access - ClauseBot cannot modify, delete, or create data",
            "Registry-First Approach - Always checks Supabase registry before making claims",
            "Staleness Awareness - Will warn if data is stale or has sync issues"
          ],
          warning: true
        }
      ]
    },
    {
      id: "security",
      title: "Security & Privacy Protection",
      icon: "🛡️",
      content: [
        {
          subtitle: "PII Protection:",
          items: [
            "Safe Views Only - ClauseBot only sees sanitized data (no emails, SSNs, etc.)",
            "Column Exposure Control - Sensitive columns are hidden from ClauseBot's view",
            "Audit Trail - All data access is logged and tracked",
            "Role-Based Access - Uses dedicated read-only role with minimal permissions"
          ]
        },
        {
          subtitle: "Authentication:",
          items: [
            "JWT Token Rotation - Keys rotate every 60 days for security",
            "API Key Management - Secure handling of Airtable PAT and Supabase keys", 
            "No Service Role Access - ClauseBot never has admin-level database access"
          ]
        }
      ]
    },
    {
      id: "freshness",
      title: "Data Freshness & Reliability", 
      icon: "🎯",
      content: [
        {
          subtitle: "Sync Health Monitoring:",
          items: [
            "Real-Time Status - Knows if data is FRESH, STALE, or has DRIFT",
            "24-Hour SLA - Data older than 24 hours is flagged as STALE",
            "Drift Detection - Automatically detects when Airtable and Supabase are out of sync",
            "MTTR < 24 Hours - Mean Time To Resolution for drift issues"
          ]
        },
        {
          subtitle: "Freshness Verdicts:",
          items: [
            "GREEN - All data fresh and synced",
            "STALE - Data older than 24 hours", 
            "DRIFT - Sync issues detected between systems",
            "CHECK - Manual verification needed"
          ]
        }
      ]
    },
    {
      id: "procedures",
      title: "Operational Procedures",
      icon: "📋", 
      content: [
        {
          subtitle: "Daily Ritual (9:00 AM PT):",
          items: [
            "30-Second Health Check - Quick validation of all systems",
            "Drift Scan - Check for any sync issues",
            "Proof Screenshot - Visual confirmation of system health",
            "Status Logging - Record GREEN/DRIFT/STALE verdicts"
          ]
        },
        {
          subtitle: "Weekly Export (Monday 9:00 AM PT):",
          items: [
            "Leadership Report - 10-minute comprehensive health summary",
            "Performance Metrics - Query success rates, response times", 
            "Drift Analysis - Historical sync health trends",
            "Action Items - Any issues requiring attention"
          ]
        }
      ]
    }
  ];


  return (
    <section className="w-full py-20 bg-gray-50" id="compliance-docs">
      <div className="container px-6 lg:px-8 mx-auto">
        <div className="text-center mb-16 animate-on-scroll">
          <div className="pulse-chip mb-4">
            <span className="inline-flex items-center justify-center w-5 h-5 rounded-full bg-pulse-500 text-white mr-2">🔒</span>
            <span>Compliance System</span>
          </div>
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-display font-bold mb-4">
            Critical User Details - <span className="text-[#FC4D0A]">Security & Compliance</span>
          </h2>
          <p className="text-lg text-gray-600 max-w-3xl mx-auto">
            Essential compliance details users must understand about ClauseBot's system - 
            built for security, accuracy, and regulatory compliance.
          </p>
        </div>

        {/* Main Compliance Sections */}
        <div className="space-y-12 mb-16">
          {sections.map((section, index) => (
            <div key={section.id} className="bg-white rounded-2xl shadow-elegant p-8 animate-on-scroll">
              <div className="flex items-center mb-6">
                <span className="text-3xl mr-4">{section.icon}</span>
                <h3 className="text-2xl font-display font-bold text-gray-900">{section.title}</h3>
              </div>
              
              <div className="grid gap-6 md:grid-cols-2">
                {section.content.map((contentBlock, contentIndex) => (
                  <div 
                    key={contentIndex}
                    className={`p-6 rounded-xl border-2 ${
                      contentBlock.warning 
                        ? 'bg-orange-50 border-orange-200' 
                        : 'bg-gray-50 border-gray-200'
                    }`}
                  >
                    <h4 className="font-semibold text-lg mb-4 text-gray-900">
                      {contentBlock.warning && "⚠️ "}
                      {contentBlock.subtitle}
                    </h4>
                    <ul className="space-y-3">
                      {contentBlock.items.map((item, itemIndex) => (
                        <li key={itemIndex} className="flex items-start gap-3">
                          <div className="w-2 h-2 rounded-full bg-pulse-500 mt-2 flex-shrink-0"></div>
                          <span className="text-gray-700 text-sm leading-relaxed">{item}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* Critical Warnings */}
        <div className="bg-red-50 border-2 border-red-200 rounded-2xl p-8 mb-12 animate-on-scroll">
          <h3 className="text-2xl font-display font-bold text-red-900 mb-6 flex items-center">
            🚨 Critical User Warnings
          </h3>
          <div className="grid gap-6 md:grid-cols-2">
            <div>
              <h4 className="font-semibold text-lg mb-4 text-red-800">When ClauseBot Cannot Help:</h4>
              <ul className="space-y-2">
                <li className="flex items-start gap-3">
                  <span className="text-red-500 font-bold">❌</span>
                  <span className="text-red-700 text-sm">Stale Data - Will warn if information is older than 24 hours</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-red-500 font-bold">❌</span>
                  <span className="text-red-700 text-sm">Drift Issues - Will refuse to answer if sync problems exist</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-red-500 font-bold">❌</span>
                  <span className="text-red-700 text-sm">PII Requests - Will not provide sensitive personal information</span>
                </li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold text-lg mb-4 text-green-800">When ClauseBot Is Reliable:</h4>
              <ul className="space-y-2">
                <li className="flex items-start gap-3">
                  <span className="text-green-500 font-bold">✅</span>
                  <span className="text-green-700 text-sm">Fresh Data - Information less than 24 hours old</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-green-500 font-bold">✅</span>
                  <span className="text-green-700 text-sm">Registry-Verified - Data confirmed in Supabase registry</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-green-500 font-bold">✅</span>
                  <span className="text-green-700 text-sm">Safe Fields Only - Only non-sensitive data fields</span>
                </li>
              </ul>
            </div>
          </div>
        </div>


        {/* Compliance Certification */}
        <div className="bg-gradient-to-br from-pulse-50 to-pulse-100 rounded-2xl p-8 animate-on-scroll">
          <h3 className="text-2xl font-display font-bold text-gray-900 mb-8 text-center">
            🏆 Compliance Certification - Primetime Ready
          </h3>
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
            <div className="text-center p-4">
              <div className="text-3xl font-bold text-pulse-600 mb-2">99%</div>
              <div className="text-sm text-gray-600">Query Success Rate</div>
            </div>
            <div className="text-center p-4">
              <div className="text-3xl font-bold text-pulse-600 mb-2">&lt;500ms</div>
              <div className="text-sm text-gray-600">Response Time</div>
            </div>
            <div className="text-center p-4">
              <div className="text-3xl font-bold text-pulse-600 mb-2">24hr</div>
              <div className="text-sm text-gray-600">MTTR Resolution</div>
            </div>
            <div className="text-center p-4">
              <div className="text-3xl font-bold text-pulse-600 mb-2">Zero</div>
              <div className="text-sm text-gray-600">PII Exposure</div>
            </div>
          </div>
          
          <div className="mt-8 p-6 bg-white rounded-xl border border-pulse-200">
            <p className="text-center text-lg font-medium text-gray-800 mb-4">
              🎯 <strong>Bottom Line for Users:</strong>
            </p>
            <p className="text-center text-gray-700 leading-relaxed">
              ClauseBot is a <strong>SECURE, RELIABLE, and COMPLIANT</strong> data assistant that 
              protects your data with enterprise-grade security, provides accurate information with 
              real-time freshness checks, and maintains complete audit trails for compliance. 
              <strong>Trust ClauseBot for data questions, but always verify critical information independently!</strong> 🚀🔒
            </p>
          </div>
        </div>
      </div>
    </section>
  );
};

export default ComplianceDocumentation;