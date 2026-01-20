import React, { useState, useRef } from 'react'
import type { AxiosError } from 'axios'
import apiClient from '../../api/client'
import { API_ENDPOINTS } from '../../api/endpoints'
import { Button } from './Button'
import { Input } from './Input'
import { Label } from './Label'
import type { Document } from '../../types/models'

interface DocumentUploadProps {
  modelName: 'property' | 'tenant' | 'lease' | 'maintenance' | 'payment'
  objectId: number
  onUploadSuccess?: (document: Document) => void
  onUploadError?: (error: AxiosError) => void
}

export const DocumentUpload: React.FC<DocumentUploadProps> = ({
  modelName,
  objectId,
  onUploadSuccess,
  onUploadError,
}) => {
  const [isUploading, setIsUploading] = useState(false)
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0]
      setFile(selectedFile)
      // Set default title if empty
      if (!title) {
        setTitle(selectedFile.name)
      }
    }
  }

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!file) return

    setIsUploading(true)
    const formData = new FormData()
    formData.append('title', title)
    formData.append('description', description)
    formData.append('file', file)
    formData.append('model_name', modelName)
    formData.append('object_id', objectId.toString())

    try {
      const response = await apiClient.post<Document>(API_ENDPOINTS.DOCUMENTS.CREATE, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      setTitle('')
      setDescription('')
      setFile(null)
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }

      if (onUploadSuccess) {
        onUploadSuccess(response.data)
      }
    } catch (error) {
      console.error('Error uploading document:', error)
      if (onUploadError) {
        onUploadError(error as AxiosError)
      }
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <div className='document-upload-container p-4 border rounded-lg bg-white shadow-sm'>
      <h3 className='text-lg font-medium mb-4'>Upload Document</h3>
      <form onSubmit={handleUpload} className='space-y-4'>
        <div>
          <Label htmlFor='doc-title'>Title</Label>
          <Input
            id='doc-title'
            value={title}
            onChange={e => setTitle(e.target.value)}
            placeholder='Document title'
            required
          />
        </div>

        <div>
          <Label htmlFor='doc-description'>Description (Optional)</Label>
          <Input
            id='doc-description'
            value={description}
            onChange={e => setDescription(e.target.value)}
            placeholder='Document description'
          />
        </div>

        <div>
          <Label htmlFor='doc-file'>File</Label>
          <input
            id='doc-file'
            type='file'
            onChange={handleFileChange}
            ref={fileInputRef}
            className='block w-full text-sm text-gray-500
              file:mr-4 file:py-2 file:px-4
              file:rounded-full file:border-0
              file:text-sm file:font-semibold
              file:bg-blue-50 file:text-blue-700
              hover:file:bg-blue-100'
            required
          />
        </div>

        <Button
          type='submit'
          disabled={!file || isUploading}
          className='w-full'
          loading={isUploading}
        >
          {isUploading ? 'Uploading...' : 'Upload Document'}
        </Button>
      </form>
    </div>
  )
}
