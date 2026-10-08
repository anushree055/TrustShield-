# TrustShield

**AI-Powered Scam Detection & Risk Intelligence** — an explainable scam-analysis PBL prototype for AI & Data Science.

## Core features

- URL scam/phishing analyzer
- Message / SMS / email analyzer
- Screenshot analyzer using OCR
- Likely scam type identification
- Explainable 0–100 risk score
- Scam Manipulation Fingerprint (urgency, fear, authority, reward, scarcity, trust, financial pressure, credential pressure)
- Scam-specific “What should I do now?” action plan
- Scam awareness library
- Local SQLite analysis history and dashboard metrics
- Built-in demo examples for presentation

## Technology

Frontend: React 18, Vite, React Router, Lucide React, Recharts, custom responsive CSS.

Backend: Python, FastAPI, SQLite, scikit-learn, pandas, joblib, Pillow, pytesseract.

ML: Random Forest for URL features and TF-IDF + Logistic Regression for message text. Bundled models are trained from a deliberately small synthetic seed dataset so the project runs immediately. Replace the seed data with larger labelled datasets for research-grade evaluation.

## Project flow

Input (URL / message / screenshot) → preprocessing → rule-based indicators + ML signal → scam category → manipulation fingerprint → risk engine → explanation → action plan.

## Run on Windows

### Backend

```bash
cd backend
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload
```

Backend: `http://127.0.0.1:8000`

Swagger API docs: `http://127.0.0.1:8000/docs`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend: `http://127.0.0.1:5173`

## Demo

Open **Analyze** → **Quick demo** → choose **Banking Phishing**, **Fake Job Scam**, **OTP Scam**, **Lottery Scam**, **UPI Scam**, or **Safe Message** → click **Analyze with TrustShield**.

## Screenshot OCR

The screenshot analyzer uses the locally installed Tesseract OCR engine through `pytesseract`. Install Tesseract on Windows and make sure `tesseract.exe` is available in PATH. If OCR is unavailable, URL and Message analysis still work, and users can paste the screenshot text manually.

## Important backend files

- `backend/main.py` — FastAPI routes
- `backend/services/url_analyzer.py` — URL features and phishing analysis
- `backend/services/message_analyzer.py` — text scam analysis
- `backend/services/scam_classifier.py` — likely scam category
- `backend/services/manipulation_analyzer.py` — manipulation fingerprint
- `backend/services/risk_engine.py` — weighted 0–100 risk score
- `backend/services/recommendation_engine.py` — “What should I do now?” actions
- `backend/services/ocr_service.py` — screenshot OCR
- `backend/database.py` — SQLite history
- `backend/ml/train_models.py` — retrain the bundled models

## Important frontend files

- `frontend/src/pages/Home.jsx` — landing page
- `frontend/src/pages/Analyze.jsx` — analyzer UI
- `frontend/src/components/ResultPanel.jsx` — results dashboard
- `frontend/src/pages/ScamTypes.jsx` — awareness library
- `frontend/src/pages/History.jsx` — local history dashboard
- `frontend/src/styles.css` — complete theme/layout

## Retrain models

Replace or extend:
- `backend/data/message_training.csv`
- `backend/data/url_training.csv`

Then run:

```bash
cd backend
python ml/train_models.py
```

Models are saved to `backend/models/`.

## API endpoints

- `GET /api/health`
- `POST /api/analyze/url`
- `POST /api/analyze/message`
- `POST /api/analyze/full`
- `POST /api/analyze/screenshot`
- `GET /api/history`
- `GET /api/history/{id}`
- `DELETE /api/history/{id}`
- `DELETE /api/history`
- `GET /api/stats`

## Limitations

TrustShield is an educational prototype and cannot prove that content is safe. It should not replace official fraud reporting, bank guidance, professional cybersecurity tools, or independent verification. The bundled ML training data is intentionally small and synthetic for a runnable classroom demo; larger real labelled datasets and formal evaluation should be used for a final research claim.
