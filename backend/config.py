import os
import secrets
from pathlib import Path

NUM_VARIANTS = 1
NUM_VARIANTS_VIDEO = 2

# LLM-related
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", None)
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", None)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", None)
OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL", None)

# LiteLLM (optional - routes to 100+ models via a unified interface)
LITELLM_MODEL = os.environ.get("LITELLM_MODEL", None)
LITELLM_API_KEY = os.environ.get("LITELLM_API_KEY", None)
LITELLM_API_BASE = os.environ.get("LITELLM_API_BASE", None)

# Image generation (optional)
REPLICATE_API_KEY = os.environ.get("REPLICATE_API_KEY", None)

# Debugging-related
IS_DEBUG_ENABLED = bool(os.environ.get("IS_DEBUG_ENABLED", True))
DEBUG_DIR = os.environ.get("DEBUG_DIR", "")

# Set to True when running in production (on the hosted version)
# Used as a feature flag to enable or disable certain features
IS_PROD = os.environ.get("IS_PROD", False)

# Deployment configuration
DEPLOY_DIR = os.environ.get("DEPLOY_DIR", str(Path(__file__).parent / "deployed"))
DEFAULT_DEPLOY_BASE_URL = "http://localhost:7001"
DEPLOY_BASE_URL = os.environ.get("DEPLOY_BASE_URL", DEFAULT_DEPLOY_BASE_URL)

# Third-party API configuration
DEFAULT_THIRD_URL = "https://store-cms.pilotglo.com/store/strategy/addAndOnline"
THIRD_PARTY_API_URL = os.environ.get("THIRD_PARTY_API_URL", DEFAULT_THIRD_URL)
THIRD_PARTY_API_AUTH = os.environ.get("THIRD_PARTY_API_AUTH", None)
THIRD_PARTY_CONDITION_CONTENT = os.environ.get("THIRD_PARTY_CONDITION_CONTENT", None)
THIRD_PARTY_CONTENT = os.environ.get("THIRD_PARTY_CONTENT", None)

# Authentication configuration
AUTH_PASSWORD = os.environ.get("AUTH_PASSWORD", "admin1234")
# Generate a random token if not provided
_auth_token_env = os.environ.get("AUTH_TOKEN", None)
if _auth_token_env:
    AUTH_TOKEN = _auth_token_env
else:
    # Generate a secure random token
    AUTH_TOKEN = secrets.token_urlsafe(32)
    print(f"Generated random auth token (set AUTH_TOKEN env var to use a fixed token): {AUTH_TOKEN}")