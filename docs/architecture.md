# Digital Clone System Architecture

## Overview

The Digital Clone System is a real-time, browser-based digital avatar that provides natural conversational interaction. The system consists of three main components:

1. **Frontend** (React/TypeScript) - Browser-based UI with WebRTC
2. **Signaling Server** (Node.js) - WebRTC signaling coordination
3. **AI Engine** (Python) - Orchestrator coordinating STT, LLM, TTS, and avatar rendering

## System Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Browser   │◄───────►│   Signaling  │◄───────►│  AI Engine  │
│  (Frontend) │ WebRTC  │    Server    │ WebRTC  │ (Orchestrator)│
└─────────────┘         └──────────────┘         └─────────────┘
     │                                                        │
     │ Audio/Video                                           │
     │                                                        │
     └────────────────────────────────────────────────────────┘
```

## Component Details

### Frontend (Browser)

**Location**: `apps/frontend/`

**Responsibilities**:
- Microphone audio capture
- WebRTC peer connection management
- Avatar video display
- User interface and controls
- Debug and status overlays

**Key Files**:
- `src/webrtc/peer.ts` - WebRTC peer connection
- `src/webrtc/audio.ts` - Audio capture
- `src/components/AvatarView.tsx` - Avatar display
- `src/components/MicController.tsx` - Microphone controls

### Signaling Server

**Location**: `apps/signaling/`

**Responsibilities**:
- WebRTC signaling (SDP offer/answer relay)
- ICE candidate exchange
- Room/session management
- Health monitoring

**Key Files**:
- `src/server.ts` - WebSocket server
- `src/relay.ts` - WebRTC message relay
- `src/rooms.ts` - Session management

**Note**: This server does NOT handle any AI logic. It is purely for WebRTC signaling.

### AI Engine

**Location**: `services/`

The AI Engine is the core of the system, consisting of:

#### Orchestrator (`services/orchestrator/`)

The orchestrator coordinates all services:

- **Pipeline** (`pipeline.py`) - Main event loop and service coordination
- **Router** (`router.py`) - Event bus for inter-service communication
- **Interrupt Handler** (`interrupt.py`) - Real-time cancellation
- **Latency Monitor** (`latency.py`) - End-to-end latency tracking

#### Services

1. **WebRTC Server** (`services/streaming/`)
   - Handles WebRTC peer connections
   - Audio input from browser
   - Video output to browser

2. **STT** (`services/stt/`)
   - Speech-to-text using Whisper
   - Voice activity detection (VAD)
   - Streaming transcription

3. **Intent/Emotion** (`services/intent_emotion/`)
   - Text classification
   - Intent detection (question, command, statement)
   - Emotion classification (positive, negative, neutral)
   - Rule-based expression mapping

4. **LLM** (`services/brain/`)
   - Local quantized language model (llama.cpp)
   - Prompt system
   - Session memory
   - Response generation

5. **TTS** (`services/tts/`)
   - Voice cloning (XTTS)
   - Streaming synthesis
   - Prosody control

6. **Avatar** (`services/avatar/`)
   - Lip sync (audio-driven)
   - Facial expressions
   - Idle motion
   - Video rendering

7. **Gesture** (`services/gesture/`)
   - Head movements
   - Micro-gestures
   - Rule-based triggers

## Data Flow

### Audio Input Flow

```
Browser Mic → WebRTC → AI Engine → STT → Intent/Emotion → LLM → TTS → Avatar → WebRTC → Browser
```

1. User speaks into microphone
2. Audio captured in browser
3. Sent via WebRTC to AI Engine
4. STT transcribes speech
5. Intent/emotion classified
6. LLM generates response
7. TTS synthesizes speech
8. Avatar renders with lip sync
9. Video sent back via WebRTC
10. Displayed in browser

### Latency Targets

- Audio capture → STT: < 200ms
- STT → LLM response start: < 500ms
- LLM → TTS start: < 100ms
- TTS → Avatar sync: < 50ms
- **Total end-to-end: < 2.5s**

## Configuration

All configuration is in `configs/`:

- `models.yaml` - Model paths and settings
- `gpu.yaml` - GPU memory allocation
- `latency.yaml` - Latency targets and buffers
- `webrtc.yaml` - WebRTC settings

## Interrupt Handling

The system supports real-time interruption:

1. User speech detection triggers interrupt
2. Current TTS synthesis cancelled
3. In-flight LLM generation cancelled
4. Avatar animation queue cleared
5. State reset to listening mode

## Memory Management

- **Session Memory**: Short-term conversation context (last 20 exchanges)
- **User Profile**: Static preferences (read-only, not learned)
- **No long-term learning**: System behavior is deterministic

## Model Selection

Default models optimized for RTX 4090:

- **STT**: faster-whisper (medium)
- **VAD**: Silero VAD
- **LLM**: Llama 3.1 8B Q4_K_M (via llama.cpp)
- **TTS**: XTTS-v2 (Coqui)
- **Lip Sync**: Wav2Lip (placeholder implementation)

## GPU Memory Allocation

Total: ~24GB VRAM (RTX 4090)

- STT: 2GB
- VAD: 0.5GB
- Intent/Emotion: 1GB
- LLM: 8GB
- TTS: 3GB
- Avatar: 4GB
- Buffer: 5.5GB

## Development

### Starting Services

1. Signaling server: `cd apps/signaling && npm run dev`
2. AI Engine: `python -m services.orchestrator.pipeline`
3. Frontend: `cd apps/frontend && npm run dev`

Or use the convenience script: `./scripts/start_all.sh`

### Environment Check

Run `python scripts/check_env.py` to validate setup.

### Latency Profiling

Run `python scripts/profile_latency.py` to measure latency.

## Design Principles

1. **Illusion over simulation** - Focus on perceived realism
2. **Responsiveness over perfection** - Low latency is critical
3. **Explicit control** - No learned unpredictability
4. **Shipping over research** - Production-ready code

## Limitations

- 2D face-centric avatar (no full-body)
- No long-term personality learning
- Deterministic behavior (not emergent)
- Single GPU operation (RTX 4090)

## Future Enhancements

Potential improvements (not in current scope):

- 3D avatar support
- Multi-user sessions
- Cloud deployment
- Advanced gesture learning
- Emotion-driven animation

