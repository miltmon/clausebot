import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";
import { componentTagger } from "lovable-tagger";
import { VitePWA } from 'vite-plugin-pwa';

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  server: {
    host: "::",
    port: 8080,
  },
  plugins: [
    react(),
    mode === 'development' &&
    componentTagger(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['clausebot-favicon.svg', 'clausebot-icon.svg', 'clausebot-logo.svg'],
      manifest: {
        name: 'ClauseBot.Ai - Compliance OS',
        short_name: 'ClauseBot.Ai',
        description: 'Clause-cited, decision-ready compliance OS for standards-driven work',
        theme_color: '#0B1220',
        background_color: '#0B1220',
        display: 'standalone',
        orientation: 'portrait',
        scope: '/',
        start_url: '/',
        categories: ['productivity', 'business', 'utilities'],
        screenshots: [
          {
            src: '/og-image-update.png',
            sizes: '1200x630',
            type: 'image/png',
            form_factor: 'wide',
            label: 'ClauseBot.Ai Dashboard'
          }
        ],
        icons: [
          {
            src: '/pwa-icon-192.png',
            sizes: '192x192',
            type: 'image/png',
            purpose: 'any'
          },
          {
            src: '/pwa-icon-512.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'any'
          },
          {
            src: '/pwa-icon-192.png',
            sizes: '192x192',
            type: 'image/png',
            purpose: 'maskable'
          },
          {
            src: '/clausebot-icon.svg',
            sizes: 'any',
            type: 'image/svg+xml',
            purpose: 'any'
          }
        ]
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,svg,webp,jpg,jpeg}'], // Explicitly exclude PNG to avoid large images
        maximumFileSizeToCacheInBytes: 5 * 1024 * 1024, // 5MB limit
        globIgnores: [
          'clausebot-image.png',
          'clausebot-image-2.png', 
          'hero-image.jpg',
          '**/clausebot-image*.png',
          '**/hero-image*.jpg'
        ],
        // Don't cache bust URLs matching these patterns
        dontCacheBustURLsMatching: /\.(?:png|jpg|jpeg|svg)$/,
        runtimeCaching: [
          {
            urlPattern: /^https:\/\/clausebot-api\.onrender\.com\/.*/i,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'clausebot-api-cache',
              expiration: {
                maxEntries: 100,
                maxAgeSeconds: 60 * 60 * 24 // 24 hours
              }
            }
          },
          {
            urlPattern: /^https:\/\/fonts\.googleapis\.com\/.*/i,
            handler: 'CacheFirst',
            options: {
              cacheName: 'google-fonts-cache',
              expiration: {
                maxEntries: 10,
                maxAgeSeconds: 60 * 60 * 24 * 365 // 1 year
              }
            }
          },
          {
            urlPattern: /^https:\/\/fonts\.gstatic\.com\/.*/i,
            handler: 'CacheFirst',
            options: {
              cacheName: 'gstatic-fonts-cache',
              expiration: {
                maxEntries: 10,
                maxAgeSeconds: 60 * 60 * 24 * 365 // 1 year
              }
            }
          },
          {
            // Only cache small images at runtime
            urlPattern: ({ request }) => {
              return request.destination === 'image' && 
                     !request.url.includes('clausebot-image') &&
                     !request.url.includes('hero-image');
            },
            handler: 'CacheFirst',
            options: {
              cacheName: 'images-cache',
              expiration: {
                maxEntries: 50,
                maxAgeSeconds: 60 * 60 * 24 * 30 // 30 days
              }
            }
          }
        ]
      },
      devOptions: {
        enabled: true
      }
    })
  ].filter(Boolean),
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
}));
