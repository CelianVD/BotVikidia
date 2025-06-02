import pywikibot
from datetime import datetime, timedelta
from collections import defaultdict

WIKI_REPORT_PAGE = "Utilisateur:LuffyBot/Rapport Vandalisme 2025"
DAYS = 365

def is_vandal_user(user, site):
    try:
        if user is None:
            return False
        if user.isAnonymous():
            return True  # IP
        if site.isBlocked(user.username):
            return True

        # Vérifie si toutes les contribs sont annulées ou supprimées
        contribs = list(user.contributions(total=20))
        if not contribs:
            return False
        total = len(contribs)
        annulées = sum(1 for c in contribs if 'révoqué' in c[3].get('tags', []))
        return annulées == total
    except Exception:
        return False

def collect_vandalism(site):
    cutoff = datetime.utcnow() - timedelta(days=DAYS)
    vandalisme_par_page = defaultdict(list)

    for change in site.recentchanges(start=cutoff, changetype="edit", namespaces=[0], reverse=True):
        tags = change.get("tags", [])
        if "révoqué" not in tags:
            continue

        title = change["title"]
        user = change.get("user")

        user_obj = None
        try:
            user_obj = pywikibot.User(site, user)
        except:
            continue

        if is_vandal_user(user_obj, site):
            vandalisme_par_page[title].append(user)

    return vandalisme_par_page

def publier_rapport(site, rapport_data):
    page = pywikibot.Page(site, WIKI_REPORT_PAGE)
    lignes = [f"== Rapport des pages vandalisées (sur les {DAYS} derniers jours) ==\n"]

    if not rapport_data:
        lignes.append("Aucun vandalisme significatif détecté.")
    else:
        for title, users in sorted(rapport_data.items(), key=lambda x: len(set(x[1])), reverse=True):
            nbre_vandales = len(set(users))
            lignes.append(f"* [[{title}]] — {len(users)} actes, {nbre_vandales} vandale(s) unique(s)")

    page.text = "\n".join(lignes)
    page.save(summary="Mise à jour automatique du rapport de vandalisme")

def main():
    site = pywikibot.Site("fr", "vikidia")
    site.login()

    print("Analyse des contributions révoquées...")
    data = collect_vandalism(site)
    print("Publication du rapport...")
    publier_rapport(site, data)
    print("Rapport publié avec succès.")

if __name__ == "__main__":
    main()
