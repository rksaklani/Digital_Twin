import { useState, useEffect } from 'react'
import { useSessionStore } from '../state/session'

export function MicController() {
  const [isMuted, setIsMuted] = useState(false)
  const [audioLevel, setAudioLevel] = useState(0)
  const { connectionState } = useSessionStore()

  useEffect(() => {
    // TODO: Implement audio level monitoring
    const interval = setInterval(() => {
      // Placeholder for audio level
      setAudioLevel(Math.random() * 0.5)
    }, 100)

    return () => clearInterval(interval)
  }, [])

  const toggleMute = () => {
    setIsMuted(!isMuted)
    // TODO: Actually mute/unmute audio track
  }

  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      gap: '15px',
    }}>
      {/* Audio level indicator */}
      <div style={{
        width: '100px',
        height: '20px',
        backgroundColor: '#333',
        borderRadius: '10px',
        overflow: 'hidden',
        position: 'relative',
      }}>
        <div
          style={{
            width: `${audioLevel * 100}%`,
            height: '100%',
            backgroundColor: connectionState === 'connected' ? '#4CAF50' : '#666',
            transition: 'width 0.1s ease',
          }}
        />
      </div>

      {/* Mute button */}
      <button
        onClick={toggleMute}
        disabled={connectionState !== 'connected'}
        style={{
          width: '50px',
          height: '50px',
          borderRadius: '50%',
          border: 'none',
          backgroundColor: isMuted ? '#f44336' : (connectionState === 'connected' ? '#4CAF50' : '#666'),
          color: '#fff',
          cursor: connectionState === 'connected' ? 'pointer' : 'not-allowed',
          fontSize: '20px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
        title={isMuted ? 'Unmute' : 'Mute'}
      >
        {isMuted ? '🔇' : '🎤'}
      </button>

      {/* Status text */}
      <span style={{ fontSize: '14px', color: '#999' }}>
        {connectionState === 'connected' ? 'Connected' : 
         connectionState === 'connecting' ? 'Connecting...' : 
         'Disconnected'}
      </span>
    </div>
  )
}

