import { useEffect, useRef } from 'react'

export function AvatarView() {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // Container for video element (created by webrtc/video.ts)
    if (containerRef.current) {
      containerRef.current.id = 'avatar-container'
    }
  }, [])

  return (
    <div
      ref={containerRef}
      style={{
        width: '100%',
        height: '100%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        position: 'relative',
      }}
    >
      <div
        className="glass-card"
        style={{
          width: '512px',
          height: '512px',
          borderRadius: '24px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#666',
          fontSize: '16px',
          fontWeight: '500',
          overflow: 'hidden',
          position: 'relative',
          transition: 'all 0.3s ease',
        }}
      >
        <div style={{
          position: 'absolute',
          inset: 0,
          background: 'radial-gradient(circle at center, rgba(0, 0, 0, 0.05) 0%, transparent 70%)',
          pointerEvents: 'none',
          zIndex: 1,
        }} />
        <span 
          id="avatar-placeholder"
          style={{ 
            position: 'relative',
            zIndex: 2,
            transition: 'opacity 0.3s ease',
          }}
        >
          Avatar will appear here
        </span>
      </div>
    </div>
  )
}

