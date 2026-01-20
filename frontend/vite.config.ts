import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// Plugin to handle React 19 compatibility for use-sync-external-store
function react19CompatPlugin() {
  return {
    name: 'react19-compat',
    enforce: 'pre' as const,
    resolveId(id: string) {
      // Handle direct imports of the shim paths
      if (id === 'use-sync-external-store/shim/with-selector' || id === 'use-sync-external-store/with-selector.js') {
        return path.resolve(__dirname, './src/shims/use-sync-external-store-with-selector.js')
      }
      if (id === 'use-sync-external-store/shim') {
        return path.resolve(__dirname, './src/shims/use-sync-external-store.js')
      }
      if (id === 'use-sync-external-store') {
        return path.resolve(__dirname, './src/shims/use-sync-external-store.js')
      }
      return null
    },
    load(id: string) {
      if (id === path.resolve(__dirname, './src/shims/use-sync-external-store-with-selector.js')) {
        return `export { useSyncExternalStoreWithSelector } from 'react'`
      }
      if (id === path.resolve(__dirname, './src/shims/use-sync-external-store.js')) {
        return `export { useSyncExternalStore } from 'react'`
      }
      return null
    }
  }
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), react19CompatPlugin()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
      "es-toolkit/compat": "lodash-es", // Redirect es-toolkit to lodash-es for better compatibility
    },
  },
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
      '@radix-ui/react-dialog',
      '@radix-ui/react-dropdown-menu',
      '@radix-ui/react-select',
      '@radix-ui/react-toast',
      '@tanstack/react-table',
      'class-variance-authority',
      'eventemitter3', // Include eventemitter3 for proper module resolution
      'react-is', // Include react-is for proper module resolution
      'recharts', // Temporarily include recharts to test module resolution
    ],
    exclude: [
      'zustand', // Exclude zustand to avoid use-sync-external-store conflicts
      '@dnd-kit/core',
      '@dnd-kit/modifiers',
      '@dnd-kit/sortable',
      '@dnd-kit/utilities'
    ]
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
  // CSS configuration
  css: {
    postcss: './postcss.config.js',
  }
})
