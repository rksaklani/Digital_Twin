import { useSessionStore } from '../state/session'

export function DebugPanel() {
  const { connectionState, roomId, clientId, latency, error } = useSessionStore()

  return (
    <div
      className="glass-card"
      style={{
        position: 'fixed',
        bottom: '120px',
        right: '24px',
        width: '320px',
        maxHeight: '450px',
        borderRadius: '20px',
        padding: '20px',
        fontSize: '12px',
        fontFamily: 'monospace',
        overflowY: 'auto',
        zIndex: 1000,
      }}
    >
      <div style={{ 
        marginBottom: '16px', 
        fontWeight: 'bold', 
        color: '#333',
        fontSize: '16px',
        borderBottom: '1px solid rgba(0, 0, 0, 0.1)',
        paddingBottom: '12px',
      }}>
        Debug Info
      </div>
      
      <div style={{ 
        display: 'flex', 
        flexDirection: 'column', 
        gap: '12px', 
        color: '#333',
      }}>
        <div style={{
          padding: '8px 12px',
          background: 'rgba(0, 0, 0, 0.03)',
          borderRadius: '8px',
        }}>
          <span style={{ color: '#999', marginRight: '8px' }}>State:</span> 
          <span style={{ fontWeight: '600' }}>{connectionState}</span>
        </div>
        {roomId && (
          <div style={{
            padding: '8px 12px',
            background: 'rgba(0, 0, 0, 0.03)',
            borderRadius: '8px',
          }}>
            <span style={{ color: '#999', marginRight: '8px' }}>Room:</span> 
            <span style={{ fontWeight: '600' }}>{roomId}</span>
          </div>
        )}
        {clientId && (
          <div style={{
            padding: '8px 12px',
            background: 'rgba(0, 0, 0, 0.03)',
            borderRadius: '8px',
          }}>
            <span style={{ color: '#999', marginRight: '8px' }}>Client:</span> 
            <span style={{ fontWeight: '600' }}>{clientId}</span>
          </div>
        )}
        {latency !== null && (
          <div style={{
            padding: '8px 12px',
            background: 'rgba(0, 0, 0, 0.03)',
            borderRadius: '8px',
          }}>
            <span style={{ color: '#999', marginRight: '8px' }}>Latency:</span> 
            <span style={{ fontWeight: '600', color: '#4CAF50' }}>{latency}ms</span>
          </div>
        )}
        {error && (
          <div style={{ 
            color: '#f44336',
            padding: '8px 12px',
            background: 'rgba(244, 67, 54, 0.1)',
            borderRadius: '8px',
            border: '1px solid rgba(244, 67, 54, 0.3)',
          }}>
            <span style={{ color: '#999', marginRight: '8px' }}>Error:</span> 
            <span style={{ fontWeight: '600' }}>{error}</span>
          </div>
        )}
      </div>
    </div>
  )
}

