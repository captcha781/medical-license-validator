
# 🏥 AI-Powered Medical Credential Validation Platform

This platform uses a series of AI agents to extract, verify, cross-check, and assess the credibility of medical credentials in India. Built with **LangGraph**, **Gemini LLM**, **Astra DB** (Vector Store), **MongoDB** (For User Data Storing), and integrated with a **React** frontend supporting sign-up/sign-in.

---

## 🚀 Features

- 🔍 **Document Classification Agent**
  - Classifies input documents into: `medical_license`, `medical_degree`, `training_certificate`, `board_certificate`

- 🧾 **Credential Extraction Agent**
  - Extracts key information: license number, dates, institution, certifying body

- 📚 **Credential Verification Agent** *(RAG based)*
  - Compares extracted credential against Astra DB vector store
  - Determines if a credential is valid/invalid

- 🔎 **Cross Check Agent**
  - Compares extracted and verified data against resume content
  - Uses Gemini to detect inconsistencies with fuzzy logic

- 📊 **Credibility Score Agent**
  - Computes credibility score (0–10) based on verification and crosscheck results
  - Outputs a human-readable summary

- 👤 **User Authentication**
  - React frontend with sign-up and sign-in
  - Secure session handling

---

## 🛠️ Tech Stack

- **Backend**: Python, FastAPI, LangGraph, LangChain, Gemini API
- **Frontend**: React + TailwindCSS
- **Vector DB**: Astra DB (via astrapy)
- **Database**: Mongo DB (via beanie)
- **LLM**: Gemini 1.5 Flash (Google Generative AI)
- **Authentication**: JWT-based session handling

---

## 📂 Directory Structure

```
backend/
├── controller/
│   ├── agent.py
│   ├── agents/
│   │   ├── classifier_agent.py
│   │   ├── credential_extraction_agent.py
│   │   ├── credential_verification_agent.py
│   │   ├── crosscheck_agent.py
│   │   └── credibility_score_agent.py
│   └── main.py
├── utils/
│   ├── embeddings.py
│   └── file_reader.py
├── config/
│   └── main.py
frontend/
├── src/
│   ├── components/
│   ├── pages/
│   ├── helper/
│   ├── redux/
│   ├── routes/
│   └── App.jsx
```

---

## 🧪 Running Locally

### 1️⃣ Backend
```bash
cd backend
mkdir backend/store
poetry install
poetry run server
```

### 2️⃣ Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## 🔐 Environment Variables
Create a `local.env` file in `backend/config/`:
```env
CORS_ORIGIN = "http://localhost:5173"
MONGO_URI = "mongodb://localhost:27017/agentic-ai-hackathon"
PORT = 5000
JWT_ACCESS_KEY = ""
JWT_REFRESH_KEY = ""
JWT_ACCESS_EXPIRY = "1h"
JWT_REFRESH_EXPIRY = "30d"
SECRET_OR_KEY = ""

ASTRA_DB_SECRET_KEY = ""
ASTRA_DB_ENDPOINT = ""
ASTRA_DB_KEYSPACE = "agentic_ai"

GEMINI_API_KEY = ""
```

---

## ✅ Sample Output
```json
{
    "success": true,
    "message": "Agent run success",
    "navigate": "/",
    "result": {
        "classifier_result": "medical_license",
        "credebility_result": {
            "credibility_score": 90,
            "summary": "Summary",
            "flag": "flag",
            "discrepancies": [
                "...",
                "..."
            ]
        }
    }
}
```

---

## ✨ TODO (Suggestions)

- [ ] Add admin dashboard to approve/reject applications
- [ ] Enable bulk credential uploads and batch scoring
- [ ] Export reports as PDF/CSV
- [ ] Add institution-level trust scoring

---

## 👥 Contributors
- Bhuvanesh (Lead Developer)

---

## 📄 License
MIT License

---

> Built for the Agentic AI Hackathon 🚀

## Github
Repository Link - Link(<https://github.com/captcha781/medical-license-validator.git>)

## Demo Video
Demo Vide Link - Link(<https://drive.google.com/file/d/1HUkz4PqcnzLRW8jFpTdTjuL9kiFV67ei/view?usp=sharing>)
