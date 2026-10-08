# PharmaGuard Project Setup & Execution Guide

This guide provides copy-paste-ready Windows PowerShell commands and exact architectural configurations to start both the Python FastAPI backend and the React Vite frontend.

---

## 1. Backend Framework
- **Framework**: **FastAPI** (v2.0 API defined in `backend/main.py`)
- **Server Gateway Interface (ASGI)**: **Uvicorn**
- **Database Connector**: **Motor** (AsyncIOMotorClient connecting to MongoDB)

---

## 2. API Base URL & Frontend URL
- **API Base URL**: `http://127.0.0.1:8000`
  - `POST /api/analyze`: Parses VCFs, executes PMGRF risk scoring, computes CatBoost predictions & SHAP, generates CPIC drug recommendations.
  - `POST /api/v1/clinical/recommendation`: Queries deterministic CPIC dosing guidelines.
- **Frontend URL**: `http://localhost:5173` (Vite Default Dev Server)

---

## 3. Required Dependencies

### Python Dependencies (`backend/requirements.txt`)
```text
fastapi
uvicorn
python-multipart
motor
pymongo
catboost
pandas
numpy
shap
matplotlib
seaborn
pytest
```

### Node.js Dependencies (`pharmaguard-frontend/package.json`)
```json
"dependencies": {
  "react": "^19.2.4",
  "react-dom": "^19.2.4"
},
"devDependencies": {
  "vite": "^8.0.4",
  "@vitejs/plugin-react": "^6.0.1",
  "tailwindcss": "^4.2.2",
  "@tailwindcss/postcss": "^4.2.2",
  "postcss": "^8.5.9",
  "autoprefixer": "^10.4.27"
}
```

---

## 4. Environment Variables Needed
- **No external `.env` environment variables are required.**
- MongoDB defaults to `mongodb://127.0.0.1:27017` in `backend/database.py`.
- CORS middleware in `backend/main.py` explicitly allows all origins (`*`).

---

## 5. Prerequisite & Missing Setup Steps
1. **MongoDB Service**: Ensure MongoDB Community Server is installed and running locally on `127.0.0.1:27017`.
   - *Note*: If MongoDB is not running, the application will still compute and render all PMGRF & CPIC clinical recommendations, but background MongoDB persistence will log a connection warning.
2. **Node.js**: Ensure Node.js (v18+) is installed.
3. **Python**: Ensure Python 3.10+ is installed.

---

## 6. Copy-Paste PowerShell Startup Commands

### Step A: Start the Backend (Terminal 1)
Open a Windows PowerShell terminal in the project root directory and execute:

```powershell
# Install Python dependencies
python -m pip install -r backend/requirements.txt

# Launch FastAPI server directly from project root
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

### Step B: Start the Frontend (Terminal 2)
Open a second Windows PowerShell terminal in the project root directory and execute:

```powershell
# Navigate to frontend directory
cd pharmaguard-frontend

# Install Node dependencies
npm install

# Launch Vite development server
npm run dev
```

---

## 7. Operational Verification

1. Open your browser and navigate to **`http://localhost:5173`**.
2. Click **Enter Analysis Portal** and upload a sample VCF file (e.g. `data/regions/CYP2C9_CYP2C19_GRCh37.vcf.gz` or any multi-sample VCF).
3. Verify that the dashboard renders:
   - **PMGRF Summary Card** (Composite Risk Score & Risk Category)
   - **Drug-Specific Pharmacogenomic Recommendations** (Clopidogrel, Warfarin, Fluorouracil, Simvastatin, Codeine)
   - **AI Predicted Risk & SHAP Feature Contributions**
