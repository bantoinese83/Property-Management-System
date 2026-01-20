/**
 * Performance testing utilities for React components.
 *
 * Provides tools to measure and assert component performance.
 */

import { ReactElement } from 'react'
import { render } from '@testing-library/react'

// Performance thresholds (in milliseconds)
export const PERFORMANCE_THRESHOLDS = {
  FAST: 100, // 100ms - instant
  GOOD: 500, // 500ms - acceptable
  SLOW: 1000, // 1s - slow
  UNACCEPTABLE: 3000, // 3s - too slow
} as const

export interface PerformanceMetrics {
  renderTime: number
  memoryUsage?: number
  componentCount: number
  domNodes: number
}

/**
 * Measures component render performance.
 */
export async function measureComponentPerformance(
  component: ReactElement,
  options: {
    iterations?: number
    warmupIterations?: number
    includeMemory?: boolean
  } = {}
): Promise<PerformanceMetrics> {
  const { iterations = 5, warmupIterations = 2, includeMemory = false } = options

  const times: number[] = []

  // Warmup runs
  for (let i = 0; i < warmupIterations; i++) {
    const { unmount } = render(component)
    unmount()
  }

  // Performance measurement runs
  for (let i = 0; i < iterations; i++) {
    const startTime = performance.now()
    const { container, unmount } = render(component)

    // Wait for any async operations
    await new Promise(resolve => setTimeout(resolve, 0))

    const endTime = performance.now()
    times.push(endTime - startTime)

    // Count DOM nodes
    const _domNodes = container.querySelectorAll('*').length

    unmount()
  }

  const avgRenderTime = times.reduce((a, b) => a + b, 0) / times.length
  const minTime = Math.min(...times)
  const maxTime = Math.max(...times)

  // Performance logging (only in development)
  if (process.env.NODE_ENV === 'development') {
    console.warn(`Performance Results:
    Average: ${avgRenderTime.toFixed(2)}ms
    Min: ${minTime.toFixed(2)}ms
    Max: ${maxTime.toFixed(2)}ms
    Iterations: ${iterations}`)
  }

  let memoryUsage: number | undefined
  if (includeMemory && 'memory' in performance) {
    const memInfo = (performance as { memory?: { usedJSHeapSize: number } }).memory
    if (memInfo) {
      memoryUsage = memInfo.usedJSHeapSize / 1024 / 1024 // MB
    }
  }

  return {
    renderTime: avgRenderTime,
    memoryUsage,
    componentCount: 1, // Would need more complex analysis
    domNodes: 0, // Would need to capture from last render
  }
}

/**
 * Asserts that component performance meets thresholds.
 */
export function assertPerformance(
  metrics: PerformanceMetrics,
  thresholds: {
    maxRenderTime?: number
    maxMemoryUsage?: number
    maxDomNodes?: number
  } = {}
) {
  const { maxRenderTime = PERFORMANCE_THRESHOLDS.GOOD, maxMemoryUsage, maxDomNodes } = thresholds

  if (metrics.renderTime > maxRenderTime) {
    throw new Error(
      `Component render time ${metrics.renderTime.toFixed(2)}ms exceeds threshold ${maxRenderTime}ms`
    )
  }

  if (maxMemoryUsage && metrics.memoryUsage && metrics.memoryUsage > maxMemoryUsage) {
    throw new Error(
      `Component memory usage ${metrics.memoryUsage.toFixed(2)}MB exceeds threshold ${maxMemoryUsage}MB`
    )
  }

  if (maxDomNodes && metrics.domNodes > maxDomNodes) {
    throw new Error(`Component DOM nodes ${metrics.domNodes} exceeds threshold ${maxDomNodes}`)
  }
}

/**
 * Performance test helper for vitest.
 */
export function performanceTest(
  name: string,
  component: ReactElement,
  options: {
    iterations?: number
    warmupIterations?: number
    thresholds?: {
      maxRenderTime?: number
      maxMemoryUsage?: number
      maxDomNodes?: number
    }
  } = {}
) {
  return test(`performance: ${name}`, async () => {
    const metrics = await measureComponentPerformance(component, options)

    assertPerformance(metrics, options.thresholds)

    // Log results for CI/CD
    console.warn(`✅ ${name}: ${metrics.renderTime.toFixed(2)}ms`)
  })
}

