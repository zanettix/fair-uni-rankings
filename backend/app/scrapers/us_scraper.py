import asyncio
from playwright.async_api import async_playwright

async def scrape_usnews():
    print("Avvio dello scraper per U.S. News (Estrazione nativa tramite JavaScript)...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        page = await context.new_page()
        
        print("Navigazione in corso... Attendi il caricamento.")
        await page.goto("https://www.usnews.com/education/best-global-universities/rankings", wait_until="domcontentloaded", timeout=60000)
        
        print("Attesa per il superamento dei controlli anti-bot (10 secondi)...")
        await asyncio.sleep(10)
        
        # 🎯 CORREZIONE 1: Aumentato a 15 click (10 iniziali + 15 * 30 = 460 università caricate)
        for i in range(1, 16):
            print(f"Caricamento blocco dinamico {i}/15...")
            await page.keyboard.press("End")
            await asyncio.sleep(2)
            
            clicked = await page.evaluate("""
                () => {
                    const buttons = Array.from(document.querySelectorAll('button'));
                    const loadBtn = buttons.find(b => b.innerText.toLowerCase().includes('load'));
                    if (loadBtn && !loadBtn.disabled) {
                        loadBtn.click();
                        return true;
                    }
                    return false;
                }
            """)
            
            if clicked:
                print("  -> Nuove università in caricamento...")
                await asyncio.sleep(4)
            else:
                print("  -> Nessun bottone trovato. Procedo con l'estrazione.")
                break
                
        print("Estrazione dati direttamente dal motore di rendering del browser...")
        
        # Estrazione tramite il browser (RAW string per evitare conflitti con Python)
        extracted_data = await page.evaluate(r"""
            () => {
                let results = [];
                let headings = document.querySelectorAll('h2, h3, h4');
                
                let invalidNames = ["read more", "search", "best global universities", "canada", "china", "france", "germany", "india", "italy", "japan", "netherlands", "united kingdom", "united states", "australia"];
                
                headings.forEach(h => {
                    let name = h.innerText.trim();
                    if (!name || name.length < 4 || invalidNames.includes(name.toLowerCase())) return;
                    
                    let card = h.parentElement;
                    let maxDepth = 6;
                    let rank = "";
                    let score = "";
                    let locationStr = ""; // Salviamo l'intera stringa temporaneamente
                    
                    while (card && maxDepth > 0) {
                        let text = card.innerText || "";
                        
                        if (!rank) {
                            let rMatch = text.match(/#\s*(\d+)/);
                            if (rMatch) rank = rMatch[1];
                        }
                        
                        if (!score) {
                            let sMatch = text.match(/Global Score[\s\n]*([0-9\.]+)/i) || text.match(/Score[\s\n]*([0-9\.]+)/i);
                            if (sMatch) score = sMatch[1];
                        }
                        
                        if (rank && score) break;
                        card = card.parentElement;
                        maxDepth--;
                    }
                    
                    if (rank && score) {
                        let locElem = h.nextElementSibling;
                        if (locElem) {
                            // 🎯 CORREZIONE 2: Catturiamo l'intero testo inclusivo di virgole e pipe
                            let rawLoc = locElem.innerText.trim();
                            // Rimuoviamo ritorni a capo se presenti all'inizio o alla fine
                            locationStr = rawLoc.split('\n')[0].trim();
                        }
                        results.push({ rank, name, score, raw_location: locationStr });
                    }
                });
                
                let uniqueData = [];
                let seen = new Set();
                results.forEach(item => {
                    if (!seen.has(item.name)) {
                        seen.add(item.name);
                        uniqueData.push(item);
                    }
                });
                
                return uniqueData;
            }
        """)
        
        await browser.close()
        
    print("Formattazione e pulizia finale in Python...")
    final_rankings = []
    
    for item in extracted_data:
        country = ""
        region = ""
        
        raw_loc = item.get('raw_location', '')
        
        # 🎯 CORREZIONE 2: Splittiamo la nazione (country) dalla città (region) basandoci sul pipe "|"
        if '|' in raw_loc:
            parts = raw_loc.split('|')
            country = parts[0].strip()
            region = parts[1].strip() if len(parts) > 1 else ""
        elif ',' in raw_loc:
            # Fallback se usassero la virgola (es: "United States, Cambridge")
            parts = raw_loc.split(',')
            country = parts[0].strip()
            region = parts[1].strip() if len(parts) > 1 else ""
        else:
            country = raw_loc.strip()

        final_rankings.append({
            "rank": item["rank"],
            "name": item["name"],
            "score": item["score"],
            "country": country,
            "region": region
        })
    
    # Ordiniamo in base al rank
    final_rankings.sort(key=lambda x: int(x['rank']))
    
    print(f"Estrazione conclusa! Salvataggio di {min(300, len(final_rankings))} università.")
    return final_rankings[:300]