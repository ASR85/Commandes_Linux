import json
import os
import sys
import datetime

def ressource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

F_COMMANDS_OFF = ressource_path("commandes.json")
F_COMMANDS_PER = "commandes_personnelles.json"
F_CATEGORIES   = "categories.json"
F_CONFIG       = "config.json"
F_SCORES       = "scores.json"

def assurer_fichiers():
    defaults = {
        F_COMMANDS_OFF: {},  # rempli manuellement ou via ajout
        F_COMMANDS_PER: {},
        F_CATEGORIES: {
            "Fichiers": {"icone": "📂", "couleur": "#E8F5E9"},
            "Réseau": {"icone": "🔵", "couleur": "#DBEAFE"},
            "Système": {"icone": "⚙️", "couleur": "#FEF3F2"},
            "Utilisateurs": {"icone": "👥", "couleur": "#F3E8FF"},
            "Textes": {"icone": "📝", "couleur": "#E0F2FE"},
            "Archives": {"icone": "📦", "couleur": "#FFF7ED"},
            "Développement": {"icone": "🛠️", "couleur": "#ECFDF5"},
            "Sécurité": {"icone": "🛡️", "couleur": "#FEF2F2"},
            "Bases de données": {"icone": "🗄️", "couleur": "#F0FDF4"},
            "Général": {"icone": "💡", "couleur": "#FEFCE8"}
        },
        F_CONFIG: {"prenom": "", "nom": "", "mode_sombre": False},
        F_SCORES: []
    }

    for path, default in defaults.items():
        if not os.path.exists(path) or os.path.getsize(path) == 0:
            print(f"[INFO] Création/réinitialisation : {path}")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(default, f, indent=4, ensure_ascii=False)

def obtenir_commandes_completes():
    try:
        with open(F_COMMANDS_OFF, "r", encoding="utf-8") as f:
            cmds_off = json.load(f) or {}
        with open(F_COMMANDS_PER, "r", encoding="utf-8") as f:
            cmds_per = json.load(f) or {}
        toutes = {**cmds_off, **cmds_per}

        categories = obtenir_categories()
        icones = {cat: data["icone"] for cat, data in categories.items() if "icone" in data}
        couleurs = {cat: data["couleur"] for cat, data in categories.items() if "couleur" in data}

        return {
            "commandes": toutes,
            "icones": icones,
            "couleurs": couleurs,
            "categories": categories
        }
    except Exception as e:
        print(f"[ERREUR] obtenir_commandes_completes: {e}")
        return {"commandes": {}, "icones": {}, "couleurs": {}, "categories": {}}

def obtenir_categories():
    try:
        with open(F_CATEGORIES, "r", encoding="utf-8") as f:
            return json.load(f) or {}
    except:
        return {}

def sauvegarder_categories(categories):
    with open(F_CATEGORIES, "w", encoding="utf-8") as f:
        json.dump(categories, f, indent=4, ensure_ascii=False)

def ajouter_categorie(nom, icone, couleur):
    cats = obtenir_categories()
    nom = nom.strip().capitalize()
    cats[nom] = {"icone": icone, "couleur": couleur}
    sauvegarder_categories(cats)

def obtenir_commandes_perso():
    try:
        with open(F_COMMANDS_PER, "r", encoding="utf-8") as f:
            return json.load(f) or {}
    except:
        return {}

def ajouter_commande(nom, description, exemple, categorie, icone="📦", couleur="#FFFFFF"):
    try:
        perso = obtenir_commandes_perso()
        key = nom.strip().lower()
        perso[key] = {
            "description": description.strip(),
            "exemple": exemple.strip(),
            "categorie": categorie.strip(),
            "icone": icone,
            "couleur": couleur
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

        now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        pourcentage = f"{round((score / total) * 100) if total > 0 else 0}%"

        scores.append({
            "date_complete": now,
            "quizz_type": quizz_type,
            "score": score,
            "total": total,
            "pourcentage": pourcentage
        })

        with open(F_SCORES, "w", encoding="utf-8") as f:
            json.dump(scores, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"[ERREUR] sauvegarde score : {e}")