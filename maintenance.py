# Script pour ajouter le modèle {{maitenance}} sur les pages qui n'ont pas certaines conditions
" Script en test.
import pywikibot
import re

# Désactiver les vérifications internes du parseur
pywikibot.config.ignore_bot_templates = True
pywikibot.config.enable_parser = False

# Connexion au site Vikidia FR
site = pywikibot.Site("fr", "vikidia")

def detect_problems(text):
    """Analyse le texte d'une page pour détecter les problèmes de structure."""
    problems = []

    # Pas d’introduction (commence directement par une section)
    if re.match(r'\s*==', text):
        problems.append("plan")

    # Pas de section
    if '==' not in text and "plan" not in problems:
        problems.append("plan")

    # Pas de catégorie
    if '[[Catégorie:' not in text:
        problems.append("catégoriser")

    # Pas de modèle portail
    if "{{Portail" not in text and "{{portail" not in text:
        problems.append("portail")

    # Pas d’image
    if not re.search(r'\[\[(Fichier|Image):', text, re.IGNORECASE):
        problems.append("illustrer")

    return problems

def add_maintenance_tag(page, problems):
    """Ajoute le modèle {{Maintenance}} avec les jobs manquants, si nécessaire."""
    try:
        content = page.text
    except Exception as e:
        print(f"❌ Erreur en lisant {page.title()}: {e}")
        return

    if "{{Maintenance" in content:
        print(f"⚠️ Maintenance déjà présente dans {page.title()}, on saute.")
        return

    if "#REDIRECTION" in content:
        print(f"⚠️ {page.title()} est une page de redirection")
        return

    if "#REDIRECT" in content:
        print(f"⚠️ {page.title()} est une page de redirection")
        return

    job_list = ', '.join(problems)
    maintenance_template = f"{{{{Maintenance|job={job_list}|~~~~~}}}}\n"
    new_text = maintenance_template + content

    try:
        page.put(new_text, summary="Ajout du modèle {{Maintenance}}", minor=False)
        print(f"✅ Ajouté à {page.title()} : {job_list}")
    except Exception as e:
        print(f"❌ Erreur en sauvegardant {page.title()}: {e}")

new_pages = site.recentchanges(
    reverse=True,
    changetype="new",
    namespaces=[0],  # espace de noms principal (articles)
    total=50  # par exemple 50 dernières pages créées
)

# Parcours des pages
for change in new_pages:
    title = change['title']  # <- accéder par clé dans le dict
    page = pywikibot.Page(site, title)
    if page.exists():
        problems = detect_problems(page.text)
        if problems:
            add_maintenance_tag(page, problems)
        else:
            print(f"✅ Aucun problème détecté dans {title}")
    else:
        print(f"❌ La page {title} n'existe plus.")
