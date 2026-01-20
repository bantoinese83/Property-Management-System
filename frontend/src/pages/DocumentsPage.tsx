import React, { useState } from 'react'
import { useApi } from '../hooks/useApi'
import { API_ENDPOINTS } from '../api/endpoints'
import { AppSidebar } from '../components/app-sidebar'
import { SiteHeader } from '../components/site-header'
import { SidebarInset, SidebarProvider } from '../components/ui/sidebar'
import { Button } from '../components/common/Button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { Input } from '../components/common/Input'
import { LoadingSpinner, Badge } from '../components/common'
import {
  FileText,
  Download,
  Search,
  AlertTriangle,
  BarChart3
} from 'lucide-react'

interface DocumentTemplate {
  id: number
  name: string
  display_name: string
  description: string
  template_type: string
  category: string
  variables: string[]
  usage_count: number
  last_used?: string
}

interface GeneratedDocument {
  id: number
  title: string
  template_name: string
  template_type: string
  status: string
  created_at: string
  created_by_name: string
}

const DocumentsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'templates' | 'generated'>('templates')
  const [searchTerm, setSearchTerm] = useState('')
  const [categoryFilter, setCategoryFilter] = useState('')
  const [typeFilter, setTypeFilter] = useState('')
  const [selectedTemplate, setSelectedTemplate] = useState<DocumentTemplate | null>(null)
  const [templateVariables, setTemplateVariables] = useState<Record<string, any>>({})
  const [documentTitle, setDocumentTitle] = useState('')
  const [generatingDocument, setGeneratingDocument] = useState(false)

  const { data: templatesData, loading: templatesLoading } = useApi<{ templates: DocumentTemplate[] }>(
    `${API_ENDPOINTS.TEMPLATES.LIST}?category=${categoryFilter}&type=${typeFilter}`
  )

  const { data: documentsData, loading: documentsLoading, refetch: refetchDocuments } = useApi<{ documents: GeneratedDocument[] }>(
    API_ENDPOINTS.GENERATED_DOCUMENTS.LIST
  )

  const templates = templatesData?.templates || []
  const documents = documentsData?.documents || []

  const getTemplateIcon = (templateType: string) => {
    switch (templateType) {
      case 'lease': return <FileText className='h-5 w-5' />
      case 'notice': return <AlertTriangle className='h-5 w-5' />
      case 'report': return <BarChart3 className='h-5 w-5' />
      case 'contract': return <FileText className='h-5 w-5' />
      case 'form': return <FileText className='h-5 w-5' />
      default: return <FileText className='h-5 w-5' />
    }
  }

  const getTemplateTypeColor = (templateType: string) => {
    switch (templateType) {
      case 'lease': return 'bg-blue-100 text-blue-800'
      case 'notice': return 'bg-orange-100 text-orange-800'
      case 'report': return 'bg-green-100 text-green-800'
      case 'contract': return 'bg-purple-100 text-purple-800'
      case 'form': return 'bg-gray-100 text-gray-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const handleGenerateDocument = async () => {
    if (!selectedTemplate) return

    setGeneratingDocument(true)
    try {
      const response = await fetch(API_ENDPOINTS.GENERATED_DOCUMENTS.GENERATE, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({
          template_id: selectedTemplate.id,
          variables: templateVariables,
          title: documentTitle || selectedTemplate.display_name,
        })
      })

      const result = await response.json()

      if (response.ok) {
        alert('Document generated successfully!')
        refetchDocuments()
        setSelectedTemplate(null)
        setTemplateVariables({})
        setDocumentTitle('')
      } else {
        alert(`Error generating document: ${result.error}`)
      }
    } catch (error) {
      console.error('Error generating document:', error)
      alert('Failed to generate document. Please try again.')
    } finally {
      setGeneratingDocument(false)
    }
  }

  const handleDownloadDocument = async (documentId: number) => {
    try {
      const response = await fetch(API_ENDPOINTS.GENERATED_DOCUMENTS.DOWNLOAD(documentId), {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
        },
      })

      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `document_${documentId}.txt`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        window.URL.revokeObjectURL(url)
      } else {
        alert('Failed to download document')
      }
    } catch (error) {
      console.error('Error downloading document:', error)
      alert('Failed to download document')
    }
  }

  const filteredTemplates = templates.filter(template =>
    template.display_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    template.description.toLowerCase().includes(searchTerm.toLowerCase())
  )

  return (
    <SidebarProvider
      style={{
        '--sidebar-width': '280px',
        '--header-height': '60px',
      } as React.CSSProperties}
    >
      <AppSidebar variant='inset' />
      <SidebarInset>
        <SiteHeader />
        <div className='flex flex-1 flex-col gap-4 p-4 lg:gap-6 lg:p-6'>
          {/* Header */}
          <div className='flex items-center justify-between'>
            <div>
              <h1 className='text-3xl font-bold tracking-tight'>Documents</h1>
              <p className='text-muted-foreground'>
                Create and manage document templates and generated documents
              </p>
            </div>
          </div>

          {/* Tabs */}
          <div className='flex space-x-1 bg-muted p-1 rounded-lg w-fit'>
            <button
              onClick={() => setActiveTab('templates')}
              className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors flex items-center gap-2 ${
                activeTab === 'templates'
                  ? 'bg-background text-foreground shadow-sm'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              <FileText className='h-4 w-4' />
              Templates
              {templates.length > 0 && (
                <span className='bg-primary text-primary-foreground text-xs px-1.5 py-0.5 rounded-full'>
                  {templates.length}
                </span>
              )}
            </button>
            <button
              onClick={() => setActiveTab('generated')}
              className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors flex items-center gap-2 ${
                activeTab === 'generated'
                  ? 'bg-background text-foreground shadow-sm'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              <Download className='h-4 w-4' />
              Generated Documents
              {documents.length > 0 && (
                <span className='bg-primary text-primary-foreground text-xs px-1.5 py-0.5 rounded-full'>
                  {documents.length}
                </span>
              )}
            </button>
          </div>

          {/* Tab Content */}
          {activeTab === 'templates' && (
            <div className='space-y-6'>
              {/* Document Generation Form */}
              {selectedTemplate && (
                <Card>
                  <CardHeader>
                    <CardTitle className='flex items-center gap-2'>
                      {getTemplateIcon(selectedTemplate.template_type)}
                      Generate {selectedTemplate.display_name}
                    </CardTitle>
                    <CardDescription>{selectedTemplate.description}</CardDescription>
                  </CardHeader>
                  <CardContent className='space-y-4'>
                    <div className='grid grid-cols-1 md:grid-cols-2 gap-4'>
                      <div>
                        <label className='text-sm font-medium mb-2 block'>Document Title</label>
                        <Input
                          placeholder='Enter document title'
                          value={documentTitle}
                          onChange={(e) => setDocumentTitle(e.target.value)}
                        />
                      </div>
                    </div>

                    <div className='space-y-3'>
                      <h4 className='font-medium'>Template Variables</h4>
                      <div className='grid grid-cols-1 md:grid-cols-2 gap-3'>
                        {selectedTemplate.variables.map((variable) => (
                          <div key={variable}>
                            <label className='text-sm font-medium mb-1 block capitalize'>
                              {variable.replace('_', ' ')}
                            </label>
                            <Input
                              placeholder={`Enter ${variable.replace('_', ' ')}`}
                              value={templateVariables[variable] || ''}
                              onChange={(e) => setTemplateVariables(prev => ({
                                ...prev,
                                [variable]: e.target.value
                              }))}
                            />
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className='flex gap-2'>
                      <Button
                        onClick={handleGenerateDocument}
                        loading={generatingDocument}
                        className='flex items-center gap-2'
                      >
                        <Download className='h-4 w-4' />
                        Generate Document
                      </Button>
                      <Button
                        variant='outline'
                        onClick={() => {
                          setSelectedTemplate(null)
                          setTemplateVariables({})
                          setDocumentTitle('')
                        }}
                      >
                        Cancel
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Filters */}
              <Card>
                <CardContent className='pt-6'>
                  <div className='flex flex-col gap-4 md:flex-row md:items-end'>
                    <div className='flex-1'>
                      <label className='text-sm font-medium mb-2 block'>Search Templates</label>
                      <div className='relative'>
                        <Search className='absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground' />
                        <Input
                          placeholder='Search by name or description...'
                          value={searchTerm}
                          onChange={(e) => setSearchTerm(e.target.value)}
                          className='pl-10'
                        />
                      </div>
                    </div>

                    <div className='w-full md:w-48'>
                      <label className='text-sm font-medium mb-2 block'>Category</label>
                      <select
                        value={categoryFilter}
                        onChange={(e) => setCategoryFilter(e.target.value)}
                        className='flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50'
                      >
                        <option value=''>All Categories</option>
                        <option value='residential'>Residential</option>
                        <option value='commercial'>Commercial</option>
                        <option value='payment'>Payment</option>
                        <option value='termination'>Termination</option>
                        <option value='general'>General</option>
                      </select>
                    </div>

                    <div className='w-full md:w-48'>
                      <label className='text-sm font-medium mb-2 block'>Type</label>
                      <select
                        value={typeFilter}
                        onChange={(e) => setTypeFilter(e.target.value)}
                        className='flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50'
                      >
                        <option value=''>All Types</option>
                        <option value='lease'>Lease</option>
                        <option value='notice'>Notice</option>
                        <option value='report'>Report</option>
                        <option value='contract'>Contract</option>
                        <option value='form'>Form</option>
                      </select>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Templates Grid */}
              {templatesLoading ? (
                <div className='flex justify-center py-8'>
                  <LoadingSpinner size='lg' />
                </div>
              ) : (
                <div className='grid gap-4 md:grid-cols-2 lg:grid-cols-3'>
                  {filteredTemplates.map((template) => (
                    <Card
                      key={template.id}
                      className={`cursor-pointer transition-all hover:shadow-md ${
                        selectedTemplate?.id === template.id ? 'ring-2 ring-primary' : ''
                      }`}
                      onClick={() => setSelectedTemplate(template)}
                    >
                      <CardHeader>
                        <div className='flex items-center gap-3'>
                          <div className={`p-2 rounded-lg ${getTemplateTypeColor(template.template_type)}`}>
                            {getTemplateIcon(template.template_type)}
                          </div>
                          <div className='flex-1'>
                            <CardTitle className='text-lg'>{template.display_name}</CardTitle>
                            <div className='flex items-center gap-2 mt-1'>
                              <Badge variant='outline' className='text-xs'>
                                {template.template_type}
                              </Badge>
                              <Badge variant='secondary' className='text-xs'>
                                {template.category}
                              </Badge>
                            </div>
                          </div>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <CardDescription className='text-sm mb-3'>
                          {template.description}
                        </CardDescription>
                        <div className='flex items-center justify-between text-xs text-muted-foreground'>
                          <span>{template.variables.length} variables</span>
                          <span>Used {template.usage_count} times</span>
                        </div>
                        <div className='mt-4'>
                          <Button
                            variant='outline'
                            size='sm'
                            className='w-full'
                            onClick={(e) => {
                              e.stopPropagation()
                              setSelectedTemplate(template)
                            }}
                          >
                            Generate Document
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </div>
          )}

          {activeTab === 'generated' && (
            <div className='space-y-6'>
              {/* Generated Documents */}
              {documentsLoading ? (
                <div className='flex justify-center py-8'>
                  <LoadingSpinner size='lg' />
                </div>
              ) : documents.length > 0 ? (
                <div className='space-y-4'>
                  {documents.map((document) => (
                    <Card key={document.id}>
                      <CardContent className='p-6'>
                        <div className='flex items-center justify-between'>
                          <div className='flex items-center gap-4'>
                            <div className={`p-2 rounded-lg ${getTemplateTypeColor(document.template_type)}`}>
                              {getTemplateIcon(document.template_type)}
                            </div>
                            <div>
                              <h3 className='font-semibold'>{document.title}</h3>
                              <div className='flex items-center gap-2 mt-1'>
                                <Badge variant='outline' className='text-xs'>
                                  {document.template_name}
                                </Badge>
                                <Badge variant={
                                  document.status === 'generated' ? 'success' :
                                  document.status === 'sent' ? 'default' : 'secondary'
                                } className='text-xs'>
                                  {document.status}
                                </Badge>
                                <span className='text-xs text-muted-foreground'>
                                  {new Date(document.created_at).toLocaleDateString()}
                                </span>
                              </div>
                            </div>
                          </div>
                          <div className='flex items-center gap-2'>
                            <Button
                              variant='outline'
                              size='sm'
                              onClick={() => handleDownloadDocument(document.id)}
                            >
                              <Download className='h-4 w-4 mr-2' />
                              Download
                            </Button>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              ) : (
                <Card>
                  <CardContent className='flex flex-col items-center justify-center py-12'>
                    <FileText className='h-12 w-12 text-muted-foreground mb-4' />
                    <h3 className='text-lg font-medium mb-2'>No documents generated yet</h3>
                    <p className='text-sm text-muted-foreground text-center max-w-sm'>
                      Generate your first document using the templates in the Templates tab.
                    </p>
                  </CardContent>
                </Card>
              )}
            </div>
          )}
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}

export default DocumentsPage