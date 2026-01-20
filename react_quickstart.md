# Quick Start React Components & Setup

This file contains copy-paste ready code to jumpstart your React frontend development.

---

## 1. Core API Client Setup

### `src/api/client.ts` — Complete Implementation

```typescript
import axios, { AxiosInstance, AxiosError, AxiosResponse } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

interface TokenResponse {
  access: string;
  refresh: string;
}

class APIClient {
  private client: AxiosInstance;
  private refreshTokenPromise: Promise<string> | null = null;

  constructor(baseURL: string) {
    this.client = axios.create({
      baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token');
        if (token && config.headers) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && originalRequest && !this.isRetry(originalRequest)) {
          if (!this.refreshTokenPromise) {
            this.refreshTokenPromise = this.performTokenRefresh();
          }

          try {
            const newToken = await this.refreshTokenPromise;
            this.refreshTokenPromise = null;

            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${newToken}`;
            }
            return this.client(originalRequest);
          } catch {
            this.logout();
            window.location.href = '/login';
            return Promise.reject(error);
          }
        }

        return Promise.reject(error);
      }
    );
  }

  private async performTokenRefresh(): Promise<string> {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    try {
      const { data } = await axios.post<TokenResponse>(
        `${API_BASE_URL}/token/refresh/`,
        { refresh: refreshToken }
      );
      localStorage.setItem('access_token', data.access);
      return data.access;
    } catch (error) {
      this.logout();
      throw error;
    }
  }

  private isRetry(config: any): boolean {
    return config.headers['X-Retry-Count'] ? parseInt(config.headers['X-Retry-Count']) > 0 : false;
  }

  private logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }

  public getClient(): AxiosInstance {
    return this.client;
  }

  public async login(username: string, password: string) {
    const response = await this.client.post<TokenResponse>('/token/', {
      username,
      password,
    });
    localStorage.setItem('access_token', response.data.access);
    localStorage.setItem('refresh_token', response.data.refresh);
    return response.data;
  }

  public logout_user() {
    this.logout();
  }
}

const apiClient = new APIClient(API_BASE_URL);
export default apiClient.getClient();
```

---

## 2. Custom Hooks

### `src/hooks/useApi.ts` — For Data Fetching

```typescript
import { useState, useEffect, useCallback, useRef } from 'react';
import client from '../api/client';

interface UseApiOptions {
  skip?: boolean;
  refetchInterval?: number;
  retryOnError?: number;
}

interface UseApiResponse<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
  isRefetching: boolean;
}

export function useApi<T>(
  url: string,
  options: UseApiOptions = {}
): UseApiResponse<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(!options.skip);
  const [error, setError] = useState<Error | null>(null);
  const [isRefetching, setIsRefetching] = useState(false);
  const retryCount = useRef(0);

  const fetchData = useCallback(async () => {
    if (options.skip) return;

    try {
      setIsRefetching(true);
      setError(null);
      const response = await client.get<T>(url);
      setData(response.data);
      retryCount.current = 0;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Unknown error occurred');
      setError(error);

      if (
        options.retryOnError &&
        retryCount.current < options.retryOnError &&
        (err as any).response?.status >= 500
      ) {
        retryCount.current++;
        setTimeout(() => fetchData(), 1000 * Math.pow(2, retryCount.current));
      }
    } finally {
      setIsRefetching(false);
      setLoading(false);
    }
  }, [url, options.skip, options.retryOnError]);

  useEffect(() => {
    if (!options.skip) {
      fetchData();
    }
  }, [url, options.skip, fetchData]);

  useEffect(() => {
    if (options.refetchInterval) {
      const interval = setInterval(fetchData, options.refetchInterval);
      return () => clearInterval(interval);
    }
  }, [options.refetchInterval, fetchData]);

  return { data, loading, error, refetch: fetchData, isRefetching };
}
```

### `src/hooks/useForm.ts` — For Form State Management

```typescript
import { useState, useCallback, ChangeEvent, FormEvent } from 'react';

interface UseFormOptions<T> {
  initialValues: T;
  onSubmit: (values: T) => Promise<void> | void;
  onError?: (error: Error) => void;
}

