import asyncio
import re
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def scrape_qs():
    print("Avvio dello scraper DEFINITIVO per QS...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        api_url = None

        async def handle_request(request):
            nonlocal api_url
            if "rankings/endpoint" in request.url:
                api_url = request.url

        page.on("request", handle_request)
        
        print("Navigazione in corso per intercettare l'API...")
        await page.goto("https://www.topuniversities.com/world-university-rankings", wait_until="domcontentloaded", timeout=60000)
        
        for _ in range(30):
            if api_url:
                break
            await asyncio.sleep(0.5)
            
        if not api_url:
            print("Errore: Impossibile trovare l'URL dell'API dei ranking.")
            await browser.close()
            return []

        print(f"API intercettata! Sostituzione paginazione in corso...")
        
        full_url = re.sub(r'items_per_page=\d+', 'items_per_page=300', api_url)
        
        print(f"Esecuzione della chiamata completa tramite browser...")
        
        try:
            json_response = await page.evaluate(f"""
                async () => {{
                    const response = await fetch('{full_url}');
                    return await response.json();
                }}
            """)
        except Exception as e:
            print(f"Errore durante il fetch dei dati: {e}")
            await browser.close()
            return []
            
        await browser.close()
        
    extracted_nodes = json_response.get("score_nodes", [])
    print(f"Fantastico! Scaricate {len(extracted_nodes)} università in un colpo solo.")
    
    cleaned_rankings = []
    for item in extracted_nodes:
        raw_title = item.get("title", "")
        clean_name = BeautifulSoup(raw_title, "html.parser").get_text(strip=True) if raw_title else "N/A"
        
        raw_rank = str(item.get("rank_display", ""))
        clean_rank = raw_rank.replace("=", "").strip()
        
        cleaned_rankings.append({
            "rank": clean_rank,
            "name": clean_name,
            "country": item.get("country", "")
        })
        
    return cleaned_rankings