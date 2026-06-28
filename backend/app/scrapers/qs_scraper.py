import asyncio
import re
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def scrape_qs():
    print("Avvio dello scraper DEFINITIVO per QS...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Il finto User-Agent resta fondamentale per aggirare l'anti-bot
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        api_url = None

        # Ascoltiamo le richieste in uscita per rubare l'URL con il NID giusto
        async def handle_request(request):
            nonlocal api_url
            if "rankings/endpoint" in request.url:
                api_url = request.url

        page.on("request", handle_request)
        
        print("Navigazione in corso per intercettare l'API...")
        await page.goto("https://www.topuniversities.com/world-university-rankings", wait_until="domcontentloaded", timeout=60000)
        
        # Aspettiamo fino a 15 secondi per trovare l'URL
        for _ in range(30):
            if api_url:
                break
            await asyncio.sleep(0.5)
            
        if not api_url:
            print("Errore: Impossibile trovare l'URL dell'API dei ranking.")
            await browser.close()
            return []

        print(f"API intercettata! Sostituzione paginazione in corso...")
        
        # Sostituiamo items_per_page=30 con items_per_page=2000 (o un numero sufficiente a prenderle tutte)
        full_url = re.sub(r'items_per_page=\d+', 'items_per_page=300', api_url)
        
        print(f"Esecuzione della chiamata completa tramite browser...")
        
        # Facciamo eseguire la chiamata fetch() direttamente dalla pagina del browser per non avere problemi di blocco
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
        
    # Fase di parsing ed estrazione dei dati dalla chiave 'score_nodes'
    extracted_nodes = json_response.get("score_nodes", [])
    print(f"Fantastico! Scaricate {len(extracted_nodes)} università in un colpo solo.")
    
    cleaned_rankings = []
    for item in extracted_nodes:
        # A volte i titoli hanno tag HTML interni (es. <div class="...">Nome Uni</div>)
        raw_title = item.get("title", "")
        clean_name = BeautifulSoup(raw_title, "html.parser").get_text(strip=True) if raw_title else "N/A"
        
        cleaned_rankings.append({
            "rank": item.get("rank_display", ""),
            "name": clean_name,
            "score": item.get("overall_score", ""),
            "country": item.get("country", ""),
            "region": item.get("region", "")
        })
        
    return cleaned_rankings