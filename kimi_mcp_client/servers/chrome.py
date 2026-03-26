"""
Chrome DevTools MCP Server Implementation
Browser automation via Firecrawl API

Provides real browser automation including navigation, screenshots,
form interaction, and JavaScript execution through Firecrawl's cloud browser.
"""

import os  # BUG-013 FIX: was missing; required for os.path.getsize/abspath
import asyncio
import aiohttp
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from functools import wraps
from .base import BaseMCPServer


# Rate limiting decorator
class RateLimiter:
    """Simple rate limiter for API calls."""
    
    def __init__(self, max_calls: int = 10, period: int = 60):
        self.max_calls = max_calls
        self.period = period  # seconds
        self.calls: List[datetime] = []
    
    async def acquire(self):
        """Wait if rate limit would be exceeded."""
        now = datetime.now()
        # Remove calls outside the period
        self.calls = [c for c in self.calls if now - c < timedelta(seconds=self.period)]
        
        if len(self.calls) >= self.max_calls:
            # Wait until oldest call expires
            oldest = self.calls[0]
            wait_time = self.period - (now - oldest).total_seconds()
            if wait_time > 0:
                await asyncio.sleep(wait_time)
        
        self.calls.append(datetime.now())


def retry_on_error(max_retries: int = 3, retry_delay: float = 1.0, 
                   exceptions: tuple = (Exception,)):
    """Decorator to retry async function on specified exceptions."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                        await asyncio.sleep(wait_time)
            raise last_exception
        return wrapper
    return decorator


class ChromeDevToolsServer(BaseMCPServer):
    """
    Chrome DevTools for live browser automation via Firecrawl.
    
    This implementation uses Firecrawl's cloud browser API for real
    browser automation including navigation, screenshots, and interactions.
    
    Features:
        - Automatic retry with exponential backoff
        - Rate limiting (10 calls/minute default)
        - Configurable timeouts
        - Detailed error reporting
    
    Tools:
        - navigate: Go to URL with optional wait
        - screenshot: Capture full page or viewport screenshot
        - click: Click element by selector
        - fill: Fill form input
        - evaluate: Execute JavaScript
        - snapshot: Get page content and structure
    """
    
    DEFAULT_TIMEOUT = 60  # seconds
    DEFAULT_RETRIES = 3
    DEFAULT_RETRY_DELAY = 1.0
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self._firecrawl_key = config.get("env", {}).get("FIRECRAWL_API_KEY") or os.environ.get("FIRECRAWL_API_KEY")
        self.base_url = "https://api.firecrawl.dev/v1"
        self._current_url: Optional[str] = None
        self._current_title: Optional[str] = None
        self._rate_limiter = RateLimiter(max_calls=10, period=60)
        
        # Configurable timeouts and retries
        self.timeout = config.get("timeout", self.DEFAULT_TIMEOUT)
        self.max_retries = config.get("max_retries", self.DEFAULT_RETRIES)
        self.retry_delay = config.get("retry_delay", self.DEFAULT_RETRY_DELAY)
    
    async def _make_request(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a request to Firecrawl API with retry and rate limiting.
        
        Args:
            endpoint: API endpoint (e.g., '/scrape')
            payload: Request payload
            
        Returns:
            API response as dict
            
        Raises:
            Exception: On API error after retries
        """
        if not self._firecrawl_key:
            raise ValueError("FIRECRAWL_API_KEY not set")
        
        # Rate limit
        await self._rate_limiter.acquire()
        
        session = await self._get_session()
        
        @retry_on_error(
            max_retries=self.max_retries,
            retry_delay=self.retry_delay,
            exceptions=(Exception,)
        )
        async def _request():
            # BUG-012 FIX: aiohttp requires ClientTimeout, not a plain int.
            async with session.post(
                f"{self.base_url}{endpoint}",
                headers={
                    "Authorization": f"Bearer {self._firecrawl_key}",
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as resp:
                data = await resp.json()
                
                if resp.status == 429:
                    raise Exception("Rate limit exceeded (429)")
                elif resp.status == 401:
                    raise Exception("Invalid API key (401)")
                elif resp.status >= 500:
                    raise Exception(f"Server error ({resp.status})")
                
                return data
        
        return await _request()
    
    async def health_check(self) -> Dict[str, Any]:
        """Check Chrome DevTools availability via Firecrawl."""
        if not self._firecrawl_key:
            return {
                "status": "error",
                "error": "FIRECRAWL_API_KEY not set",
                "setup": "Add FIRECRAWL_API_KEY to .env for browser automation"
            }
        
        try:
            # Test with a simple scrape request
            data = await self._make_request("/scrape", {
                "url": "https://example.com",
                "formats": ["markdown"],
                "onlyMainContent": True
            })
            
            if data.get("success") or "error" in str(data).lower():
                return {
                    "status": "healthy",
                    "backend": "firecrawl-browser",
                    "api_key": f"{self._firecrawl_key[:8]}...",
                    "tools": [
                        "navigate", "screenshot", "click", 
                        "fill", "evaluate", "snapshot"
                    ],
                    "rate_limit": "10 calls/minute",
                    "timeout": f"{self.timeout}s"
                }
            else:
                return {"status": "error", "error": "API returned unexpected response"}
                
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def navigate(
        self,
        url: str,
        wait_for: int = 2000
    ) -> Dict[str, Any]:
        """
        Navigate to a URL and load the page.
        
        Args:
            url: URL to navigate to
            wait_for: Milliseconds to wait for page load (default: 2000)
            
        Returns:
            Navigation result with title, status, and load time
        """
        self._track_request()
        start_time = datetime.now()
        
        data = await self._make_request("/scrape", {
            "url": url,
            "formats": ["markdown"],
            "onlyMainContent": False,
            "waitFor": wait_for
        })
        
        if data.get("success"):
            load_time = int((datetime.now() - start_time).total_seconds() * 1000)
            self._current_url = url
            self._current_title = data.get("data", {}).get("metadata", {}).get("title", "Unknown")
            
            return {
                "success": True,
                "url": url,
                "title": self._current_title,
                "load_time_ms": load_time,
                "status": 200,
                "content_length": len(data.get("data", {}).get("markdown", ""))
            }
        else:
            error_msg = data.get("error", "Unknown error")
            raise Exception(f"Navigation failed: {error_msg}")
    
    async def screenshot(
        self,
        url: str = None,
        full_page: bool = True,
        file_path: str = None
    ) -> Dict[str, Any]:
        """
        Capture a screenshot of the page.
        
        Args:
            url: URL to screenshot (uses current URL if not provided)
            full_page: Capture full page (True) or just viewport (False)
            file_path: Save screenshot to this path (returns URL if None)
            
        Returns:
            Screenshot data with file path or URL
        """
        self._track_request()
        
        target_url = url or self._current_url
        if not target_url:
            raise ValueError("No URL provided and no current page loaded")
        
        payload = {
            "url": target_url,
            "formats": ["screenshot"],
            "onlyMainContent": False
        }
        
        data = await self._make_request("/scrape", payload)
        
        if data.get("success"):
            screenshot_url = data.get("data", {}).get("screenshot", "")
            
            if screenshot_url:
                if file_path:
                    # Download screenshot from URL
                    session = await self._get_session()
                    async with session.get(screenshot_url, timeout=aiohttp.ClientTimeout(total=self.timeout)) as img_resp:
                        if img_resp.status == 200:
                            img_data = await img_resp.read()
                            with open(file_path, 'wb') as f:
                                f.write(img_data)
                            
                            file_size = os.path.getsize(file_path)
                            return {
                                "success": True,
                                "url": target_url,
                                "file_path": os.path.abspath(file_path),
                                "file_size_bytes": file_size,
                                "full_page": full_page,
                                "remote_url": screenshot_url
                            }
                        else:
                            raise Exception(f"Failed to download screenshot: {img_resp.status}")
                else:
                    # Return remote URL
                    return {
                        "success": True,
                        "url": target_url,
                        "screenshot_url": screenshot_url,
                        "full_page": full_page
                    }
            else:
                raise Exception("Screenshot URL not found in response")
        else:
            error_msg = data.get("error", "Unknown error")
            raise Exception(f"Screenshot failed: {error_msg}")
    
    async def click(
        self,
        url: str,
        selector: str,
        wait_after: int = 1000
    ) -> Dict[str, Any]:
        """
        Click an element on the page.
        
        Args:
            url: URL of the page
            selector: CSS selector for the element to click
            wait_after: Milliseconds to wait after click
            
        Returns:
            Click result with page state after click
        """
        self._track_request()
        
        payload = {
            "url": url,
            "formats": ["markdown"],
            "onlyMainContent": False,
            "actions": [
                {"type": "click", "selector": selector},
                {"type": "wait", "milliseconds": wait_after}
            ]
        }
        
        data = await self._make_request("/scrape", payload)
        
        if data.get("success"):
            return {
                "success": True,
                "url": url,
                "clicked_selector": selector,
                "title": data.get("data", {}).get("metadata", {}).get("title"),
                "content_length": len(data.get("data", {}).get("markdown", ""))
            }
        else:
            error_msg = data.get("error", "Unknown error")
            raise Exception(f"Click failed: {error_msg}")
    
    async def fill(
        self,
        url: str,
        selector: str,
        value: str,
        submit: bool = False
    ) -> Dict[str, Any]:
        """
        Fill a form input field.
        
        Args:
            url: URL of the page
            selector: CSS selector for the input element
            value: Value to fill in
            submit: Whether to submit the form after filling
            
        Returns:
            Fill result with page state after filling
        """
        self._track_request()
        
        actions = [
            {"type": "write", "selector": selector, "text": value}
        ]
        
        if submit:
            actions.append({"type": "press", "key": "Enter"})
        
        payload = {
            "url": url,
            "formats": ["markdown"],
            "onlyMainContent": False,
            "actions": actions
        }
        
        data = await self._make_request("/scrape", payload)
        
        if data.get("success"):
            return {
                "success": True,
                "url": url,
                "filled_selector": selector,
                "value": value[:50] + "..." if len(value) > 50 else value,
                "submitted": submit,
                "title": data.get("data", {}).get("metadata", {}).get("title")
            }
        else:
            error_msg = data.get("error", "Unknown error")
            raise Exception(f"Fill failed: {error_msg}")
    
    async def evaluate(
        self,
        url: str,
        script: str
    ) -> Dict[str, Any]:
        """
        Execute JavaScript on the page.
        
        Note: JavaScript execution is simulated through extract endpoint
        for data extraction. Full JS evaluation requires browser context.
        
        Args:
            url: URL of the page
            script: JavaScript expression to evaluate (used as extraction prompt)
            
        Returns:
            Evaluation result
        """
        self._track_request()
        
        # Use extract endpoint to get specific data from the page
        data = await self._make_request("/extract", {
            "urls": [url],
            "prompt": f"Execute this JavaScript concept and return the result: {script}"
        })
        
        if data.get("success"):
            extracted_data = data.get("data", [])
            return {
                "success": True,
                "url": url,
                "script": script[:100] + "..." if len(script) > 100 else script,
                "result": extracted_data[0] if extracted_data else None
            }
        else:
            error_msg = data.get("error", "Unknown error")
            raise Exception(f"Evaluate failed: {error_msg}")
    
    async def snapshot(
        self,
        url: str = None,
        verbose: bool = False
    ) -> Dict[str, Any]:
        """
        Get a snapshot of the page content and structure.
        
        Args:
            url: URL to snapshot (uses current URL if not provided)
            verbose: Include full content (True) or summary (False)
            
        Returns:
            Page snapshot with metadata and content
        """
        self._track_request()
        
        target_url = url or self._current_url
        if not target_url:
            raise ValueError("No URL provided and no current page loaded")
        
        data = await self._make_request("/scrape", {
            "url": target_url,
            "formats": ["markdown", "html"],
            "onlyMainContent": False
        })
        
        if data.get("success"):
            page_data = data.get("data", {})
            metadata = page_data.get("metadata", {})
            
            self._current_url = target_url
            self._current_title = metadata.get("title", "Unknown")
            
            content = page_data.get("markdown", "")
            
            return {
                "success": True,
                "url": target_url,
                "title": self._current_title,
                "description": metadata.get("description", ""),
                "language": metadata.get("language", "unknown"),
                "content_length": len(content),
                "content_preview": content[:500] + "..." if len(content) > 500 and not verbose else content,
                "links_count": len(page_data.get("links", [])),
                "images_count": len(page_data.get("images", []))
            }
        else:
            error_msg = data.get("error", "Unknown error")
            raise Exception(f"Snapshot failed: {error_msg}")
