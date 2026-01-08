let videoElement: HTMLVideoElement | null = null

export function setupVideoTrack(stream: MediaStream): void {
  if (!videoElement) {
    videoElement = document.createElement('video')
    videoElement.autoplay = true
    videoElement.playsInline = true
    videoElement.style.width = '100%'
    videoElement.style.height = '100%'
    videoElement.style.objectFit = 'contain'
    
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