interface UseFormReturn<T> {
  values: T;
  errors: Record<string, string>;
  touched: Record<string, boolean>;
  loading: boolean;
  handleChange: (e: ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => void;
  handleBlur: (e: ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => void;
  handleSubmit: (e: FormEvent<HTMLFormElement>) => Promise<void>;
  setValue: (field: keyof T, value: any) => void;
  resetForm: () => void;
}

export function useForm<T extends Record<string, any>>({
  initialValues,
  onSubmit,
  onError,
}: UseFormOptions<T>): UseFormReturn<T> {
  const [values, setValues] = useState<T>(initialValues);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [touched, setTouched] = useState<Record<string, boolean>>({});
  const [loading, setLoading] = useState(false);

  const handleChange = useCallback(
    (e: ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
      const { name, value, type } = e.target;
      const fieldValue = type === 'checkbox' ? (e.target as HTMLInputElement).checked : value;

      setValues((prev) => ({
        ...prev,
        [name]: fieldValue,
      }));

      // Clear error when user starts typing
      if (errors[name]) {
        setErrors((prev) => ({
          ...prev,
          [name]: '',
        }));
      }
    },
    [errors]
  );

  const handleBlur = useCallback((e: ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name } = e.target;
    setTouched((prev) => ({
      ...prev,
      [name]: true,
    }));
  }, []);

  const handleSubmit = useCallback(
    async (e: FormEvent<HTMLFormElement>) => {
      e.preventDefault();
      setLoading(true);

      try {
        await onSubmit(values);
      } catch (error) {
        const err = error instanceof Error ? error : new Error('Unknown error');
        setErrors((prev) => ({
          ...prev,
          submit: err.message,
        }));
        onError?.(err);
      } finally {
        setLoading(false);
      }
    },
    [values, onSubmit, onError]
  );

  const setValue = useCallback((field: keyof T, value: any) => {
    setValues((prev) => ({
      ...prev,
      [field]: value,
    }));
  }, []);

  const resetForm = useCallback(() => {
    setValues(initialValues);
    setErrors({});
    setTouched({});
  }, [initialValues]);

  return {
    values,
    errors,
    touched,
    loading,
    handleChange,
    handleBlur,
    handleSubmit,
    setValue,
    resetForm,
  };
}
```

---

## 3. Reusable Components

### `src/components/common/Button.tsx`

```typescript
import React from 'react';
import classNames from 'classnames';
import '../styles/Button.css';

interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  fullWidth?: boolean;
  onClick?: () => void;
  type?: 'button' | 'submit' | 'reset';
  children: React.ReactNode;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = 'primary',
      size = 'md',
      disabled = false,
      loading = false,
      fullWidth = false,
      onClick,
      type = 'button',
      children,
    },
    ref
  ) => {
    return (
      <button
        ref={ref}
        type={type}
        disabled={disabled || loading}
        onClick={onClick}
        className={classNames('btn', `btn-${variant}`, `btn-${size}`, {
          'btn-full-width': fullWidth,
          'btn-loading': loading,
        })}
      >
        {loading ? <span className="spinner"></span> : null}
        {children}
      </button>
    );
  }
);

Button.displayName = 'Button';
export default Button;
```

### `src/components/common/Card.tsx`

```typescript
import React from 'react';
import '../styles/Card.css';

interface CardProps {
  title?: string;
  subtitle?: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
  className?: string;
  onClick?: () => void;
}

const Card: React.FC<CardProps> = ({
  title,
  subtitle,
  children,
  footer,
  className,
  onClick,
}) => {
  return (
    <div className={`card ${className || ''}`} onClick={onClick}>
      {title && (
        <div className="card-header">
          <h3 className="card-title">{title}</h3>
          {subtitle && <p className="card-subtitle">{subtitle}</p>}
        </div>
      )}
      <div className="card-body">{children}</div>
      {footer && <div className="card-footer">{footer}</div>}
    </div>
  );
};

export default Card;
```

### `src/components/common/Modal.tsx`

```typescript
import React, { useEffect } from 'react';
import '../styles/Modal.css';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
  size?: 'sm' | 'md' | 'lg';
}

const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  children,
  footer,
  size = 'md',
}) => {
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
      return () => {
        document.removeEventListener('keydown', handleEscape);
        document.body.style.overflow = 'unset';
      };
    }
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <>
      <div className="modal-overlay" onClick={onClose}></div>
      <div className={`modal modal-${size}`}>
        <div className="modal-header">
          <h2>{title}</h2>
          <button className="modal-close" onClick={onClose}>
            ×
          </button>
        </div>
        <div className="modal-body">{children}</div>
        {footer && <div className="modal-footer">{footer}</div>}
      </div>
    </>
  );
};

