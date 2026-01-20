import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    host: '0.0.0.0',
    allowedHosts: ['localhost', '127.0.0.1', '172.18.0.1', '172.18.0.5']
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: (id) => {
          // Vendor chunks for better caching
          if (id.includes('node_modules')) {
            if (id.includes('react') || id.includes('react-dom') || id.includes('react-router')) {
              return 'react-vendor'
            }
            if (id.includes('@radix-ui')) {
              return 'radix-vendor'
            }
            if (id.includes('lucide-react') || id.includes('react-icons')) {
              return 'icons-vendor'
            }
            if (id.includes('axios') || id.includes('date-fns') || id.includes('clsx')) {
              return 'utils-vendor'
            }
            if (id.includes('recharts') || id.includes('zod') || id.includes('@tanstack')) {
              return 'data-vendor'
            }
            return 'vendor'
          }
          // Feature-based code splitting
          if (id.includes('/pages/')) {
            const pageName = id.split('/pages/')[1].split('.')[0].toLowerCase()
            return `page-${pageName}`
          }
          // Component chunks
          if (id.includes('/components/')) {
            if (id.includes('/ui/')) {
              return 'ui-components'
            }
            if (id.includes('/common/')) {
              return 'common-components'
            }
            return 'feature-components'
          }
        }
      }
    },
    // Performance optimizations
    chunkSizeWarningLimit: 600,
    minify: 'esbuild',
    sourcemap: process.env.NODE_ENV === 'development',
    cssCodeSplit: true,
    // Enable compression
    reportCompressedSize: false,
    // Target modern browsers for smaller bundles
    target: 'esnext',
    // Optimize assets
    assetsInlineLimit: 4096
  },
  // Optimize dependencies for faster development
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      'react-router-dom',
      'axios',
      'lucide-react',
      'date-fns',
      'clsx',
      'tailwind-merge',
      'zod',
      'sonner',
      // Core UI libraries
      '@radix-ui/react-dialog',
      '@radix-ui/react-dropdown-menu',
      '@radix-ui/react-select',
      '@radix-ui/react-toast',
      // Table and data libraries
      '@tanstack/react-table',
      // Utility libraries
      'class-variance-authority'
    ],
    exclude: [
      // Exclude large libraries that should be lazy loaded
      'recharts',
      '@dnd-kit/core',
      '@dnd-kit/modifiers',
      '@dnd-kit/sortable',
      '@dnd-kit/utilities'
    ]
  },
  // CSS configuration
  css: {
    postcss: './postcss.config.js',
  }
})
