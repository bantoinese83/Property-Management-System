/// <reference types="vitest" />
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    // Performance and reliability
    testTimeout: 10000,
    hookTimeout: 5000,
    // Coverage configuration
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/test/',
        '**/*.d.ts',
        '**/*.config.*',
        'dist/',
      ],
      thresholds: {
        global: {
          branches: 70,
          functions: 75,
          lines: 75,
          statements: 75,
        },
      },
    },
    // Performance testing
    pool: 'threads',
    threads: {
      singleThread: false,
      useAtomics: true,
    },
    // Retry failed tests
    retry: 2,
    // Bail out on first failure in CI
    bail: process.env.CI ? 1 : 0,
  },
})