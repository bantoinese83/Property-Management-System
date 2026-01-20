import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { visualizer } from 'rollup-plugin-visualizer'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
    // Bundle analyzer - run with ANALYZE=true npm run build
    ...(process.env.ANALYZE === 'true' ? [visualizer({ filename: 'dist/stats.html', open: true })] : [])
  ],
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
          'utils-vendor': ['axios', 'date-fns', 'clsx', 'tailwind-merge', 'tailwindcss'],
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
      'date-fns',
      'tailwindcss'
    ]
  }
})
