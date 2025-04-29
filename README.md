# FastAPI Server for Vercel

A high-performance FastAPI server template designed for deployment on Vercel.

## Features

- FastAPI with automatic OpenAPI documentation
- Pydantic for data validation
- Poetry for dependency management
- Vercel deployment configuration
- CORS middleware enabled

## Getting Started

### Installation

```bash
# Install dependencies
poetry install

# Run development server
poetry run uvicorn app.main:app --reload
```

### API Routes

- `/` - Root endpoint
- `/hello` - Hello world example
- `/docs` - OpenAPI documentation