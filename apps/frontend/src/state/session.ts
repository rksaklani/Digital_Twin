import { create } from 'zustand'

interface SessionState {
  connectionState: 'disconnected' | 'connecting' | 'connected' | 'error'
  roomId: string | null
  clientId: string | null
  latency: number | null
  error: string | null
  initialize: () => void
  setConnectionState: (state: SessionState['connectionState']) => void
  setRoomId: (roomId: string) => void
  setClientId: (clientId: string) => void
  setLatency: (latency: number) => void
  setError: (error: string | null) => void
}

export const useSessionStore = create<SessionState>((set) => ({
  connectionState: 'disconnected',
  roomId: null,
  clientId: null,
  latency: null,
  error: null,
  
  initialize: () => {
    set({ connectionState: 'disconnected' })
  },
  
  setConnectionState: (state) => {
    set({ connectionState: state })
  },
  
  setRoomId: (roomId) => {
    set({ roomId })
  },
  
  setClientId: (clientId) => {
    set({ clientId })
  },
  
  setLatency: (latency) => {
    set({ latency })
  },
  
  setError: (error) => {
    set({ error })
  },
}))

