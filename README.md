# hello-ameba — minimal ameba-sdk app

The smallest useful third-party MEC app built on **ameba-sdk**: a single
`main.py` FastAPI server that the phone calls, which in turn calls the cluster's
LLM / ASR / TTS through the SDK. Start here to learn the shape; graduate to
[`hello-world`](https://github.com/Ameba-Ran/hello-world) for the realistic app-server shape (chat,
ASR, TTS, embeddings, RAG, Dockerfile).

## Endpoints

| Endpoint | Purpose |
|---|---|
| `GET /healthz` | liveness (operators wire this to k8s probes) |
| `GET /services` | what AI services this app can see on its cluster (debug) |
| `POST /speech-translate` | multipart audio + `target` → JSON (+ base64 audio) |

## Run

```bash
cp .env.example .env                       # fill in AMEBA_LLM_BASE_URL (and ASR/TTS if used)
set -a && . ./.env && set +a               # the SDK reads os.environ; it never loads .env itself

uv run --with wheels/ameba_ai_sdk-0.4.0-py3-none-any.whl \
  --with fastapi --with "uvicorn[standard]" --with python-multipart \
  uvicorn main:app --host 0.0.0.0 --port 8000
```

Or with a plain venv:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install wheels/ameba_ai_sdk-*.whl -r requirements.txt   # wheel: see wheels/README.md
set -a && . ./.env && set +a
uvicorn main:app --host 0.0.0.0 --port 8000
```

```bash
# quick smoke test
curl -s localhost:8000/healthz
curl -s -X POST localhost:8000/speech-translate -F file=@hello.wav -F target=zh-TW
```

Configuration is the standard `AMEBA_*` set — see [`.env.example`](.env.example)
and the configuration table on the Amebaran doc-hub (Docs → Python SDK).
