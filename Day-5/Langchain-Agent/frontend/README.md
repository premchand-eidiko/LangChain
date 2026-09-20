# Frontend

React/Vite interface for the Private AI Workspace.

## Install

Run once after cloning or whenever `node_modules` is missing:

```powershell
npm ci
```

Do not commit `node_modules`; it is already listed in `.gitignore`.

## Run

From the `frontend` folder:

```powershell
npm run dev
```

Open http://localhost:5173. The app calls the backend at http://127.0.0.1:8000 by default.

Override the API URL when needed:

```powershell
$env:VITE_API_URL = "http://127.0.0.1:8000"
npm run dev
```

## Build

```powershell
npm run build
npm run preview
```
