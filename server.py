"""
Network Speed Test Server — FastAPI / HTTP
Deploy this on Render (or any cloud).  Run locally with:
    uvicorn server:app --host 0.0.0.0 --port 8000
"""

import time
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse

app = FastAPI(title="Network Speed Test Server", version="2.0")

# Allow all origins so the Streamlit client can reach the server from anywhere
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Health / root ────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "Network Speed Test Server is running",
        "endpoints": ["/ping", "/download", "/upload"]
    }


# ── Latency (replaces UDP ping) ──────────────────────────────────────────────
@app.get("/ping")
def ping():
    """Lightweight endpoint for measuring round-trip latency."""
    return {"pong": True, "server_time": time.time()}


# ── Download test ────────────────────────────────────────────────────────────
@app.get("/download")
def download(size_mb: int = 25):
    """
    Streams `size_mb` megabytes of dummy data to the client.
    The client measures how long it takes → download speed.
    """
    size_mb  = max(1, min(size_mb, 100))      # clamp 1–100 MB
    target   = size_mb * 1024 * 1024
    CHUNK    = b"Z" * 65536

    def generate():
        sent = 0
        while sent < target:
            block = min(len(CHUNK), target - sent)
            yield CHUNK[:block]
            sent += block

    return StreamingResponse(
        generate(),
        media_type="application/octet-stream",
        headers={
            "Content-Length": str(target),
            "Cache-Control": "no-store, no-cache, must-revalidate",
            "X-Size-MB": str(size_mb),
        },
    )


# ── Upload test ──────────────────────────────────────────────────────────────
@app.post("/upload")
async def upload(request: Request):
    """
    Receives a data stream from the client and reports upload speed.
    The client sends `size_mb` MB of dummy data → server measures throughput.
    """
    start      = time.perf_counter()
    total_bytes = 0

    async for chunk in request.stream():
        total_bytes += len(chunk)

    duration   = max(time.perf_counter() - start, 0.001)
    speed_mbps = (total_bytes * 8) / (duration * 1_000_000)

    return JSONResponse({
        "bytes_received": total_bytes,
        "duration_s":     round(duration, 3),
        "speed_mbps":     round(speed_mbps, 2),
    })


# ── Entry point (local dev) ──────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print("=" * 50)
    print("  Network Speed Test Server  (HTTP / FastAPI)")
    print(f"  Listening on  http://0.0.0.0:{port}")
    print("  Endpoints: /ping  /download  /upload")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=port)