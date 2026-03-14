# -*- mode: python ; coding: utf-8 -*-
# ============================================================
#  commandes_linux.spec  —  PyInstaller spec (v2)
#  Compatible Windows & Linux (one-file, windowed)
# ============================================================

import os
from pathlib import Path

# Racine du projet = dossier contenant ce .spec
ROOT = Path(SPECPATH)

block_cipher = None

a = Analysis(
    [str(ROOT / "main.py")],
    pathex=[str(ROOT)],
    binaries=[],
    # ------------------------------------------------------------------
    # Données embarquées dans l'exécutable.
    # Format : (source, destination_dans_bundle)
    # commandes.json est en lecture seule (base officielle).
    # Les autres JSON (perso, config, scores) sont écrits à l'exécution
    # dans le répertoire courant — ils ne sont PAS embarqués.
    # ------------------------------------------------------------------
    datas=[
        (str(ROOT / "commandes.json"),   "."),
        (str(ROOT / "categories.json"),  "."),
        # Décommente la ligne suivante si tu as une icône favicon.ico
        # (str(ROOT / "favicon.ico"),    "."),
    ],
    hiddenimports=[
        # Modules tkinter parfois manquants selon la plateforme
        "tkinter",
        "tkinter.ttk",
        "tkinter.messagebox",
        "tkinter.simpledialog",
        # Encodages JSON
        "json",
        "datetime",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclusions explicites pour alléger le bundle
        "matplotlib",
        "numpy",
        "pandas",
        "PIL",
        "scipy",
        "pytest",
        "setuptools",
        "email",
        "html",
        "http",
        "urllib",
        "xml",
        "xmlrpc",
        "unittest",
        "doctest",
        "pdb",
        "profile",
        "pstats",
        "difflib",
        "pickle",
        "shelve",
        "dbm",
        "sqlite3",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="CommandesLinux_v2",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,            # compression UPX si disponible (réduit la taille)
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,       # pas de fenêtre console (windowed)
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # Icône — décommente et adapte le chemin si tu as un .ico / .icns
    # icon=str(ROOT / "favicon.ico"),
)
