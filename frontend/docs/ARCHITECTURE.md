# ClauseBot.Ai Architecture

This document describes the technical architecture, design patterns, and system components of ClauseBot.Ai.

## 🏗️ System Overview

ClauseBot.Ai is built as a modern, offline-first Progressive Web Application (PWA) using React and TypeScript. The architecture follows industry best practices for scalability, maintainability, and user experience.

```
┌─────────────────────────────────────────────────────────────┐
│                        User Browser                          │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              React Application (PWA)                   │  │
│  │  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐  │  │
│  │  │  Pages/     │  │  Components/ │  │   Hooks/    │  │  │
│  │  │  Routing    │  │  UI Library  │  │   Services  │  │  │
│  │  └─────────────┘  └──────────────┘  └─────────────┘  │  │
│  │                                                         │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │         Service Worker (Workbox)                │  │  │
│  │  │  - Cache Management                             │  │  │
│  │  │  - Offline Fallback                             │  │  │
│  │  │  - Background Sync                              │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓ HTTPS
┌─────────────────────────────────────────────────────────────┐
│                   ClauseBot API (Render.com)                 │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  /v1/answers/verify     - Answer verification         │  │
│  │  /v1/questions/search   - Question search             │  │
│  │  /v1/edition            - API version info            │  │
│  │  /ready                 - Health check                │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  Knowledge Base / Database                   │
│  - AWS D1.1:2025 Standard                                   │
│  - D1.1:2020 → 2025 Crosswalk Data                         │
│  - ASME IX, API 1104 Standards                              │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
clausebot-ai/
├── public/                      # Static assets
│   ├── *.webp, *.png, *.jpg    # Images and graphics
│   ├── *.svg                   # Logo and icons
│   ├── *.webm, *.lottie        # Animations
│   └── pwa-icon-512.png        # PWA app icon
│
├── src/
│   ├── components/             # React components
│   │   ├── ui/                 # shadcn/ui components
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── dialog.tsx
│   │   │   └── ...
│   │   ├── AskClauseBot.tsx    # Main Q&A interface
│   │   ├── ComplianceDocumentation.tsx
│   │   ├── ComplianceShowcaseSection.tsx
│   │   ├── Hero.tsx
│   │   ├── Features.tsx
│   │   └── ...
│   │
│   ├── pages/                  # Route pages
│   │   ├── Index.tsx           # Landing page
│   │   ├── Academy.tsx         # Learning platform
│   │   ├── Professional.tsx    # Pro features
│   │   ├── Demo.tsx            # Interactive demos
│   │   ├── Pricing.tsx         # Pricing plans
│   │   ├── WeldTrackFoundation.tsx
│   │   └── NotFound.tsx
│   │
│   ├── hooks/                  # Custom React hooks
│   │   ├── useClauesbotApi.ts  # API integration
│   │   ├── useOfflineCapability.ts
│   │   ├── use-mobile.tsx
│   │   └── use-toast.ts
│   │
│   ├── services/               # API services
│   │   └── clausebotApi.ts     # API client
│   │
│   ├── lib/                    # Utilities
│   │   ├── utils.ts
│   │   └── codeMeta.ts         # AWS D1.1 version config
│   │
│   ├── types/                  # TypeScript definitions
│   │   └── gtag.d.ts
│   │
│   ├── App.tsx                 # Root component
│   ├── main.tsx                # Entry point
│   └── index.css               # Global styles
│
├── docs/                       # Documentation
├── vite.config.ts              # Vite configuration
├── tailwind.config.ts          # Tailwind configuration
├── tsconfig.json               # TypeScript configuration
└── package.json                # Dependencies

```

## 🎨 Design System

### Color System
ClauseBot.Ai uses a semantic color system defined in `index.css` and `tailwind.config.ts`:

```css
:root {
  /* Primary Colors - Deep Blues */
  --primary: 221 83% 53%;           /* #1976D2 - Primary brand */
  --primary-foreground: 0 0% 100%;
  
  /* Secondary Colors */
  --secondary: 210 40% 96%;
  --secondary-foreground: 222 47% 11%;
  
  /* Accent Colors */
  --accent: 210 40% 96%;
  --accent-foreground: 222 47% 11%;
  
  /* Semantic Colors */
  --success: 142 71% 45%;
  --warning: 45 93% 47%;
  --error: 0 84% 60%;
}
```

