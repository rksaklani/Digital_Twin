# Running the Digital Clone Project

## ✅ Services Started

### 1. Signaling Server
- **Status**: Running in background
- **URL**: http://localhost:8080
- **Health Check**: http://localhost:8080/health

### 2. Frontend
- **Status**: Running in background  
- **URL**: http://localhost:3000
- **Open in browser**: http://localhost:3000

### 3. AI Engine
- **Status**: Not started (requires PyTorch)
- **To start**: See instructions below

## 🚀 Starting Services Manually

### Option 1: Start All Services (Recommended)

Open **3 separate terminal windows**:

#### Terminal 1 - Signaling Server
```powershell
cd "M:\RK Drive\digtal_Twin\apps\signaling"
npm run dev
```

#### Terminal 2 - Frontend
```powershell
cd "M:\RK Drive\digtal_Twin\apps\frontend"
npm run dev
```

#### Terminal 3 - AI Engine
```powershell
cd "M:\RK Drive\digtal_Twin"
.\venv\Scripts\Activate.ps1
python -m services.orchestrator.pipeline
```

### Option 2: Use the Start Script

```powershell
cd "M:\RK Drive\digtal_Twin"
.\scripts\start_all.sh
```

## ⚠️ Prerequisites for AI Engine

Before starting the AI Engine, you need to install:

1. **PyTorch** (Required):
   ```powershell
   .\venv\Scripts\python.exe -m pip install torch torchaudio
   ```

2. **TTS** (For voice cloning):
   ```powershell
   .\venv\Scripts\python.exe -m pip install TTS
   ```

3. **LLM** (For local language model):
   ```powershell
   .\venv\Scripts\python.exe -m pip install llama-cpp-python
   ```

## 📋 Current Status

- ✅ Git repository initialized and pushed to GitHub
- ✅ Node.js dependencies installed (signaling + frontend)
- ✅ Python virtual environment created
- ✅ Core Python packages installed
- ⚠️ PyTorch and heavy ML packages pending (see INSTALLATION_STATUS.md)

## 🔍 Verify Services

### Check Signaling Server
```powershell
curl http://localhost:8080/health
```

### Check Frontend
Open browser: http://localhost:3000

### Check AI Engine
```powershell
.\venv\Scripts\python.exe scripts/check_env.py
```

## 🛑 Stopping Services

Press `Ctrl+C` in each terminal window, or:

```powershell
# Find and kill Node processes
Get-Process node | Stop-Process
```

## 📝 Next Steps

1. **Install PyTorch** to enable AI Engine
2. **Download models** (see configs/models.yaml for paths)
3. **Configure .env** file with your settings
4. **Test the system** end-to-end

## 🐛 Troubleshooting

### Port Already in Use
If ports 8080 or 3000 are in use:
- Change ports in `.env` file
- Or kill existing processes: `Get-Process -Name node | Stop-Process`

### Frontend Not Loading
- Check if Vite dev server started: Look for "Local: http://localhost:3000"
- Check browser console for errors

### AI Engine Errors
- Ensure PyTorch is installed
- Check GPU availability: `python -c "import torch; print(torch.cuda.is_available())"`
- Verify model paths in `configs/models.yaml`

