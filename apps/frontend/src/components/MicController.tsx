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
    <div className="glass-card" style={{
      display: 'flex',
      alignItems: 'center',
      gap: '20px',
      padding: '16px 24px',
      borderRadius: '16px',
    }}>
      {/* Audio level indicator */}
      <div className="glass-dark" style={{
        width: '120px',
        height: '8px',
        borderRadius: '10px',
        overflow: 'hidden',
        position: 'relative',
      }}>
        <div
          className={connectionState === 'connected' ? 'glow-pulse' : ''}
          style={{
            width: `${audioLevel * 100}%`,
            height: '100%',
            background: connectionState === 'connected' 
              ? 'linear-gradient(90deg, #4CAF50, #66BB6A)' 
              : 'linear-gradient(90deg, #666, #888)',
            transition: 'width 0.1s ease',
            borderRadius: '10px',
            boxShadow: connectionState === 'connected' 
              ? '0 0 10px rgba(76, 175, 80, 0.5)' 
              : 'none',
          }}
        />
      </div>

      {/* Mute button */}
      <button
        onClick={toggleMute}
        disabled={connectionState !== 'connected'}
        className={connectionState === 'connected' ? 'glass-button' : ''}
        style={{
          width: '56px',
          height: '56px',
          borderRadius: '50%',
          background: isMuted 
            ? 'linear-gradient(135deg, rgba(244, 67, 54, 0.85), rgba(198, 40, 40, 0.75))'
            : connectionState === 'connected'
            ? 'linear-gradient(135deg, rgba(76, 175, 80, 0.85), rgba(56, 142, 60, 0.75))'
            : 'linear-gradient(135deg, rgba(200, 200, 200, 0.6), rgba(180, 180, 180, 0.5))',
          backdropFilter: 'blur(20px) saturate(180%)',
          WebkitBackdropFilter: 'blur(20px) saturate(180%)',
          border: isMuted
            ? '1px solid rgba(244, 67, 54, 0.4)'
            : connectionState === 'connected'
            ? '1px solid rgba(76, 175, 80, 0.4)'
            : '1px solid rgba(255, 255, 255, 0.4)',
          boxShadow: isMuted
            ? '0 4px 20px rgba(244, 67, 54, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.3)'
            : connectionState === 'connected'
            ? '0 4px 20px rgba(76, 175, 80, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.3)'
            : '0 4px 16px rgba(0, 0, 0, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.5)',
          color: '#fff',
          cursor: connectionState === 'connected' ? 'pointer' : 'not-allowed',
          fontSize: '24px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          transition: 'all 0.3s ease',
        }}
        onMouseEnter={(e) => {
          if (connectionState === 'connected') {
            e.currentTarget.style.transform = 'scale(1.1)'
            e.currentTarget.style.boxShadow = '0 6px 25px rgba(76, 175, 80, 0.5)'
          }
        }}
        onMouseLeave={(e) => {
          if (connectionState === 'connected') {
            e.currentTarget.style.transform = 'scale(1)'
            e.currentTarget.style.boxShadow = '0 4px 20px rgba(76, 175, 80, 0.3)'
          }
        }}
        title={isMuted ? 'Unmute' : 'Mute'}
      >
        {isMuted ? '🔇' : '🎤'}
      </button>

      {/* Status text */}
      <span style={{ 
        fontSize: '14px', 
        color: '#333',
        fontWeight: '500',
        minWidth: '100px',
      }}>
        {connectionState === 'connected' ? 'Connected' : 
         connectionState === 'connecting' ? 'Connecting...' : 
         connectionState === 'error' ? 'Error' :
         'Disconnected'}
      </span>
    </div>
  )
}

