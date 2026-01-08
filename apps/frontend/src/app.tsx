import { useEffect, useState } from 'react'
import { AvatarView } from './components/AvatarView'
import { MicController } from './components/MicController'
import { StatusOverlay } from './components/StatusOverlay'
import { DebugPanel } from './components/DebugPanel'
import { useSessionStore } from './state/session'
import { initializeWebRTC } from './webrtc/peer'

function App() {
  const [debugVisible, setDebugVisible] = useState(false)
  const [micPermissionRequested, setMicPermissionRequested] = useState(false)
  const { connectionState, initialize, error } = useSessionStore()

  useEffect(() => {
    initialize()
    // Don't automatically request microphone - wait for user action
  }, [initialize])

  const handleRequestMic = async () => {
    setMicPermissionRequested(true)
    try {
      // Check if browser supports getUserMedia before attempting
      if (!navigator.mediaDevices && !(navigator as any).getUserMedia) {
        useSessionStore.getState().setError('Microphone access is not supported in this browser. Please use Chrome, Firefox, or Edge.')
        return
      }
      await initializeWebRTC()
    } catch (err) {
      console.error('Failed to initialize WebRTC:', err)
      // Error is already set in the store by initializeWebRTC
    }
  }

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
        
        {/* Permission request overlay */}
        {!micPermissionRequested && connectionState === 'disconnected' && (
          <div style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            backgroundColor: 'rgba(0, 0, 0, 0.9)',
            padding: '30px',
            borderRadius: '8px',
            textAlign: 'center',
            border: '1px solid #444',
            zIndex: 1000,
          }}>
            <h2 style={{ margin: '0 0 15px 0', color: '#fff' }}>Microphone Access Required</h2>
            <p style={{ margin: '0 0 20px 0', color: '#ccc', fontSize: '14px' }}>
              This application needs microphone access to enable voice interaction.
            </p>
            <button
              onClick={handleRequestMic}
              style={{
                padding: '12px 24px',
                backgroundColor: '#4CAF50',
                color: '#fff',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '16px',
                fontWeight: 'bold',
              }}
            >
              Allow Microphone Access
            </button>
          </div>
        )}
        
        {/* Error message */}
        {error && (
          <div style={{
            position: 'absolute',
            bottom: '100px',
            left: '50%',
            transform: 'translateX(-50%)',
            backgroundColor: 'rgba(244, 67, 54, 0.9)',
            padding: '15px 20px',
            borderRadius: '4px',
            color: '#fff',
            maxWidth: '500px',
            textAlign: 'center',
            zIndex: 1000,
          }}>
            <p style={{ margin: 0, fontSize: '14px' }}>{error}</p>
            <button
              onClick={handleRequestMic}
              style={{
                marginTop: '10px',
                padding: '8px 16px',
                backgroundColor: '#fff',
                color: '#f44336',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '12px',
              }}
            >
              Try Again
            </button>
          </div>
        )}
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