### Typography
- **Headings**: Inter font family (system fallback)
- **Body**: -apple-system, BlinkMacSystemFont, system-ui
- **Code**: Brockmann Medium (custom welding industry font)

### Component Library
Using **shadcn/ui** - a collection of re-usable, accessible components built with Radix UI and Tailwind CSS:
- Buttons, Cards, Dialogs, Dropdowns
- Forms, Tables, Badges, Alerts
- Toast notifications (Sonner)
- All components customizable via Tailwind

## 🔌 API Integration

### ClauseBot API Service
Location: `src/services/clausebotApi.ts`

```typescript
const API_BASE_URL = 'https://clausebot-api.onrender.com';

class ClauseBotAPIService {
  // Health check
  async checkHealth(): Promise<{ status: string }>
  
  // Get API edition/version
  async getEdition(): Promise<{ version: string; edition: string }>
  
  // Search questions
  async searchQuestions(query: string): Promise<Question[]>
  
  // Verify answer with citations
  async verifyAnswer(request: VerifyAnswerRequest): Promise<Answer>
  
  // Get specific question/answer by ID
  async getQuestion(id: string): Promise<Question>
  async getAnswer(id: string): Promise<Answer>
}
```

### Request/Response Types

```typescript
interface VerifyAnswerRequest {
  question: string;
  intent: 'audit' | 'clause_lookup' | 'study_help' | 'visual' | 'fallback';
  mode: 'audit' | 'standard';
}

interface Answer {
  id: string;
  answer: string;
  confidence: number;
  citations: string[];
  verdict: 'VERIFIED' | 'INSUFFICIENT_EVIDENCE' | 'ERROR';
  timestamp: string;
}
```

## 🪝 Custom Hooks

### useClausebotApi
Manages API calls with loading states and error handling:

```typescript
const {
  isLoading,
  error,
  searchQuestions,
  verifyAnswer,
  checkHealth,
  getEdition
} = useClausebotApi();
```

### useOfflineCapability
Provides offline functionality with caching:

```typescript
const {
  isOnline,              // Network status
  hasOfflineData,        // Cache status
  cacheQuestion,         // Cache a question
  cacheAnswer,           // Cache an answer
  getCachedAnswer,       // Retrieve cached answer
  getRecentQuestions,    // Get recent queries
  syncOfflineData        // Sync when online
} = useOfflineCapability();
```

## 📱 PWA Implementation

### Service Worker Strategy
Using Workbox with the following strategies:

1. **Network First** (default)
   - Try network first, fall back to cache
   - Used for API calls and dynamic content

2. **Cache First**
   - Try cache first, update in background
   - Used for static assets, images, fonts

3. **Stale While Revalidate**
   - Return cached version immediately
   - Fetch fresh version in background
   - Used for CSS, JS bundles

### Offline Features
- **Question/Answer Caching**: Last 50 Q&A pairs stored locally
- **7-Day Cache Retention**: Automatic cleanup of old data
- **Smart Fallback**: Shows cached answers when offline
- **Sync Queue**: Queues operations for sync when online
- **Visual Indicators**: Shows offline/cached status to users

### PWA Configuration
Location: `vite.config.ts`

```typescript
VitePWA({
  registerType: 'autoUpdate',
  workbox: {
    globPatterns: ['**/*.{js,css,html,ico,png,svg,webp,jpg,webm}'],
    runtimeCaching: [
      {
        urlPattern: /^https:\/\/clausebot-api\.onrender\.com\/.*/i,
        handler: 'NetworkFirst',
        options: {
          cacheName: 'clausebot-api-cache',
          expiration: { maxEntries: 100, maxAgeSeconds: 86400 }
        }
      }
    ]
  }
})
```

## 🔄 State Management

### TanStack Query (React Query)
Used for server state management:

```typescript
const queryClient = new QueryClient();

// Automatic caching, background updates, stale data handling
// Request deduplication, optimistic updates
```

### Local State
- **Component State**: useState for local UI state
- **Form State**: react-hook-form for complex forms
- **Global UI State**: Context API for theme, toast notifications

## 🛣️ Routing

Using React Router v6:

