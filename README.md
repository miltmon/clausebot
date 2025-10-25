# ClauseBot - Professional Welding Education Platform

**Monorepo consolidation:** Backend (Python/FastAPI) + Frontend (React/TypeScript)

---

## **Repository Structure**

```
clausebot/
├── backend/          # FastAPI API (Python 3.11+)
├── frontend/         # React + TypeScript + Vite
├── docs/            # Combined documentation
├── scripts/         # Deployment & utility scripts
└── .github/workflows/  # Unified CI/CD
```

---

## **Deployment**

### **Backend (Render)**
- **Platform:** Render
- **Service:** clausebot-api
- **URL:** https://clausebot-api.onrender.com
- **Root Directory:** `backend/`
- **Health Check:** `/health`

### **Frontend (Vercel)**
- **Platform:** Vercel
- **URL:** https://clausebot.miltmonndt.com (production)
- **Root Directory:** `frontend/`
- **Framework:** Vite (React)

---

## **Local Development**

### **Backend**
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn clausebot_api.main:app --reload
```

### **Frontend**
```bash
cd frontend
npm install
npm run dev
```

---

## **Environment Variables**

### **Backend** (`backend/.env`)
```env
AIRTABLE_API_KEY=your_key_here
AIRTABLE_BASE_ID=appJQ23u70iwOl5Nn
AIRTABLE_TABLE=Questions
AIRTABLE_VIEW=Grid view
```

### **Frontend** (`frontend/.env.production`)
```env
VITE_API_BASE=https://clausebot-api.onrender.com
VITE_GA_ID=G-XXXXXXXX
```

---

## **CI/CD**

GitHub Actions workflow runs on every push to `main`:
- Backend: Python tests + linting
- Frontend: Build + type checking

See `.github/workflows/monorepo.yml`

---

## **Migration Notes**

This monorepo consolidates:
- **Backend:** Previously `clausebot-api` repository
- **Frontend:** Previously `clausebotai` repository

**Benefits:**
- Single source of truth
- Coordinated deployments
- Simpler maintenance
- Unified CI/CD

---

## **Documentation**

- Backend API: `backend/docs/`
- Frontend: `frontend/docs/`
- Deployment: `docs/DEPLOYMENT.md`
- Architecture: `docs/ARCHITECTURE.md`

---

## **Contact**

**MiltmonNDT Platform**  
Professional welding education and compliance tools

---

**Last Updated:** October 25, 2025  
**Consolidated by:** Cursor AI Agent

