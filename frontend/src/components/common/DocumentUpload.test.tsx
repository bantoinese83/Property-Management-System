import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react'
import { DocumentUpload } from './DocumentUpload'
import apiClient from '../../api/client'

// Mock apiClient
vi.mock('../../api/client', () => ({
  default: {
    post: vi.fn(),
  },
}))

describe('DocumentUpload', () => {
  const defaultProps = {
    modelName: 'property' as const,
    objectId: 1,
    onUploadSuccess: vi.fn(),
    onUploadError: vi.fn(),
  }

  let consoleSpy: any

  beforeEach(() => {
    vi.clearAllMocks()
    consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
  })

  afterEach(() => {
    consoleSpy.mockRestore()
  })

  it('renders the upload form', () => {
    render(<DocumentUpload {...defaultProps} />)
    expect(screen.getByRole('heading', { name: /Upload Document/i })).toBeDefined()
    expect(screen.getByLabelText(/Title/i)).toBeDefined()
    expect(screen.getByLabelText(/Description/i)).toBeDefined()
    expect(screen.getByLabelText(/File/i)).toBeDefined()
    expect(screen.getByRole('button', { name: /Upload Document/i })).toBeDefined()
  })

  it('handles file selection and updates title', async () => {
    render(<DocumentUpload {...defaultProps} />)
    const fileInput = screen.getByLabelText(/File/i) as HTMLInputElement
    const titleInput = screen.getByLabelText(/Title/i) as HTMLInputElement

    const file = new File(['hello'], 'hello.png', { type: 'image/png' })
    await act(async () => {
      fireEvent.change(fileInput, { target: { files: [file] } })
    })

    expect(fileInput.files?.[0]).toBe(file)
    expect(titleInput.value).toBe('hello.png')
  })

  it('calls onUploadSuccess when upload is successful', async () => {
    const mockResponse = { data: { id: 1, title: 'hello.png' } }
    vi.mocked(apiClient.post).mockResolvedValueOnce(mockResponse)

    render(<DocumentUpload {...defaultProps} />)

    const fileInput = screen.getByLabelText(/File/i)
    const file = new File(['hello'], 'hello.png', { type: 'image/png' })
    await act(async () => {
      fireEvent.change(fileInput, { target: { files: [file] } })
    })

    // Fill in title (it should be auto-filled, but let's be sure)
    const titleInput = screen.getByLabelText(/Title/i)
    await act(async () => {
      fireEvent.change(titleInput, { target: { value: 'hello.png' } })
    })

    const form = screen.getByRole('button', { name: /Upload Document/i }).closest('form')!
    await act(async () => {
      fireEvent.submit(form)
    })

    await waitFor(() => {
      expect(apiClient.post).toHaveBeenCalled()
      expect(defaultProps.onUploadSuccess).toHaveBeenCalledWith(mockResponse.data)
    })
  })

  it('calls onUploadError when upload fails', async () => {
    const error = new Error('Upload failed')
    vi.mocked(apiClient.post).mockRejectedValueOnce(error)

    render(<DocumentUpload {...defaultProps} />)

    const fileInput = screen.getByLabelText(/File/i)
    const file = new File(['hello'], 'hello.png', { type: 'image/png' })
    await act(async () => {
      fireEvent.change(fileInput, { target: { files: [file] } })
    })

    const form = screen.getByRole('button', { name: /Upload Document/i }).closest('form')!
    await act(async () => {
      fireEvent.submit(form)
    })

    await waitFor(() => {
      expect(apiClient.post).toHaveBeenCalled()
      expect(defaultProps.onUploadError).toHaveBeenCalledWith(error)
    })

    expect(consoleSpy).toHaveBeenCalled()
  })
})
