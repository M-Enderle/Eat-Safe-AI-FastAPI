# FastAPI Server for Vercel

A high-performance FastAPI server designed for deployment on Vercel, featuring AI-powered food image generation and content safety checks.

## Features

- FastAPI with automatic OpenAPI documentation
- Pydantic for data validation
- Poetry for dependency management
- Vercel deployment configuration
- CORS middleware enabled
- Gemini AI integration for image generation
- Content safety validation
- Vercel Blob storage for image caching

## Getting Started

### Prerequisites

- Python 3.10 or newer
- Poetry package manager
- Gemini API Key

### Environment Setup

Create a `.env` file in the project root with:

```
GEMINI_API_KEY=your_gemini_api_key_here
```

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
- `/search` - Image generation endpoint for food queries
- `/docs` - OpenAPI documentation

## API Documentation

### GET /hello

Returns a simple greeting message.

**Response:**
```json
{
  "message": "Hello, World!"
}
```

### GET /search

Generate a food image based on search query.

**Parameters:**
- `query` (string, required): The food item to generate an image for

**Response:**
```json
{
  "status": "success",
  "imageBase64": "base64_encoded_image_string",
  "name": "food_name",
  "overall_rating": 4.5
}
```

**Error Responses:**
- 400: Unsafe content detected
- 500: Image generation failed

## Project Structure

```
/
├── ai/                   # AI module
│   ├── image_gen.py      # Image generation with Gemini
│   ├── safety.py         # Content safety validation
│   └── utils.py          # Utility functions for AI services
├── app/                  # FastAPI application
│   ├── main.py           # Main application entry point
│   └── routers/          # API route handlers
│       ├── hello.py      # Hello world endpoint
│       └── search.py     # Search endpoint for image generation
├── pyproject.toml        # Poetry configuration
├── requirements.txt      # Generated dependencies
└── vercel.json           # Vercel deployment configuration
```

## Technologies

- FastAPI: Web framework for building APIs
- Pydantic: Data validation and settings management
- Google Gemini: AI service for image generation
- Vercel Blob: Object storage for caching generated images
- Joblib: Memory caching for improved performance
- Poetry: Dependency management
- Uvicorn: ASGI server

## Development

### Code Style

This project uses:
- Black for code formatting
- isort for import sorting
- mypy for type checking

Run formatting and checks:

```bash
# Format code
poetry run black .
poetry run isort .

# Type checking
poetry run mypy .
```

### Testing

```bash
poetry run pytest
```

## Deployment

This project is configured for deployment on Vercel. The `vercel.json` file contains the necessary configuration for deployment.

```bash
# Deploy to Vercel
vercel
```