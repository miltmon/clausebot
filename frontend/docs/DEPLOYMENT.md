# ClauseBot.Ai Deployment Guide

Complete guide for deploying ClauseBot.Ai to production environments.

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ installed
- npm or yarn package manager
- Git
- Deployment platform account (Vercel/Netlify recommended)

### Build & Deploy
```bash
# Install dependencies
npm install

# Build for production
npm run build

# Preview production build locally
npm run preview

# Deploy (platform-specific)
# See platform sections below
```

## 🏗️ Build Process

### Production Build
```bash
npm run build
```

This generates:
- `dist/` - Optimized production files
- `dist/assets/` - Hashed static assets
- `dist/index.html` - Entry point
- Service worker files
- PWA manifest

### Build Output
```
dist/
├── index.html
├── assets/
│   ├── index-[hash].js        # Main bundle
│   ├── index-[hash].css       # Styles
│   ├── vendor-[hash].js       # Dependencies
│   └── [images]               # Optimized images
├── pwa-icon-512.png
├── manifest.webmanifest
├── sw.js                       # Service worker
└── workbox-*.js                # Workbox runtime
```

## ☁️ Deployment Platforms

### Vercel (Recommended)

**Why Vercel?**
- Zero-config deployment
- Automatic HTTPS
- CDN edge network
- Preview deployments
- Analytics included

**Deployment Steps:**

1. **Install Vercel CLI**
   ```bash
   npm i -g vercel
   ```

2. **Login**
   ```bash
   vercel login
   ```

3. **Deploy**
   ```bash
   vercel
   ```

4. **Configure (vercel.json)**
   ```json
   {
     "version": 2,
     "builds": [
       {
         "src": "package.json",
         "use": "@vercel/static-build",
         "config": {
           "distDir": "dist"
         }
       }
     ],
     "routes": [
       {
         "src": "/(.*)",
         "dest": "/index.html"
       }
     ],
     "headers": [
       {
         "source": "/sw.js",
         "headers": [
           {
             "key": "Cache-Control",
             "value": "public, max-age=0, must-revalidate"
           }
         ]
       }
     ]
   }
   ```

5. **Environment Variables**
   ```bash
   vercel env add VITE_API_BASE_URL
   vercel env add VITE_GA_MEASUREMENT_ID
   ```

**GitHub Integration:**
- Connect repo to Vercel
- Automatic deployments on push
- Preview URLs for PRs

---

### Netlify

**Why Netlify?**
- Easy PWA support
- Form handling
- Serverless functions
- Split testing
- Deploy previews

**Deployment Steps:**

1. **Install Netlify CLI**
   ```bash
   npm i -g netlify-cli
   ```

2. **Login**
   ```bash
   netlify login
   ```

3. **Deploy**
   ```bash
   netlify deploy --prod
   ```

4. **Configure (netlify.toml)**
   ```toml
   [build]
     command = "npm run build"
     publish = "dist"
   
   [[redirects]]
     from = "/*"
     to = "/index.html"
     status = 200
   
   [[headers]]
     for = "/sw.js"
     [headers.values]
       Cache-Control = "public, max-age=0, must-revalidate"
   
   [[headers]]
     for = "/assets/*"
     [headers.values]
       Cache-Control = "public, max-age=31536000, immutable"
   ```

5. **Environment Variables**
   ```bash
   netlify env:set VITE_API_BASE_URL "https://clausebot-api.onrender.com"
   netlify env:set VITE_GA_MEASUREMENT_ID "G-XXXXXXXXXX"
   ```

---

### Render.com

**Why Render?**
- Full-stack platform
- Backend + frontend together
- Automatic SSL
- Database hosting
- CDN included

**Deployment Steps:**

1. **Create Static Site**
   - Go to Render dashboard
   - Click "New Static Site"
   - Connect GitHub repo

2. **Configure Build**
   - Build Command: `npm run build`
   - Publish Directory: `dist`

