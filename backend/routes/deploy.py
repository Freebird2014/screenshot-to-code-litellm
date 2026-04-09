import os
import secrets
import string
from pathlib import Path
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel, Field
import httpx
from config import DEPLOY_DIR, DEPLOY_BASE_URL, THIRD_PARTY_API_URL, THIRD_PARTY_API_AUTH,THIRD_PARTY_CONDITION_CONTENT,THIRD_PARTY_CONTENT
from auth import verify_token

router = APIRouter()

# Ensure deploy directory exists
os.makedirs(DEPLOY_DIR, exist_ok=True)


async def call_web_strategy(deploy_id: str, url: str) -> None:
    """
    Call the third-party API after successful deployment.
    This runs as a background task and does not block the response.
    """
    payload = {
        "taskName": f"示例1 {deploy_id}",
        "taskType": "web",
        "limitNum": "10",
        "content": {
            "isOpen": 1, "tacticsInterval": 8,
            "webControl": {
                "isOpen": 1,
                "causes": [
                    {
                        "target": "com.android.chrome",
                        "href": f"{url}",
                        "pkg": "com.android.chrome",
                        "interval": 10080
                    }]}
        },
        "conditionGroups":[
            {"type":"IMEI","conditions":[{"compareType":"CONTAIN","content":f"{THIRD_PARTY_CONDITION_CONTENT}"}]}
        ],
    }

    headers = {
        "Content-Type": "application/json"
    }
    if THIRD_PARTY_API_AUTH:
        headers["authorization"] = THIRD_PARTY_API_AUTH

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(THIRD_PARTY_API_URL, headers=headers, json=payload)
            print(f"Third-party API call completed: {response.status_code}")
    except Exception as e:
        # Log error but don't fail the deployment
        print(f"Failed to call third-party API: {e}")


def generate_deploy_id(length: int = 8) -> str:
    """Generate a unique deployment ID using cryptographically secure random."""
    alphabet = string.ascii_lowercase + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


class DeployRequest(BaseModel):
    """Request model for deploying HTML code."""
    code: str = Field(..., description="The HTML code to deploy")
    title: str = Field(default="", description="Optional title for the deployment")


class DeployResponse(BaseModel):
    """Response model for successful deployment."""
    id: str
    url: str


@router.post("/api/deploy", response_model=DeployResponse, dependencies=[Depends(verify_token)])
async def deploy_html(
    request: DeployRequest, background_tasks: BackgroundTasks
) -> DeployResponse:
    """
    Deploy HTML code to the server and return a unique URL.

    The HTML will be saved to a directory with a randomly generated ID
    and can be accessed at /deploy/{id}.
    """
    if not request.code or not request.code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty")

    # Generate unique deployment ID
    deploy_id = generate_deploy_id()

    # Ensure ID is unique
    deploy_path = Path(DEPLOY_DIR) / deploy_id
    while deploy_path.exists():
        deploy_id = generate_deploy_id()
        deploy_path = Path(DEPLOY_DIR) / deploy_id

    # Create deployment directory
    deploy_path.mkdir(parents=True, exist_ok=True)

    # Write HTML file
    index_path = deploy_path / "index.html"
    try:
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(request.code)
    except Exception as e:
        # Clean up on error
        if deploy_path.exists():
            import shutil
            shutil.rmtree(deploy_path)
        raise HTTPException(status_code=500, detail=f"Failed to write deployment: {str(e)}")

    # Construct the URL
    url = f"{DEPLOY_BASE_URL}/deploy/{deploy_id}"

    # Call third-party API in the background (non-blocking)
    background_tasks.add_task(call_web_strategy, deploy_id, url)

    return DeployResponse(id=deploy_id, url=url)


@router.get("/deploy/{deploy_id}", response_class=HTMLResponse)
async def get_deployment(deploy_id: str) -> HTMLResponse:
    """
    Serve a deployed HTML file by its ID.

    Returns the index.html content for the given deployment ID.
    """
    # Validate deploy_id to prevent path traversal
    if not deploy_id or len(deploy_id) > 32:
        raise HTTPException(status_code=400, detail="Invalid deployment ID")

    # Only allow alphanumeric characters
    if not all(c.isalnum() for c in deploy_id):
        raise HTTPException(status_code=400, detail="Invalid deployment ID format")

    deploy_path = Path(DEPLOY_DIR) / deploy_id / "index.html"

    if not deploy_path.exists():
        raise HTTPException(status_code=404, detail="Deployment not found")

    try:
        with open(deploy_path, "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read deployment: {str(e)}")


@router.get("/api/deploy/{deploy_id}/status")
async def get_deployment_status(deploy_id: str) -> dict:
    """
    Check if a deployment exists and return its metadata.
    """
    # Validate deploy_id
    if not deploy_id or len(deploy_id) > 32:
        raise HTTPException(status_code=400, detail="Invalid deployment ID")

    if not all(c.isalnum() for c in deploy_id):
        raise HTTPException(status_code=400, detail="Invalid deployment ID format")

    deploy_path = Path(DEPLOY_DIR) / deploy_id / "index.html"

    if not deploy_path.exists():
        raise HTTPException(status_code=404, detail="Deployment not found")

    # Get file stats
    stat = deploy_path.stat()

    return {
        "id": deploy_id,
        "exists": True,
        "url": f"{DEPLOY_BASE_URL}/deploy/{deploy_id}",
        "size_bytes": stat.st_size,
        "created_at": stat.st_mtime,
    }
