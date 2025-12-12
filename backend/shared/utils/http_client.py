import httpx
from typing import Optional, Dict, Any
from fastapi import HTTPException


class HTTPClient:
    """Async HTTP client wrapper for making external API calls"""

    def __init__(self, base_url: str, headers: Optional[Dict[str, str]] = None):
        self.base_url = base_url
        self.headers = headers or {}

    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make GET request"""
        url = f"{self.base_url}{endpoint}"
        request_headers = {**self.headers, **(headers or {})}

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    url, params=params, headers=request_headers, timeout=30.0
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                raise HTTPException(
                    status_code=e.response.status_code,
                    detail=f"External API error: {e.response.text}",
                )
            except httpx.RequestError as e:
                raise HTTPException(
                    status_code=503, detail=f"Service unavailable: {str(e)}"
                )

    async def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make POST request"""
        url = f"{self.base_url}{endpoint}"
        request_headers = {**self.headers, **(headers or {})}

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url,
                    data=data,
                    json=json,
                    headers=request_headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                raise HTTPException(
                    status_code=e.response.status_code,
                    detail=f"External API error: {e.response.text}",
                )
            except httpx.RequestError as e:
                raise HTTPException(
                    status_code=503, detail=f"Service unavailable: {str(e)}"
                )
