from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.config import get_settings

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI): 
    print(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    yield
    print(f"Shutting down {settings.APP_NAME}")


app = FastAPI(
    title=settings.APP_NAME, 
    version=settings.APP_VERSION, 
    debug=settings.APP_DEBUG, 
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware, 
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router)

@app.get("/health")
async def health_check(): 
    return {
        "status": "healthy", 
        "app": settings.APP_NAME, 
        "version": settings.APP_VERSION
    }

if __name__ == "__main__": 
    import uvicorn
    uvicorn.run(
        "main:app", 
        host=settings.APP_HOST, 
        port=settings.APP_PORT,
        reload=settings.APP_DEBUG
    )