```typescript
<Routes>
  <Route path="/" element={<Index />} />
  <Route path="/academy" element={<Academy />} />
  <Route path="/academy/onboarding" element={<AcademyOnboarding />} />
  <Route path="/academy/weldtrack-foundation" element={<WeldTrackFoundation />} />
  <Route path="/professional" element={<Professional />} />
  <Route path="/demo" element={<Demo />} />
  <Route path="/pricing" element={<Pricing />} />
  <Route path="*" element={<NotFound />} />
</Routes>
```

## 📊 Analytics Integration

Google Analytics 4 (GA4) tracking:

```typescript
// Track page views
gtag('config', 'G-MEASUREMENT-ID', {
  page_path: window.location.pathname
});

// Track custom events
gtag('event', 'answer_verify', {
  verdict: 'VERIFIED',
  has_citations: true,
  is_cached: false
});
```

## 🔐 Security Considerations

### API Security
- HTTPS-only communication
- CORS headers properly configured
- API rate limiting on backend
- No sensitive data in client-side code

### Data Privacy
- No user authentication implemented yet (planned)
- Local storage used only for cache
- No PII stored in localStorage
- Analytics data anonymized

### Content Security
- CSP headers in production
- XSS protection via React's built-in escaping
- No eval() or unsafe JavaScript execution

## 🚀 Build & Deployment

### Production Build
```bash
npm run build
```

Generates:
- Optimized JS bundles with code splitting
- Minified CSS with Tailwind purging
- Service worker with cache manifest
- Static assets with content hashing

### Deployment Platforms
- **Vercel** (recommended) - Automatic deployments
- **Netlify** - Easy PWA support
- **Render.com** - Full-stack platform
- **Static hosting** - Any CDN/static host

### Environment Variables
```bash
VITE_API_BASE_URL=https://clausebot-api.onrender.com
VITE_GA_MEASUREMENT_ID=G-XXXXXXXXXX
```

## 📈 Performance Optimizations

1. **Code Splitting**: Route-based lazy loading
2. **Image Optimization**: WebP format, lazy loading
3. **Bundle Size**: Tree shaking, minification
4. **Caching**: Aggressive caching with service worker
5. **CDN**: Static assets served from CDN
6. **Compression**: Gzip/Brotli for text assets

### Performance Metrics (Target)
- **FCP** (First Contentful Paint): < 1.5s
- **LCP** (Largest Contentful Paint): < 2.5s
- **TTI** (Time to Interactive): < 3.5s
- **CLS** (Cumulative Layout Shift): < 0.1

## 🧪 Testing Strategy

### Current Testing
- Manual testing across browsers
- PWA lighthouse audits
- API integration testing

### Planned Testing
- Unit tests: Vitest
- Component tests: React Testing Library
- E2E tests: Playwright/Cypress
- Performance tests: Lighthouse CI

## 📦 Dependencies

### Core Dependencies
- `react` ^18.3.1
- `react-dom` ^18.3.1
- `react-router-dom` ^6.26.2
- `@tanstack/react-query` ^5.56.2

### UI Libraries
- `@radix-ui/*` - Accessible components
- `lucide-react` ^0.462.0 - Icons
- `tailwindcss` - Styling
- `class-variance-authority` - Component variants

### PWA & Performance
- `vite-plugin-pwa` ^1.0.3
- `workbox-window` ^7.3.0

### Forms & Validation
- `react-hook-form` ^7.53.0
- `zod` ^3.23.8
- `@hookform/resolvers` ^3.9.0

### Utilities
- `date-fns` ^3.6.0
- `sonner` ^1.5.0 (toast notifications)
- `lottie-react` ^2.4.0 (animations)

## 🔄 Future Architecture Considerations

### Backend Integration (Planned)
- Supabase for database and auth
- Edge functions for server-side logic
- Real-time subscriptions for live updates

### Advanced Features (Planned)
- User authentication and profiles
- Personal certification tracking
- Team/organization features
- Advanced analytics dashboard
- Payment processing (Stripe)

### Scalability Considerations
- CDN for global distribution
- Database read replicas
- Caching layers (Redis)
- Load balancing for API
- WebSocket for real-time features

---

**Last Updated**: 2025-01-18  
**Version**: 1.0.0
