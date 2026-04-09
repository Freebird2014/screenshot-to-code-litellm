# Load environment variables first
from dotenv import load_dotenv

load_dotenv()


from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from config import IS_DEBUG_ENABLED
from routes import screenshot, generate_code, home, evals, deploy
from auth import router as auth_router, verify_token

app = FastAPI(openapi_url=None, docs_url=None, redoc_url=None)


@app.on_event("startup")
async def log_debug_mode() -> None:
    debug_status = "ENABLED" if IS_DEBUG_ENABLED else "DISABLED"
    print(f"Backend startup complete. Debug mode is {debug_status}.")

# Configure CORS settings
# Note: For WebSocket support, we need to allow all origins
# allow_credentials=True cannot be used with allow_origins=["*"]
# so we use a custom allow_origin_regex to match all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,  # Must be False when using wildcard origins
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add routes
# Auth route (public)
app.include_router(auth_router)

# Protected HTTP routes (WebSocket routes handle auth internally)
app.include_router(screenshot.router, dependencies=[Depends(verify_token)])
app.include_router(home.router, dependencies=[Depends(verify_token)])
app.include_router(evals.router, dependencies=[Depends(verify_token)])

# WebSocket routes handle auth internally via query parameter
app.include_router(generate_code.router)

# Deploy routes (/api/deploy is protected, others are public)
app.include_router(deploy.router)
