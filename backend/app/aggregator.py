import json
import re
import unicodedata
import difflib
from pathlib import Path
from collections import defaultdict

# 1. DIZIONARIO DEGLI ALIAS: Mappatura esplicita per i casi più difficili (Acronimi o nomi completamente diversi)
ALIAS_MAP = {
    "mit": "massachusetts institute of technology",
    "ucl": "university college london",
    "nus": "national university of singapore",
    "ntu": "nanyang technological university",
    "eth zurich": "swiss federal institute of technology zurich",
    "epfl": "ecole polytechnique federale de lausanne",
    "lse": "london school of economics and political science",
    "psl research university paris comue": "universite psl",
    "paris sciences et lettres psl research university paris": "universite psl",
    "psl university": "universite psl",
    "penn state main campus": "pennsylvania state university",
    "pennsylvania state university university park": "pennsylvania state university",
    "kaist": "korea advanced institute of science and technology",
    "postech": "pohang university of science and technology"
}

def normalize_uni_name(name):
    """
    Pulisce il nome in modo molto aggressivo rimuovendo accenti, 
    uniformando le lingue e gestendo le stop words.
    """
    # Rimuove gli accenti (es. é -> e, à -> a)
    name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('utf-8').lower()
    
    # Traduzioni di base per uniformare le lingue
    name = name.replace("universite", "university").replace("universidad", "university")
    name = name.replace("universitat", "university").replace("universita", "university")
    name = name.replace("ecole", "school").replace("polytechnique", "polytechnic")
    
    # Rimuove la punteggiatura e sostituisce con spazi
    name = re.sub(r'[^a-z0-9\s]', ' ', name)
    
    # Pulizia degli spazi extra creati
    name = " ".join(name.split())
    
    # Se la stringa intera matcha un alias (es. "mit"), lo espandiamo subito
    if name in ALIAS_MAP:
        return ALIAS_MAP[name]
        
    # Rimuove stop words per creare una "chiave scheletro"
    stop_words = {'university', 'of', 'the', 'institute', 'technology', 'and', 'college', 'for', 'at', 'state', 'sciences', 'main', 'campus'}
    words = [w for w in name.split() if w not in stop_words]
    
    final_key = " ".join(words).strip()
    
    # Ricontrolla se lo scheletro matcha un alias
    return ALIAS_MAP.get(final_key, final_key)

def find_best_match(norm_key, existing_keys, threshold=0.88):
    """
    Usa la logica Fuzzy per trovare se esiste già una chiave molto simile.
    Threshold a 0.88 significa che devono essere uguali all'88% (ignora refusi minimi).
    """
    matches = difflib.get_close_matches(norm_key, existing_keys, n=1, cutoff=threshold)
    if matches:
        return matches[0]
    return norm_key

def parse_rank(rank_str):
    """
    Estrae il numero del rank. Se è un range (es. 201-300), calcola la mediana.
    """
    nums = re.findall(r'\d+', str(rank_str))
    if not nums:
        return None
    if len(nums) == 1:
        return float(nums[0])
    elif len(nums) >= 2:
        return (float(nums[0]) + float(nums[1])) / 2.0
    return None

def generate_ultimate_ranking():
    print("Calcolo dell'Ultimate Ranking (Top 100) con Fuzzy Matching...")
    
    rankings_dir = Path(__file__).parent.parent.parent / "frontend" / "src" / "assets" / "rankings"
    
    files = {
        "qs": rankings_dir / "qs.json",
        "the": rankings_dir / "the.json",
        "arwu": rankings_dir / "arwu.json",
        "usnews": rankings_dir / "usnews.json"
    }
    
    master_dict = defaultdict(lambda: {
        "original_name": "",
        "country": "",
        "ranks": {}
    })
    
    for source, file_path in files.items():
        if not file_path.exists():
            continue
            
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for item in data:
                raw_rank = item.get("rank", "")
                rank_value = parse_rank(raw_rank)
                
                if rank_value is None:
                    continue
                    
                original_name = item.get("name", "N/A")
                country = item.get("country", "")
                
                # 1. Normalizziamo la chiave
                norm_key = normalize_uni_name(original_name)
                
                # 2. Fuzzy Matching: Controlliamo se esiste già una chiave quasi identica nel master_dict
                best_key = find_best_match(norm_key, master_dict.keys())
                
                # Salviamo la posizione in base alla fonte
                master_dict[best_key]["ranks"][source] = rank_value
                
                # Teniamo il nome originale più lungo/dettagliato per la visualizzazione finale
                if len(original_name) > len(master_dict[best_key]["original_name"]):
                    master_dict[best_key]["original_name"] = original_name
                    
                if country and not master_dict[best_key]["country"]:
                    master_dict[best_key]["country"] = country

    ultimate_rankings = []
    
    for _, data in master_dict.items():
        ranks = data["ranks"]
        sources_count = len(ranks)
        
        if sources_count > 0:
            average_rank = sum(ranks.values()) / sources_count
            
            ultimate_rankings.append({
                "name": data["original_name"],
                "country": data["country"],
                "average_rank": round(average_rank, 1),
                "sources_count": sources_count,
                "breakdown": ranks
            })
            
    # Ordinamento finale: Media più bassa, poi maggior numero di fonti
    ultimate_rankings.sort(key=lambda x: (x["average_rank"], -x["sources_count"]))
    
    top_100 = ultimate_rankings[:100]
    for index, uni in enumerate(top_100):
        uni["ultimate_rank"] = index + 1
        
    out_file = rankings_dir / "ultimate-ranking.json"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(top_100, f, ensure_ascii=False, indent=2)
        
    print(f"✅ Ultimate Ranking generato! Abbiamo combinato in modo intelligente le università.")
    
    return {
        "total_universities": len(top_100),
        "file_path": str(out_file)
    }