from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import json
from typing import List, Dict, Any

# Crea l'istanza dell'applicazione FastAPI
app = FastAPI(
    title="University Rankings Scraper",
    description="API per lo scraping dei ranking universitari",
    version="1.0.0"
)

# Configura CORS per permettere ad Angular (in sviluppo) di chiamare il backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # Angular in sviluppo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Endpoint di test ---
@app.get("/")
async def root():
    return {"message": "FastAPI backend per University Rankings"}

# --- Endpoint per lo scraping (esempio) ---
@app.get("/api/scrape/test")
async def scrape_test():
    """Endpoint di test che genera un file JSON di esempio"""
    
    # Dati di esempio
    sample_data = [
        {"rank": 1, "name": "Harvard University", "score": 100, "country": "USA"},
        {"rank": 2, "name": "Stanford University", "score": 98.5, "country": "USA"},
        {"rank": 3, "name": "MIT", "score": 97.2, "country": "USA"},
    ]
    
    # Salva nella cartella assets/data del frontend
    frontend_path = Path(__file__).parent.parent.parent / "frontend" / "src" / "assets" / "data"
    frontend_path.mkdir(parents=True, exist_ok=True)
    
    file_path = frontend_path / "test-2025.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(sample_data, f, ensure_ascii=False, indent=2)
    
    return {
        "message": f"Dati salvati in {file_path}",
        "data": sample_data
    }

# --- Avvio del server (se eseguito direttamente) ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)