# Demo Flow Guide

This guide walks through the complete flow of the Digital Clone system from user interaction to avatar response.

## Prerequisites

1. All services running:
   - Signaling server (port 8080)
   - AI Engine (Python orchestrator)
   - Frontend (port 3000)

2. Required models downloaded:
   - Whisper model (auto-downloaded)
   - LLM model (GGUF format)
   - TTS model (auto-downloaded)
   - Reference audio for voice cloning

3. Browser with microphone permissions granted

## Demo Flow

### Step 1: Initialization

1. **Browser loads frontend** (`http://localhost:3000`)
2. **Frontend initializes WebRTC**
   - Requests microphone access
   - Creates RTCPeerConnection
   - Connects to signaling server

3. **Signaling server creates room**
   - Generates room ID
   - Waits for AI Engine connection

4. **AI Engine initializes**
   - Loads all models (STT, LLM, TTS, Avatar)
   - Connects to signaling server
   - Establishes WebRTC connection

5. **WebRTC connection established**
   - Audio track active
   - Video track ready
   - Status: "Connected"

### Step 2: User Speaks

1. **User speaks into microphone**
   - Audio captured at 16kHz
   - Sent via WebRTC to AI Engine

2. **AI Engine receives audio**
   - Latency monitor marks: `audio_received`
   - Audio buffered for STT

3. **STT processes audio**
   - VAD detects speech
   - Whisper transcribes
   - Partial results available

4. **Transcription complete**
   - Latency monitor marks: `transcription_complete`
   - Text: "Hello, how are you?"

### Step 3: Intent Classification

1. **Intent classifier processes text**
   - Detects: intent="question", emotion="neutral"
   - Extracts keywords: ["hello", "how", "are"]

2. **Event routed to LLM**
   - Intent result included
   - Context from session memory

### Step 4: LLM Response

1. **LLM generates response**
   - Prompt built with system/style/safety prompts
   - Conversation history included
   - Streaming generation starts

2. **First token generated**
   - Latency monitor marks: `llm_first_token`
   - Response: "I'm doing well, thank you for asking!"

3. **Response complete**
   - Latency monitor marks: `llm_complete`
   - Stored in session memory

### Step 5: TTS Synthesis

1. **TTS synthesizes speech**
   - Voice cloning from reference audio
   - Prosody adjusted for emotion (neutral)
   - Streaming audio chunks generated

2. **Audio chunks emitted**
   - Latency monitor marks: `tts_complete`
   - Sent to avatar for lip sync

### Step 6: Avatar Rendering

1. **Avatar processes audio**
   - Lip sync generates visemes
   - Expressions applied (neutral)
   - Idle motion continues

2. **Video frame rendered**
   - Face with lip sync
   - Natural expressions
   - Sent via WebRTC

3. **Browser displays avatar**
   - Video track receives frame
   - Avatar speaks with lip sync
   - User sees response

### Step 7: Interrupt Handling (Optional)

If user speaks during avatar response:

1. **Interrupt detected**
   - New audio received
   - Interrupt handler triggered

2. **Cancellation**
   - TTS synthesis stopped
   - LLM generation cancelled
   - Avatar animation cleared

3. **State reset**
   - Back to listening mode
   - Ready for new input

## Latency Timeline

Example timeline for a complete interaction:

```
0ms     - User starts speaking
200ms   - Audio received by AI Engine
400ms   - STT transcription complete
900ms   - LLM first token
1500ms  - LLM response complete
1600ms  - TTS synthesis starts
2000ms  - First audio chunk
2050ms  - Avatar lip sync active
2100ms  - Video frame sent
2200ms  - Browser displays response
```

**Total: ~2.2 seconds** (within 2.5s target)

## Debugging

### Check Connection Status

- Frontend: Look at StatusOverlay component
- Signaling: Check WebSocket connection
- AI Engine: Check logs for service initialization

### Monitor Latency

- Enable debug panel in frontend
- Check latency metrics in orchestrator logs
- Run `python scripts/profile_latency.py`

### Common Issues

1. **No audio input**
   - Check microphone permissions
   - Verify WebRTC audio track is active
   - Check browser console for errors

2. **No transcription**
   - Verify STT model loaded
   - Check audio format (16kHz, mono)
   - Check VAD threshold

3. **No LLM response**
   - Verify LLM model path
   - Check GPU memory
   - Check prompt system files

4. **No avatar video**
   - Verify face source loaded
   - Check avatar renderer logs
   - Verify WebRTC video track

## Performance Tips

1. **Pre-warm models**: Run `python scripts/warmup_gpu.py`
2. **Optimize buffers**: Adjust in `configs/latency.yaml`
3. **Monitor GPU**: Use `nvidia-smi` to check memory
4. **Profile latency**: Use profiling script regularly

## Demo Script

For a smooth demo:

1. Start all services
2. Open browser to frontend
3. Wait for "Connected" status
4. Speak clearly into microphone
5. Observe avatar response
6. Try interrupting during response
7. Check debug panel for metrics

## Success Criteria

A successful demo shows:

- ✅ Avatar responds within 2.5 seconds
- ✅ Lip sync matches audio
- ✅ Natural facial expressions
- ✅ Smooth interruption handling
- ✅ Stable connection throughout
- ✅ Recognizable voice cloning

## Next Steps

After successful demo:

1. Fine-tune latency targets
2. Optimize model settings
3. Improve avatar realism
4. Add more gesture types
5. Enhance expression system

