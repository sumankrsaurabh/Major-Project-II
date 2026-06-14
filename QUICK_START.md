# Quick Start Guide

## 🚀 Run the Full Application

### Terminal 1: Backend Server
```bash
cd backend
python main.py
```
✅ Backend will start on **http://localhost:8000**

### Terminal 2: Frontend Development Server
```bash
cd frontend
npm run dev
```
✅ Frontend will start on **http://localhost:3000**

### Access the Application
Open browser: **http://localhost:3000**

---

## 📦 First-Time Setup

### Backend Setup (One-time)
```bash
cd backend
pip install -r requirements.txt
python verify_setup.py
```

### Frontend Setup (One-time)
```bash
cd frontend
npm install
npm run build    # Optional: test production build
```

---

## 🔧 Common Commands

### Frontend

**Development**
```bash
cd frontend
npm run dev           # Start dev server
npm run build         # Build for production
npm run preview       # Preview production build
npm run lint          # Check code quality
```

### Backend

**Development**
```bash
cd backend
python main.py        # Start server
python test_pipeline.py
python verify_setup.py
```

**Using Batch Files**
```
start_server_dev.bat  # Development server
start_server.bat      # Production server
```

---

## 🧪 Testing

### Frontend
```bash
cd frontend
npm run lint
```

### Backend
```bash
cd backend
python verify_setup.py
python test_pipeline.py
```

---

## 🔍 Health Check

### Backend Health
```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "ok",
  "models_loaded": true,
  "embedding_model": true,
  "llm_model": true
}
```

---

## 📱 API Endpoints

### File Upload
```
POST http://localhost:8000/upload
```

### Chat
```
POST http://localhost:8000/chat
```

### Analysis
```
POST http://localhost:8000/analysis/query
POST http://localhost:8000/analysis/answer
POST http://localhost:8000/analysis/document
```

---

## 🐛 Troubleshooting

### Backend Won't Start
```
❌ "Port 8000 already in use"
→ Kill process on port 8000 or use different port

❌ "Module not found"
→ Run: pip install -r requirements.txt

❌ "Python not found"
→ Add Python to PATH or use python3 main.py
```

### Frontend Won't Start
```
❌ "Port 3000 already in use"
→ Kill process on port 3000 or use different port

❌ "npm modules missing"
→ Run: npm install

❌ "Build fails"
→ Delete node_modules and dist/, then npm install
```

### Network Issues
```
❌ "Cannot reach backend from frontend"
→ Check backend is running on port 8000
→ Check .env.local has correct API_URL
→ Check CORS is enabled in backend
```

---

## 📂 Key Files

### Frontend
- `frontend/vite.config.js` - Build config
- `frontend/eslint.config.js` - Linter config
- `frontend/.env.local` - Environment variables
- `frontend/src/services/api.jsx` - API service
- `frontend/src/services/StateManager.jsx` - State management

### Backend
- `backend/main.py` - FastAPI app
- `backend/config.py` - Configuration
- `backend/requirements.txt` - Dependencies
- `backend/core/` - Core processing
- `backend/services/` - Service layer

---

## 📊 Project Structure

```
.
├── frontend/              # React + Vite app
│   ├── src/
│   ├── dist/             # Production build
│   ├── node_modules/
│   ├── package.json
│   └── vite.config.js
│
├── backend/              # FastAPI server
│   ├── core/
│   ├── services/
│   ├── routes/
│   ├── main.py
│   ├── config.py
│   └── requirements.txt
│
├── COMPLETION_SUMMARY.md
├── FRONTEND_SETUP.md
└── BACKEND_SETUP.md
```

---

## ✨ Features

### Chat with PDF
1. Upload PDF file
2. Ask questions about content
3. Get AI-powered answers

### Analysis
- Query intent recognition
- Entity extraction
- Text summarization
- Document analysis
- Sentiment analysis

---

## 🎯 Tips

✅ **Development**
- Frontend auto-reloads on file changes (HMR)
- Backend reloads on code changes (with auto-reload tools)
- Check ESLint for code quality

✅ **Performance**
- Backend loads models on startup (few seconds)
- Vite build takes ~7 seconds
- Production build is ~75KB gzipped

✅ **Debug**
- Frontend DevTools: F12 in browser
- Network tab to check API calls
- Console for JavaScript errors
- Backend logs in terminal

---

## 📚 Documentation

- **[COMPLETION_SUMMARY.md](./COMPLETION_SUMMARY.md)** - Project overview
- **[FRONTEND_SETUP.md](./FRONTEND_SETUP.md)** - Frontend details
- **[BACKEND_SETUP.md](./BACKEND_SETUP.md)** - Backend details

---

## ✅ Checklist

Before running:
- [ ] Python 3.8+ installed
- [ ] Node.js 16+ installed
- [ ] Ports 3000 & 8000 free
- [ ] Dependencies installed (`npm install`, `pip install -r requirements.txt`)

When running:
- [ ] Backend terminal shows "Application startup complete"
- [ ] Frontend terminal shows "VITE v5.X.X  ready in XXXms"
- [ ] Browser loads http://localhost:3000
- [ ] API calls work in browser console

---

## 🆘 Emergency Stop

```bash
# Kill backend (Ctrl+C in terminal)
Ctrl+C

# Kill frontend (Ctrl+C in terminal)
Ctrl+C

# Or kill by port (Windows)
netstat -ano | findstr :8000
taskkill /PID <PID> /F

netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

---

**Ready to start? Follow the instructions at the top! 🚀**
