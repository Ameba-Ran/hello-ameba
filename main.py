"""hello-ameba — the minimal reference app built on ameba-sdk.

The smallest useful third-party MEC app: the phone calls THIS app's API; this
app calls the cluster's AI services through the SDK. Start here, then see
``github.com/Ameba-Ran/hello-world`` for the realistic app-server shape (chat, ASR, TTS,
embeddings, RAG).

Endpoints:

    GET  /healthz                 liveness (operators wire this to probes)
    GET  /services                what AI services this app can see (debug)
    POST /speech-translate        multipart audio + target -> JSON (+audio b64)

Run locally:  uvicorn main:app --host 0.0.0.0 --port 8000
"""
from __future__ import annotations

import base64
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from ameba_sdk import AmebaAI, AmebaError

logger = logging.getLogger("hello-ameba")


@asynccontextmanager
async def lifespan(app: FastAPI):
    ai = AmebaAI.from_env()
    app.state.ai = ai
    funcs = ai.available()
    logger.info(
        "AI functions available on this cluster: %s",
        ", ".join(f"{f.name}[{f.kind}] -> {f.base_url}" for f in funcs) or "none",
    )
    yield
    ai.close()


app = FastAPI(title="hello-ameba", lifespan=lifespan)


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/services")
def services():
    ai: AmebaAI = app.state.ai
    return [
        {"name": s.name, "kind": s.kind, "phase": s.phase, "ready": s.ready}
        for s in ai.services(refresh=True)
    ]


@app.post("/speech-translate")
async def speech_translate(
    file: UploadFile = File(...),
    target: str = Form("zh-TW"),
    speak: bool = Form(True),
):
    ai: AmebaAI = app.state.ai
    audio = await file.read()
    try:
        result = ai.pipelines.speech_translate(audio, target=target, synthesize=speak)
    except AmebaError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return {
        "source_text": result.source_text,
        "translated": result.translated_text,
        "audio_mp3_b64": base64.b64encode(result.audio).decode() if result.audio else None,
    }
