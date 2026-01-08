<<<<<<< HEAD
# Digital_Twin
=======
# Real-Time Digital Clone System

A real-time, browser-based digital avatar that looks and sounds like the user and delivers natural conversational interaction.

## Architecture

- **Frontend**: React + TypeScript + WebRTC (Browser)
- **Signaling Server**: Node.js WebSocket server (WebRTC signaling only)
- **AI Engine**: Python orchestrator coordinating STT, LLM, TTS, and avatar rendering

## Requirements

- NVIDIA RTX 4090 (or similar GPU with 24GB VRAM)
- Python 3.10+
- Node.js 18+
- CUDA 12.0+

## Quick Start

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install frontend dependencies:
```bash
cd apps/frontend && npm install
```

3. Install signaling server dependencies:
```bash
cd apps/signaling && npm install
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your settings
```

5. Start services:
```bash
# Terminal 1: Signaling server
cd apps/signaling && npm run dev

# Terminal 2: AI Engine
python -m services.orchestrator.pipeline

# Terminal 3: Frontend
cd apps/frontend && npm run dev
```

## Project Structure

See `docs/architecture.md` for detailed architecture documentation.

## License

MIT

>>>>>>> 6d3ac84 (Initial commit: digital clone architecture scaffold)
