import json
import os
import sys


def ressource_path(relative_path):
    """Gestion des chemins pour PyInstaller (fichiers inclus dans l'EXE)"""
    try:
        base_path = sys._MEIPASS # noqa
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# F_OFF est inclus DANS l'exécutable (Lecture seule)
F_OFF = ressource_path("commandes.json")

# F_PER est à CÔTÉ de l'exécutable (Lecture/Écriture pour l'utilisateur)
F_PER = "commandes_personnelles.json"


def assurer_fichiers():
    """Vérifie que les fichiers nécessaires existent au lancement."""
    # Le fichier OFF est normalement géré par l'installeur,
    # mais on s'assure que l'application ne s'arrête pas s'il manque.
    if not os.path.exists(F_OFF):
        with open(F_OFF, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=4, ensure_ascii=False)

    if not os.path.exists(F_PER):
        with open(F_PER, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=4, ensure_ascii=False)


def obtenir_commandes_completes():
    assurer_fichiers()

    try:
        with open(F_OFF, "r", encoding="utf-8") as f:
            cmds = json.load(f)

        with open(F_PER, "r", encoding="utf-8") as f:
            cmds_perso = json.load(f)

        # Fusion des deux dictionnaires
        cmds.update(cmds_perso)

        # Extraction dynamique des icônes par catégorie
        icones = {}
        for info in cmds.values():
            cat = info.get("categorie")
            ico = info.get("icone")
            if cat and ico:
                icones[cat] = ico

        return {"commandes": cmds, "icones": icones}

    except Exception as e:
        print(f"Erreur fusion : {e}")
        return {"commandes": {}, "icones": {}}


def obtenir_commandes_perso():
    try:
        with open(F_PER, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


def ajouter_commande(n, d, e, c, icone="📦"):
    try:
        p = obtenir_commandes_perso()
        # Stockage en minuscule pour un tri et une recherche fiable
        nom_propre = n.strip().lower()

        p[nom_propre] = {"description": d, "exemple": e, "categorie": c, "icone": icone}

        with open(F_PER, "w", encoding="utf-8") as f:
            json.dump(p, f, indent=4, ensure_ascii=False)
        return True
    except:
        return False


def supprimer_commande(n):
    try:
        p = obtenir_commandes_perso()
        cible = n.strip().lower()
        if cible in p:
            del p[cible]
            with open(F_PER, "w", encoding="utf-8") as f:
                json.dump(p, f, indent=4, ensure_ascii=False)
            return True
        return False
    except:
        return False
