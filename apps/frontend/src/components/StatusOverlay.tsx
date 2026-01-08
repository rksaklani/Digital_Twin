import { useSessionStore } from '../state/session'

export function StatusOverlay() {
  const { connectionState, latency, error } = useSessionStore()

  if (connectionState === 'disconnected' && !error) {
    return null
  }

  return (
    <div
      style={{
        position: 'absolute',
        top: '20px',
        right: '20px',
        padding: '10px 15px',
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        borderRadius: '4px',
        fontSize: '12px',
        display: 'flex',
        flexDirection: 'column',
        gap: '5px',
      }}
    >
      <div style={{
        color: connectionState === 'connected' ? '#4CAF50' : 
               connectionState === 'connecting' ? '#FFC107' : '#f44336',
      }}>
        {connectionState.toUpperCase()}
      </div>
      {latency !== null && (
        <div style={{ color: '#999' }}>
          Latency: {latency}ms
        </div>
      )}
      {error && (
        <div style={{ color: '#f44336' }}>
          Error: {error}
        </div>
      )}
    </div>
  )
}

