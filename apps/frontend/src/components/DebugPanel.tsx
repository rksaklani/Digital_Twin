import { useSessionStore } from '../state/session'

export function DebugPanel() {
  const { connectionState, roomId, clientId, latency, error } = useSessionStore()

  return (
    <div
      style={{
        position: 'fixed',
        bottom: '100px',
        right: '20px',
        width: '300px',
        maxHeight: '400px',
        backgroundColor: 'rgba(0, 0, 0, 0.9)',
        border: '1px solid #444',
        borderRadius: '4px',
        padding: '15px',
        fontSize: '12px',
        fontFamily: 'monospace',
        overflowY: 'auto',
        zIndex: 1000,
      }}
    >
      <div style={{ marginBottom: '10px', fontWeight: 'bold', color: '#fff' }}>
        Debug Info
      </div>
      
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', color: '#ccc' }}>
        <div>
          <span style={{ color: '#888' }}>State:</span> {connectionState}
        </div>
        {roomId && (
          <div>
            <span style={{ color: '#888' }}>Room:</span> {roomId}
          </div>
        )}
        {clientId && (
          <div>
            <span style={{ color: '#888' }}>Client:</span> {clientId}
          </div>
        )}
        {latency !== null && (
          <div>
            <span style={{ color: '#888' }}>Latency:</span> {latency}ms
          </div>
        )}
        {error && (
          <div style={{ color: '#f44336' }}>
            <span style={{ color: '#888' }}>Error:</span> {error}
          </div>
        )}
      </div>
    </div>
  )
}

