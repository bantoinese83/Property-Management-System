import React, { useState } from 'react'
import { useApi } from '../hooks/useApi'
import { API_ENDPOINTS } from '../api/endpoints'
import { toast } from 'sonner'
import { AppSidebar } from '../components/app-sidebar'
import { SiteHeader } from '../components/site-header'
import { SidebarInset, SidebarProvider } from '../components/ui/sidebar'
import { Button } from '../components/common/Button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { Input } from '../components/common/Input'
import { Label } from '../components/common/Label'
import { LoadingSpinner, ErrorMessage } from '../components/common'
import { User, Mail, Phone, MapPin, Calendar, Shield, Camera } from 'lucide-react'

interface UserProfile {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  user_type: string
  phone_number: string
  profile_picture?: string
  date_of_birth?: string
  address: string
  city: string
  state: string
  zip_code: string
  is_verified: boolean
  is_email_verified: boolean
  two_factor_enabled: boolean
  profile?: {
    bio: string
    company_name: string
    website: string
  }
}

const AccountPage: React.FC = () => {
  const [isEditing, setIsEditing] = useState(false)

  const {
    data: userData,
    loading,
    error,
    refetch,
  } = useApi<UserProfile>(`${API_ENDPOINTS.USERS.ME}`)

  const [formData, setFormData] = useState<Partial<UserProfile>>(() => userData || {})

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value,
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    try {
      const response = await fetch(API_ENDPOINTS.USERS.ME, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify(formData),
      })

      if (response.ok) {
        toast.success('Profile updated successfully!', {
          description: 'Your account information has been saved.',
        })
        setIsEditing(false)
        refetch()
      } else {
        const errorData = await response.json()
        toast.error('Failed to update profile', {
          description: errorData.detail || 'Please check your information and try again.',
        })
      }
    } catch (error) {
      console.error('Error updating profile:', error)
      toast.error('An error occurred', {
        description: 'Please try again or contact support if the problem persists.',
      })
    }
  }

  const getUserTypeColor = (userType: string) => {
    switch (userType) {
      case 'admin':
        return 'bg-red-100 text-red-800'
      case 'manager':
        return 'bg-blue-100 text-blue-800'
      case 'owner':
        return 'bg-green-100 text-green-800'
      case 'tenant':
        return 'bg-yellow-100 text-yellow-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  if (loading) {
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
          <div className='flex flex-1 items-center justify-center p-4 lg:p-6'>
            <LoadingSpinner size='lg' />
          </div>
        </SidebarInset>
      </SidebarProvider>
    )
  }

  if (error) {
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
          <div className='flex flex-1 items-center justify-center p-4 lg:p-6'>
            <ErrorMessage message={error.message} title='Failed to load account information' />
          </div>
        </SidebarInset>
      </SidebarProvider>
    )
  }

  if (!userData) {
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
          <div className='flex flex-1 items-center justify-center p-4 lg:p-6'>
            <ErrorMessage message='No account data found' title='Account Not Found' />
          </div>
        </SidebarInset>
      </SidebarProvider>
    )
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
              <h1 className='text-3xl font-bold tracking-tight'>Account Settings</h1>
              <p className='text-muted-foreground'>
                Manage your account information and preferences
              </p>
            </div>
            <Button
              onClick={() => setIsEditing(!isEditing)}
              variant={isEditing ? 'outline' : 'default'}
            >
              {isEditing ? 'Cancel' : 'Edit Profile'}
            </Button>
          </div>

          <div className='grid gap-6 md:grid-cols-2'>
            {/* Profile Information */}
            <Card>
              <CardHeader>
                <CardTitle className='flex items-center gap-2'>
                  <User className='h-5 w-5' />
                  Profile Information
                </CardTitle>
                <CardDescription>Your basic account information</CardDescription>
              </CardHeader>
              <CardContent className='space-y-4'>
                {isEditing ? (
                  <form onSubmit={handleSubmit} className='space-y-4'>
                    <div className='grid grid-cols-2 gap-4'>
                      <div className='space-y-2'>
                        <Label htmlFor='first_name'>First Name</Label>
                        <Input
                          id='first_name'
                          value={formData.first_name || ''}
                          onChange={e => handleInputChange('first_name', e.target.value)}
                        />
                      </div>
                      <div className='space-y-2'>
                        <Label htmlFor='last_name'>Last Name</Label>
                        <Input
                          id='last_name'
                          value={formData.last_name || ''}
                          onChange={e => handleInputChange('last_name', e.target.value)}
                        />
                      </div>
                    </div>
                    <div className='space-y-2'>
                      <Label htmlFor='email'>Email</Label>
                      <Input
                        id='email'
                        type='email'
                        value={formData.email || ''}
                        onChange={e => handleInputChange('email', e.target.value)}
                      />
                    </div>
                    <div className='space-y-2'>
                      <Label htmlFor='phone_number'>Phone Number</Label>
                      <Input
                        id='phone_number'
                        value={formData.phone_number || ''}
                        onChange={e => handleInputChange('phone_number', e.target.value)}
                      />
                    </div>
                    <div className='space-y-2'>
                      <Label htmlFor='date_of_birth'>Date of Birth</Label>
                      <Input
                        id='date_of_birth'
                        type='date'
                        value={formData.date_of_birth || ''}
                        onChange={e => handleInputChange('date_of_birth', e.target.value)}
                      />
                    </div>
                    <div className='space-y-2'>
                      <Label htmlFor='address'>Address</Label>
                      <Input
                        id='address'
                        value={formData.address || ''}
                        onChange={e => handleInputChange('address', e.target.value)}
                      />
                    </div>
                    <div className='grid grid-cols-3 gap-4'>
                      <div className='space-y-2'>
                        <Label htmlFor='city'>City</Label>
                        <Input
                          id='city'
                          value={formData.city || ''}
                          onChange={e => handleInputChange('city', e.target.value)}
                        />
                      </div>
                      <div className='space-y-2'>
                        <Label htmlFor='state'>State</Label>
                        <Input
                          id='state'
                          value={formData.state || ''}
                          onChange={e => handleInputChange('state', e.target.value)}
                        />
                      </div>
                      <div className='space-y-2'>
                        <Label htmlFor='zip_code'>ZIP Code</Label>
                        <Input
                          id='zip_code'
                          value={formData.zip_code || ''}
                          onChange={e => handleInputChange('zip_code', e.target.value)}
                        />
                      </div>
                    </div>
                    <div className='flex gap-2 pt-4'>
                      <Button type='submit'>Save Changes</Button>
                      <Button type='button' variant='outline' onClick={() => setIsEditing(false)}>
                        Cancel
                      </Button>
                    </div>
                  </form>
                ) : (
                  <div className='space-y-4'>
                    <div className='flex items-center gap-4'>
                      <div className='flex h-16 w-16 items-center justify-center rounded-full bg-primary/10'>
                        {userData.profile_picture ? (
                          <img
                            src={userData.profile_picture}
                            alt='Profile'
                            className='h-16 w-16 rounded-full object-cover'
                          />
                        ) : (
                          <User className='h-8 w-8 text-primary' />
                        )}
                      </div>
                      <div>
                        <h3 className='text-lg font-medium'>
                          {userData.first_name} {userData.last_name}
                        </h3>
                        <p className='text-sm text-muted-foreground'>@{userData.username}</p>
                        <span
                          className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium mt-1 ${getUserTypeColor(userData.user_type)}`}
                        >
                          {userData.user_type.charAt(0).toUpperCase() + userData.user_type.slice(1)}
                        </span>
                      </div>
                    </div>

                    <div className='grid gap-4 pt-4'>
                      <div className='flex items-center gap-3'>
                        <Mail className='h-4 w-4 text-muted-foreground' />
                        <div>
                          <p className='text-sm font-medium'>Email</p>
                          <p className='text-sm text-muted-foreground'>{userData.email}</p>
                        </div>
                      </div>

                      {userData.phone_number && (
                        <div className='flex items-center gap-3'>
                          <Phone className='h-4 w-4 text-muted-foreground' />
                          <div>
                            <p className='text-sm font-medium'>Phone</p>
                            <p className='text-sm text-muted-foreground'>{userData.phone_number}</p>
                          </div>
                        </div>
                      )}

                      {userData.date_of_birth && (
                        <div className='flex items-center gap-3'>
                          <Calendar className='h-4 w-4 text-muted-foreground' />
                          <div>
                            <p className='text-sm font-medium'>Date of Birth</p>
                            <p className='text-sm text-muted-foreground'>
                              {new Date(userData.date_of_birth).toLocaleDateString()}
                            </p>
                          </div>
                        </div>
                      )}

                      {(userData.address || userData.city || userData.state) && (
                        <div className='flex items-center gap-3'>
                          <MapPin className='h-4 w-4 text-muted-foreground' />
                          <div>
                            <p className='text-sm font-medium'>Address</p>
                            <p className='text-sm text-muted-foreground'>
                              {[userData.address, userData.city, userData.state, userData.zip_code]
                                .filter(Boolean)
                                .join(', ')}
                            </p>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Account Status & Security */}
            <Card>
              <CardHeader>
                <CardTitle className='flex items-center gap-2'>
                  <Shield className='h-5 w-5' />
                  Account Status & Security
                </CardTitle>
                <CardDescription>Account verification and security settings</CardDescription>
              </CardHeader>
              <CardContent className='space-y-4'>
                <div className='flex items-center justify-between'>
                  <div>
                    <p className='text-sm font-medium'>Email Verification</p>
                    <p className='text-xs text-muted-foreground'>
                      {userData.is_email_verified ? 'Verified' : 'Not verified'}
                    </p>
                  </div>
                  <div
                    className={`h-3 w-3 rounded-full ${userData.is_email_verified ? 'bg-green-500' : 'bg-yellow-500'}`}
                  />
                </div>

                <div className='flex items-center justify-between'>
                  <div>
                    <p className='text-sm font-medium'>Account Verification</p>
                    <p className='text-xs text-muted-foreground'>
                      {userData.is_verified ? 'Verified' : 'Pending verification'}
                    </p>
                  </div>
                  <div
                    className={`h-3 w-3 rounded-full ${userData.is_verified ? 'bg-green-500' : 'bg-yellow-500'}`}
                  />
                </div>

                <div className='flex items-center justify-between'>
                  <div>
                    <p className='text-sm font-medium'>Two-Factor Authentication</p>
                    <p className='text-xs text-muted-foreground'>
                      {userData.two_factor_enabled ? 'Enabled' : 'Disabled'}
                    </p>
                  </div>
                  <div
                    className={`h-3 w-3 rounded-full ${userData.two_factor_enabled ? 'bg-green-500' : 'bg-gray-400'}`}
                  />
                </div>

                <div className='pt-4 border-t'>
                  <Button variant='outline' className='w-full'>
                    <Camera className='h-4 w-4 mr-2' />
                    Change Profile Picture
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Profile Information (if exists) */}
          {userData.profile && (
            <Card>
              <CardHeader>
                <CardTitle>Additional Information</CardTitle>
                <CardDescription>Company and professional information</CardDescription>
              </CardHeader>
              <CardContent className='space-y-4'>
                {userData.profile.company_name && (
                  <div>
                    <Label>Company</Label>
                    <p className='text-sm text-muted-foreground mt-1'>
                      {userData.profile.company_name}
                    </p>
                  </div>
                )}

                {userData.profile.website && (
                  <div>
                    <Label>Website</Label>
                    <p className='text-sm text-muted-foreground mt-1'>
                      <a
                        href={userData.profile.website}
                        target='_blank'
                        rel='noopener noreferrer'
                        className='text-primary hover:underline'
                      >
                        {userData.profile.website}
                      </a>
                    </p>
                  </div>
                )}

                {userData.profile.bio && (
                  <div>
                    <Label>Bio</Label>
                    <p className='text-sm text-muted-foreground mt-1'>{userData.profile.bio}</p>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}

export default AccountPage
