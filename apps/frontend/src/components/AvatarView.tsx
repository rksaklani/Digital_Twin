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
        backgroundColor: '#111',
        position: 'relative',
      }}
    >
      <div
        style={{
          width: '512px',
          height: '512px',
          backgroundColor: '#222',
          borderRadius: '8px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#666',
          fontSize: '14px',
        }}
      >
        Avatar will appear here
      </div>
    </div>
  )
}

