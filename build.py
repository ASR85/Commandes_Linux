#!/usr/bin/env python3
"""
build.py  —  Script de build automatisé pour CommandesLinux v2
--------------------------------------------------------------
Usage :
    python build.py              # build normal
    python build.py --clean      # supprime dist/ et build/ avant de compiler

Prérequis : Python 3.9+ avec tkinter installé.
PyInstaller sera installé automatiquement s'il est absent.
"""

import subprocess
import sys
import os
import shutil
import argparse
from pathlib import Path

ROOT    = Path(__file__).parent.resolve()
SPEC    = ROOT / "commandes_linux.spec"
DIST    = ROOT / "dist"
BUILD   = ROOT / "build"

# ── Couleurs terminal (désactivées sur Windows si pas de support ANSI) ────────
USE_COLOR = sys.platform != "win32" or os.environ.get("TERM")
def c(code, text): return f"\033[{code}m{text}\033[0m" if USE_COLOR else text
OK   = lambda t: print(c("32;1", f"  ✔  {t}"))
ERR  = lambda t: print(c("31;1", f"  ✘  {t}"), file=sys.stderr)
INFO = lambda t: print(c("36",   f"  ➜  {t}"))
HEAD = lambda t: print(c("35;1", f"\n{'─'*55}\n  {t}\n{'─'*55}"))


def run(cmd, **kwargs):
    """Lance une commande et lève une exception si elle échoue."""
    INFO(f"$ {' '.join(str(x) for x in cmd)}")
    result = subprocess.run(cmd, **kwargs)
    if result.returncode != 0:
        ERR(f"Commande échouée (code {result.returncode})")
        sys.exit(result.returncode)
    return result


def ensure_pyinstaller():
    HEAD("Vérification de PyInstaller")
    try:
        import PyInstaller
        OK(f"PyInstaller {PyInstaller.__version__} déjà installé")
    except ImportError:
        INFO("PyInstaller absent — installation en cours...")
        run([sys.executable, "-m", "pip", "install", "--quiet", "pyinstaller"])
        OK("PyInstaller installé")


def check_tkinter():
    HEAD("Vérification de Tkinter")
    try:
        import tkinter
        OK(f"Tkinter OK ({tkinter.TkVersion})")
    except ImportError:
        ERR("Tkinter est absent !")
        if sys.platform.startswith("linux"):
            ERR("Sur Debian/Ubuntu : sudo apt install python3-tk")
            ERR("Sur Fedora        : sudo dnf install python3-tkinter")
        sys.exit(1)


def check_files():
    HEAD("Vérification des fichiers requis")
    required = ["main.py", "commandes.json", "categories.json",
                "app/__init__.py", "app/application.py", "app/dialogs.py",
                "app/quiz.py", "app/theme_utils.py",
                "data/__init__.py", "data/data.py"]
    all_ok = True
    for f in required:
        p = ROOT / f
        if p.exists():
            OK(f"{f}")
        else:
            ERR(f"{f}  ← MANQUANT")
            all_ok = False
    if not all_ok:
        ERR("Des fichiers sont manquants. Vérifiez la structure du projet.")
        sys.exit(1)


def clean():
    HEAD("Nettoyage")
    for d in [DIST, BUILD]:
        if d.exists():
            shutil.rmtree(d)
            OK(f"Supprimé : {d}")
    # Supprimer aussi les __pycache__
    for p in ROOT.rglob("__pycache__"):
        shutil.rmtree(p)
    OK("__pycache__ nettoyés")


def build():
    HEAD("Compilation PyInstaller")
    run([
        sys.executable, "-m", "PyInstaller",
        "--clean",           # force un build propre
        "--noconfirm",       # écrase dist/ sans demander
        str(SPEC),
    ], cwd=ROOT)


def post_build():
    HEAD("Post-build")

    exe_name = "CommandesLinux_v2"
    if sys.platform == "win32":
        exe_path = DIST / f"{exe_name}.exe"
    else:
        exe_path = DIST / exe_name

    if not exe_path.exists():
        ERR(f"Exécutable introuvable : {exe_path}")
        sys.exit(1)

    size_mb = exe_path.stat().st_size / (1024 * 1024)
    OK(f"Exécutable généré : {exe_path}")
    OK(f"Taille            : {size_mb:.1f} Mo")

    # Copier les fichiers JSON écrits à l'exécution à côté de l'exe
    # (config.json, scores.json, commandes_personnelles.json)
    # → ils seront créés automatiquement au premier lancement,
    #   mais on les pré-copie pour éviter des erreurs sur certaines configs.
    runtime_jsons = [
        "commandes_personnelles.json",
        "scores.json",
    ]
    for fname in runtime_jsons:
        src = ROOT / fname
        dst = DIST / fname
        if src.exists() and not dst.exists():
            shutil.copy2(src, dst)
            INFO(f"Copié à côté de l'exe : {fname}")

    print()
    HEAD("Build terminé 🎉")
    print(f"  Exécutable : {exe_path}")
    print(f"  Dossier    : {DIST}\n")


def main():
    parser = argparse.ArgumentParser(description="Build CommandesLinux v2")
    parser.add_argument("--clean", action="store_true",
                        help="Supprime dist/ et build/ avant de compiler")
    args = parser.parse_args()

    print(c("35;1", "\n  CommandesLinux v2 — Build Script"))
    print(c("35",   "  ===================================\n"))

    check_tkinter()
    check_files()
    ensure_pyinstaller()

    if args.clean:
        clean()

    build()
    post_build()


if __name__ == "__main__":
    main()
