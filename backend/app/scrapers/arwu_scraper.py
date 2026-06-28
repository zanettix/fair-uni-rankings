import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def scrape_arwu():
    print("Avvio dello scraper paginato per ARWU 2025 (Top 300 - Cleaned)...")
    all_rankings = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        print("Navigazione verso la pagina iniziale di ARWU 2025...")
        await page.goto("https://www.shanghairanking.com/rankings/arwu/2025", wait_until="domcontentloaded", timeout=60000)
        
        await page.wait_for_selector("table tbody tr", timeout=15000)

        for current_page in range(1, 11):
            print(f"Estrazione dei dati dalla pagina {current_page}/10...")

            html_content = await page.content()
            soup = BeautifulSoup(html_content, "html.parser")
            rows = soup.select("table tbody tr")
            
            for row in rows:
                cols = row.find_all("td")

                if len(cols) >= 2:
                    rank = cols[0].get_text(strip=True)

                    strings = list(cols[1].stripped_strings)
                    
                    if strings:
                        name = strings[0] 
                        country = strings[-1] if len(strings) > 1 else ""
                    else:
                        name = ""
                        country = ""
                    
                    if name:
                        all_rankings.append({
                            "rank": rank,
                            "name": name,
                            "country": country
                        })
            
            if len(all_rankings) >= 300:
                print("Raggiunto il limite di 300 università!")
                break
                
            if current_page < 10:
                try:
                    next_button = page.locator("li.ant-pagination-next")
                    
                    class_attr = await next_button.get_attribute("class")
                    if class_attr and "ant-pagination-disabled" not in class_attr:
                        await next_button.click(force=True)
                        await asyncio.sleep(2)
                        await page.wait_for_selector("table tbody tr", state="visible", timeout=15000)
                    else:
                        print("Pulsante 'Avanti' disabilitato o non cliccabile.")
                        break
                except Exception as e:
                    print(f"Errore durante il passaggio alla pagina successiva: {e}")
        
        await browser.close()
        
    print(f"Estrazione completata con successo per ARWU. Totale università recuperate: {len(all_rankings)}.")
    
    return all_rankings[:300]