from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.routers import hello, search

app = FastAPI(
    title="FastAPI Server",
    description="A FastAPI server for Vercel deployment",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(hello.router, tags=["hello"])
app.include_router(search.router, tags=["search"])