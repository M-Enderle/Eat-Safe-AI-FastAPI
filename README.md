# FastAPI AI Food Analysis Server

A high-performance FastAPI server for AI-powered food analysis, image generation, and personalized dietary tips. Designed for seamless deployment on Vercel.

---

## 🚀 Features

- **AI-powered dish and ingredient analysis** (Google Gemini)
- **Personalized daily tips** based on user intolerance profiles
- **Photorealistic food image generation** with caching (Vercel Blob)
- **Content safety validation** for all queries
- **Automatic OpenAPI docs** (`/docs`)
- **Modern Python stack**: FastAPI, Pydantic, Poetry
- **CORS enabled** for frontend integration

---

## 🗂️ Project Structure

```
/
├── ai/                   # AI logic and integrations
│   ├── dish_analysis.py      # Dish analysis and rating
│   ├── ingredient_analysis.py# Ingredient analysis and rating
│   ├── image_gen.py          # Food image generation and caching
│   ├── safety.py             # Content safety validation
│   ├── tips_generator.py     # Daily tip generation
│   └── utils.py              # Shared utilities
├── app/                  # FastAPI application
│   ├── main.py               # App entry point, router registration
│   └── routers/              # API endpoints
│       ├── hello.py          # /hello endpoint
│       ├── search.py         # /search endpoint
│       └── tip.py            # /tip endpoint
├── requirements.txt      # Exported dependencies
├── pyproject.toml        # Poetry configuration
├── vercel.json           # Vercel deployment config
└── README.md             # Project documentation
```

---

## 🧑‍💻 API Endpoints

### `GET /hello`
Returns a simple greeting.

**Response:**
```json
{ "message": "Hello, World!" }
```

---

### `POST /search`
Analyze a dish or ingredient, generate an image, and return ratings and tips.

**Request Body:**
```json
{
  "query": "pizza",
  "user_profile": { "intolerances": ["fructose"], "notes": "" }
}
```

**Response (dish):**
```json
{
  "status": "success",
  "imageBase64": "...",
  "name": "pizza",
  "overall_rating": 85.0,
  "text": [ { "keyword": "Tip", "text": "..." } ],
  "ingredients_rating": [ { "ingredient": "cheese", "rating": 90, "explanation": "..." } ],
  "timestamp": "2024-06-01T12:00:00",
  "is_ingredient": false
}
```

**Response (ingredient):**
```json
{
  "status": "success",
  "imageBase64": "...",
  "name": "tomato",
  "overall_rating": 95.0,
  "text": [ { "keyword": "Tip", "text": "..." } ],
  "ingredients_rating": [],
  "timestamp": "2024-06-01T12:00:00",
  "is_ingredient": true
}
```

**Error Responses:**
- 400: Unsafe or invalid food query
- 500: Image generation or analysis failed

---

### `POST /tip`
Get a daily tip based on the user's intolerance profile.

**Request Body:**
```json
{
  "user_profile": { "intolerances": ["fructose"], "notes": "" }
}
```

**Response:**
```json
{ "tip": "..." }
```

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.10+
- [Poetry](https://python-poetry.org/docs/#installation)
- Google Gemini API Key

### Environment Variables
Create a `.env` file in the project root:
```
GEMINI_API_KEY=your_gemini_api_key_here
```

### Install & Run
```bash
# Install dependencies
poetry install

# Run the development server
poetry run uvicorn app.main:app --reload
```

---

## 🧪 Development

### Code Style & Linting
- **Black**: `poetry run black .`
- **isort**: `poetry run isort .`
- **mypy**: `poetry run mypy .`

### Testing
- **pytest**: `poetry run pytest`

---

## ☁️ Deployment (Vercel)

This project is ready for [Vercel](https://vercel.com/) deployment. The `vercel.json` configures Python builds and routes.

```bash
vercel
```

---

## 🛠️ Technologies Used
- **FastAPI**: API framework
- **Pydantic**: Data validation
- **Google Gemini**: AI for analysis & image generation
- **Vercel Blob**: Image caching
- **Joblib**: Local caching
- **Poetry**: Dependency management
- **Uvicorn**: ASGI server
- **Pillow**: Image processing
- **Rich**: CLI output

---

## 📄 License
MIT (or specify your license)

## 👤 Contact
Your Name — your.email@example.com