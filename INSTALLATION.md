# BuildWise-AI — Windows Installation & Setup Guide

This guide provides step-by-step instructions for installing and running BuildWise-AI on a fresh Windows 10 or Windows 11 machine.

---

## 1. Prerequisites

Before starting, install the required prerequisites:

1. **Python 3.10+ (Recommended: Python 3.11.x)**
   - Download: https://www.python.org/downloads/
   - **Important:** During setup, check the box: **"Add Python to PATH"**.
2. **Node.js (Recommended: v20 LTS or v22 LTS)**
   - Download: https://nodejs.org/
   - Includes `npm` package manager.
3. **Git for Windows**
   - Download: https://git-scm.com/download/win

Verify installations in Command Prompt or PowerShell:
```bat
python --version
node --version
npm --version
git --version
```

---

## 2. Clone the Repository

```bat
git clone https://github.com/1nishanth-s/buildwise.git
cd buildwise
```

---

## 3. Python Virtual Environment Setup

1. Create a virtual environment named `.venv`:
   ```bat
   python -m venv .venv
   ```

2. Activate the virtual environment:
   - **Command Prompt (`cmd`)**:
     ```bat
     .venv\Scripts\activate.bat
     ```
   - **PowerShell**:
     ```powershell
     .venv\Scripts\Activate.ps1
     ```
     *(If script execution is disabled in PowerShell, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` and retry).*

3. Upgrade `pip` and install all required packages:
   ```bat
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

---

## 4. Frontend Setup & Build

1. Open a terminal, navigate into the `frontend/` directory:
   ```bat
   cd frontend
   ```

2. Install JavaScript dependencies:
   ```bat
   npm install
   ```

3. Build the production React frontend:
   ```bat
   npm run build
   ```
   *(This compiles TypeScript and builds optimized static assets into `frontend/dist/`).*

---

## 5. Running the Application

### Option 1: Modern Full-Stack Platform (FastAPI + React Canvas)

From the project root directory (with `.venv` activated):

```bat
python -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000 --reload
```

Open your browser at:
```
http://127.0.0.1:8000/
```

- **Build Mode:** Enter usage (Gaming, Content Creation, Workstation) and total budget (₹18,000+).
- **Upgrade Mode:** Enter existing components and upgrade goal to get a multi-component, dependency-aware upgrade plan.
- **Interactive Canvas:** Inspect components, click "Compatible Alternatives" to swap parts, and download PDF / CSV reports.

### Option 2: Standalone Streamlit App

```bat
streamlit run app.py
```
Open your browser at `http://localhost:8501/`.

---

## 6. Running Test Suites

Verify that all components and models function correctly on your machine:

1. **Backend Unit & Integration Tests (189 tests):**
   ```bat
   python -m unittest discover -s tests -v
   ```

2. **Frontend Component & Workflow Tests (14 tests):**
   ```bat
   cd frontend
   npm run test
   ```

3. **Playwright Browser End-to-End Tests (10 tests):**
   ```bat
   cd frontend
   npx playwright install chromium
   npx playwright test
   ```

---

## 7. Troubleshooting

- **PowerShell script execution disabled:**
  Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` before activating `.venv`.
- **Port 8000 already in use:**
  Run on a different port: `python -m uvicorn src.api.main:app --host 127.0.0.1 --port 8080`.
- **Database file location:**
  SQLite database is created automatically on startup at `data/buildwise_projects.db`. No manual schema setup or SQL commands required.