/**
 * Bundle size monitoring.
 */
export interface BundleMetrics {
  totalSize: number
  gzippedSize: number
  chunkCount: number
  largestChunk: {
    name: string
    size: number
  }
}

/**
 * Mock bundle analyzer for development.
 * In production, use tools like webpack-bundle-analyzer.
 */
export function analyzeBundle(assets: Record<string, number>): BundleMetrics {
  const chunks = Object.entries(assets)
  const totalSize = chunks.reduce((sum, [, size]) => sum + size, 0)
  const largestChunk = chunks.reduce(
    (max, [name, size]) => {
      return size > max.size ? { name, size } : max
    },
    { name: '', size: 0 }
  )

  // Estimate gzipped size (rough approximation)
  const gzippedSize = Math.round(totalSize * 0.3)

  return {
    totalSize,
    gzippedSize,
    chunkCount: chunks.length,
    largestChunk,
  }
}

/**
 * Accessibility performance test.
 */
export async function measureAccessibilityPerformance(component: ReactElement): Promise<{
  renderTime: number
  accessibilityScore: number
  violations: number
}> {
  const startTime = performance.now()
  const { container } = render(component)
  const renderTime = performance.now() - startTime

  // Basic accessibility checks
  const images = container.querySelectorAll('img')
  const imagesWithoutAlt = Array.from(images).filter(img => !img.alt)

  const buttons = container.querySelectorAll('button')
  const buttonsWithoutLabel = Array.from(buttons).filter(
    button => !button.getAttribute('aria-label') && !button.textContent?.trim()
  )

  const inputs = container.querySelectorAll('input')
  const inputsWithoutLabel = Array.from(inputs).filter(
    input =>
      !input.getAttribute('aria-label') &&
      !input.getAttribute('aria-labelledby') &&
      !container.querySelector(`label[for="${input.id}"]`)
  )

  const violations =
    imagesWithoutAlt.length + buttonsWithoutLabel.length + inputsWithoutLabel.length
  const totalElements = images.length + buttons.length + inputs.length
  const accessibilityScore =
    totalElements > 0 ? ((totalElements - violations) / totalElements) * 100 : 100

  return {
    renderTime,
    accessibilityScore,
    violations,
  }
}

/**
 * Memory leak detection helper.
 */
export async function detectMemoryLeaks(
  component: ReactElement,
  options: {
    iterations?: number
    growthThreshold?: number
  } = {}
): Promise<{
  hasMemoryLeak: boolean
  memoryGrowth: number
  averageMemoryUsage: number
}> {
  const { iterations = 10, growthThreshold = 1.5 } = options // 50% growth threshold

  const memoryUsages: number[] = []

  for (let i = 0; i < iterations; i++) {
    const _startTime = performance.now()
    const { unmount } = render(component)

    await new Promise(resolve => setTimeout(resolve, 100)) // Allow for async operations

    if ('memory' in performance) {
      const memInfo = (performance as { memory?: { usedJSHeapSize: number } }).memory
      if (memInfo) {
        memoryUsages.push(memInfo.usedJSHeapSize)
      }
    }

    unmount()
    const _endTime = performance.now()
  }

  if (memoryUsages.length < 2) {
    return {
      hasMemoryLeak: false,
      memoryGrowth: 0,
      averageMemoryUsage: 0,
    }
  }

  const initialMemory = memoryUsages[0]
  const finalMemory = memoryUsages[memoryUsages.length - 1]
  const memoryGrowth = finalMemory / initialMemory
  const hasMemoryLeak = memoryGrowth > growthThreshold
  const averageMemoryUsage = memoryUsages.reduce((a, b) => a + b, 0) / memoryUsages.length

  return {
    hasMemoryLeak,
    memoryGrowth,
    averageMemoryUsage,
  }
}
