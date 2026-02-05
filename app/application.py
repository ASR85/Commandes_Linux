import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import sys
import winshell
from win32com.client import Dispatch

from data.data import obtenir_commandes_completes, obtenir_commandes_perso, ajouter_commande, supprimer_commande, ressource_path
from app.dialogs import demander_profil, ouvrir_aide, ouvrir_parametres, ouvrir_ajout, ouvrir_suppression, ouvrir_statistiques
from app.quiz import lancer_quiz_pre, quitter_quiz
from app.theme_utils import appliquer_theme, basculer_theme, reinitialiser_application, nettoyer_recherche, centrer_fenetre

class ApplicationLinux:
    def __init__(self, root):
        self.root = root
        self.root.title("🐧 Commandes Linux")
        self.root.withdraw()

        try:
            chemin_ico = ressource_path("favicon.ico")
            self.root.iconbitmap(chemin_ico)
        except:
            pass

        self.config_file = "config.json"
        self.utilisateur = self.charger_profil()
        if self.utilisateur is None:
            self.root.destroy()
            return

        self.mode_sombre = self.utilisateur.get("mode_sombre", False)
        self.largeur, self.hauteur = 1050, 800
        centrer_fenetre(self, self.root, self.largeur, self.hauteur)
        self.quiz_en_cours = False
        self.ordre_tri = {"cmd": False, "cat": False}

        self.categories = [
            "Fichiers", "Réseau", "Système", "Utilisateurs", "Textes",
            "Archives", "Développement", "Sécurité", "Bases de données", "Général",
        ]

        self.icones = {
            "Réseau": "🔵",
            "Système": "⚙️",
            "Fichiers": "📂",
            "Sécurité": "🛡️",
            "Perso": "👤",
            "Général": "💡",
            "Utilisateurs": "👥",
            "Textes": "📝",
            "Archives": "📦",
            "Développement": "🛠️",
            "Bases de données": "🗄️",
        }

        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.construire_interface()
        appliquer_theme(self)

        self.actualiser_tableau()
        self.ordre_tri["cmd"] = True
        self.trier_colonne("cmd")

        self.root.deiconify()

    def creer_raccourci_bureau(self):
        try:
            desktop = winshell.desktop()
            path = os.path.join(desktop, "Commandes Linux.lnk")
            if not os.path.exists(path):
                target = sys.executable
                shell = Dispatch('WScript.Shell')
                shortcut = shell.CreateShortCut(path)
                shortcut.Targetpath = target
                shortcut.WorkingDirectory = os.path.dirname(target)
                shortcut.IconLocation = target
                shortcut.save()
        except Exception:
            pass

    def charger_profil(self):
        if not os.path.exists(self.config_file):
            return demander_profil(self)
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data if data.get("prenom") else demander_profil(self)
        except:
            return demander_profil(self)

    def construire_interface(self):
        self.entete = tk.Frame(self.root, pady=20)
        self.entete.pack(fill="x")
        self.lbl_titre = tk.Label(self.entete, text="🐧 Commandes Linux", font=("Segoe UI", 22, "bold"))
        self.lbl_titre.pack(side="left", padx=30)
        self.cadre_profil = tk.Frame(self.entete)
        self.cadre_profil.pack(side="right", padx=30)
        user_txt = f"👤 {self.utilisateur['prenom'].capitalize()} {self.utilisateur['nom'].upper()}"
        self.lbl_user = tk.Label(self.cadre_profil, text=user_txt, font=("Segoe UI", 10, "bold"))
        self.lbl_user.pack()

        self.bas_page = tk.Frame(self.root, pady=15, highlightthickness=1)
        self.bas_page.pack(fill="x", side="bottom")
        btn_f = ("Segoe UI", 9, "bold")
        tk.Button(self.bas_page, text="🎯 QUIZ", bg="#10B981", fg="white", font=btn_f, padx=20, pady=8,
                  command=lambda: lancer_quiz_pre(self), relief="flat").pack(side="left", padx=20)
        tk.Button(self.bas_page, text="💡 AIDE", bg="#6B7280", fg="white", font=btn_f, padx=15, pady=8,
                  command=lambda: ouvrir_aide(self), relief="flat").pack(side="left", padx=5)
        tk.Button(self.bas_page, text="⚙️ PARAMÈTRES", bg="#4B5563", fg="white", font=btn_f, padx=15, pady=8,
                  command=lambda: ouvrir_parametres(self), relief="flat").pack(side="left", padx=5)
        tk.Button(self.bas_page, text="📊 STATISTIQUES", bg="#3B82F6", fg="white", font=btn_f, padx=15, pady=8,
                  command=lambda: ouvrir_statistiques(self), relief="flat").pack(side="left", padx=5)
        tk.Button(self.bas_page, text="➕ AJOUTER", bg="#6366F1", fg="white", font=btn_f, padx=15, pady=8,
                  command=lambda: ouvrir_ajout(self), relief="flat").pack(side="right", padx=10)
        tk.Button(self.bas_page, text="🗑️ SUPPRIMER", bg="#EF4444", fg="white", font=btn_f, padx=15, pady=8,
                  command=lambda: ouvrir_suppression(self), relief="flat").pack(side="right", padx=10)

        self.zone_recherche = tk.Frame(self.root, pady=15)
        self.zone_recherche.pack(fill="x", padx=30)
        self.cadre_saisie = tk.Frame(self.zone_recherche, highlightthickness=1)
        self.cadre_saisie.pack(fill="x", padx=10)
        self.lbl_loupe = tk.Label(self.cadre_saisie, text=" 🔍 ", font=("Segoe UI", 12))
        self.lbl_loupe.pack(side="left", padx=5)
        self.champ_recherche = tk.Entry(self.cadre_saisie, font=("Segoe UI", 11), relief="flat")
        self.champ_recherche.insert(0, "Rechercher une commande ou une catégorie...")
        self.champ_recherche.pack(side="left", fill="x", expand=True, ipady=10)
        self.champ_recherche.bind("<FocusIn>", lambda e: nettoyer_recherche(self, e))
        self.champ_recherche.bind("<KeyRelease>", lambda e: self.actualiser_tableau(self.champ_recherche.get()))

        self.corps = tk.Frame(self.root)
        self.corps.pack(fill="both", expand=True, padx=30, pady=10)

        self.cadre_liste = tk.Frame(self.corps, highlightthickness=1)
        self.cadre_liste.pack(side="left", fill="both")

        self.tableau = ttk.Treeview(self.cadre_liste, columns=("cmd", "cat"), show="headings", height=15)
        self.tableau.heading("cmd", text="COMMANDE ↑", command=lambda: self.trier_colonne("cmd"))
        self.tableau.heading("cat", text="CATÉGORIE ↑", command=lambda: self.trier_colonne("cat"))
        self.tableau.column("cmd", width=260)
        self.tableau.column("cat", width=130, anchor="center")

        self.scroll_y = ttk.Scrollbar(self.cadre_liste, orient="vertical", command=self.tableau.yview)
        self.tableau.configure(yscrollcommand=self.scroll_y.set)
        self.tableau.pack(side="left", fill="both")
        self.scroll_y.pack(side="right", fill="y")
        self.tableau.bind("<<TreeviewSelect>>", self.gerer_clic_tableau)

        self.cadre_details = tk.Frame(self.corps, highlightthickness=1, padx=25, pady=25)
        self.cadre_details.pack(side="right", fill="both", expand=True, padx=(25, 0))

        self.zone_affichage = tk.Text(self.cadre_details, font=("Segoe UI", 11), relief="flat", wrap="word", state="disabled")
        self.zone_affichage.pack(fill="both", expand=True)

        self.cadre_quiz = tk.Frame(self.cadre_details)

    def actualiser_tableau(self, recherche=""):
        if recherche == "Rechercher une commande ou une catégorie...":
            recherche = ""

        data_totale = obtenir_commandes_completes()
        self.donnees = data_totale["commandes"]
        self.couleurs = data_totale["couleurs"]

        # Nettoyage complet du tableau
        for item in self.tableau.get_children():
            self.tableau.delete(item)

        # Tri alphabétique des commandes
        noms_tries = sorted(self.donnees.keys())

        for nom in noms_tries:
            info = self.donnees[nom]
            cat = info.get("categorie", "Général")

            if recherche.lower() in nom.lower() or recherche.lower() in cat.lower():
                tag = f"cat_{cat.replace(' ', '_').lower()}"
                # Insertion avec tag pour couleur
                iid = self.tableau.insert("", tk.END, values=(nom.strip().upper(), cat), tags=(tag,))

        # Application des couleurs APRÈS insertion (clé du fix)
        self.tableau.tag_configure("Treeview", background=self.c_card)  # fond par défaut
        self.configurer_couleurs_categories()

        # Forcer rafraîchissement visuel
        self.tableau.update_idletasks()

    def configurer_couleurs_categories(self):
        for cat, couleur in self.couleurs.items():
            tag = f"cat_{cat.replace(' ', '_').lower()}"
            # Couleur de fond normale pour la ligne
            self.tableau.tag_configure(tag, background=couleur)
            # Couleur quand sélectionnée (plus visible)
            self.tableau.tag_configure(tag + "_selected", background=self.c_accent, foreground="white")

    def configurer_couleurs_categories(self):
        for cat, couleur in self.couleurs.items():
            tag = f"cat_{cat.replace(' ', '_').lower()}"
            self.style.configure(tag, background=couleur)
            self.style.map(tag, background=[("selected", self.c_accent)], foreground=[("selected", "white")])

    def trier_colonne(self, col):
        self.ordre_tri[col] = not self.ordre_tri[col]
        lignes = []
        for k in self.tableau.get_children(""):
            valeur = str(self.tableau.set(k, col)).lower()
            lignes.append((valeur, k))
        lignes.sort(reverse=self.ordre_tri[col])
        for index, (_, k) in enumerate(lignes):
            self.tableau.move(k, "", index)
        sym = " ↓" if self.ordre_tri[col] else " ↑"
        self.tableau.heading("cmd", text=f"COMMANDE{sym if col == 'cmd' else ' ↑'}")
        self.tableau.heading("cat", text=f"CATÉGORIE{sym if col == 'cat' else ' ↑'}")

    def gerer_clic_tableau(self, event):
        if not self.quiz_en_cours:
            self.afficher_details(event)

    def afficher_details(self, event):
        self.quiz_en_cours = False
        self.cadre_quiz.pack_forget()
        self.zone_affichage.pack(fill="both", expand=True)

        sel = self.tableau.selection()
        if not sel:
            return

        item_values = self.tableau.item(sel)["values"]
        if not item_values:
            return

        nom_extrait = str(item_values[0]).strip()

        data_totale = obtenir_commandes_completes()
        self.donnees = data_totale["commandes"]

        info = None
        nom_reel = nom_extrait
        for cle in self.donnees.keys():
            if cle.lower() == nom_extrait.lower():
                info = self.donnees[cle]
                nom_reel = cle
                break

        if info is None:
            return

        self.zone_affichage.config(state="normal")
        self.zone_affichage.delete("1.0", tk.END)

        self.zone_affichage.tag_config("titre", font=("Segoe UI", 26, "bold"), foreground=self.c_accent)
        self.zone_affichage.tag_config("label", font=("Segoe UI", 10, "bold"), foreground="#9CA3AF")
        self.zone_affichage.tag_config("terminal", font=("Consolas", 12, "bold"), background="#000000", foreground="#10B981")

        ico = info.get("icone", "📂")
        self.zone_affichage.insert(tk.END, f"{ico} {nom_reel.upper()}\n", "titre")
        self.zone_affichage.insert(tk.END, f"\n📂 CATÉGORIE : {info.get('categorie', 'N/A')}\n", "label")
        self.zone_affichage.insert(tk.END, f"\n📌 DESCRIPTION\n", "label")
        self.zone_affichage.insert(tk.END, f"{info.get('description', '')}\n\n")
        self.zone_affichage.insert(tk.END, f"💻 TERMINAL SIMULATION\n", "label")
        self.zone_affichage.insert(tk.END, "\n")

        u = self.utilisateur.get("prenom", "user").lower()
        n = self.utilisateur.get("nom", "linux").lower()
        login = f"{u}.{n}"
        prompt = f" {login}@linux:~$ {info.get('exemple', '')} "
        self.zone_affichage.insert(tk.END, f"{prompt}\n", "terminal")

        self.zone_affichage.config(state="disabled")