import json
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

def find_rankings(data):
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
                first_item = value[0]
                if ("name" in first_item or "institutionName" in first_item) and "rank" in first_item:
                    return value
            
            result = find_rankings(value)
            if result:
                return result
    elif isinstance(data, list):
        if len(data) > 0 and isinstance(data[0], dict):
            first = data[0]
            if ("name" in first or "institutionName" in first) and "rank" in first:
                return data
        for item in data:
            result = find_rankings(item)
            if result:
                return result
    return None

async def scrape_the():
    print("Avvio dello scraper DEFINITIVO per THE (Estrazione Next.js)...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        print("Navigazione in corso su Times Higher Education...")
        await page.goto("https://www.timeshighereducation.com/world-university-rankings/latest/world-ranking", wait_until="domcontentloaded", timeout=60000)
        
        try:
            next_data_content = await page.evaluate("() => document.getElementById('__NEXT_DATA__').innerText")
            next_data_json = json.loads(next_data_content)
            print("Dati Next.js estratti con successo dal DOM!")
        except Exception as e:
            print(f"Errore durante l'estrazione o il parsing di __NEXT_DATA__: {e}")
            await browser.close()
            return []
            
        await browser.close()

    print("Ricerca dell'array delle università nel JSON...")
    raw_rankings = find_rankings(next_data_json)
    
    if not raw_rankings:
        print("Non sono riuscito a trovare l'array delle università all'interno dei dati Next.js.")
        return []

    print(f"Bingo! Trovate {len(raw_rankings)} università. Inizio formattazione...")

    cleaned_rankings = []
    for item in raw_rankings[:300]:
        raw_name = item.get("name") or item.get("institutionName", "")
        clean_name = BeautifulSoup(raw_name, "html.parser").get_text(strip=True) if raw_name else "N/A"
        
        raw_rank = str(item.get("rank", ""))
        clean_rank = raw_rank.replace("=", "").strip()
        
        cleaned_rankings.append({
            "rank": clean_rank,
            "name": clean_name,
            "country": item.get("location") or item.get("country", "")
        })
        
    return cleaned_rankings