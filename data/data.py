import json
import os
import sys
import datetime


def ressource_path(relative_path):
    """
    Retourne le chemin absolu vers un fichier embarqué dans l'exe (via _MEIPASS)
    ou dans le répertoire courant en mode développement.
    Utilisé pour les fichiers READ-ONLY : commandes.json, categories.json, favicon.ico
    """
    try:
        base_path = sys._MEIPASS          # dans l'exe PyInstaller
    except AttributeError:
        base_path = os.path.abspath(".")  # en développement
    return os.path.join(base_path, relative_path)


def runtime_path(relative_path):
    """
    Retourne le chemin absolu vers un fichier de données UTILISATEUR.
    Ces fichiers sont créés/modifiés à l'exécution, à côté de l'exe
    (ou dans le répertoire courant en développement).
    Utilisé pour : config.json, scores.json, commandes_personnelles.json
    """
    if getattr(sys, "frozen", False):
        # Mode exe : écrire à côté de l'exécutable, pas dans _MEIPASS (read-only)
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# ── Chemins des fichiers ──────────────────────────────────────────────────────

# Lecture seule — embarqués dans l'exe
F_COMMANDS_OFF = ressource_path("commandes.json")
F_CATEGORIES_RO = ressource_path("categories.json")   # version embarquée (fallback)

# Lecture/écriture — à côté de l'exe ou dans le dossier courant
F_COMMANDS_PER = runtime_path("commandes_personnelles.json")
F_CATEGORIES   = runtime_path("categories.json")       # copie locale modifiable
F_CONFIG       = runtime_path("config.json")
F_SCORES       = runtime_path("scores.json")


def assurer_fichiers():
    """
    Crée les fichiers runtime manquants au premier lancement.
    - categories.json : copié depuis la version embarquée si absent
    - Les autres sont initialisés avec des valeurs par défaut
    """

    # categories.json : on part de la version embarquée si disponible
    if not os.path.exists(F_CATEGORIES) or os.path.getsize(F_CATEGORIES) == 0:
        if os.path.exists(F_CATEGORIES_RO):
            import shutil
            shutil.copy2(F_CATEGORIES_RO, F_CATEGORIES)
            print(f"[INFO] Copié depuis le bundle : {F_CATEGORIES}")
        else:
            # Fallback si même la version embarquée est absente
            categories_defaut = {
                "Fichiers":       {"icone": "📂", "couleur": "#E8F5E9"},
                "Réseau":         {"icone": "🔵", "couleur": "#DBEAFE"},
                "Système":        {"icone": "⚙️", "couleur": "#FEF3F2"},
                "Utilisateurs":   {"icone": "👥", "couleur": "#F3E8FF"},
                "Textes":         {"icone": "📝", "couleur": "#E0F2FE"},
                "Archives":       {"icone": "📦", "couleur": "#FFF7ED"},
                "Développement":  {"icone": "🛠️", "couleur": "#ECFDF5"},
                "Sécurité":       {"icone": "🛡️", "couleur": "#FEF2F2"},
                "Bases de données":{"icone": "🗄️", "couleur": "#F0FDF4"},
                "Général":        {"icone": "💡", "couleur": "#FEFCE8"},
            }
            with open(F_CATEGORIES, "w", encoding="utf-8") as f:
                json.dump(categories_defaut, f, indent=4, ensure_ascii=False)
            print(f"[INFO] Créé par défaut : {F_CATEGORIES}")

    # Autres fichiers runtime
    defaults_runtime = {
        F_COMMANDS_PER: {},
        F_CONFIG:       {"prenom": "", "nom": "", "mode_sombre": False},
        F_SCORES:       [],
    }
    for path, default in defaults_runtime.items():
        if not os.path.exists(path) or os.path.getsize(path) == 0:
            print(f"[INFO] Création : {path}")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(default, f, indent=4, ensure_ascii=False)


# ── Lecture des données ───────────────────────────────────────────────────────

def obtenir_commandes_completes():
    try:
        with open(F_COMMANDS_OFF, "r", encoding="utf-8") as f:
            cmds_off = json.load(f) or {}
        with open(F_COMMANDS_PER, "r", encoding="utf-8") as f:
            cmds_per = json.load(f) or {}
        toutes = {**cmds_off, **cmds_per}

        categories = obtenir_categories()
        icones  = {cat: d["icone"]  for cat, d in categories.items() if "icone"  in d}
        couleurs = {cat: d["couleur"] for cat, d in categories.items() if "couleur" in d}

        return {
            "commandes":  toutes,
            "icones":     icones,
            "couleurs":   couleurs,
            "categories": categories,
        }
    except Exception as e:
        print(f"[ERREUR] obtenir_commandes_completes: {e}")
        return {"commandes": {}, "icones": {}, "couleurs": {}, "categories": {}}


def obtenir_categories():
    try:
        with open(F_CATEGORIES, "r", encoding="utf-8") as f:
            return json.load(f) or {}
    except Exception:
        return {}


def sauvegarder_categories(categories):
    with open(F_CATEGORIES, "w", encoding="utf-8") as f:
        json.dump(categories, f, indent=4, ensure_ascii=False)


def ajouter_categorie(nom, icone, couleur):
    cats = obtenir_categories()
    cats[nom.strip().capitalize()] = {"icone": icone, "couleur": couleur}
    sauvegarder_categories(cats)


def obtenir_commandes_perso():
    try:
        with open(F_COMMANDS_PER, "r", encoding="utf-8") as f:
            return json.load(f) or {}
    except Exception:
        return {}


def ajouter_commande(nom, description, exemple, categorie, icone="📦", couleur="#FFFFFF"):
    try:
        perso = obtenir_commandes_perso()
        perso[nom.strip().lower()] = {
            "description": description.strip(),
            "exemple":     exemple.strip(),
            "categorie":   categorie.strip(),
            "icone":       icone,
            "couleur":     couleur,
        }
        with open(F_COMMANDS_PER, "w", encoding="utf-8") as f:
            json.dump(perso, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"[ERREUR] ajout commande : {e}")
        return False


def supprimer_commande(nom):
    try:
        perso = obtenir_commandes_perso()
        key = nom.strip().lower()
        if key in perso:
            del perso[key]
            with open(F_COMMANDS_PER, "w", encoding="utf-8") as f:
                json.dump(perso, f, indent=4, ensure_ascii=False)
            return True
        return False
    except Exception as e:
        print(f"[ERREUR] suppression : {e}")
        return False


def enregistrer_score(score, total, quizz_type):
    try:
        scores = []
        if os.path.exists(F_SCORES) and os.path.getsize(F_SCORES) > 0:
            with open(F_SCORES, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    scores = json.loads(content)

        now        = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        pourcentage = f"{round((score / total) * 100) if total > 0 else 0}%"

        scores.append({
            "date_complete": now,
            "quizz_type":   quizz_type,
            "score":        score,
            "total":        total,
            "pourcentage":  pourcentage,
        })

        with open(F_SCORES, "w", encoding="utf-8") as f:
            json.dump(scores, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"[ERREUR] sauvegarde score : {e}")