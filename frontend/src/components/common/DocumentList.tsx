import React, { useEffect, useState, useCallback } from 'react'
import apiClient from '../../api/client'
import { API_ENDPOINTS } from '../../api/endpoints'
import type { Document } from '../../types/models'
import { LoadingSpinner } from './LoadingSpinner'
import { Trash2, FileText, Download } from 'lucide-react'

interface DocumentListProps {
  modelName: 'property' | 'tenant' | 'lease' | 'maintenance' | 'payment'
  objectId: number
  refreshTrigger?: number
}

export const DocumentList: React.FC<DocumentListProps> = ({
  modelName,
  objectId,
  refreshTrigger = 0,
}) => {
  const [documents, setDocuments] = useState<Document[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchDocuments = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      const response = await apiClient.get<Document[]>(API_ENDPOINTS.DOCUMENTS.LIST, {
        params: {
          model_name: modelName,
          object_id: objectId,
        },
      })
      setDocuments(response.data)
    } catch (err) {
      console.error('Error fetching documents:', err)
      setError('Failed to load documents.')
    } finally {
      setIsLoading(false)
    }
  }, [modelName, objectId])

  useEffect(() => {
    fetchDocuments()
  }, [fetchDocuments, refreshTrigger])

  const handleDelete = async (id: number) => {
    if (!window.confirm('Are you sure you want to delete this document?')) return

    try {
      await apiClient.delete(API_ENDPOINTS.DOCUMENTS.DETAIL(id))
      setDocuments(documents.filter(doc => doc.id !== id))
    } catch (err) {
      console.error('Error deleting document:', err)
      alert('Failed to delete document.')
    }
  }

  if (isLoading) return <LoadingSpinner size='md' />
  if (error) return <div className='text-red-500'>{error}</div>
  if (documents.length === 0) return <div className='text-gray-500'>No documents found.</div>

  return (
    <div className='document-list space-y-2'>
      {documents.map(doc => (
        <div
          key={doc.id}
          className='document-item flex items-center justify-between p-3 border rounded bg-white hover:bg-gray-50 transition-colors'
        >
          <div className='flex items-center space-x-3 overflow-hidden'>
            <div className='flex-shrink-0'>
              <FileText className='h-6 w-6 text-blue-500' />
            </div>
            <div className='overflow-hidden'>
              <p className='font-medium truncate' title={doc.title}>
                {doc.title}
              </p>
              <p className='text-xs text-gray-400'>
                {new Date(doc.created_at).toLocaleDateString()} •{' '}
                {(doc.file_size / 1024).toFixed(1)} KB
              </p>
            </div>
          </div>

          <div className='flex items-center space-x-1 flex-shrink-0'>
            <a
              href={doc.file}
              target='_blank'
              rel='noopener noreferrer'
              className='p-2 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-full transition-colors'
              title='Download'
            >
              <Download className='h-4 w-4' />
            </a>
            <button
              onClick={() => handleDelete(doc.id)}
              className='p-2 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded-full transition-colors'
              title='Delete'
            >
              <Trash2 className='h-4 w-4' />
            </button>
          </div>
        </div>
      ))}
    </div>
  )
}
