# LiveVoiceAI

A fully-offline, real-time voice assistant showcasing:

- **VAD** (webrtcvad) for voice activity detection  
- **Vosk** for speech-to-text transcription  
- **Ollama + LLAMA3** for local LLM-based responses  
- **FastAPI** providing a WebSocket API  
- **Vanilla JavaScript** for client-side mic capture, transcription display, and TTS  

## Features

- Streaming voice-activated transcription and chat  
- Real-time speech segmentation and buffering  
- Local model inference with llama3 (no cloud required)  
- Customizable TTS voices and playback settings  
- Transcript export as plain text file     

## Prerequisites

- Python 3.10+  
- Ollama CLI with your chosen model(s) pulled (e.g. `llama3`)  
- Vosk model downloaded under `model/vosk-model-small-en-us-0.15/`  

## Installation

```bash
git clone https://github.com/DhavalTalaviya/livevoiceai.git
pip install -r requirements.txt
```

## Usage

```bash
cd api
uvicorn api.main:app --reload
```

Then open your browser to:

```
http://localhost:8000/
```

## Project Layout

```
livevoiceai/
├── api/
│   ├── main.py
│   └── requirements.txt
├── client/
│   └── index.html
├── model/
│   └── vosk-model-small-en-us-0.15/   ← Vosk model files
├── .gitignore                          ← Python artifacts, model zips, etc.
└── README.md                           ← This file
```

## .gitignore

```
__pycache__/
*.py[cod]
*.zip
model/*.zip
.env
```
