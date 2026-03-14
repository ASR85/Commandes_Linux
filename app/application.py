import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import sys

from data.data import (
    obtenir_commandes_completes, obtenir_commandes_perso,
    ajouter_commande, supprimer_commande,
    ressource_path, F_CONFIG,
)
from app.dialogs import (
    demander_profil, ouvrir_aide, ouvrir_parametres,
    ouvrir_ajout, ouvrir_suppression, ouvrir_statistiques,
)
from app.quiz import lancer_quiz_pre, quitter_quiz
from app.theme_utils import (
    appliquer_theme, basculer_theme, reinitialiser_application,
    nettoyer_recherche, centrer_fenetre,
)

ROW_H = 28  # hauteur d'une ligne du tableau canvas


# ─────────────────────────────────────────────────────────────────────────────
# Tableau 100 % Canvas — emojis couleur garantis sur Windows ET Linux
# ─────────────────────────────────────────────────────────────────────────────

class TableauCanvas(tk.Frame):
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, bg=parent["bg"])
        self._app      = app
        self._lignes   = []
        self._sel_idx  = None
        self._sort_rev = {"cmd": False, "cat": False}

        # En-têtes
        hdr = tk.Frame(self, bg="#312E81")
        hdr.pack(fill="x")
        self._hdr = hdr

        self._btn_cmd = tk.Button(
            hdr, text="COMMANDE ↑",
            font=("Segoe UI", 10, "bold"), bg="#312E81", fg="white",
            relief="flat", anchor="w", padx=10, width=22,
            command=lambda: self.trier("cmd"),
        )
        self._btn_cmd.pack(side="left")

        tk.Frame(hdr, width=1, bg="#ffffff").pack(side="left", fill="y")

        self._btn_cat = tk.Button(
            hdr, text="CATÉGORIE ↑",
            font=("Segoe UI", 10, "bold"), bg="#312E81", fg="white",
            relief="flat", anchor="center", padx=10,
            command=lambda: self.trier("cat"),
        )
        self._btn_cat.pack(side="left", fill="x", expand=True)

        # Canvas + scrollbar
        body = tk.Frame(self)
        body.pack(fill="both", expand=True)

        self._canvas = tk.Canvas(body, highlightthickness=0, width=390)
        self._scroll = tk.Scrollbar(body, orient="vertical", command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=self._scroll.set)
        self._canvas.pack(side="left", fill="both", expand=True)
        self._scroll.pack(side="right", fill="y")

        self._canvas.bind("<Configure>",  lambda e: self._draw())
        self._canvas.bind("<Button-1>",   self._on_click)
        self._canvas.bind("<MouseWheel>", self._on_wheel)
        self._canvas.bind("<Button-4>",   self._on_wheel)
        self._canvas.bind("<Button-5>",   self._on_wheel)

    # ── API publique ──────────────────────────────────────────

    def set_lignes(self, lignes):
        self._lignes  = lignes
        self._sel_idx = None
        self._canvas.yview_moveto(0)
        self._draw()

    def trier(self, col):
        self._sort_rev[col] = not self._sort_rev[col]
        self._lignes.sort(key=lambda r: r[col].lower(), reverse=self._sort_rev[col])
        sym = " ↓" if self._sort_rev[col] else " ↑"
        self._btn_cmd["text"] = f"COMMANDE{sym if col == 'cmd' else ' ↑'}"
        self._btn_cat["text"] = f"CATÉGORIE{sym if col == 'cat' else ' ↑'}"
        self._draw()

    def appliquer_theme(self, accent, border, card):
        self._hdr.config(bg=accent)
        self._btn_cmd.config(bg=accent)
        self._btn_cat.config(bg=accent)
        self._canvas.config(bg=card)
        self._scroll.config(bg=card)
        self._draw()

    # ── Rendu ─────────────────────────────────────────────────

    def _draw(self):
        c   = self._canvas
        app = self._app
        c.delete("all")

        w       = c.winfo_width() or 390
        ico_w   = 28
        cmd_w   = 220
        sep_x   = ico_w + cmd_w
        total_h = max(len(self._lignes) * ROW_H, 1)
        c.configure(scrollregion=(0, 0, w, total_h))

        font_normal = ("Segoe UI", 10)
        font_emoji  = ("Segoe UI", 13)

        for i, row in enumerate(self._lignes):
            y0 = i * ROW_H
            y1 = y0 + ROW_H
            yc = y0 + ROW_H // 2

            bg = app.c_accent if i == self._sel_idx else row["bg"]
            fg = "white"      if i == self._sel_idx else row["fg"]

            c.create_rectangle(0, y0, w, y1, fill=bg, outline="")
            c.create_line(0, y1 - 1, w, y1 - 1, fill=app.c_border)
            c.create_text(ico_w // 2 + 2, yc, text=row["ico"], font=font_emoji,  fill=fg, anchor="center")
            c.create_line(ico_w, y0, ico_w, y1, fill=app.c_border)
            c.create_text(ico_w + 8,      yc, text=row["cmd"], font=font_normal, fill=fg, anchor="w")
            c.create_line(sep_x, y0, sep_x, y1, fill=app.c_border)
            cat_cx = sep_x + (w - sep_x) // 2
            c.create_text(cat_cx, yc, text=row["cat"], font=font_normal, fill=fg, anchor="center")

    # ── Événements ────────────────────────────────────────────

    def _on_click(self, event):
        y_abs = self._canvas.canvasy(event.y)
        idx   = int(y_abs // ROW_H)
        if 0 <= idx < len(self._lignes):
            self._sel_idx = idx
            self._draw()
            self._app.afficher_details_depuis_canvas(self._lignes[idx]["cmd"])

    def _on_wheel(self, event):
        if event.delta:
            self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        elif event.num == 4:
            self._canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self._canvas.yview_scroll(1, "units")


# ─────────────────────────────────────────────────────────────────────────────

class ApplicationLinux:
    def __init__(self, root):
        self.root = root
        self.root.title("🐧 Commandes Linux")
        self.root.withdraw()

        try:
            self.root.iconbitmap(ressource_path("favicon.ico"))
        except Exception:
            pass

        # F_CONFIG est le chemin correct (runtime_path) dans data.py
        # On l'utilise partout pour la cohérence exe/dev
        from data.data import F_CONFIG
        self.config_file = F_CONFIG

        self.utilisateur = self.charger_profil()
        if self.utilisateur is None:
            self.root.destroy()
            return

        self.mode_sombre = self.utilisateur.get("mode_sombre", False)
        self.largeur, self.hauteur = 1050, 800
        centrer_fenetre(self, self.root, self.largeur, self.hauteur)
        self.quiz_en_cours = False

        self.categories = [
            "Fichiers", "Réseau", "Système", "Utilisateurs", "Textes",
            "Archives", "Développement", "Sécurité", "Bases de données", "Général",
        ]

        self.icones = {
            "Réseau": "🔵", "Système": "⚙️", "Fichiers": "📂",
            "Sécurité": "🛡️", "Perso": "👤", "Général": "💡",
            "Utilisateurs": "👥", "Textes": "📝", "Archives": "📦",
            "Développement": "🛠️", "Bases de données": "🗄️",
        }

        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.construire_interface()
        appliquer_theme(self)

        self.actualiser_tableau()
        self.tableau.trier("cmd")
        self.root.deiconify()

    # ── Profil ────────────────────────────────────────────────

    def charger_profil(self):
        if not os.path.exists(self.config_file):
            return demander_profil(self)
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data if data.get("prenom") else demander_profil(self)
        except Exception:
            return demander_profil(self)

    # ── Interface ─────────────────────────────────────────────

    def construire_interface(self):
        # En-tête
        self.entete = tk.Frame(self.root, pady=20)
        self.entete.pack(fill="x")
        self.lbl_titre = tk.Label(self.entete, text="🐧 Commandes Linux", font=("Segoe UI", 22, "bold"))
        self.lbl_titre.pack(side="left", padx=30)
        self.cadre_profil = tk.Frame(self.entete)
        self.cadre_profil.pack(side="right", padx=30)
        user_txt = f"👤 {self.utilisateur['prenom'].capitalize()} {self.utilisateur['nom'].upper()}"
        self.lbl_user = tk.Label(self.cadre_profil, text=user_txt, font=("Segoe UI", 10, "bold"))
        self.lbl_user.pack()

        # Barre bas
        self.bas_page = tk.Frame(self.root, pady=15, highlightthickness=1)
        self.bas_page.pack(fill="x", side="bottom")
        bf = ("Segoe UI", 9, "bold")
        tk.Button(self.bas_page, text="🎯 QUIZ",          bg="#10B981", fg="white", font=bf, padx=20, pady=8, relief="flat", command=lambda: lancer_quiz_pre(self)).pack(side="left", padx=20)
        tk.Button(self.bas_page, text="💡 AIDE",          bg="#6B7280", fg="white", font=bf, padx=15, pady=8, relief="flat", command=lambda: ouvrir_aide(self)).pack(side="left", padx=5)
        tk.Button(self.bas_page, text="⚙️ PARAMÈTRES",   bg="#4B5563", fg="white", font=bf, padx=15, pady=8, relief="flat", command=lambda: ouvrir_parametres(self)).pack(side="left", padx=5)
        tk.Button(self.bas_page, text="📊 STATISTIQUES",  bg="#3B82F6", fg="white", font=bf, padx=15, pady=8, relief="flat", command=lambda: ouvrir_statistiques(self)).pack(side="left", padx=5)
        tk.Button(self.bas_page, text="➕ AJOUTER",       bg="#6366F1", fg="white", font=bf, padx=15, pady=8, relief="flat", command=lambda: ouvrir_ajout(self)).pack(side="right", padx=10)
        tk.Button(self.bas_page, text="🗑️ SUPPRIMER",    bg="#EF4444", fg="white", font=bf, padx=15, pady=8, relief="flat", command=lambda: ouvrir_suppression(self)).pack(side="right", padx=10)

        # Recherche
        self.zone_recherche = tk.Frame(self.root, pady=15)
        self.zone_recherche.pack(fill="x", padx=30)
        self.cadre_saisie = tk.Frame(self.zone_recherche, highlightthickness=1)
        self.cadre_saisie.pack(fill="x", padx=10)
        self.lbl_loupe = tk.Label(self.cadre_saisie, text=" 🔍 ", font=("Segoe UI", 12))
        self.lbl_loupe.pack(side="left", padx=5)
        self.champ_recherche = tk.Entry(self.cadre_saisie, font=("Segoe UI", 11), relief="flat")
        self.champ_recherche.insert(0, "Rechercher une commande ou une catégorie...")
        self.champ_recherche.pack(side="left", fill="x", expand=True, ipady=10)
        self.champ_recherche.bind("<FocusIn>",    lambda e: nettoyer_recherche(self, e))
        self.champ_recherche.bind("<KeyRelease>", lambda e: self.actualiser_tableau(self.champ_recherche.get()))

        # Corps
        self.corps = tk.Frame(self.root)
        self.corps.pack(fill="both", expand=True, padx=30, pady=10)

        # Tableau (gauche)
        self.cadre_liste = tk.Frame(self.corps, highlightthickness=1)
        self.cadre_liste.pack(side="left", fill="both")
        self.tableau = TableauCanvas(self.cadre_liste, app=self)
        self.tableau.pack(fill="both", expand=True)

        # Détails (droite)
        self.cadre_details = tk.Frame(self.corps, highlightthickness=1, padx=25, pady=25)
        self.cadre_details.pack(side="right", fill="both", expand=True, padx=(25, 0))
        self.zone_affichage = tk.Text(
            self.cadre_details, font=("Segoe UI", 11),
            relief="flat", wrap="word", state="disabled",
        )
        self.zone_affichage.pack(fill="both", expand=True)
        self.cadre_quiz = tk.Frame(self.cadre_details)

    # ── Données ───────────────────────────────────────────────

    def actualiser_tableau(self, recherche=""):
        if recherche == "Rechercher une commande ou une catégorie...":
            recherche = ""

        data = obtenir_commandes_completes()
        self.donnees  = data["commandes"]
        self.couleurs = data["couleurs"]
        self.icones.update(data.get("icones", {}))

        lignes = []
        for nom in sorted(self.donnees.keys()):
            info = self.donnees[nom]
            cat  = info.get("categorie", "Général")
            if recherche.lower() in nom.lower() or recherche.lower() in cat.lower():
                lignes.append({
                    "cmd": nom.strip().upper(),
                    "cat": cat,
                    "ico": self.icones.get(cat, info.get("icone", "📦")),
                    "bg":  self.couleurs.get(cat, "#FFFFFF"),
                    "fg":  "#111827",
                })
        self.tableau.set_lignes(lignes)

    # ── Affichage détail ──────────────────────────────────────

    def afficher_details_depuis_canvas(self, nom_cmd):
        """Appelé par TableauCanvas sur clic."""
        if not self.quiz_en_cours:
            self._afficher_details_nom(nom_cmd)

    def afficher_details(self, _event):
        """Alias conservé pour quitter_quiz()."""
        self._afficher_details_nom(None)

    def _afficher_details_nom(self, nom_extrait):
        self.quiz_en_cours = False
        self.cadre_quiz.pack_forget()
        self.zone_affichage.pack(fill="both", expand=True)

        if nom_extrait is None:
            return

        nom_extrait = nom_extrait.strip()
        data = obtenir_commandes_completes()
        self.donnees = data["commandes"]

        info, nom_reel = None, nom_extrait
        for cle in self.donnees:
            if cle.lower() == nom_extrait.lower():
                info, nom_reel = self.donnees[cle], cle
                break
        if info is None:
            return

        self.zone_affichage.config(state="normal")
        self.zone_affichage.delete("1.0", tk.END)

        self.zone_affichage.tag_config("titre",    font=("Segoe UI", 26, "bold"), foreground=self.c_accent)
        self.zone_affichage.tag_config("label",    font=("Segoe UI", 10, "bold"), foreground="#9CA3AF")
        self.zone_affichage.tag_config("terminal", font=("Consolas", 12, "bold"), background="#000000", foreground="#10B981")

        ico = info.get("icone", "📂")
        self.zone_affichage.insert(tk.END, f"{ico} {nom_reel.upper()}\n",                       "titre")
        self.zone_affichage.insert(tk.END, f"\n📂 CATÉGORIE : {info.get('categorie','N/A')}\n", "label")
        self.zone_affichage.insert(tk.END, "\n📌 DESCRIPTION\n",                                "label")
        self.zone_affichage.insert(tk.END, f"{info.get('description', '')}\n\n")
        self.zone_affichage.insert(tk.END, "💻 TERMINAL SIMULATION\n",                          "label")
        self.zone_affichage.insert(tk.END, "\n")

        u  = self.utilisateur.get("prenom", "user").lower()
        n  = self.utilisateur.get("nom",    "linux").lower()
        prompt = f" {u}.{n}@linux:~$ {info.get('exemple', '')} "
        self.zone_affichage.insert(tk.END, f"{prompt}\n", "terminal")
        self.zone_affichage.config(state="disabled")