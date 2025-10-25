# ClauseBot.Ai Documentation

Welcome to the ClauseBot.Ai documentation. This guide provides comprehensive information about the architecture, features, APIs, and deployment of the ClauseBot.Ai platform.

## 📚 Documentation Index

### Core Documentation
- **[Architecture](./ARCHITECTURE.md)** - System architecture, tech stack, and design patterns
- **[API Documentation](./API.md)** - API endpoints, authentication, and integration guide
- **[Features](./FEATURES.md)** - Detailed feature documentation and use cases
- **[PWA Guide](./PWA.md)** - Progressive Web App capabilities and offline support

### Development & Deployment
- **[Deployment Guide](./DEPLOYMENT.md)** - Production deployment and configuration
- **[Contributing Guide](./CONTRIBUTING.md)** - Development setup and best practices
- **[Roadmap](./ROADMAP.md)** - Current status, next steps, and future plans

## 🎯 What is ClauseBot.Ai?

ClauseBot.Ai is an AI-powered welding code compliance assistant designed to help welding professionals, inspectors, and students master AWS D1.1:2025 and other welding standards. Built by a 40-year AWS CWI veteran, it combines deep industry expertise with cutting-edge AI technology.

### Key Capabilities

**🔍 Instant Code Intelligence**
- Sub-1.2 second clause lookups
- Citation-backed answers from AWS D1.1, ASME IX, API 1104
- Real-time compliance verification

**📚 Educational Platform**
- CWI exam preparation with guided practice
- Interactive learning tracks (WeldTrack Foundation, SPLI Foundation)
- Integration with MiltmonNDT Academy

**⚡ Professional Tools**
- WPS/PQR compliance checking
- Visual inspection guidance
- Audit-ready documentation generation

**📱 Offline-First PWA**
- Works without internet connection
- Automatic caching and sync
- Mobile and desktop optimized

## 🏗️ Technology Stack

- **Frontend**: React 18, TypeScript, Vite
- **Styling**: Tailwind CSS, shadcn/ui components
- **State Management**: TanStack Query (React Query)
- **Routing**: React Router v6
- **PWA**: Vite PWA plugin with Workbox
- **API**: ClauseBot API (Render.com hosted)
- **Analytics**: Google Analytics 4

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## 📖 Key Concepts

### AWS D1.1:2025 Crosswalk System
ClauseBot.Ai features a sophisticated crosswalk system that maps clauses between AWS D1.1:2020 and D1.1:2025 editions. This system:
- Tracks clause changes, additions, and deletions
- Maintains verification status for teaching accuracy
- Provides audit trails for compliance verification
- Supports gradual content migration

### Offline Capability
The PWA implementation provides:
- Automatic caching of questions and answers
- Smart cache management (7-day retention)
- Offline fallback with cached responses
- Automatic sync when connection restored

### Multi-Page Architecture
- **/** - Main landing page with feature showcase
- **/academy** - Learning paths and certification tracks
- **/professional** - Professional features and capabilities
- **/demo** - Interactive demos and use cases
- **/pricing** - Pricing tiers and plans
- **/academy/weldtrack-foundation** - WeldTrack learning track

## 🔐 Security & Compliance

- API authentication with service-role protection
- Row-level security (RLS) for data access
- Audit logging for verification workflow
- HTTPS-only communication
- Secure secret management

## 📊 Current Status

**Version**: 1.0.0  
**Status**: Production Ready ✅  
**Last Updated**: 2025-01-18

### Completed Features
✅ Live API integration with ClauseBot API  
✅ PWA with offline support  
✅ Multi-page architecture with routing  
✅ D1.1:2025 crosswalk system  
✅ Analytics integration (GA4)  
✅ Responsive design system  
✅ Component library (shadcn/ui)  

### In Progress
🚧 Backend integration for user authentication  
🚧 Database schema for user data  
🚧 Payment integration (Stripe)  

See [ROADMAP.md](./ROADMAP.md) for detailed status and next steps.

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](./CONTRIBUTING.md) for:
- Development setup
- Code standards
- Pull request process
- Testing requirements

## 📞 Support

- **Documentation Issues**: Open an issue on GitHub
- **API Issues**: Contact ClauseBot API team
- **General Questions**: support@clausebot.ai

## 📝 License

Copyright © 2025 MiltmonNDT. All rights reserved.

---

**Built with ❤️ by welding professionals, for welding professionals.**
