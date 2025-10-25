
import React from "react";
import { SystemHealth } from './SystemHealth';

const Footer = () => {
  return (
    <footer className="border-t">
      <div className="max-w-6xl mx-auto px-6 py-8 text-sm text-gray-600">
        <div className="flex flex-col md:flex-row justify-between gap-4">
          <p>
            © {new Date().getFullYear()} ClauseBot by MILTMON NDT. All rights reserved.
          </p>
          <nav className="flex gap-4">
            <a href="https://www.miltmonndt.com/about" className="hover:text-gray-800 transition-colors">
              About
            </a>
            <a href="https://www.miltmonndt.com/pricing-plans/offerings" className="hover:text-gray-800 transition-colors">
              Pricing
            </a>
            <a href="https://www.miltmonndt.com/ops" className="hover:text-gray-800 transition-colors">
              Ops Logs
            </a>
          </nav>
        </div>
        
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-3 mt-4 pt-4 border-t border-gray-200">
          <p className="text-gray-500">
            Important: ClauseBot supports compliance decisions; it does not replace the engineer of record.
          </p>
          <SystemHealth />
        </div>
      </div>
    </footer>
  );
};
export default Footer;
