let videoElement: HTMLVideoElement | null = null

export function setupVideoTrack(stream: MediaStream): void {
  if (!videoElement) {
    videoElement = document.createElement('video')
    videoElement.autoplay = true
    videoElement.playsInline = true
    videoElement.style.width = '100%'
    videoElement.style.height = '100%'
    videoElement.style.objectFit = 'cover'
    videoElement.style.borderRadius = '24px'
    videoElement.style.boxShadow = '0 8px 32px 0 rgba(31, 38, 135, 0.37)'
    videoElement.style.opacity = '0'
    videoElement.style.transition = 'opacity 0.5s ease'
    
    // Hide placeholder when video starts playing
    videoElement.addEventListener('playing', () => {
      const placeholder = document.getElementById('avatar-placeholder')
      if (placeholder) {
        placeholder.style.opacity = '0'
        placeholder.style.pointerEvents = 'none'
      }
      if (videoElement) {
        videoElement.style.opacity = '1'
      }
    })
    
    const container = document.getElementById('avatar-container')
    if (container) {
      container.appendChild(videoElement)
    } else {
      console.warn('[Video] Avatar container not found')
    }
  }
  
  videoElement.srcObject = stream
  console.log('[Video] Video track set up')
}

export function getVideoElement(): HTMLVideoElement | null {
  return videoElement
}

