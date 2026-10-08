from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="L&F - Lost And Found")

# Permite que el frontend (Astro, puerto 4321) llame a esta API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4321"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}