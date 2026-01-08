import { useSessionStore } from '../state/session'

export function StatusOverlay() {
  const { connectionState, latency, error } = useSessionStore()

  if (connectionState === 'disconnected' && !error) {
    return null
  }

  return (
    <div
      className="glass-card"
      style={{
        position: 'absolute',
        top: '24px',
        right: '24px',
        padding: '16px 20px',
        borderRadius: '16px',
        fontSize: '13px',
        display: 'flex',
        flexDirection: 'column',
        gap: '8px',
        minWidth: '150px',
      }}
    >
      <div style={{
        color: connectionState === 'connected' 
          ? '#4CAF50' 
          : connectionState === 'connecting' 
          ? '#FFC107' 
          : '#f44336',
        fontWeight: '600',
        fontSize: '14px',
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
      }}>
        <span style={{
          width: '8px',
          height: '8px',
          borderRadius: '50%',
          background: connectionState === 'connected' 
            ? '#4CAF50' 
            : connectionState === 'connecting' 
            ? '#FFC107' 
            : '#f44336',
          boxShadow: connectionState === 'connected'
            ? '0 0 10px rgba(76, 175, 80, 0.8)'
            : connectionState === 'connecting'
            ? '0 0 10px rgba(255, 193, 7, 0.8)'
            : '0 0 10px rgba(244, 67, 54, 0.8)',
        }} />
        {connectionState.toUpperCase()}
      </div>
      {latency !== null && (
        <div style={{ 
          color: '#666',
          fontSize: '12px',
        }}>
          Latency: <span style={{ fontWeight: '600' }}>{latency}ms</span>
        </div>
      )}
      {error && (
        <div style={{ 
          color: '#f44336',
          fontSize: '12px',
          fontWeight: '500',
        }}>
          Error: {error}
        </div>
      )}
    </div>
  )
}