export default Modal;
```

### `src/components/common/Input.tsx`

```typescript
import React from 'react';
import classNames from 'classnames';
import '../styles/Input.css';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  fullWidth?: boolean;
  icon?: React.ReactNode;
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  (
    {
      label,
      error,
      helperText,
      fullWidth = false,
      icon,
      className,
      ...props
    },
    ref
  ) => {
    return (
      <div className={classNames('input-group', { 'input-full-width': fullWidth })}>
        {label && <label className="input-label">{label}</label>}
        <div className={classNames('input-wrapper', { 'input-with-icon': icon })}>
          {icon && <div className="input-icon">{icon}</div>}
          <input
            ref={ref}
            className={classNames('input', className, {
              'input-error': error,
            })}
            {...props}
          />
        </div>
        {error && <span className="input-error-text">{error}</span>}
        {helperText && <span className="input-helper-text">{helperText}</span>}
      </div>
    );
  }
);

Input.displayName = 'Input';
export default Input;
```

---

## 4. Authentication Context & Provider

### `src/context/AuthContext.tsx`

```typescript
import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';
import client from '../api/client';

interface User {
  id: number;
  username: string;
  email: string;
  user_type: 'admin' | 'manager' | 'owner' | 'tenant';
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is already authenticated
    const checkAuth = async () => {
      const token = localStorage.getItem('access_token');
      if (token) {
        try {
          // You might want to call a /me endpoint to get user data
          // For now, we'll just verify the token works
          await client.get('/users/me/');
        } catch (error) {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
        }
      }
      setLoading(false);
    };

    checkAuth();
  }, []);

  const login = useCallback(async (username: string, password: string) => {
    setLoading(true);
    try {
      const response = await client.post<{ access: string; refresh: string; user: User }>(
        '/token/',
        { username, password }
      );
      localStorage.setItem('access_token', response.data.access);
      localStorage.setItem('refresh_token', response.data.refresh);
      setUser(response.data.user);
    } finally {
      setLoading(false);
    }
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
  }, []);

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    login,
    logout,
    loading,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
```

---

## 5. Main App Component

### `src/App.tsx`

```typescript
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import PrivateRoute from './components/auth/PrivateRoute';
import Layout from './components/common/Layout';

// Pages
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import PropertiesPage from './pages/PropertiesPage';
import TenantsPage from './pages/TenantsPage';
import LeasesPage from './pages/LeasesPage';
import MaintenancePage from './pages/MaintenancePage';
import PaymentsPage from './pages/PaymentsPage';

import './App.css';

function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />

          <Route
            element={
              <PrivateRoute>
                <Layout />
              </PrivateRoute>
            }
          >
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/properties" element={<PropertiesPage />} />
            <Route path="/tenants" element={<TenantsPage />} />
            <Route path="/leases" element={<LeasesPage />} />
            <Route path="/maintenance" element={<MaintenancePage />} />
            <Route path="/payments" element={<PaymentsPage />} />
          </Route>

          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;
```

---

## 6. Login Page Example

### `src/pages/LoginPage.tsx`

```typescript
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Input from '../components/common/Input';
import Button from '../components/common/Button';
import '../styles/pages/LoginPage.css';

const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(username, password);
      navigate('/dashboard');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-container">
        <div className="login-header">
          <h1>Property Management</h1>
          <p>Sign in to your account</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          {error && <div className="alert alert-error">{error}</div>}

          <Input
            label="Username"
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Enter your username"
            fullWidth
            required
          />

          <Input
            label="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Enter your password"
            fullWidth
            required
          />

          <Button type="submit" variant="primary" fullWidth loading={loading}>
            Sign In
          </Button>
        </form>

        <div className="login-footer">
          <p>Demo credentials: admin / password</p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
```

---

## 7. Essential CSS Files

### `src/styles/globals.css`

```css
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

:root {
  --color-primary: #2563eb;
  --color-secondary: #64748b;
  --color-danger: #ef4444;
  --color-success: #10b981;
  --color-warning: #f59e0b;
  --color-white: #ffffff;
  --color-gray-50: #f9fafb;
  --color-gray-100: #f3f4f6;
  --color-gray-200: #e5e7eb;
  --color-gray-300: #d1d5db;
  --color-gray-400: #9ca3af;
  --color-gray-500: #6b7280;
  --color-gray-600: #4b5563;
  --color-gray-700: #374151;
  --color-gray-800: #1f2937;
  --color-gray-900: #111827;

  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;
  --spacing-2xl: 3rem;

  --border-radius-sm: 0.375rem;
  --border-radius-md: 0.5rem;
  --border-radius-lg: 0.75rem;

  --font-primary: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;

  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
}

