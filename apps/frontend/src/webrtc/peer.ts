import { captureAudio } from './audio'
import { setupVideoTrack } from './video'
import { useSessionStore } from '../state/session'

const SIGNALING_URL = process.env.VITE_SIGNALING_URL || 'ws://localhost:8080'

let peerConnection: RTCPeerConnection | null = null
let signalingWs: WebSocket | null = null
let localStream: MediaStream | null = null

export async function initializeWebRTC(): Promise<void> {
  const { setConnectionState, setError } = useSessionStore.getState()
  
  try {
    setConnectionState('connecting')
    
    // Create peer connection
    peerConnection = new RTCPeerConnection({
      iceServers: [
        { urls: 'stun:stun.l.google.com:19302' },
      ],
    })

    // Handle ICE candidates
    peerConnection.onicecandidate = (event) => {
      if (event.candidate && signalingWs) {
        signalingWs.send(JSON.stringify({
          type: 'ice-candidate',
          candidate: event.candidate,
        }))
      }
    }

    // Handle connection state changes
    peerConnection.onconnectionstatechange = () => {
      const state = peerConnection?.connectionState
      if (state === 'connected') {
        setConnectionState('connected')
      } else if (state === 'disconnected' || state === 'failed') {
        setConnectionState('disconnected')
      }
    }

    // Handle incoming tracks
    peerConnection.ontrack = (event) => {
      const [remoteStream] = event.streams
      setupVideoTrack(remoteStream)
    }

    // Capture local audio
    localStream = await captureAudio()
    localStream.getTracks().forEach((track) => {
      if (peerConnection) {
        peerConnection.addTrack(track, localStream!)
      }
    })

    // Connect to signaling server
    await connectSignaling()

  } catch (error) {
    console.error('[WebRTC] Initialization error:', error)
    setError(error instanceof Error ? error.message : 'Unknown error')
    setConnectionState('error')
  }
}

async function connectSignaling(): Promise<void> {
  return new Promise((resolve, reject) => {
    signalingWs = new WebSocket(SIGNALING_URL)

    signalingWs.onopen = async () => {
      console.log('[WebRTC] Connected to signaling server')
      
      // Join room
      const roomId = `room_${Date.now()}`
      signalingWs!.send(JSON.stringify({
        type: 'join',
        roomId,
        clientId: `client_${Date.now()}`,
      }))

      // Create and send offer
      if (peerConnection) {
        const offer = await peerConnection.createOffer()
        await peerConnection.setLocalDescription(offer)
        
        signalingWs!.send(JSON.stringify({
          type: 'offer',
          offer: offer,
        }))
      }

      resolve()
    }

    signalingWs.onmessage = async (event) => {
      const message = JSON.parse(event.data)

      switch (message.type) {
        case 'joined':
          useSessionStore.getState().setRoomId(message.roomId)
          useSessionStore.getState().setClientId(message.clientId)
          break

        case 'answer':
          if (peerConnection && message.answer) {
            await peerConnection.setRemoteDescription(
              new RTCSessionDescription(message.answer)
            )
          }
          break

        case 'ice-candidate':
          if (peerConnection && message.candidate) {
            await peerConnection.addIceCandidate(
              new RTCIceCandidate(message.candidate)
            )
          }
          break

        case 'error':
          console.error('[WebRTC] Signaling error:', message.message)
          useSessionStore.getState().setError(message.message)
          reject(new Error(message.message))
          break
      }
    }

    signalingWs.onerror = (error) => {
      console.error('[WebRTC] Signaling error:', error)
      reject(error)
    }

    signalingWs.onclose = () => {
      console.log('[WebRTC] Signaling connection closed')
      useSessionStore.getState().setConnectionState('disconnected')
    }
  })
}

export function cleanupWebRTC(): void {
  if (localStream) {
    localStream.getTracks().forEach((track) => track.stop())
    localStream = null
  }
  
  if (peerConnection) {
    peerConnection.close()
    peerConnection = null
  }
  
  if (signalingWs) {
    signalingWs.close()
    signalingWs = null
  }
}

