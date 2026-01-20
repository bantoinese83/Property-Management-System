import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Button } from './Button'

describe('Button', () => {
  it('renders with default props', () => {
    render(<Button>Click me</Button>)
    const button = screen.getByRole('button', { name: /click me/i })
    expect(button).toBeInTheDocument()
    expect(button).toHaveClass('btn', 'btn-primary', 'btn-md')
  })

  it('renders with different variants', () => {
    render(<Button variant='secondary'>Secondary</Button>)
    const button = screen.getByRole('button', { name: /secondary/i })
    expect(button).toHaveClass('btn-secondary')
  })

  it('renders with different sizes', () => {
    render(<Button size='lg'>Large Button</Button>)
    const button = screen.getByRole('button', { name: /large button/i })
    expect(button).toHaveClass('btn-lg')
  })

  it('shows loading state', () => {
    render(<Button loading>Loading</Button>)
    const button = screen.getByRole('button', { name: /loading/i })
    expect(button).toHaveClass('btn-loading')
    expect(button).toBeDisabled()
  })

  it('is disabled when disabled prop is true', () => {
    render(<Button disabled>Disabled</Button>)
    const button = screen.getByRole('button', { name: /disabled/i })
    expect(button).toBeDisabled()
  })

  it('calls onClick when clicked', async () => {
    const user = userEvent.setup()
    const handleClick = vi.fn()
    render(<Button onClick={handleClick}>Click me</Button>)

    const button = screen.getByRole('button', { name: /click me/i })
    await user.click(button)

    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('renders with full width', () => {
    render(<Button fullWidth>Full Width</Button>)
    const button = screen.getByRole('button', { name: /full width/i })
    expect(button).toHaveClass('btn-full-width')
  })

  it('renders with custom className', () => {
    render(<Button className='custom-class'>Custom</Button>)
    const button = screen.getByRole('button', { name: /custom/i })
    expect(button).toHaveClass('custom-class')
  })
})
