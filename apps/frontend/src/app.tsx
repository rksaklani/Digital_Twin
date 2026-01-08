import { useEffect, useState } from 'react'
import { AvatarView } from './components/AvatarView'
import { MicController } from './components/MicController'
import { StatusOverlay } from './components/StatusOverlay'
import { DebugPanel } from './components/DebugPanel'
import { useSessionStore } from './state/session'
import { initializeWebRTC } from './webrtc/peer'
import './styles.css'

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
    <div className="white-bg" style={{
      width: '100vw',
      height: '100vh',
      display: 'flex',
      flexDirection: 'column',
      color: '#333',
      position: 'relative',
      overflow: 'hidden',
    }}>
      {/* Main content area */}
      <div style={{
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        position: 'relative',
        padding: '20px',
      }}>
        <AvatarView />
        <StatusOverlay />
        
        {/* Permission request overlay */}
        {!micPermissionRequested && connectionState === 'disconnected' && (
          <div className="glass-card" style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            padding: '40px',
            borderRadius: '20px',
            textAlign: 'center',
            zIndex: 1000,
            minWidth: '400px',
          }}>
            <h2 style={{ 
              margin: '0 0 15px 0', 
              color: '#333',
              fontSize: '24px',
              fontWeight: '600',
            }}>
              Microphone Access Required
            </h2>
            <p style={{ 
              margin: '0 0 30px 0', 
              color: '#666', 
              fontSize: '14px',
              lineHeight: '1.6',
            }}>
              This application needs microphone access to enable voice interaction with your digital twin.
            </p>
            <button
              onClick={handleRequestMic}
              className="glass-button glass-button-primary"
              style={{
                padding: '14px 32px',
                color: '#fff',
                borderRadius: '12px',
                fontSize: '16px',
                fontWeight: '600',
                border: 'none',
                cursor: 'pointer',
              }}
            >
              Allow Microphone Access
            </button>
          </div>
        )}
        
        {/* Error message */}
        {error && (
          <div className="glass-card" style={{
            position: 'absolute',
            bottom: '120px',
            left: '50%',
            transform: 'translateX(-50%)',
            padding: '20px 30px',
            borderRadius: '16px',
            color: '#333',
            maxWidth: '500px',
            textAlign: 'center',
            zIndex: 1000,
            background: 'rgba(244, 67, 54, 0.1)',
            border: '1px solid rgba(244, 67, 54, 0.3)',
          }}>
            <p style={{ margin: 0, fontSize: '14px', fontWeight: '500', color: '#d32f2f' }}>{error}</p>
            <button
              onClick={handleRequestMic}
              className="glass-button"
              style={{
                marginTop: '15px',
                padding: '10px 20px',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '12px',
                fontWeight: '500',
              }}
            >
              Try Again
            </button>
          </div>
        )}
      </div>

      {/* Controls */}
      <div className="glass-dark" style={{
        padding: '24px',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        gap: '20px',
        borderRadius: '24px 24px 0 0',
        margin: '0 20px 0 20px',
        position: 'relative',
      }}>
        <MicController />
        <button
          onClick={() => setDebugVisible(!debugVisible)}
          className="glass-button"
          style={{
            padding: '12px 24px',
            borderRadius: '12px',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: '500',
            border: 'none',
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

