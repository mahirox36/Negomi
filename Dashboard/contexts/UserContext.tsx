'use client'

import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import type DiscordOAuth2 from 'discord-oauth2'

interface UserContextType {
  user: DiscordOAuth2.User | null
  setUser: (user: DiscordOAuth2.User | null) => void
  isLoading: boolean
}

const UserContext = createContext<UserContextType>({
  user: null,
  setUser: () => {},
  isLoading: true
})

export function UserProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<DiscordOAuth2.User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      const fetchUser = async () => {
        try {
          const response = await fetch('/api/v1/auth/user', {
            credentials: 'include'
          });
          if (response.ok) {
            const data = await response.json();
            setUser(data.user);
          }
        } catch (error) {
          console.error('Error fetching user data:', error);
        } finally {
          setIsLoading(false);
        }
      };

      fetchUser();
    } else {
      setIsLoading(false);
    }
  }, []);

  const handleSetUser = (newUser: DiscordOAuth2.User | null) => {
    setUser(newUser);
    if (newUser) {
      localStorage.setItem('user', JSON.stringify(newUser));
    } else {
      localStorage.removeItem('user');
    }
  }

  return (
    <UserContext.Provider value={{ user, setUser: handleSetUser, isLoading }}>
      {children}
    </UserContext.Provider>
  )
}

export function useUser() {
  const context = useContext(UserContext)
  if (!context) {
    throw new Error('useUser must be used within a UserProvider')
  }
  return context
}