3. **Environment Variables**
   - Add in Render dashboard
   - `VITE_API_BASE_URL`
   - `VITE_GA_MEASUREMENT_ID`

4. **Custom Domain**
   - Add domain in Render dashboard
   - Update DNS records

---

### AWS S3 + CloudFront

**Why AWS?**
- Enterprise-grade infrastructure
- Global CDN
- Advanced security
- Cost-effective at scale

**Deployment Steps:**

1. **Create S3 Bucket**
   ```bash
   aws s3 mb s3://clausebot-ai-prod
   ```

2. **Configure Bucket for Static Hosting**
   ```bash
   aws s3 website s3://clausebot-ai-prod \
     --index-document index.html \
     --error-document index.html
   ```

3. **Upload Build**
   ```bash
   npm run build
   aws s3 sync dist/ s3://clausebot-ai-prod \
     --delete \
     --cache-control "public, max-age=31536000"
   ```

4. **Create CloudFront Distribution**
   - Origin: S3 bucket
   - Cache behavior: All files
   - SSL certificate: ACM
   - Custom domain: clausebot.ai

5. **Invalidate Cache on Deploy**
   ```bash
   aws cloudfront create-invalidation \
     --distribution-id E1234567890ABC \
     --paths "/*"
   ```

---

## 🔐 Environment Variables

### Required Variables

```bash
# API Base URL
VITE_API_BASE_URL=https://clausebot-api.onrender.com

# Google Analytics
VITE_GA_MEASUREMENT_ID=G-XXXXXXXXXX
```

### Optional Variables

```bash
# Supabase (when backend added)
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key

# Stripe (when payments added)
VITE_STRIPE_PUBLIC_KEY=pk_live_...

# Sentry (error tracking)
VITE_SENTRY_DSN=https://...
```

### Setting Variables

**Vercel:**
```bash
vercel env add VITE_API_BASE_URL
```

**Netlify:**
```bash
netlify env:set VITE_API_BASE_URL "https://clausebot-api.onrender.com"
```

**Local (.env):**
```bash
# .env.local (not committed to git)
VITE_API_BASE_URL=https://clausebot-api.onrender.com
VITE_GA_MEASUREMENT_ID=G-XXXXXXXXXX
```

---

## 🌐 Custom Domain Setup

### DNS Configuration

**For Vercel:**
```
Type: A
Name: @
Value: 76.76.21.21

Type: CNAME
Name: www
Value: cname.vercel-dns.com
```

**For Netlify:**
```
Type: A
Name: @
Value: 75.2.60.5

Type: CNAME
Name: www
Value: your-site.netlify.app
```

**For CloudFront:**
```
Type: A (Alias)
Name: @
Value: d111111abcdef8.cloudfront.net

Type: CNAME
Name: www
Value: d111111abcdef8.cloudfront.net
```

### SSL Certificate

