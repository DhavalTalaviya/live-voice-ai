import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import webrtcvad
import uvicorn
from vosk import Model, KaldiRecognizer
from ollama import AsyncClient

app = FastAPI(
    title="LiveVoiceAI Real‑Time Demo (PCM)",
    version="0.4.0"
)

# 1) Load Vosk model once
SAMPLE_RATE = 16000
vosk_model = Model("model/vosk-model-small-en-us-0.15")
recognizer = KaldiRecognizer(vosk_model, SAMPLE_RATE)
recognizer.SetWords(True)

# 2) VAD (aggressiveness: 0–3)
vad = webrtcvad.Vad(2)

# ————— Ollama client —————
ollama_client = AsyncClient()


async def process_audio_stream(ws: WebSocket):
    await ws.accept()

    FRAME_MS = 30
    FRAME_BYTES = int(SAMPLE_RATE * 2 * FRAME_MS / 1000)  # 30 ms @16 kHz ×16‑bit

    buffer = b""
    speech_frames = []
    silence_frames = 0
    SILENCE_THRESHOLD = 10  # 10×30ms = 300ms of silence ⇒ end of segment

    try:
        while True:
            data = await ws.receive_bytes()
            buffer += data

            # chop into 30 ms frames
            while len(buffer) >= FRAME_BYTES:
                frame = buffer[:FRAME_BYTES]
                buffer = buffer[FRAME_BYTES:]

                if vad.is_speech(frame, SAMPLE_RATE):
                    # voice detected → add to buffer, reset silence count
                    speech_frames.append(frame)
                    silence_frames = 0

                elif speech_frames:
                    # still in tail of speech segment
                    silence_frames += 1
                    if silence_frames >= SILENCE_THRESHOLD:
                        # segment complete
                        segment = b"".join(speech_frames)

                        # transcribe entire segment in one pass
                        recognizer = KaldiRecognizer(vosk_model, SAMPLE_RATE)
                        recognizer.SetWords(True)
                        recognizer.AcceptWaveform(segment)
                        result = json.loads(recognizer.Result())
                        text = result.get("text", "")
                        
                        if text:
                            await ws.send_text(text)

                            # Generate an assistant reply via llama3
                            resp = await ollama_client.chat(
                                model="llama3", 
                                messages=[{"role": "user", "content": text}],
                                stream=True
                            )
                            # reply = resp.message.content
                            # if reply:
                            #     await ws.send_text(reply)
                            async for partial in resp:
                                token = partial.message.content  # each chunk
                                if token:
                                    await ws.send_text(token)

                        # reset for next utterance
                        speech_frames = []
                        silence_frames = 0
                else:
                    pass

    except WebSocketDisconnect:
        print("Client disconnected")

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await process_audio_stream(ws)

# 1) Serve client files
app.mount("/", StaticFiles(directory="client", html=True), name="client")


if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True, 
        log_level="info"
    )
