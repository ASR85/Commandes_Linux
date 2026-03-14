# 🐧 CommandesLinux — Guide de Build v2

## Structure du projet

```
CommandesLinux/
├── main.py
├── build.py                  ← script de build automatisé
├── commandes_linux.spec      ← configuration PyInstaller
├── commandes.json            ← base officielle (embarquée dans l'exe)
├── categories.json           ← catégories par défaut (embarquée)
├── commandes_personnelles.json
├── scores.json
├── config.json
├── favicon.ico               ← (optionnel) icône de l'exe
├── app/
│   ├── __init__.py
│   ├── application.py
│   ├── dialogs.py
│   ├── quiz.py
│   └── theme_utils.py
└── data/
    ├── __init__.py
    └── data.py
```

---

## Prérequis

| OS       | Prérequis                                      |
|----------|------------------------------------------------|
| Windows  | Python 3.9+ (avec `tkinter` inclus par défaut) |
| Linux    | Python 3.9+ + `python3-tk`                     |

### Installer tkinter sur Linux

```bash
# Debian / Ubuntu / Kali
sudo apt install python3-tk

# Fedora
sudo dnf install python3-tkinter

# Arch
sudo pacman -S tk
```

> ⚠️ **Important** : l'exécutable généré sur Windows ne fonctionnera que sur Windows, et vice-versa. Il faut builder sur chaque OS cible.

---

## Build rapide

```bash
# 1. Se placer dans le dossier du projet
cd CommandesLinux

# 2. Lancer le build (installe PyInstaller automatiquement si absent)
python build.py

# 3. L'exécutable est dans dist/
#   Windows : dist/CommandesLinux_v2.exe
#   Linux   : dist/CommandesLinux_v2
```

### Options

```bash
python build.py --clean    # supprime dist/ et build/ avant de recompiler
```

---

## Build manuel (sans build.py)

```bash
pip install pyinstaller

pyinstaller --clean --noconfirm commandes_linux.spec
```

---

## Fichiers générés après le build

```
dist/
├── CommandesLinux_v2(.exe)       ← exécutable standalone
├── commandes_personnelles.json   ← pré-copié (créé au 1er lancement sinon)
└── scores.json                   ← pré-copié (créé au 1er lancement sinon)
```

> `commandes.json` et `categories.json` sont **embarqués** dans l'exécutable
> (via `ressource_path()`). Les fichiers de données utilisateur (`config.json`,
> `commandes_personnelles.json`, `scores.json`) sont écrits dans le **répertoire
> courant** à l'exécution, pas dans l'exe.

---

## Ajouter une icône personnalisée

1. Placer `favicon.ico` à la racine du projet.
2. Dans `commandes_linux.spec`, décommenter les deux lignes marquées `favicon.ico` :

```python
datas=[
    ...
    (str(ROOT / "favicon.ico"), "."),   # ← décommenter
],
...
exe = EXE(
    ...
    icon=str(ROOT / "favicon.ico"),     # ← décommenter
)
```

3. Relancer `python build.py --clean`.

---

## Workflow Git recommandé

```bash
# Depuis la branche dev, une fois le build validé
git checkout dev
git add .
git commit -m "feat: v2 - tableau canvas emoji couleur, cross-platform"

# Merger dans main pour la release
git checkout main
git merge dev --no-ff -m "release: v2"
git tag v2.0.0
git push origin main --tags
```

---

## Réduction de la taille de l'exe

Le `.spec` exclut déjà `matplotlib`, `numpy`, `pandas`, etc.
Si UPX est installé sur la machine, PyInstaller l'utilise automatiquement
pour compresser l'exe (gain ~30%).

```bash
# Windows : https://upx.github.io/
# Linux
sudo apt install upx
```

---

## Dépannage

| Problème | Solution |
|----------|----------|
| `ModuleNotFoundError: tkinter` | Installer `python3-tk` (Linux) |
| L'exe ne trouve pas `commandes.json` | Vérifier que `ressource_path()` est utilisé dans `data.py` |
| Fenêtre noire qui s'ouvre/ferme immédiatement | Passer `console=True` dans le `.spec` pour voir l'erreur |
| Emojis en noir & blanc sur Linux | Installer `fonts-noto-color-emoji` : `sudo apt install fonts-noto-color-emoji` |
| Erreur `UPX is not available` | Ignorer (le build fonctionne sans), ou installer UPX |