- **Vercel/Netlify**: Automatic (Let's Encrypt)
- **AWS**: Use AWS Certificate Manager (ACM)
- **Custom**: Upload certificate in platform dashboard

---

## 📊 Performance Optimization

### Build Optimizations

**Vite Configuration:**
```typescript
// vite.config.ts
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor': ['react', 'react-dom'],
          'ui': ['@radix-ui/react-dialog', '@radix-ui/react-dropdown-menu'],
          'router': ['react-router-dom']
        }
      }
    },
    chunkSizeWarningLimit: 1000
  }
});
```

### Asset Optimization

**Images:**
- Use WebP format
- Lazy load images
- Responsive images with `srcset`
- Compress with `imagemin`

**Fonts:**
- Preload critical fonts
- Use font-display: swap
- Subset fonts for used characters

### Caching Strategy

**Cache Headers:**
```
# HTML (no cache)
Cache-Control: public, max-age=0, must-revalidate

# JS/CSS (1 year)
Cache-Control: public, max-age=31536000, immutable

# Images (1 week)
Cache-Control: public, max-age=604800

# Service Worker (no cache)
Cache-Control: public, max-age=0, must-revalidate
```

---

## 🔍 Monitoring & Analytics

### Google Analytics 4

**Setup:**
1. Create GA4 property
2. Get Measurement ID
3. Add to environment variables
4. Analytics auto-tracks on page load

**Custom Events:**
```typescript
gtag('event', 'answer_verify', {
  verdict: 'VERIFIED',
  confidence: 0.95
});
```

### Error Tracking (Sentry)

**Installation:**
```bash
npm install @sentry/react @sentry/tracing
```

**Configuration:**
```typescript
import * as Sentry from '@sentry/react';

Sentry.init({
  dsn: import.meta.env.VITE_SENTRY_DSN,
  environment: import.meta.env.MODE,
  tracesSampleRate: 1.0
});
```

### Performance Monitoring

**Lighthouse CI:**
```bash
npm install -D @lhci/cli

# lighthouse.config.js
module.exports = {
  ci: {
    collect: {
      startServerCommand: 'npm run preview',
      url: ['http://localhost:4173']
    },
    assert: {
      preset: 'lighthouse:recommended',
      assertions: {
        'categories:performance': ['error', {minScore: 0.9}],
        'categories:accessibility': ['error', {minScore: 0.9}]
      }
    }
  }
};
```

---

## 🧪 Testing Before Deployment

### Pre-deployment Checklist

- [ ] All tests passing
- [ ] Build completes without errors
- [ ] Service worker registers
- [ ] Offline mode works
- [ ] All routes accessible
- [ ] API calls successful
- [ ] Analytics tracking
- [ ] Performance metrics meet targets
- [ ] Accessibility audit passes
- [ ] Security headers configured
- [ ] Environment variables set

### Testing Commands

```bash
# Build
npm run build

# Preview locally
npm run preview

# Test production build
open http://localhost:4173

# Lighthouse audit
npx lighthouse http://localhost:4173 --view

# PWA audit
npx lighthouse http://localhost:4173 --view --preset=pwa
```

---

## 🔄 CI/CD Pipeline

### GitHub Actions

**.github/workflows/deploy.yml:**
```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          
      - name: Install dependencies
        run: npm ci
        
      - name: Build
        run: npm run build
        env:
          VITE_API_BASE_URL: ${{ secrets.API_BASE_URL }}
          VITE_GA_MEASUREMENT_ID: ${{ secrets.GA_ID }}
          
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.ORG_ID }}
          vercel-project-id: ${{ secrets.PROJECT_ID }}
          vercel-args: '--prod'
```

---

## 🐛 Troubleshooting

### Common Issues

**Issue: Service Worker Not Updating**
```bash
# Solution: Hard refresh (Ctrl+Shift+R)
# Or unregister manually in DevTools
navigator.serviceWorker.getRegistrations().then(regs => 
  regs.forEach(reg => reg.unregister())
);
```

**Issue: Routing 404s**
```bash
# Solution: Configure SPA redirects
# Vercel: Add rewrites in vercel.json
# Netlify: Add _redirects file
```

**Issue: Environment Variables Not Working**
```bash
# Solution: Variables must start with VITE_
VITE_API_URL=https://... # ✅ Works
API_URL=https://...      # ❌ Doesn't work
```

---

## 📝 Post-Deployment

### Verification Checklist

- [ ] Site accessible at domain
- [ ] HTTPS working
- [ ] PWA installable
- [ ] Offline mode works
- [ ] Analytics tracking
- [ ] All pages load
- [ ] API calls successful
- [ ] Performance acceptable

### Monitoring Setup

- [ ] Uptime monitoring (UptimeRobot)
- [ ] Error tracking (Sentry)
- [ ] Analytics dashboard (GA4)
- [ ] Performance monitoring (Lighthouse CI)

---

**Deployment Status**: Production Ready ✅  
**Last Updated**: 2025-01-18  
**Maintained By**: ClauseBot.Ai Team
