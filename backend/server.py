"""
FastAPI Backend Proxy for LuciferOS
Routes /api/* requests to the Flask backend
Serves the Flask dashboard for all other routes
"""
import os
import httpx
from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="LuciferOS Backend Proxy")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Flask backend URL (internal)
FLASK_BACKEND_URL = "http://127.0.0.1:5000"
FLASK_DASHBOARD_URL = "http://127.0.0.1:3000"


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy_all(request: Request, path: str):
    """Proxy all requests to appropriate Flask service"""
    
    # Determine target URL
    if path.startswith("api/") or path.startswith("_dash/"):
        # API routes go to dashboard (which has the proxy logic)
        target_url = f"{FLASK_DASHBOARD_URL}/{path}"
    elif path in ["", "/"]:
        # Root goes to dashboard
        target_url = f"{FLASK_DASHBOARD_URL}/"
    else:
        # Everything else to dashboard
        target_url = f"{FLASK_DASHBOARD_URL}/{path}"
    
    # Get request body if present
    body = None
    if request.method in ["POST", "PUT", "PATCH"]:
        body = await request.body()
    
    # Forward headers (excluding host)
    headers = dict(request.headers)
    headers.pop("host", None)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body,
                params=dict(request.query_params)
            )
            
            # Return response with same status and headers
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.headers.get("content-type")
            )
        except httpx.ConnectError:
            return JSONResponse(
                {"error": "Dashboard service unavailable", "target": target_url},
                status_code=503
            )
        except Exception as e:
            return JSONResponse(
                {"error": str(e)},
                status_code=500
            )
