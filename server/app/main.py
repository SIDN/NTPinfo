from typing import Union
from fastapi import FastAPI, Request, Response
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from server.app.api.routing import router
from server.app.rate_limiter import limiter
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

app = FastAPI()
app.state.limiter = limiter
app.include_router(router)

"""
Creates a FastAPI application instance.
This instance is used to define all API endpoints and serve the application.
"""

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> Union[JSONResponse, Response]:
    """
    Handle requests that exceed the configured rate limit.

    Args:
       request (Request): The incoming HTTP request that triggered the exception.
       exc (RateLimitExceeded): The exception raised due to rate limiting.

    Returns:
       Union[JSONResponse, Response]: A response with HTTP 429 Too Many Requests.
    """
    return _rate_limit_exceeded_handler(request, exc)


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handle generic HTTPException errors and return a custom error structure.

    Overrides FastAPI's default error response by returning an object with an "error" key
    instead of the default "detail" key for better frontend compatibility or customization.

    Args:
        request (Request): The incoming HTTP request that caused the error.
        exc (HTTPException): The raised HTTPException.

    Returns:
        JSONResponse: A response with the appropriate status code and custom error format.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", reload=True)
