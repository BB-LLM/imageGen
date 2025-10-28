# Soul MVP - AI Character Image Generation System

FastAPI-based AI image generation system with intelligent deduplication and user-specific variant delivery.

## 📁 Project Structure

```
soul/
├── app/
│   ├── api/              # API routes
│   │   ├── routes_image.py      # Image generation endpoints
│   │   ├── routes_tasks.py      # Task management endpoints
│   │   ├── routes_style.py      # Style-specific endpoints
│   │   └── routes_static.py     # Static file serving
│   ├── core/
│   │   ├── task_manager.py      # Background task manager with queue
│   │   ├── locks.py             # In-process locking
│   │   ├── ids.py               # ULID generation
│   │   ├── lww.py               # Last Write Wins semantics
│   │   └── idem.py              # Idempotency helpers
│   ├── data/
│   │   ├── models.py            # Pydantic schemas
│   │   └── dal.py               # Data access layer
│   ├── logic/
│   │   ├── service_image.py     # Core image service
│   │   ├── prompt_cache.py      # Prompt normalization and caching
│   │   ├── place_chooser.py    # Selfie location selection
│   │   └── ai_model_service.py # AI model wrapper
│   ├── config.py                # Configuration management
│   └── test/                    # Test suite
├── static/                      # Frontend files
│   ├── index.html
│   ├── script.js
│   └── style.css
├── main.py                      # FastAPI application entry
├── init_db.py                   # Database initialization
├── start_server.py              # Server startup script
└── requirements.txt             # Python dependencies
```


## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone <your-gitlab-url>
cd soul
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: If you need GPU support, install the CUDA-enabled version of PyTorch:
```bash
pip install torch==2.9.0+cu128 torchvision==0.24.0+cu128 --index-url https://download.pytorch.org/whl/cu128
```

### 4. Set Up PostgreSQL Database

**Option A: Using Docker (Recommended)**

```bash
docker run -d \
  --name soul-mvp \
  -e POSTGRES_USER=mvpdbuser \
  -e POSTGRES_PASSWORD=mvpdbpw \
  -e POSTGRES_DB=mvpdb \
  -p 5432:5432 \
  postgres:15.14-alpine3.21
```

**Option B: Local PostgreSQL**

Create a database:
```sql
CREATE DATABASE mvpdb;
CREATE USER mvpdbuser WITH PASSWORD 'mvpdbpw';
GRANT ALL PRIVILEGES ON DATABASE mvpdb TO mvpdbuser;
```

### 5. Configure Environment Variables

Create a `.env` file in the project root:

```env
# Database
DATABASE_URL=postgresql://mvpdbuser:mvpdbpw@localhost:5432/mvpdb

# Google Cloud Storage (Optional)
GCS_BUCKET_NAME=artifacts-dev-soulmedia
GCS_PROJECT_ID=your-project-id

# GPU Settings (Optional)
FORCE_CPU=false
DEVICE_MEMORY_FRACTION=0.8

# Task Queue Settings
MAX_CONCURRENT_TASKS=1
LOG_LEVEL=INFO
```

### 6. Initialize Database

```bash
python init_db.py
```

This will create all necessary tables in the database.

### 7. Download AI Model

Place your Stable Diffusion XL model in `app/model/` directory:
```bash
# Example: Download from Civitai https://civitai.com/models/101055/sd-xl
# Place sdXL_v10VAEFix.safetensors in app/model/
```

**Note**: If no model is provided, the system will run in simulation mode.

## 🚀 Running the Server

### Development Mode

```bash
python main.py
```

or

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
python start_server.py
```

Access the application:
- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🧪 Running Tests

```bash
# Run all tests
python -m pytest app/test/

# Run specific test file
python -m pytest app/test/test_database.py -v

# Run with coverage
python -m pytest app/test/ --cov=app
```

## 📝 Configuration Options

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://mvpdbuser:mvpdbpw@localhost:5432/mvpdb` | Database connection string |
| `FORCE_CPU` | `false` | Force CPU-only mode |
| `DEVICE_MEMORY_FRACTION` | `0.8` | GPU memory fraction to use |
| `MAX_CONCURRENT_TASKS` | `1` | Maximum concurrent image generation tasks |
| `LOG_LEVEL` | `INFO` | Logging level |

### API Endpoints

- `POST /api/image/generate` - Generate a styled image
- `POST /api/image/selfie` - Generate a selfie
- `GET /api/tasks/{task_id}` - Get task status
- `POST /api/tasks/{task_id}/cancel` - Cancel a task
- `GET /api/image/variant/{variant_id}/mark-seen` - Mark variant as seen
- `GET /health` - Health check

