import { createContext } from 'react'
import type { User, AuthContextType } from './AuthContext.types'

export const AuthContext = createContext<AuthContextType | undefined>(undefined)

export type { User, AuthContextType }
