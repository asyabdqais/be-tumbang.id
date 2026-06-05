from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base

# Import semua model agar SQLAlchemy tahu tabel yang harus dibuat
import models.user_model        # noqa: F401
import models.balita_model      # noqa: F401
import models.antropometri_model  # noqa: F401
import models.intervensi_model  # noqa: F401

from controllers.auth_controller       import router as auth_router
from controllers.balita_controller     import router as balita_router
from controllers.antropometri_controller import router as antropometri_router
from controllers.intervensi_controller import router as intervensi_router
from controllers.laporan_controller    import router as laporan_router

# Buat semua tabel saat startup
Base.metadata.create_all(bind=engine)

from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse

# Inisialisasi Aplikasi
app = FastAPI(
    title="be-tumbang.id API",
    description="Backend API untuk Sistem Pemantauan Gizi Balita",
    version="1.0.0",
    docs_url=None,
)

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    html_response = get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        swagger_favicon_url="",
    )
    body = html_response.body.decode("utf-8")
    custom_css = "<style>.swagger-ui .topbar { display: none !important; }</style>"
    body = body.replace("</head>", f"{custom_css}</head>")
    return HTMLResponse(body)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # Ganti ke domain spesifik saat production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers (tanpa versioning)
app.include_router(auth_router,          prefix="/api/auth",          tags=["Auth"])
app.include_router(balita_router,        prefix="/api/balita",        tags=["Balita"])
app.include_router(antropometri_router,  prefix="/api/antropometri",  tags=["Antropometri"])
app.include_router(intervensi_router,    prefix="/api/intervensi",    tags=["Intervensi"])
app.include_router(laporan_router,       prefix="/api/laporan",       tags=["Laporan"])


@app.get("/", tags=["Root"])
def read_root():
    return {
        "message": "Selamat datang di be-tumbang.id API",
        "docs":    "/docs",
        "version": "1.0.0"
    }
