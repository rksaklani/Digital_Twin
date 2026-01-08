import { useEffect, useState } from 'react'
import { AvatarView } from './components/AvatarView'
import { MicController } from './components/MicController'
import { StatusOverlay } from './components/StatusOverlay'
import { DebugPanel } from './components/DebugPanel'
import { useSessionStore } from './state/session'
import { initializeWebRTC } from './webrtc/peer'

function App() {
  const [debugVisible, setDebugVisible] = useState(false)
  const { connectionState, initialize } = useSessionStore()

  useEffect(() => {
    initialize()
    initializeWebRTC()
  }, [initialize])

  return (
    <div style={{
      width: '100vw',
      height: '100vh',
      display: 'flex',
      flexDirection: 'column',
      backgroundColor: '#000',
      color: '#fff',
      fontFamily: 'system-ui, -apple-system, sans-serif',
    }}>
      {/* Main content area */}
      <div style={{
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        position: 'relative',
      }}>
        <AvatarView />
        <StatusOverlay />
      </div>

      {/* Controls */}
      <div style={{
        padding: '20px',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        gap: '20px',
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
      }}>
        <MicController />
        <button
          onClick={() => setDebugVisible(!debugVisible)}
          style={{
            padding: '10px 20px',
            backgroundColor: debugVisible ? '#444' : '#222',
            color: '#fff',
            border: '1px solid #666',
            borderRadius: '4px',
            cursor: 'pointer',
          }}
        >
          {debugVisible ? 'Hide' : 'Show'} Debug
        </button>
      </div>

      {/* Debug panel */}
      {debugVisible && <DebugPanel />}
    </div>
  )
}

export default App

