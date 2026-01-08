# Directory Structure Usage Guide

This guide explains how to use the directory structure and what files to place where.

## Directory Overview

```
Digital_Twin/
├── data/
│   ├── audio/
│   │   ├── raw/         # Raw audio files (input)
│   │   └── clean/       # Cleaned audio (voice cloning reference)
│   └── video/           # Video files (face source for avatar)
├── models/              # AI model files (.gguf, .pth)
├── logs/                # Log files (auto-generated)
└── tmp/                 # Temporary files (auto-generated)
```

## Required Files

### 1. Voice Cloning Reference Audio

**Location:** `data/audio/clean/reference.wav`

**Purpose:** Used by the TTS service to clone your voice. The avatar will speak in this voice.

**Requirements:**
- Format: WAV file
- Sample rate: 24kHz (recommended) or 16kHz
- Duration: 5-30 seconds of clear speech
- Quality: High quality, minimal background noise
- Content: Natural speech (reading a paragraph works well)

**How to prepare:**
1. Record yourself speaking clearly for 10-20 seconds
2. Remove background noise using audio editing software (Audacity, etc.)
3. Export as WAV format
4. Place the file at: `data/audio/clean/reference.wav`

**Configuration:** Set in `configs/models.yaml`:
```yaml
tts:
  voice_clone_reference: "./data/audio/clean/reference.wav"
```

### 2. Face Source Video

**Location:** `data/video/face_source.mp4`

**Purpose:** Used as the base face for the avatar. The system will animate this face with lip sync.

**Requirements:**
- Format: MP4 or AVI
- Resolution: 512x512 or higher (will be resized)
- FPS: 25 fps (recommended)
- Content: Front-facing face, good lighting, neutral expression
- Duration: Can be a single frame or short video loop

**How to prepare:**
1. Record a short video (1-5 seconds) of your face looking at the camera
2. Ensure good lighting and clear face visibility
3. Export as MP4 with H.264 codec
4. Place the file at: `data/video/face_source.mp4`

**Configuration:** Set in `configs/models.yaml`:
```yaml
avatar:
  face_source:
    type: "video"
    path: "./data/video/face_source.mp4"
```

### 3. AI Models

**Location:** `models/`

**Required Models:**

#### LLM Model (Language Model)
- **File:** `models/llama-3.1-8b-instruct-q4_k_m.gguf`
- **Purpose:** Generates conversational responses
- **Download:** 
  - From Hugging Face: https://huggingface.co/models?search=llama-3.1-8b-instruct-gguf
  - Or use llama.cpp to convert from original model
- **Size:** ~5-6 GB (quantized Q4_K_M)

#### Wav2Lip Model (Lip Sync)
- **File:** `models/wav2lip_gan.pth`
- **Purpose:** Synchronizes lip movements with audio
- **Download:** 
  - From: https://github.com/Rudrabha/Wav2Lip
  - Direct link: https://iiitaphyd-my.sharepoint.com/:u:/g/personal/radrabha_m_research_iiit_ac_in/Eb3LEzbfuKlJiR600lQWRxgBUY-PZ8KLEe59pK9Tbq3HWA?e=n9ljGW
- **Size:** ~400 MB

#### Face Detection Model
- **File:** `models/mobilenet.pth`
- **Purpose:** Detects faces in video frames
- **Download:**
  - From: https://github.com/Rudrabha/Wav2Lip
  - Direct link: https://github.com/Rudrabha/Wav2Lip/releases/download/v1.0.0/mobilenet.pth
- **Size:** ~1.5 MB

**Configuration:** Set in `configs/models.yaml`:
```yaml
llm:
  model_path: "./models/llama-3.1-8b-instruct-q4_k_m.gguf"

avatar:
  lip_sync:
    model_path: "./models/wav2lip_gan.pth"
    face_detection_model: "./models/mobilenet.pth"
```

## Optional Files

### Raw Audio Files
**Location:** `data/audio/raw/`

Use this directory to store:
- Original audio recordings before processing
- Test audio files
- Training data (if applicable)

### Logs
**Location:** `logs/`

Automatically generated log files:
- Application logs
- Error logs
- Debug logs

**Note:** You may want to add `logs/` to `.gitignore` to avoid committing log files.

### Temporary Files
**Location:** `tmp/`

Automatically used for:
- Intermediate processing files
- Cache files
- Temporary video/audio frames

**Note:** You may want to add `tmp/` to `.gitignore` and periodically clean this directory.

## Quick Setup Checklist

- [ ] Create directory structure (already done)
- [ ] Download LLM model → `models/llama-3.1-8b-instruct-q4_k_m.gguf`
- [ ] Download Wav2Lip model → `models/wav2lip_gan.pth`
- [ ] Download face detection model → `models/mobilenet.pth`
- [ ] Prepare and place reference audio → `data/audio/clean/reference.wav`
- [ ] Prepare and place face video → `data/video/face_source.mp4`
- [ ] Verify paths in `configs/models.yaml`
- [ ] Test the system

## Verification

After placing files, verify they exist:

```powershell
# Check reference audio
Test-Path "data\audio\clean\reference.wav"

# Check face video
Test-Path "data\video\face_source.mp4"

# Check models
Test-Path "models\llama-3.1-8b-instruct-q4_k_m.gguf"
Test-Path "models\wav2lip_gan.pth"
Test-Path "models\mobilenet.pth"
```

## Troubleshooting

### "File not found" errors
- Check that file paths in `configs/models.yaml` match actual file locations
- Use relative paths starting with `./` (e.g., `./data/audio/clean/reference.wav`)
- Ensure file names match exactly (case-sensitive on Linux/Mac)

### Audio quality issues
- Ensure reference audio is clean (no background noise)
- Use 24kHz sample rate for best results
- Minimum 5 seconds of speech recommended

### Video quality issues
- Ensure face is clearly visible and well-lit
- Use front-facing angle
- Recommended resolution: 512x512 or higher
- Use H.264 codec for MP4 files

### Model loading errors
- Verify model files are complete (check file sizes)
- Ensure you have enough disk space
- Check GPU memory availability for large models

## Next Steps

Once all files are in place:
1. Review `configs/models.yaml` to ensure paths are correct
2. Start the services (see `RUN_PROJECT.md`)
3. Test voice cloning and avatar rendering
4. Adjust settings in config files as needed
