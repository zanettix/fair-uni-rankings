from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import json

from .scrapers.qs_scraper import scrape_qs
from .scrapers.the_scraper import scrape_the
from .scrapers.arwu_scraper import scrape_arwu
from .scrapers.us_scraper import scrape_usnews

app = FastAPI(
    title="University Rankings Scraper",
    description="API per lo scraping dei ranking universitari",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "FastAPI backend per fair-uni-rankings"}

@app.get("/api/scrape/qs")
async def trigger_qs_scrape():
    """Endpoint che lancia lo scraping di QS e salva il JSON per Angular"""
    
    print("Inizio operazione di scraping per QS...")
    # Esegue lo scraping
    qs_data = await scrape_qs()
    
    if not qs_data:
        return {"error": "Nessun dato recuperato. La struttura del sito potrebbe essere cambiata."}
    
    # Percorso: fair-uni-rankings/frontend/src/assets/rankings
    frontend_path = Path(__file__).parent.parent.parent / "frontend" / "src" / "assets" / "rankings"
    
    # Crea le cartelle se non esistono (equivale al mkdir -p)
    frontend_path.mkdir(parents=True, exist_ok=True)
    
    file_path = frontend_path / "qs.json"
    
    # Salva il file
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(qs_data, f, ensure_ascii=False, indent=2)
    
    return {
        "message": f"Scraping completato con successo!",
        "total_universities": len(qs_data),
        "file_saved_at": str(file_path)
    }

@app.get("/api/scrape/the")
async def trigger_the_scrape():
    """Endpoint che lancia lo scraping di THE e salva il JSON per Angular"""
    
    print("Inizio operazione di scraping per THE...")
    the_data = await scrape_the()
    
    if not the_data:
        return {"error": "Nessun dato recuperato. La struttura del sito potrebbe essere cambiata o c'è un blocco anti-bot."}
    
    frontend_path = Path(__file__).parent.parent.parent / "frontend" / "src" / "assets" / "rankings"
    frontend_path.mkdir(parents=True, exist_ok=True)
    
    file_path = frontend_path / "the.json"
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(the_data, f, ensure_ascii=False, indent=2)
    
    return {
        "message": "Scraping completato con successo!",
        "total_universities": len(the_data),
        "file_saved_at": str(file_path)
    }

@app.get("/api/scrape/arwu")
async def trigger_arwu_scrape():
    """Endpoint che lancia lo scraping di ARWU e salva il JSON per Angular"""
    
    print("Inizio operazione di scraping per ARWU...")
    arwu_data = await scrape_arwu()
    
    if not arwu_data:
        return {"error": "Nessun dato recuperato (Il Sonar è attivo o la struttura è cambiata)."}
    
    frontend_path = Path(__file__).parent.parent.parent / "frontend" / "src" / "assets" / "rankings"
    frontend_path.mkdir(parents=True, exist_ok=True)
    
    file_path = frontend_path / "arwu.json"
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(arwu_data, f, ensure_ascii=False, indent=2)
    
    return {
        "message": "Scraping completato con successo!",
        "total_universities": len(arwu_data),
        "file_saved_at": str(file_path)
    }

@app.get("/api/scrape/us")
async def trigger_usnews_scrape():
    """Endpoint che lancia lo scraping di U.S. News e salva il JSON per Angular"""
    
    print("Inizio operazione di scraping per U.S. News...")
    usnews_data = await scrape_usnews()
    
    if not usnews_data:
        return {"error": "Nessun dato recuperato (Il Sonar è attivo o siamo stati bloccati dall'anti-bot)."}
    
    frontend_path = Path(__file__).parent.parent.parent / "frontend" / "src" / "assets" / "rankings"
    frontend_path.mkdir(parents=True, exist_ok=True)
    
    file_path = frontend_path / "us.json"     
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(usnews_data, f, ensure_ascii=False, indent=2)
    
    return {
        "message": "Scraping completato con successo!",
        "total_universities": len(usnews_data),
        "file_saved_at": str(file_path)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)