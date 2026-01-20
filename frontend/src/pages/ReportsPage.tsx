import React, { useState, useEffect } from 'react'
import { useApi } from '../hooks/useApi'
import { API_ENDPOINTS } from '../api/endpoints'
import { AppSidebar } from '../components/app-sidebar'
import { SiteHeader } from '../components/site-header'
import { SidebarInset, SidebarProvider } from '../components/ui/sidebar'
import { Button } from '../components/common/Button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { Input } from '../components/common/Input'
import { LoadingSpinner } from '../components/common'
import { Badge } from '../components/common/Badge'
import { FileText, BarChart3, Download, Building2, Users, Wrench, DollarSign } from 'lucide-react'

interface ReportTemplate {
  id: number
  name: string
  display_name: string
  description: string
  report_type: string
  category: string
  default_parameters: Record<string, unknown>
}

interface GeneratedReport {
  id: number
  title: string
  report_type: string
  status: string
  created_at: string
  start_date?: string
  end_date?: string
  is_ready: boolean
  download_count: number
}

const ReportsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'templates' | 'generated'>('templates')
  const [selectedTemplate, setSelectedTemplate] = useState<ReportTemplate | null>(null)
  const [reportParams, setReportParams] = useState({
    start_date: '',
    end_date: '',
    title: '',
  })
  const [generatingReport, setGeneratingReport] = useState(false)

  const { data: templatesData, loading: templatesLoading } = useApi<{
    templates: ReportTemplate[]
  }>(API_ENDPOINTS.REPORTS.TEMPLATES)

  const {
    data: reportsData,
    loading: reportsLoading,
    refetch: refetchReports,
  } = useApi<{ reports: GeneratedReport[] }>(API_ENDPOINTS.REPORTS.LIST)

  const templates = templatesData?.templates || []
  const reports = reportsData?.reports || []

  // Set default date range (last 30 days)
  useEffect(() => {
    const today = new Date()
    const thirtyDaysAgo = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000)

    setReportParams(prev => ({
      ...prev,
      start_date: thirtyDaysAgo.toISOString().split('T')[0],
      end_date: today.toISOString().split('T')[0],
    }))
  }, [])

  const getReportTypeIcon = (reportType: string) => {
    switch (reportType) {
      case 'financial_summary':
        return <DollarSign className='h-5 w-5' />
      case 'property_performance':
        return <Building2 className='h-5 w-5' />
      case 'tenant_report':
        return <Users className='h-5 w-5' />
      case 'maintenance_report':
        return <Wrench className='h-5 w-5' />
      default:
        return <FileText className='h-5 w-5' />
    }
  }

  const getReportTypeColor = (reportType: string) => {
    switch (reportType) {
      case 'financial_summary':
        return 'bg-green-100 text-green-800'
      case 'property_performance':
        return 'bg-blue-100 text-blue-800'
      case 'tenant_report':
        return 'bg-purple-100 text-purple-800'
      case 'maintenance_report':
        return 'bg-orange-100 text-orange-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const handleGenerateReport = async () => {
    if (!selectedTemplate) return

    setGeneratingReport(true)
    try {
      const response = await fetch(API_ENDPOINTS.REPORTS.GENERATE, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({
          report_type: selectedTemplate.report_type,
          start_date: reportParams.start_date,
          end_date: reportParams.end_date,
          title: reportParams.title || selectedTemplate.display_name,
          ...selectedTemplate.default_parameters,
        }),
      })

      const result = await response.json()

      if (response.ok) {
        // Open report in new tab or show download
        window.open(`/api/reports/${result.report_id}/download/`, '_blank')
        refetchReports()
        setSelectedTemplate(null)
      } else {
        alert(`Error generating report: ${result.error}`)
      }
    } catch (error) {
      console.error('Error generating report:', error)
      alert('Failed to generate report. Please try again.')
    } finally {
      setGeneratingReport(false)
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString()
  }

  return (
    <SidebarProvider
      style={
        {
          '--sidebar-width': '280px',
          '--header-height': '60px',
        } as React.CSSProperties
      }
    >
      <AppSidebar variant='inset' />
      <SidebarInset>
        <SiteHeader />
        <div className='flex flex-1 flex-col gap-4 p-4 lg:gap-6 lg:p-6'>
          {/* Header */}
          <div className='flex items-center justify-between'>
            <div>
              <h1 className='text-3xl font-bold tracking-tight'>Reports</h1>
              <p className='text-muted-foreground'>
                Generate and manage comprehensive property reports
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
            </button>
            <button
              onClick={() => setActiveTab('generated')}
              className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors flex items-center gap-2 ${
                activeTab === 'generated'
                  ? 'bg-background text-foreground shadow-sm'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              <BarChart3 className='h-4 w-4' />
              Generated Reports
              {reports.length > 0 && (
                <span className='bg-primary text-primary-foreground text-xs px-1.5 py-0.5 rounded-full'>
                  {reports.length}
                </span>
              )}
            </button>
          </div>

          {/* Tab Content */}
          {activeTab === 'templates' && (
            <div className='space-y-6'>
              {/* Report Generation Form */}
              {selectedTemplate && (
                <Card>
                  <CardHeader>
                    <CardTitle className='flex items-center gap-2'>
                      {getReportTypeIcon(selectedTemplate.report_type)}
                      Generate {selectedTemplate.display_name}
                    </CardTitle>
                    <CardDescription>{selectedTemplate.description}</CardDescription>
                  </CardHeader>
                  <CardContent className='space-y-4'>
                    <div className='grid grid-cols-1 md:grid-cols-3 gap-4'>
                      <div>
                        <label className='text-sm font-medium mb-2 block'>Start Date</label>
                        <Input
                          type='date'
                          value={reportParams.start_date}
                          onChange={e =>
                            setReportParams(prev => ({ ...prev, start_date: e.target.value }))
                          }
                        />
                      </div>
                      <div>
                        <label className='text-sm font-medium mb-2 block'>End Date</label>
                        <Input
                          type='date'
                          value={reportParams.end_date}
                          onChange={e =>
                            setReportParams(prev => ({ ...prev, end_date: e.target.value }))
                          }
                        />
                      </div>
                      <div>
                        <label className='text-sm font-medium mb-2 block'>Report Title</label>
                        <Input
                          placeholder='Custom report title'
                          value={reportParams.title}
                          onChange={e =>
                            setReportParams(prev => ({ ...prev, title: e.target.value }))
                          }
                        />
                      </div>
                    </div>
                    <div className='flex gap-2'>
                      <Button
                        onClick={handleGenerateReport}
                        loading={generatingReport}
                        className='flex items-center gap-2'
                      >
                        <Download className='h-4 w-4' />
                        Generate Report
                      </Button>
                      <Button variant='outline' onClick={() => setSelectedTemplate(null)}>
                        Cancel
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Report Templates */}
              {templatesLoading ? (
                <div className='flex justify-center py-8'>
                  <LoadingSpinner size='lg' />
                </div>
              ) : (
                <div className='grid gap-4 md:grid-cols-2 lg:grid-cols-3'>
                  {templates.map(template => (
                    <Card
                      key={template.id}
                      className={`cursor-pointer transition-all hover:shadow-md ${
                        selectedTemplate?.id === template.id ? 'ring-2 ring-primary' : ''
                      }`}
                      onClick={() => setSelectedTemplate(template)}
                    >
                      <CardHeader>
                        <div className='flex items-center gap-3'>
                          <div
                            className={`p-2 rounded-lg ${getReportTypeColor(template.report_type)}`}
                          >
                            {getReportTypeIcon(template.report_type)}
                          </div>
                          <div className='flex-1'>
                            <CardTitle className='text-lg'>{template.display_name}</CardTitle>
                            <Badge variant='outline' className='text-xs'>
                              {template.category}
                            </Badge>
                          </div>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <CardDescription className='text-sm'>
                          {template.description}
                        </CardDescription>
                        <div className='mt-4'>
                          <Button
                            variant='outline'
                            size='sm'
                            className='w-full'
                            onClick={e => {
                              e.stopPropagation()
                              setSelectedTemplate(template)
                            }}
                          >
                            Generate Report
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
              {/* Generated Reports */}
              {reportsLoading ? (
                <div className='flex justify-center py-8'>
                  <LoadingSpinner size='lg' />
                </div>
              ) : reports.length > 0 ? (
                <div className='space-y-4'>
                  {reports.map(report => (
                    <Card key={report.id}>
                      <CardContent className='p-6'>
                        <div className='flex items-center justify-between'>
                          <div className='flex items-center gap-4'>
                            <div
                              className={`p-2 rounded-lg ${getReportTypeColor(report.report_type)}`}
                            >
                              {getReportTypeIcon(report.report_type)}
                            </div>
                            <div>
                              <h3 className='font-semibold'>{report.title}</h3>
                              <div className='flex items-center gap-2 mt-1'>
                                <Badge variant='outline'>
                                  {report.report_type.replace('_', ' ')}
                                </Badge>
                                <span className='text-sm text-muted-foreground'>
                                  {formatDate(report.created_at)}
                                </span>
                                {report.start_date && report.end_date && (
                                  <span className='text-sm text-muted-foreground'>
                                    • {formatDate(report.start_date)} -{' '}
                                    {formatDate(report.end_date)}
                                  </span>
                                )}
                              </div>
                            </div>
                          </div>
                          <div className='flex items-center gap-2'>
                            <Badge variant={report.status === 'completed' ? 'success' : 'default'}>
                              {report.status}
                            </Badge>
                            {report.is_ready && (
                              <Button
                                variant='outline'
                                size='sm'
                                onClick={() =>
                                  window.open(`/api/reports/${report.id}/download/`, '_blank')
                                }
                              >
                                <Download className='h-4 w-4 mr-2' />
                                Download
                              </Button>
                            )}
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
                    <h3 className='text-lg font-medium mb-2'>No reports generated yet</h3>
                    <p className='text-sm text-muted-foreground text-center max-w-sm'>
                      Generate your first report using the templates in the Templates tab.
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

export default ReportsPage
