export async function captureAudio(): Promise<MediaStream> {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
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
  } catch (error) {
    console.error('[Audio] Failed to capture microphone:', error)
    throw new Error('Failed to access microphone. Please check permissions.')
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

