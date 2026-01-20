import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    allowedHosts: ['localhost', '127.0.0.1', '172.18.0.1', '172.18.0.5']
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          // Vendor chunks
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'ui-vendor': ['@radix-ui/react-dialog', '@radix-ui/react-dropdown-menu', '@radix-ui/react-select'],
          'form-vendor': ['react-hook-form', 'zod'],
          'utils-vendor': ['axios', 'date-fns', 'clsx', 'tailwind-merge'],
          'icons-vendor': ['lucide-react']
        }
      }
    },
    // Performance optimizations
    chunkSizeWarningLimit: 1000,
    minify: 'esbuild',
    sourcemap: process.env.NODE_ENV === 'development',
    // Enable CSS code splitting
    cssCodeSplit: true
  },
  // Optimize dependencies
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      'axios',
      '@radix-ui/react-dialog',
      'lucide-react',
      'date-fns'
    ]
  },
  // CSS configuration
  css: {
    postcss: {},
  }
})
