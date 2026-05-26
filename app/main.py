from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import auth, balita, antropometri, intervensi, laporan
from app.core.database import engine, Base

# Buat semua tabel di database secara otomatis saat startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="be-tumbang.id API",
    description="Backend API untuk Sistem Pemantauan Gizi Balita berbasis AI",
    version="1.0.0",
)

# ───────────────────────────────────────────
# CORS Configuration
# Izinkan React frontend (dev & prod) mengakses API
# ───────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ganti ke domain spesifik saat production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ───────────────────────────────────────────
# API Routers v1
# ───────────────────────────────────────────
app.include_router(auth.router,         prefix="/api/v1/auth",         tags=["🔐 Auth"])
app.include_router(balita.router,       prefix="/api/v1/balita",       tags=["👶 Balita"])
app.include_router(antropometri.router, prefix="/api/v1/antropometri", tags=["⚖️ Antropometri"])
app.include_router(intervensi.router,   prefix="/api/v1/intervensi",   tags=["🤖 Intervensi AI"])
app.include_router(laporan.router,      prefix="/api/v1/laporan",      tags=["📊 Laporan"])


@app.get("/", tags=["Root"])
def read_root():
    return {
        "message": "Selamat datang di be-tumbang.id API",
        "docs": "/docs",
        "version": "1.0.0"
    }
