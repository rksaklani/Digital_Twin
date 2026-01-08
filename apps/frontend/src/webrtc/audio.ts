export async function captureAudio(): Promise<MediaStream> {
  try {
    // Check if getUserMedia is available (with fallback for older browsers)
    let getUserMedia: (constraints: MediaStreamConstraints) => Promise<MediaStream>
    
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      getUserMedia = navigator.mediaDevices.getUserMedia.bind(navigator.mediaDevices)
    } else if ((navigator as any).getUserMedia) {
      // Fallback for older browsers
      getUserMedia = (constraints: MediaStreamConstraints) => {
        return new Promise((resolve, reject) => {
          (navigator as any).getUserMedia(constraints, resolve, reject)
        })
      }
    } else {
      throw new Error('Microphone access is not supported in this browser. Please use a modern browser like Chrome, Firefox, or Edge.')
    }

    const stream = await getUserMedia({
      audio: {
        channelCount: 1,
        sampleRate: 16000,
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true,
      },
      video: false,
    })

    console.log('[Audio] Microphone captured')
    return stream
  } catch (error: any) {
    console.error('[Audio] Failed to capture microphone:', error)
    
    // Provide more specific error messages
    let errorMessage = 'Failed to access microphone.'
    
    if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
      errorMessage = 'Microphone permission denied. Please allow microphone access in your browser settings and try again.'
    } else if (error.name === 'NotFoundError' || error.name === 'DevicesNotFoundError') {
      errorMessage = 'No microphone found. Please connect a microphone and try again.'
    } else if (error.name === 'NotReadableError' || error.name === 'TrackStartError') {
      errorMessage = 'Microphone is already in use by another application. Please close other applications using the microphone.'
    } else if (error.name === 'OverconstrainedError') {
      errorMessage = 'Microphone constraints could not be satisfied. Trying with default settings...'
      // Try again with simpler constraints
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false })
        console.log('[Audio] Microphone captured with default constraints')
        return stream
      } catch (retryError: any) {
        errorMessage = 'Could not access microphone. Please check your browser settings.'
      }
    } else if (error.message && error.message.includes('not supported')) {
      errorMessage = error.message
    }
    
    throw new Error(errorMessage)
  }
}

export function getAudioLevel(stream: MediaStream): Promise<number> {
  return new Promise((resolve) => {
    const audioContext = new AudioContext()
    const analyser = audioContext.createAnalyser()
    const microphone = audioContext.createMediaStreamSource(stream)
    
    analyser.fftSize = 256
    microphone.connect(analyser)
    
    const dataArray = new Uint8Array(analyser.frequencyBinCount)
    
    const updateLevel = () => {
      analyser.getByteFrequencyData(dataArray)
      const average = dataArray.reduce((a, b) => a + b) / dataArray.length
      resolve(average / 255) // Normalize to 0-1
    }
    
    updateLevel()
  })
}

