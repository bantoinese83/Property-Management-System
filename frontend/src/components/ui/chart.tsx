'use client'

import * as React from 'react'
import * as RechartsPrimitive from 'recharts'

import { cn } from '@/lib/utils'

// Format: { THEME_NAME: CSS_SELECTOR }
const _THEMES = { light: '', dark: '.dark' } as const

export type ChartConfig = {
  [k in string]: {
    label?: React.ReactNode
    icon?: React.ComponentType
  } & (
    | { color?: string; theme?: never }
    | { color?: never; theme: Record<keyof typeof _THEMES, string> }
  )
}

type ChartContextProps = {
  config: ChartConfig
}

const ChartContext = React.createContext<ChartContextProps | null>(null)

const ChartContainer = React.forwardRef<
  HTMLDivElement,
  React.ComponentProps<'div'> & {
    config: ChartConfig
    children: React.ComponentProps<typeof RechartsPrimitive.ResponsiveContainer>['children']
  }
>(({ id, className, children, config, ...props }, ref) => {
  const uniqueId = React.useId()
  const chartId = `chart-${id || uniqueId.replace(/:/g, '')}`

  return (
    <ChartContext.Provider value={{ config }}>
      <div
        data-chart={chartId}
        ref={ref}
        className={cn(
          "flex aspect-video justify-center text-xs [&_.recharts-cartesian-axis-tick_text]:fill-muted-foreground [&_.recharts-cartesian-grid_line[stroke='#ccc']]:stroke-border/50 [&_.recharts-curve.recharts-tooltip-cursor]:stroke-border [&_.recharts-dot[stroke='#fff']]:stroke-transparent [&_.recharts-layer]:outline-none [&_.recharts-polar-grid_[stroke='#ccc']]:stroke-border [&_.recharts-radial-bar-background-sector]:fill-muted [&_.recharts-rectangle.recharts-tooltip-cursor]:fill-muted [&_.recharts-reference-line_[stroke='#ccc']]:stroke-border [&_.recharts-sector[stroke='#fff']]:stroke-transparent [&_.recharts-sector]:outline-none [&_.recharts-surface]:outline-none",
          className
        )}
        {...props}
      >
        <RechartsPrimitive.ResponsiveContainer width='100%' height='100%'>
          {children}
        </RechartsPrimitive.ResponsiveContainer>
      </div>
    </ChartContext.Provider>
  )
})
ChartContainer.displayName = 'ChartContainer'

const ChartTooltip = RechartsPrimitive.Tooltip

const ChartTooltipContent = React.forwardRef<
  HTMLDivElement,
  React.ComponentProps<'div'> & {
    active?: boolean
    payload?: Array<{
      color: string
      name: string
      value: string | number
    }>
    label?: string
    labelFormatter?: (value: string | number | Date) => string
    indicator?: string
  }
>(({ active, payload, label, labelFormatter, indicator = 'dot', className }, ref) => {
  if (active && payload && payload.length) {
    const formattedLabel = labelFormatter && label ? labelFormatter(label) : label

    return (
      <div
        ref={ref}
        className={cn(
          'grid min-w-[8rem] items-start gap-1.5 rounded-lg border border-border/50 bg-background px-2.5 py-1.5 text-xs shadow-xl',
          className
        )}
      >
        {formattedLabel && <div className='font-medium leading-none'>{formattedLabel}</div>}
        <div className='grid gap-1.5'>
          {payload.map((item, index) => (
            <div key={index} className='flex w-full items-stretch gap-2'>
              {indicator !== 'none' && (
                <div
                  className={cn(
                    'shrink-0 rounded-[2px]',
                    indicator === 'dot' ? 'h-2.5 w-2.5' : 'w-1 flex-1'
                  )}
                  style={{ backgroundColor: item.color }}
                />
              )}
              <div className='flex flex-1 justify-between leading-none'>
                <span className='text-muted-foreground'>{item.name}</span>
                <span className='font-mono font-medium tabular-nums text-foreground'>
                  {item.value}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  return null
})
ChartTooltipContent.displayName = 'ChartTooltipContent'

const ChartLegend = RechartsPrimitive.Legend

const ChartLegendContent = React.forwardRef<HTMLDivElement, React.ComponentProps<'div'>>(
  ({ className }, ref) => {
    return (
      <div ref={ref} className={cn('flex items-center justify-center gap-4 pt-3', className)}>
        {/* Legend content will be handled by recharts automatically */}
      </div>
    )
  }
)
ChartLegendContent.displayName = 'ChartLegendContent'

export { ChartContainer, ChartTooltip, ChartTooltipContent, ChartLegend, ChartLegendContent }