html, body, #root {
  width: 100%;
  height: 100%;
}

body {
  font-family: var(--font-primary);
  background-color: var(--color-gray-50);
  color: var(--color-gray-900);
  line-height: 1.5;
}

a {
  color: var(--color-primary);
  text-decoration: none;
  &:hover {
    text-decoration: underline;
  }
}

/* Alerts */
.alert {
  padding: var(--spacing-md);
  border-radius: var(--border-radius-md);
  margin-bottom: var(--spacing-md);
}

.alert-success {
  background-color: #d1fae5;
  color: #065f46;
  border: 1px solid #6ee7b7;
}

.alert-error {
  background-color: #fee2e2;
  color: #991b1b;
  border: 1px solid #fca5a5;
}

.alert-warning {
  background-color: #fef3c7;
  color: #92400e;
  border: 1px solid #fcd34d;
}
```

### `src/styles/Button.css`

```css
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-md);
  border: none;
  border-radius: var(--border-radius-md);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: inherit;

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  &.btn-primary {
    background-color: var(--color-primary);
    color: white;

    &:hover:not(:disabled) {
      background-color: #1d4ed8;
      box-shadow: var(--shadow-md);
    }
  }

  &.btn-secondary {
    background-color: var(--color-secondary);
    color: white;

    &:hover:not(:disabled) {
      background-color: #475569;
    }
  }

  &.btn-danger {
    background-color: var(--color-danger);
    color: white;

    &:hover:not(:disabled) {
      background-color: #dc2626;
    }
  }

  &.btn-ghost {
    background-color: transparent;
    color: var(--color-primary);
    border: 1px solid var(--color-gray-300);

    &:hover:not(:disabled) {
      background-color: var(--color-gray-50);
    }
  }

  &.btn-sm {
    padding: var(--spacing-xs) var(--spacing-sm);
    font-size: 0.875rem;
  }

  &.btn-md {
    padding: var(--spacing-sm) var(--spacing-md);
    font-size: 1rem;
  }

  &.btn-lg {
    padding: var(--spacing-md) var(--spacing-lg);
    font-size: 1.125rem;
  }

  &.btn-full-width {
    width: 100%;
  }

  &.btn-loading {
    pointer-events: none;
  }

  .spinner {
    display: inline-block;
    width: 1em;
    height: 1em;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-radius: 50%;
    border-top-color: white;
    animation: spin 0.6s linear infinite;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }
}
```

### `src/styles/Input.css`

```css
.input-group {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-md);
}

.input-group.input-full-width {
  width: 100%;
}

.input-label {
  font-weight: 500;
  color: var(--color-gray-700);
  font-size: 0.875rem;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-wrapper.input-with-icon {
  .input {
    padding-left: var(--spacing-lg);
  }
}

.input-icon {
  position: absolute;
  left: var(--spacing-sm);
  display: flex;
  align-items: center;
  color: var(--color-gray-400);
}

.input {
  width: 100%;
  padding: var(--spacing-sm) var(--spacing-md);
  border: 1px solid var(--color-gray-300);
  border-radius: var(--border-radius-md);
  font-family: inherit;
  font-size: 1rem;
  transition: all 0.2s ease;

  &:focus {
    outline: none;
    border-color: var(--color-primary);
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
  }

  &:disabled {
    background-color: var(--color-gray-100);
    color: var(--color-gray-500);
    cursor: not-allowed;
  }

  &.input-error {
    border-color: var(--color-danger);

    &:focus {
      box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
    }
  }
}

.input-error-text {
  color: var(--color-danger);
  font-size: 0.875rem;
}

.input-helper-text {
  color: var(--color-gray-500);
  font-size: 0.875rem;
}
```

---

## Quick Commands

```bash
# Install all dependencies
npm install

# Development
npm run dev

# Build for production
npm run build

# Type checking
npm run type-check

# Linting
npm run lint
```

---

## Environment Variables (.env)

```
VITE_API_URL=http://localhost:8000/api
VITE_APP_NAME=Property Management System
VITE_APP_VERSION=1.0.0
```

---

**Ready to start?** Copy these files into your React project and start building!
