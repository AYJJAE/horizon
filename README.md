# 🔭 Horizon — Automated Exoplanet Detection & Characterization Platform

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green.svg)](https://fastapi.tiangolo.com/)
[![React 18](https://img.shields.io/badge/React-18-61DAFB.svg)](https://react.dev/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)](https://docker.com/)

> Automated pipeline for TESS exoplanet transit detection using TLS/BLS algorithms and AI-powered candidate validation.

---

## ✨ Features

| Module | Capability |
|--------|-----------|
| **Data Acquisition** | Search & download from MAST archive via Lightkurve, upload FITS/CSV |
| **Preprocessing** | Sigma-clipping, Savitzky-Golay / Spline / Wotan detrending, gap interpolation, median normalization |
| **Transit Detection** | Transit Least Squares (TLS) + Box Least Squares (BLS) with periodograms |
| **ML Validation** | CNN transit classifier + statistical tests (odd-even, shape, depth stability) + SHAP explainability |
| **Characterization** | Planet radius, semi-major axis, equilibrium temperature, orbital inclination, planet type classification |
| **Visualization** | Interactive Plotly.js: light curves, periodograms, phase-folded transits, detection timelines |
| **Reports** | PDF (ReportLab) + CSV scientific reports, downloadable via API |

---

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Clone & navigate
cd horizon

# Copy environment file
cp .env.example .env

# Start all services (frontend, backend, postgres, redis)
docker-compose up --build
```

- **Frontend**: http://localhost:80
- **Backend API**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs

---

### Option 2: Local Development

**Backend:**
```bash
cd horizon

# Install Python deps (venv recommended)
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r backend/requirements.txt

# Set env (SQLite mode — no PostgreSQL needed)
copy .env.example .env
# Edit .env: set USE_SQLITE=true, USE_REDIS=false

# Run FastAPI
python -m uvicorn backend.main:app --reload --port 8000
```

**Frontend:**
```bash
cd horizon/frontend
npm install
npm run dev       # → http://localhost:5173
```

---

## 📁 Project Structure

```
horizon/
├── backend/
│   ├── api/routes/          # FastAPI endpoints
│   ├── core/                # Config, database, cache, logging
│   ├── preprocessing/       # Outlier removal, detrending, normalization
│   ├── transit_detection/   # TLS & BLS detectors
│   ├── candidate_validation/# ML classifier, statistical tests, FP classifier
│   ├── characterization/    # Planet + stellar parameter estimation
│   ├── visualization/       # Plotly data generators
│   ├── reports/             # PDF (ReportLab) + CSV generation
│   ├── models/              # SQLAlchemy ORM + Pydantic schemas
│   └── main.py              # FastAPI app entry point
├── frontend/
│   └── src/
│       ├── pages/           # Dashboard, Datasets, Preprocessing, Detection,
│       │                    # Validation, Characterization, Visualization, Reports
│       ├── components/      # Sidebar, Navbar, PlotlyChart
│       ├── api/             # Axios API client
│       └── store/           # Zustand global state
├── tests/                   # pytest unit tests
├── docker/                  # Dockerfiles + Nginx config
├── database/migrations/     # SQL initialization
├── docker-compose.yml
└── .env.example
```

---

## 🔬 Pipeline Workflow

```
TIC ID / FITS / CSV
        ↓
  MAST Download / Upload
        ↓
  Preprocessing (Sigma-clip → Savgol → Interpolate → Normalize)
        ↓
  Transit Detection (TLS + BLS periodogram)
        ↓
  Candidate Extraction (period, depth, epoch, SNR, SDE)
        ↓
  Statistical Validation (odd-even, shape, depth stability)
        ↓
  ML Classification (CNN → confidence score + SHAP)
        ↓
  False-Positive Classification (planet / EB / background EB / artifact)
        ↓
  Planet Characterization (Rp, a, Teq, inclination, type)
        ↓
  Interactive Dashboard + PDF/CSV Report
```

---

## 🧪 Running Tests

```bash
# From the project root
pip install -r backend/requirements.txt
pytest tests/ -v --cov=backend --cov-report=term-missing
```

---

## 🤖 ML Model Training

```python
from backend.candidate_validation.model_training import train_model

metrics = train_model(
    model_save_path="backend/ml_models/transit_classifier.h5",
    n_planet=2000,
    n_fp=2000,
    epochs=100,
)
print(metrics)
# TensorBoard: tensorboard --logdir backend/ml_models/logs
```

---

## 🌐 API Reference

Full Swagger documentation at **`/docs`** when the backend is running.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/datasets/search?tic_id=...` | Search MAST archive |
| POST | `/api/datasets/download` | Download TESS light curve |
| POST | `/api/datasets/upload` | Upload FITS/CSV file |
| GET | `/api/datasets/{id}/preview` | Preview raw time/flux |
| POST | `/api/preprocessing/{id}` | Run preprocessing pipeline |
| POST | `/api/detection/{id}` | Run TLS + BLS detection |
| POST | `/api/validation/{candidate_id}` | Validate transit candidate |
| POST | `/api/characterization/{candidate_id}` | Estimate planet parameters |
| GET | `/api/visualization/{id}` | Get all plot data |
| POST | `/api/reports/generate` | Generate PDF + CSV report |
| GET | `/api/reports/download/{filename}` | Download report |
| WS | `/ws/jobs/{job_id}` | Real-time job progress |

---

## 🛰 Demo Target

For demonstration purposes, search for **TIC 261136679** — a confirmed TESS planet host.

---

## 🏗 Built With

- **FastAPI** + **SQLAlchemy** + **asyncpg**
- **Lightkurve** + **Astropy** + **Astroquery**
- **transitleastsquares** + **Wotan**
- **TensorFlow/Keras** + **SHAP**
- **React 18** + **Tailwind CSS** + **Plotly.js** + **Zustand**
- **PostgreSQL** + **Redis**
- **Docker** + **Nginx**
- **ReportLab** (PDF) + **structlog**

---

*Horizon Exoplanet Platform — Automated TESS Transit Detection*  
*Developed by [@AYJJAE](https://github.com/AYJJAE)*
