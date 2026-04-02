# deepsentrix

AI-powered deepfake detection and pixel protection platform.

---

## Features

- **Deepfake Detection** – Upload any image and get an AI-driven confidence score indicating whether it is authentic or manipulated.
- **Pixel Protection** – Detected deepfakes are automatically obfuscated using pixelation, Gaussian blur, noise injection, or a combination.
- **Results History** – Every analysis is stored locally (SQLite) and surfaced in the dashboard.
- **REST API** – Clean FastAPI endpoints with interactive Swagger docs at `/docs`.

---

## Project Structure

```
deepsentrix/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application entry-point
│   │   ├── config.py            # Pydantic settings
│   │   ├── models/
│   │   │   ├── detection.py     # Deepfake detection model
│   │   │   └── protection.py    # Pixel protection algorithms
│   │   ├── routes/
│   │   │   └── api.py           # /api/* endpoints
│   │   └── utils/
│   │       ├── image_processing.py
│   │       └── deepfake_detector.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── public/index.html
│   ├── src/
│   │   ├── components/
│   │   │   ├── ImageUpload.tsx
│   │   │   ├── AnalysisResults.tsx
│   │   │   └── Dashboard.tsx
│   │   ├── pages/Home.tsx
│   │   ├── services/api.ts
│   │   ├── styles/globals.css
│   │   ├── App.tsx
│   │   └── index.tsx
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   ├── Dockerfile
│   └── .env.example
├── docker-compose.yml
├── .gitignore
└── README.md
```

---

## Quick Start

### Using Docker Compose (recommended)

```bash
# Clone the repository
git clone https://github.com/Sofiya-06/deepsentrix.git
cd deepsentrix

# Start backend + frontend
docker-compose up --build

# Open in browser
# Frontend:  http://localhost:3000
# API docs:  http://localhost:8000/docs
```

### Manual setup

**Backend**

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

**Frontend**

```bash
cd frontend
npm install
cp .env.example .env
npm start                         # opens http://localhost:3000
```

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/analyze` | Detect deepfakes in an uploaded image |
| `POST` | `/api/protect` | Apply pixel protection to any image |
| `GET`  | `/api/results/{id}` | Retrieve a stored result by ID |
| `GET`  | `/api/results` | List recent analysis results |
| `GET`  | `/docs` | Interactive Swagger UI |

### Example – analyse an image with `curl`

```bash
curl -X POST http://localhost:8000/api/analyze \
  -F "file=@photo.jpg" \
  -F "protection_technique=pixelate" \
  -F "protection_level=medium"
```

---

## Configuration

Copy the provided example files and adjust as needed:

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

Key backend variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `DEBUG` | `false` | Enable debug logging |
| `UPLOAD_DIR` | `uploads` | Directory for uploaded files |
| `RESULTS_DB` | `deepsentrix.db` | SQLite database path |
| `DETECTION_MODEL_PATH` | *(empty)* | Path to a trained `.h5` model; leave empty to use the built-in heuristic analyser |
| `ALLOWED_ORIGINS` | `http://localhost:3000` | CORS-allowed origins |

---

## Detection Modes

| Mode | When used | Description |
|------|-----------|-------------|
| **Neural network** | When `DETECTION_MODEL_PATH` points to a valid Keras model | Runs inference through a ResNet50-based classifier |
| **Heuristic** | Default (no model file) | Uses noise and colour-channel statistics – good for demos without downloading model weights |

---

## Technologies

- **Backend** – Python 3.11, FastAPI, Pillow, OpenCV, NumPy, TensorFlow (optional), SQLite
- **Frontend** – React 18, TypeScript, Tailwind CSS, Axios
- **Infrastructure** – Docker, Docker Compose, Nginx

---

## License

MIT
