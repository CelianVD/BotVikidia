# Script pour enlever les portails sur les pages d'homonymies.

import pywikibot
import re
import mwparserfromhell
from datetime import datetime, timedelta

LOG_FILE = "ebauche_scan_once_log.txt"
WIKI_LOG_PAGE = "Utilisateur:LuffyBot/Logs/2025"

def log(message):
    timestamp = datetime.utcnow().strftime("[%Y-%m-%d %H:%M:%S UTC] ")
    full_message = f"* {timestamp}{message}"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(full_message + "\n")
    print(full_message)
    log_to_wiki(full_message)

def log_to_wiki(message):
    site = pywikibot.Site("fr", "vikidia")
    page = pywikibot.Page(site, WIKI_LOG_PAGE)
    try:
        old_text = page.text if page.exists() else ""
        new_text = old_text.strip() + "\n" + message
        page.text = new_text
        page.save(summary="Mise à jour automatique du journal du bot", minor=True)
    except Exception as e:
        print(f"Erreur lors de l’écriture sur la page de logs wiki : {e}")

def extract_portails(text):
    try:
        wikicode = mwparserfromhell.parse(text)
        for template in wikicode.filter_templates():
            if template.name.strip().lower() == "portail":
                return [param.value.strip() for param in template.params if param.value.strip()]
    except Exception:
        raise ValueError("Texte illisible ou mal formé")
    return []

def has_Homonymie(text):
    return re.search(r'\{\{\s*homonymie\s*\}\}', text, re.IGNORECASE)

def supression_portail():
    site = pywikibot.Site("fr", "vikidia")
    cat = pywikibot.Category(site, "Catégorie:Homonymie")
    pages = cat.articles()

    for page in pages:
        try:
            text = page.text

            # Vérifie que le modèle {{homonymie}} est présent
            if not has_Homonymie(text):
                log(f"[[{page.title()}]] est dans la catégorie 'Homonymie' mais ne contient pas le modèle {{homonymie}}.")
                continue

            wikicode = mwparserfromhell.parse(text)
            modified = False

            # Suppression du ou des modèles {{Portail}}
            for template in wikicode.filter_templates():
                if template.name.strip().lower() == "portail":
                    log(f"Suppression du modèle {{Portail}} sur [[{page.title()}]] : {template}.")
                    wikicode.remove(template)
                    modified = True

            if modified:
                new_text = str(wikicode).strip()
                page.text = new_text
                page.save(summary="Retrait du modèle {{Portail}} sur une page d’homonymie", minor=False)
                log(f"Portails retirés de [[{page.title()}]].")
            else:
                log(f"Aucun modèle {{Portail}} trouvé sur [[{page.title()}]].")

        except Exception as e:
            log(f"Erreur avec la page [[{page.title()}]] : {e}")
          
if __name__ == "__main__":
    supression_portail()
