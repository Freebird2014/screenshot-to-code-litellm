"""Authentication module for simple token-based auth."""

from fastapi import APIRouter, Depends, HTTPException, WebSocket, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from config import AUTH_TOKEN, AUTH_PASSWORD

router = APIRouter()
security = HTTPBearer()


class LoginRequest(BaseModel):
    """Request model for login."""
    password: str


class LoginResponse(BaseModel):
    """Response model for successful login."""
    token: str


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Verify the Bearer token from the Authorization header.

    Args:
        credentials: The HTTP Authorization credentials

    Returns:
        The token string if valid

    Raises:
        HTTPException: If the token is invalid or missing
    """
    token = credentials.credentials
    if token != AUTH_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token


async def verify_websocket_token(websocket: WebSocket) -> str:
    """Verify token from WebSocket query parameter.

    Args:
        websocket: The WebSocket connection

    Returns:
        The token string if valid

    Raises:
        WebSocketDisconnect: If the token is invalid
    """
    token = websocket.query_params.get("token")
    if not token or token != AUTH_TOKEN:
        await websocket.close(code=4001, reason="Invalid or missing token")
        raise ValueError("Invalid or missing token")
    return token


@router.post("/api/login", response_model=LoginResponse)
async def login(request: LoginRequest) -> LoginResponse:
    """Authenticate with password and receive a token.

    Args:
        request: The login request containing the password

    Returns:
        LoginResponse containing the auth token

    Raises:
        HTTPException: If the password is incorrect
    """
    if request.password != AUTH_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password",
        )
    return LoginResponse(token=AUTH_TOKEN)


@router.get("/api/verify-token")
async def verify_token_endpoint(_: str = Depends(verify_token)) -> dict[str, bool]:
    """Verify if the provided token is valid.

    Returns:
        A success response if the token is valid

    Raises:
        HTTPException: If the token is invalid
    """
    return {"valid": True}
