import httpx
from typing import Optional, Dict, Any, Literal, Union
from altscore.common.http_errors import raise_for_status_improved, retry_on_401, retry_on_401_async
from altscore.borrower_central.helpers import build_headers


HttpMethod = Literal["GET", "POST", "PUT", "PATCH", "DELETE"]


class APIRequestSyncModule:
    """
    A module for making custom API requests to the Borrower Central API
    with automatic authentication headers.
    
    Example usage:
        # GET request with query params
        response = altscore.borrower_central.api.get(
            "/v1/borrowers",
            params={"page": 1, "per-page": 10}
        )
        
        # POST request with JSON body
        response = altscore.borrower_central.api.post(
            "/v1/borrowers",
            json={"persona": "individual", "label": "Test"}
        )
        
        # Generic request with any method
        response = altscore.borrower_central.api.request(
            method="PATCH",
            path="/v1/borrowers/123",
            json={"label": "Updated"}
        )
    """

    def __init__(self, altscore_client):
        self.altscore_client = altscore_client

    def renew_token(self):
        self.altscore_client.renew_token()

    def build_headers(self, extra_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Build headers with auth + any extra headers provided."""
        headers = build_headers(self)
        if extra_headers:
            headers.update(extra_headers)
        return headers

    @property
    def base_url(self) -> str:
        return self.altscore_client._borrower_central_base_url

    @retry_on_401
    def request(
        self,
        method: HttpMethod,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Union[Dict[str, Any], list]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 30,
        raise_for_status: bool = True,
    ) -> httpx.Response:
        """
        Make a custom API request to the Borrower Central API.
        
        Args:
            method: HTTP method (GET, POST, PUT, PATCH, DELETE)
            path: API path (e.g., "/v1/borrowers" or "/v1/borrowers/123")
            params: Query parameters
            json: JSON body (will be serialized)
            data: Form data body
            headers: Additional headers to merge with auth headers
            timeout: Request timeout in seconds (default: 30)
            raise_for_status: Whether to raise an exception on non-2xx responses (default: True)
            
        Returns:
            httpx.Response object
        """
        # Ensure path starts with /
        if not path.startswith("/"):
            path = f"/{path}"
        
        url = f"{self.base_url}{path}"
        merged_headers = self.build_headers(headers)
        
        with httpx.Client() as client:
            response = client.request(
                method=method,
                url=url,
                params=params,
                json=json,
                data=data,
                headers=merged_headers,
                timeout=timeout,
            )
            
            if raise_for_status:
                raise_for_status_improved(response)
            
            return response

    def get(
        self,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 30,
        raise_for_status: bool = True,
    ) -> httpx.Response:
        """Make a GET request."""
        return self.request(
            method="GET",
            path=path,
            params=params,
            headers=headers,
            timeout=timeout,
            raise_for_status=raise_for_status,
        )

    def post(
        self,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Union[Dict[str, Any], list]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 30,
        raise_for_status: bool = True,
    ) -> httpx.Response:
        """Make a POST request."""
        return self.request(
            method="POST",
            path=path,
            params=params,
            json=json,
            data=data,
            headers=headers,
            timeout=timeout,
            raise_for_status=raise_for_status,
        )

    def put(
        self,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Union[Dict[str, Any], list]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 30,
        raise_for_status: bool = True,
    ) -> httpx.Response:
        """Make a PUT request."""
        return self.request(
            method="PUT",
            path=path,
            params=params,
            json=json,
            data=data,
            headers=headers,
            timeout=timeout,
            raise_for_status=raise_for_status,
        )

    def patch(
        self,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Union[Dict[str, Any], list]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 30,
        raise_for_status: bool = True,
    ) -> httpx.Response:
        """Make a PATCH request."""
        return self.request(
            method="PATCH",
            path=path,
            params=params,
            json=json,
            data=data,
            headers=headers,
            timeout=timeout,
            raise_for_status=raise_for_status,
        )

    def delete(
        self,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 30,
        raise_for_status: bool = True,
    ) -> httpx.Response:
        """Make a DELETE request."""
        return self.request(
            method="DELETE",
            path=path,
            params=params,
            headers=headers,
            timeout=timeout,
            raise_for_status=raise_for_status,
        )


class APIRequestAsyncModule:
    """
    Async module for making custom API requests to the Borrower Central API
    with automatic authentication headers.
    
    Example usage:
        # GET request with query params
        response = await altscore.borrower_central.api.get(
            "/v1/borrowers",
            params={"page": 1, "per-page": 10}
        )
        
        # POST request with JSON body
        response = await altscore.borrower_central.api.post(
            "/v1/borrowers",
            json={"persona": "individual", "label": "Test"}
        )
        
        # Generic request with any method
        response = await altscore.borrower_central.api.request(
            method="PATCH",
            path="/v1/borrowers/123",
            json={"label": "Updated"}
        )
    """

    def __init__(self, altscore_client):
        self.altscore_client = altscore_client

    def renew_token(self):
        self.altscore_client.renew_token()

    def build_headers(self, extra_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Build headers with auth + any extra headers provided."""
        headers = build_headers(self)
        if extra_headers:
            headers.update(extra_headers)
        return headers

    @property
    def base_url(self) -> str:
        return self.altscore_client._borrower_central_base_url

    @retry_on_401_async
    async def request(
        self,
        method: HttpMethod,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Union[Dict[str, Any], list]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 30,
        raise_for_status: bool = True,
    ) -> httpx.Response:
        """
        Make a custom async API request to the Borrower Central API.
        
        Args:
            method: HTTP method (GET, POST, PUT, PATCH, DELETE)
            path: API path (e.g., "/v1/borrowers" or "/v1/borrowers/123")
            params: Query parameters
            json: JSON body (will be serialized)
            data: Form data body
            headers: Additional headers to merge with auth headers
            timeout: Request timeout in seconds (default: 30)
            raise_for_status: Whether to raise an exception on non-2xx responses (default: True)
            
        Returns:
            httpx.Response object
        """
        # Ensure path starts with /
        if not path.startswith("/"):
            path = f"/{path}"
        
        url = f"{self.base_url}{path}"
        merged_headers = self.build_headers(headers)
        
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method,
                url=url,
                params=params,
                json=json,
                data=data,
                headers=merged_headers,
                timeout=timeout,
            )
            
            if raise_for_status:
                raise_for_status_improved(response)
            
            return response

    async def get(
        self,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 30,
        raise_for_status: bool = True,
    ) -> httpx.Response:
        """Make an async GET request."""
        return await self.request(
            method="GET",
            path=path,
            params=params,
            headers=headers,
            timeout=timeout,
            raise_for_status=raise_for_status,
        )

    async def post(
        self,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Union[Dict[str, Any], list]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 30,
        raise_for_status: bool = True,
    ) -> httpx.Response:
        """Make an async POST request."""
        return await self.request(
            method="POST",
            path=path,
            params=params,
            json=json,
            data=data,
            headers=headers,
            timeout=timeout,
            raise_for_status=raise_for_status,
        )

    async def put(
        self,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Union[Dict[str, Any], list]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 30,
        raise_for_status: bool = True,
    ) -> httpx.Response:
        """Make an async PUT request."""
        return await self.request(
            method="PUT",
            path=path,
            params=params,
            json=json,
            data=data,
            headers=headers,
            timeout=timeout,
            raise_for_status=raise_for_status,
        )

    async def patch(
        self,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Union[Dict[str, Any], list]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 30,
        raise_for_status: bool = True,
    ) -> httpx.Response:
        """Make an async PATCH request."""
        return await self.request(
            method="PATCH",
            path=path,
            params=params,
            json=json,
            data=data,
            headers=headers,
            timeout=timeout,
            raise_for_status=raise_for_status,
        )

    async def delete(
        self,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 30,
        raise_for_status: bool = True,
    ) -> httpx.Response:
        """Make an async DELETE request."""
        return await self.request(
            method="DELETE",
            path=path,
            params=params,
            headers=headers,
            timeout=timeout,
            raise_for_status=raise_for_status,
        )
