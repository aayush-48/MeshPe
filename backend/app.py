from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes.enrollment_routes import router as enroll_router
from backend.routes.auth_routes import router as auth_router
from backend.routes.stt_routes import router as stt_router
from backend.routes.payment_routes import router as pay_router
from backend.routes.encryption_routes import router as enc_router

app = FastAPI(title="VoiceWave MeshPay Backend")

# Allow frontend (Vite dev server) to talk to backend, including OPTIONS preflight
app.add_middleware(
    CORSMiddleware,
    # During development, allow all origins so Vite dev server/previews work reliably.
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(enroll_router, prefix="/enroll", tags=["enrollment"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(stt_router, prefix="/stt", tags=["stt"])
app.include_router(pay_router, prefix="/payment", tags=["payment"])
app.include_router(enc_router, prefix="/encrypt", tags=["encrypt"])
