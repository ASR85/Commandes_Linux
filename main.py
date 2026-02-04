import tkinter as tk
from tkinter import ttk, messagebox
import random
import json
import os
import sys
import winshell
from win32com.client import Dispatch

class ApplicationLinux:
    def __init__(self, root):

        self.root = root
        self.root.title("🐧 Commandes Linux")
        self.root.withdraw()

        # --- GESTION DE L'ICÔNE (Version EXE) ---
        try:
            # On demande à utils de trouver le chemin réel dans l'exécutable
            chemin_ico = utils.ressource_path("favicon.ico")
            self.root.iconbitmap(chemin_ico)
        except:
            # Si l'icône échoue, le programme continue sans planter
            pass

        self.config_file = "config.json"
        self.utilisateur = self.charger_profil()

        if self.utilisateur is None:
            self.root.destroy()
            return

        self.mode_sombre = self.utilisateur.get("mode_sombre", False)
        self.largeur, self.hauteur = 1050, 800
        self.centrer_fenetre(self.root, self.largeur, self.hauteur)

        self.quiz_en_cours = False

        # On initialise l'état des tris (False = Ascendant au premier clic.)
        self.ordre_tri = {"cmd": False, "cat": False}

        self.categories = [
            "Fichiers",
            "Réseau",
            "Système",
            "Utilisateurs",
            "Textes",
            "Archives",
            "Développement",
            "Sécurité",
            "Bases de données",
            "Général",
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
        self.appliquer_theme()

        # --- INITIALISATION DES DONNÉES ET TRI ---
        self.actualiser_tableau()

        # Tri alphabétique forcé au départ
        self.ordre_tri["cmd"] = True
        self.trier_colonne("cmd")

        self.root.deiconify()

        def creer_raccourci_bureau(self):

            try:
                desktop = winshell.desktop()
                path = os.path.join(desktop, "Commandes Linux.lnk")

                # On ne le crée que s'il n'existe pas déjà
                if not os.path.exists(path):
                    # sys.executable donne le chemin du .exe quand il est lancé
                    target = sys.executable

                    shell = Dispatch('WScript.Shell')
                    shortcut = shell.CreateShortCut(path)
                    shortcut.Targetpath = target
                    shortcut.WorkingDirectory = os.path.dirname(target)

                    # On pointe sur l'icône intégrée à l'EXE
                    shortcut.IconLocation = target
                    shortcut.save()
            except Exception:
                # On ignore si ça échoue (ex: droits restreints)
                pass

    def charger_profil(self):
        if not os.path.exists(self.config_file):
            return self.demander_profil()
        try:
            with open(self.config_file, "r") as f:
                data = json.load(f)
                return data if data.get("prenom") else self.demander_profil()
        except:
            return self.demander_profil()

    def demander_profil(self):
        fen = tk.Toplevel(self.root)
        fen.title("🐧 Configuration")
        self.centrer_fenetre(fen, 400, 450)
        fen.configure(bg="#F9FAFB")
        fen.grab_set()

        # --- AJOUT DE L'ICÔNE ICI ---
        try:
            fen.iconbitmap(utils.ressource_path("favicon.ico"))
        except:
            pass

        self.profil_valide = False
        fen.protocol("WM_DELETE_WINDOW", lambda: fen.destroy())

        tk.Label(
            fen,
            text="BIENVENUE",
            font=("Segoe UI", 18, "bold"),
            bg="#F9FAFB",
            fg="#312E81",
            pady=25,
        ).pack()

        tk.Label(fen, text="Prénom :", bg="#F9FAFB", font=("Segoe UI", 9, "bold")).pack(
            anchor="w", padx=50
        )
        ep = tk.Entry(fen, font=("Segoe UI", 11), relief="solid", bd=1)
        ep.pack(pady=5, padx=50, fill="x")

        tk.Label(fen, text="Nom :", bg="#F9FAFB", font=("Segoe UI", 9, "bold")).pack(
            anchor="w", padx=50, pady=(10, 0)
        )
        en = tk.Entry(fen, font=("Segoe UI", 11), relief="solid", bd=1)
        en.pack(pady=5, padx=50, fill="x")

        def valider():
            p, n = ep.get().strip(), en.get().strip()
            if p and n:
                res = {"prenom": p, "nom": n, "mode_sombre": False}
                with open(self.config_file, "w") as f:
                    json.dump(res, f)
                self.profil_valide = True
                fen.destroy()
            else:
                messagebox.showwarning(
                    "Champs requis", "Veuillez entrer votre nom et prénom."
                )

        tk.Button(
            fen,
            text="CRÉER MON PROFIL 🐧",
            bg="#312E81",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            command=valider,
            pady=15,
            relief="flat",
        ).pack(pady=40, padx=50, fill="x")

        self.root.wait_window(fen)
        return self.charger_profil() if self.profil_valide else None

    def appliquer_theme(self):
        if self.mode_sombre:
            self.c_bg, self.c_fg, self.c_card = "#111827", "#F9FAFB", "#1F2937"
            self.c_accent, self.c_border = "#4F46E5", "#374151"
        else:
            self.c_bg, self.c_fg, self.c_card = "#F3F4F6", "#111827", "#FFFFFF"
            self.c_accent, self.c_border = "#312E81", "#D1D5DB"

        self.root.configure(bg=self.c_bg)
        self.entete.configure(bg=self.c_accent)
        self.lbl_titre.configure(bg=self.c_accent, fg="white")
        self.cadre_profil.configure(bg=self.c_accent)
        self.lbl_user.configure(bg=self.c_accent, fg="white")
        self.corps.configure(bg=self.c_bg)
        self.zone_recherche.configure(bg=self.c_bg)
        self.cadre_saisie.configure(bg=self.c_card, highlightbackground=self.c_border)
        self.lbl_loupe.configure(bg=self.c_card, fg="#64748B")
        self.champ_recherche.configure(
            bg=self.c_card, fg=self.c_fg, insertbackground=self.c_fg
        )
        self.style.configure(
            "Treeview",
            background=self.c_card,
            foreground=self.c_fg,
            fieldbackground=self.c_card,
        )
        self.cadre_details.configure(bg=self.c_card, highlightbackground=self.c_border)
        self.zone_affichage.configure(bg=self.c_card, foreground=self.c_fg)
        self.cadre_liste.configure(bg=self.c_card)
        self.bas_page.configure(bg=self.c_card, highlightbackground=self.c_border)

    def construire_interface(self):
        # --- EN-TÊTE ---
        self.entete = tk.Frame(self.root, pady=20)
        self.entete.pack(fill="x")

        self.lbl_titre = tk.Label(
            self.entete, text="🐧 Commandes Linux", font=("Segoe UI", 22, "bold")
        )
        self.lbl_titre.pack(side="left", padx=30)

        self.cadre_profil = tk.Frame(self.entete)
        self.cadre_profil.pack(side="right", padx=30)

        user_txt = f"👤 {self.utilisateur['prenom'].capitalize()} {self.utilisateur['nom'].upper()}"
        self.lbl_user = tk.Label(
            self.cadre_profil, text=user_txt, font=("Segoe UI", 10, "bold")
        )
        self.lbl_user.pack()

        # --- PIED DE PAGE ---
        self.bas_page = tk.Frame(self.root, pady=15, highlightthickness=1)
        self.bas_page.pack(fill="x", side="bottom")
        btn_f = ("Segoe UI", 9, "bold")

        tk.Button(
            self.bas_page,
            text="🎯 QUIZ",
            bg="#10B981",
            fg="white",
            font=btn_f,
            padx=20,
            pady=8,
            command=self.lancer_quiz_pre,
            relief="flat",
        ).pack(side="left", padx=20)

        tk.Button(
            self.bas_page,
            text="💡 AIDE",
            bg="#6B7280",
            fg="white",
            font=btn_f,
            padx=15,
            pady=8,
            command=self.ouvrir_aide,
            relief="flat",
        ).pack(side="left", padx=5)

        tk.Button(
            self.bas_page,
            text="⚙️ PARAMÈTRES",
            bg="#4B5563",
            fg="white",
            font=btn_f,
            padx=15,
            pady=8,
            command=self.ouvrir_parametres,
            relief="flat",
        ).pack(side="left", padx=5)

        tk.Button(
            self.bas_page,
            text="➕ AJOUTER",
            bg="#6366F1",
            fg="white",
            font=btn_f,
            padx=15,
            pady=8,
            command=self.ouvrir_ajout,
            relief="flat",
        ).pack(side="right", padx=10)

        tk.Button(
            self.bas_page,
            text="🗑️ SUPPRIMER",
            bg="#EF4444",
            fg="white",
            font=btn_f,
            padx=15,
            pady=8,
            command=self.ouvrir_suppression,
            relief="flat",
        ).pack(side="right", padx=10)

        # --- RECHERCHE ---
        self.zone_recherche = tk.Frame(self.root, pady=15)
        self.zone_recherche.pack(fill="x", padx=30)
        self.cadre_saisie = tk.Frame(self.zone_recherche, highlightthickness=1)
        self.cadre_saisie.pack(fill="x", padx=10)
        self.lbl_loupe = tk.Label(self.cadre_saisie, text=" 🔍 ", font=("Segoe UI", 12))
        self.lbl_loupe.pack(side="left", padx=5)
        self.champ_recherche = tk.Entry(
            self.cadre_saisie, font=("Segoe UI", 11), relief="flat"
        )
        self.champ_recherche.insert(0, "Rechercher une commande ou une catégorie...")
        self.champ_recherche.pack(side="left", fill="x", expand=True, ipady=10)
        self.champ_recherche.bind("<FocusIn>", self.nettoyer_recherche)
        self.champ_recherche.bind(
            "<KeyRelease>",
            lambda e: self.actualiser_tableau(self.champ_recherche.get()),
        )

        # --- CORPS ---
        self.corps = tk.Frame(self.root)
        self.corps.pack(fill="both", expand=True, padx=30, pady=10)
        self.cadre_liste = tk.Frame(self.corps, highlightthickness=1)
        self.cadre_liste.pack(side="left", fill="both")
        self.tableau = ttk.Treeview(
            self.cadre_liste, columns=("cmd", "cat"), show="headings", height=15
        )
        self.tableau.heading(
            "cmd", text="COMMANDE ↑", command=lambda: self.trier_colonne("cmd")
        )
        self.tableau.heading(
            "cat", text="CATÉGORIE ↑", command=lambda: self.trier_colonne("cat")
        )
        self.tableau.column("cmd", width=260)
        self.tableau.column("cat", width=130, anchor="center")
        self.scroll_y = ttk.Scrollbar(
            self.cadre_liste, orient="vertical", command=self.tableau.yview
        )
        self.tableau.configure(yscrollcommand=self.scroll_y.set)
        self.tableau.pack(side="left", fill="both")
        self.scroll_y.pack(side="right", fill="y")
        self.tableau.bind("<<TreeviewSelect>>", self.gerer_clic_tableau)
        self.cadre_details = tk.Frame(
            self.corps, highlightthickness=1, padx=25, pady=25
        )
        self.cadre_details.pack(side="right", fill="both", expand=True, padx=(25, 0))
        self.zone_affichage = tk.Text(
            self.cadre_details,
            font=("Segoe UI", 11),
            relief="flat",
            wrap="word",
            state="disabled",
        )
        self.zone_affichage.pack(fill="both", expand=True)
        self.cadre_quiz = tk.Frame(self.cadre_details)

    def lancer_quiz_pre(self):

        # Récupération de l'objet global
        data_globale = utils.obtenir_commandes_completes()

        # On isole les commandes pour le quiz
        self.donnees = data_globale["commandes"]

        if len(self.donnees) < 4:
            messagebox.showwarning("Quiz", "Il faut au moins 4 commandes pour jouer !")
            return

        for w in self.cadre_quiz.winfo_children():
            w.destroy()

        self.quiz_en_cours = True
        self.zone_affichage.pack_forget()
        self.cadre_quiz.pack(fill="both", expand=True)
        self.cadre_quiz.configure(bg=self.c_card)

        tk.Label(
            self.cadre_quiz,
            text=f"Prêt pour le Quiz, {self.utilisateur['prenom'].capitalize()} ? 🐧",
            font=("Segoe UI", 13, "bold"),
            bg=self.c_card,
            fg=self.c_accent,
        ).pack(pady=20)

        tk.Label(
            self.cadre_quiz,
            text="Choisissez la difficulté du défi :",
            bg=self.c_card,
            fg=self.c_fg,
        ).pack(pady=10)

        config_quiz = [
            (5, "🚀 Défi Rapide (5)", "#10B981"),
            (10, "🎯 Entraînement (10)", "#3B82F6"),
            (15, "🛡️ Mode Expert (15)", "#8B5CF6"),
            (20, "🔥 Marathon Linux (20)", "#EF4444"),
        ]

        for nb, texte, couleur in config_quiz:
            if nb <= len(self.donnees):
                tk.Button(
                    self.cadre_quiz,
                    text=texte,
                    bg=couleur,
                    fg="white",
                    font=("Segoe UI", 10, "bold"),
                    command=lambda n=nb: self.lancer_quiz_action(n),
                    relief="flat",
                    pady=10,
                ).pack(fill="x", pady=5, padx=80)

        tk.Button(
            self.cadre_quiz,
            text="ANNULER",
            command=self.quitter_quiz,
            bg="#6B7280",
            fg="white",
            pady=8,
        ).pack(pady=20)

    def lancer_quiz_action(self, nb):

        self.score_q, self.index_q = 0, 0

        # On prend les noms des commandes disponibles
        cles_disponibles = list(self.donnees.keys())
        self.questions = []

        # On s'assure de ne pas demander plus de questions qu'on a de commandes
        nb = min(nb, len(cles_disponibles))

        for _ in range(nb):
            # On choisit la bonne réponse
            bonne_reponse = random.choice(cles_disponibles)
            cles_disponibles.remove(bonne_reponse)

            # On génère 3 fausses réponses
            autres_commandes = [c for c in self.donnees.keys() if c != bonne_reponse]
            options = random.sample(autres_commandes, 3) + [bonne_reponse]
            random.shuffle(options)

            self.questions.append(
                {
                    "d": self.donnees[bonne_reponse]["description"],
                    "o": options,
                    "a": bonne_reponse,
                }
            )

        self.prochaine_question()

    def prochaine_question(self):
        for w in self.cadre_quiz.winfo_children():
            w.destroy()
        if self.index_q >= len(self.questions):
            ratio = self.score_q / len(self.questions)
            msg = (
                "FÉLICITATIONS ! 🎉" if ratio >= 0.8 else "BEL EFFORT, PERSÉVÉREZ ! 💪"
            )

            tk.Label(
                self.cadre_quiz,
                text=msg,
                font=("Segoe UI", 14, "bold"),
                bg=self.c_card,
                fg=self.c_accent,
            ).pack(pady=20)
            tk.Label(
                self.cadre_quiz,
                text=f"SCORE FINAL : {self.score_q} / {len(self.questions)}",
                font=("Segoe UI", 25, "bold"),
                bg=self.c_card,
                fg="#10B981",
            ).pack()

            tk.Button(
                self.cadre_quiz,
                text="🔄 RECOMMENCER",
                command=self.lancer_quiz_pre,
                bg="#10B981",
                fg="white",
                font=("Segoe UI", 10, "bold"),
                pady=12,
                padx=40,
                relief="flat",
            ).pack(pady=(30, 10))

            tk.Button(
                self.cadre_quiz,
                text="🚪 QUITTER LE QUIZ",
                command=self.quitter_quiz,
                bg="#EF4444",
                fg="white",
                font=("Segoe UI", 10, "bold"),
                pady=12,
                padx=40,
                relief="flat",
            ).pack()
            return

        q = self.questions[self.index_q]
        tk.Label(
            self.cadre_quiz,
            text=f"Question {self.index_q + 1} sur {len(self.questions)}",
            bg=self.c_card,
            fg="#6B7280",
        ).pack()
        tk.Label(
            self.cadre_quiz,
            text=q["d"],
            font=("Segoe UI", 11),
            bg=self.c_card,
            fg=self.c_fg,
            wraplength=400,
            pady=25,
        ).pack()

        for opt in q["o"]:
            tk.Button(
                self.cadre_quiz,
                text=opt.upper(),
                bg="#E5E7EB" if not self.mode_sombre else "#374151",
                fg=self.c_fg,
                pady=12,
                relief="flat",
                command=lambda v=opt: self.valider(v, q),
            ).pack(fill="x", pady=4, padx=50)

    def valider(self, v, q):
        if v == q["a"]:
            self.score_q += 1
        self.index_q += 1
        self.prochaine_question()

    def quitter_quiz(self):
        self.quiz_en_cours = False
        self.afficher_details(None)

    def afficher_details(self, event):

        self.quiz_en_cours = False
        self.cadre_quiz.pack_forget()
        self.zone_affichage.pack(fill="both", expand=True)

        sel = self.tableau.selection()

        if not sel:
            return

        # 1. Récupération directe du nom (plus d'icône à découper)
        item_values = self.tableau.item(sel)["values"]

        if not item_values:
            return

        nom_extrait = str(item_values[0]).strip()

        # 2. Mise à jour des données pour inclure les nouveaux ajouts
        data_totale = utils.obtenir_commandes_completes()
        self.donnees = data_totale["commandes"]

        # 3. Recherche de la commande dans le dictionnaire
        info = None
        nom_reel = nom_extrait

        for cle in self.donnees.keys():
            if cle.lower() == nom_extrait.lower():
                info = self.donnees[cle]
                nom_reel = cle
                break

        if info is None:
            return

        # 4. Préparation de la zone de texte
        self.zone_affichage.config(state="normal")
        self.zone_affichage.delete("1.0", tk.END)

        # Configuration des styles
        self.zone_affichage.tag_config(
            "titre", font=("Segoe UI", 26, "bold"), foreground=self.c_accent
        )
        self.zone_affichage.tag_config(
            "label", font=("Segoe UI", 10, "bold"), foreground="#9CA3AF"
        )
        self.zone_affichage.tag_config(
            "terminal",
            font=("Consolas", 12, "bold"),
            background="#000000",
            foreground="#10B981",
        )

        # 5. Affichage de l'icône (récupérée du JSON) et du titre
        ico = info.get("icone", "📂")
        self.zone_affichage.insert(tk.END, f"{ico} {nom_reel.upper()}\n", "titre")

        # Catégorie et Description
        self.zone_affichage.insert(
            tk.END, f"\n📂 CATÉGORIE : {info.get('categorie', 'N/A')}\n", "label"
        )
        self.zone_affichage.insert(tk.END, f"\n📌 DESCRIPTION\n", "label")
        self.zone_affichage.insert(tk.END, f"{info.get('description', '')}\n\n")

        # 6. Simulation du terminal
        self.zone_affichage.insert(tk.END, f"💻 TERMINAL SIMULATION\n", "label")
        self.zone_affichage.insert(tk.END, "\n")

        # Génération du login utilisateur
        try:
            u = self.utilisateur.get("prenom", "user").lower()
            n = self.utilisateur.get("nom", "linux").lower()
            login = f"{u}.{n}"
        except:
            login = "user.linux"

        # Insertion de la ligne de commande
        prompt = f" {login}@linux:~$ {info.get('exemple', '')} "
        self.zone_affichage.insert(tk.END, f"{prompt}\n", "terminal")

        self.zone_affichage.config(state="disabled")

    def ouvrir_aide(self):
        fen = tk.Toplevel(self.root)
        fen.title("🐧 Manuel d'Utilisation Complet")

        # Fenêtre fixe
        fen.resizable(False, False)
        self.centrer_fenetre(fen, 650, 800)
        fen.configure(bg=self.c_card)
        fen.grab_set()

        # --- AJOUT DE L'ICÔNE ICI ---
        try:
            fen.iconbitmap(utils.ressource_path("favicon.ico"))
        except:
            pass

        # --- 1. LE BOUTON FERMER (FIXÉ EN BAS) ---
        def fermer():
            canevas.unbind_all("<MouseWheel>")
            fen.destroy()

        btn_fermer = tk.Button(
            fen,
            text="J'AI COMPRIS 🐧",
            command=fermer,
            bg=self.c_accent,
            fg="white",
            font=("Segoe UI", 11, "bold"),
            pady=15,
            relief="flat",
        )
        btn_fermer.pack(side="bottom", fill="x")

        # --- 2. LE CONTENEUR DE SCROLL (PREND LE RESTE DE LA PLACE) ---
        canevas = tk.Canvas(fen, bg=self.c_card, highlightthickness=0)
        scrollbar = ttk.Scrollbar(fen, orient="vertical", command=canevas.yview)
        scrollbar.pack(side="right", fill="y")
        canevas.pack(side="left", fill="both", expand=True)

        scroll_frame = tk.Frame(canevas, bg=self.c_card)

        scroll_frame.bind(
            "<Configure>", lambda e: canevas.configure(scrollregion=canevas.bbox("all"))
        )

        canevas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canevas.configure(yscrollcommand=scrollbar.set)

        # --- 3. SCROLL SOURIS ---
        def _on_mousewheel(event):
            canevas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canevas.bind_all("<MouseWheel>", _on_mousewheel)

        # --- 4. Le guide
        tk.Label(
            scroll_frame,
            text="🐧 GUIDE COMPLET LINUX PRO",
            font=("Segoe UI", 16, "bold"),
            bg=self.c_card,
            fg=self.c_accent,
        ).pack(pady=20, padx=40)

        def ajouter_section(titre, texte):
            f = tk.Frame(scroll_frame, bg=self.c_card, pady=10)
            f.pack(fill="x", padx=40)

            tk.Label(
                f,
                text=titre,
                font=("Segoe UI", 11, "bold"),
                bg=self.c_card,
                fg=self.c_fg,
                wraplength=520,
                justify="left",
            ).pack(anchor="w")

            tk.Label(
                f,
                text=texte,
                font=("Segoe UI", 11),
                bg=self.c_card,
                fg=self.c_fg,
                wraplength=520,
                justify="left",
            ).pack(anchor="w", pady=5)

            tk.Frame(scroll_frame, height=1, bg=self.c_border).pack(
                fill="x", padx=40, pady=5
            )

        ajouter_section(
            "👤 GESTION DU PROFIL",
            "Au premier lancement, le logiciel vous demande votre Nom et Prénom. Ces informations "
            "servent à personnaliser votre expérience. Votre identifiant Linux (ex: jean.dupont) "
            "est généré automatiquement pour simuler le terminal dans les détails des commandes. "
            "Vous pouvez réinitialiser ce profil dans les Paramètres.",
        )

        ajouter_section(
            "🌓 THÈMES ET APPARENCE",
            "Linux Pro dispose de deux modes : Clair et Sombre. Le mode sombre est conçu pour "
            "réduire la fatigue oculaire. Vous pouvez basculer entre les deux via le bouton "
            "'PARAMÈTRES'. Votre choix est sauvegardé automatiquement dans le fichier de configuration.",
        )

        ajouter_section(
            "🔍 NAVIGATION ET RECHERCHE",
            "La barre de recherche en haut vous permet de filtrer instantanément les commandes par "
            "leur nom ou par catégorie. Vous pouvez également cliquer sur les en-têtes du tableau "
            "pour trier la liste par ordre alphabétique (↑) ou inversé (↓).",
        )

        ajouter_section(
            "🎯 FONCTIONNEMENT DU QUIZ",
            "Le quiz teste vos connaissances sur les commandes Linux. "
            "\n1. Choisissez un défi (5 à 20 questions)."
            "\n2. Une description s'affiche, vous devez trouver la commande correspondante."
            "\n3. À la fin, un score global s'affiche avec un message de félicitations."
            "\n4. Vous pouvez recommencer ou quitter le quiz à tout moment.",
        )

        ajouter_section(
            "➕ AJOUTER UNE COMMANDE",
            "Pour enrichir la base de données :\n"
            "1. Définissez la catégorie (Badge existant ou création d'une nouvelle via le bouton +).\n"
            "2. Remplissez tous les champs (Nom, Description, Exemple).\n"
            "IMPORTANT : Le logiciel formate automatiquement le nom et la catégorie avec une "
            "majuscule au début (ex: 'ssh' devient 'Ssh'). Les catégories ne doivent contenir que des lettres.",
        )

        ajouter_section(
            "🎨 SYSTÈME D'ICÔNES ET VALIDATION",
            "Lors de la création d'une nouvelle catégorie, vous devez obligatoirement cliquer sur 'VALIDER' "
            "pour confirmer le nom. Cela fera apparaître une grille d'émojis tech. "
            "Sélectionnez l'icône de votre choix pour finaliser la création. "
            "Si vous sélectionnez une catégorie déjà existante, l'icône officielle sera utilisée automatiquement.",
        )

        ajouter_section(
            "🗑️ SUPPRESSION ET SÉCURITÉ",
            "Le logiciel fait une distinction stricte entre deux types de commandes :\n"
            "• COMMANDES SYSTÈME : Les commandes de base (ls, cd, etc.) sont protégées. Elles ne peuvent pas être supprimées.\n"
            "• COMMANDES PERSONNELLES : Seules les commandes que vous avez créées via le bouton 'AJOUTER' "
            "apparaissent dans la liste de suppression et peuvent être retirées.",
        )

    def ouvrir_parametres(self):
        fen = tk.Toplevel(self.root)
        fen.title("🐧 Paramètres")
        self.centrer_fenetre(fen, 450, 400)
        fen.configure(bg=self.c_card, padx=30, pady=30)
        fen.grab_set()

        # --- AJOUT DE L'ICÔNE ICI ---
        try:
            fen.iconbitmap(utils.ressource_path("favicon.ico"))
        except:
            pass

        tk.Label(
            fen,
            text="⚙️ RÉGLAGES",
            font=("Segoe UI", 13, "bold"),
            bg=self.c_card,
            fg=self.c_fg,
        ).pack(pady=(0, 25))
        txt = (
            "PASSER AU MODE CLAIR ☀️"
            if self.mode_sombre
            else "PASSER AU MODE SOMBRE 🌙"
        )
        tk.Button(
            fen,
            text=txt,
            font=("Segoe UI", 10, "bold"),
            bg=self.c_accent,
            fg="white",
            pady=12,
            relief="flat",
            command=lambda: [self.basculer_theme(), fen.destroy()],
        ).pack(fill="x", pady=8)
        tk.Button(
            fen,
            text="RÉINITIALISER LE PROFIL 🔄",
            font=("Segoe UI", 10, "bold"),
            bg="#F59E0B",
            fg="white",
            pady=12,
            relief="flat",
            command=self.reinitialiser_application,
        ).pack(fill="x", pady=8)

    def actualiser_tableau(self, recherche=""):

        if recherche == "Rechercher une commande ou une catégorie...":
            recherche = ""

        # On récupère les données
        data_totale = utils.obtenir_commandes_completes()
        self.donnees = data_totale["commandes"]

        # On vide le tableau
        for ligne in self.tableau.get_children():
            self.tableau.delete(ligne)

        # --- LA CORRECTION EST ICI : on trie les clés (noms) avant la boucle ---
        noms_tries = sorted(self.donnees.keys())

        for nom in noms_tries:
            info = self.donnees[nom]
            cat = info.get("categorie", "Général")

            # Filtrage par recherche
            if recherche.lower() in nom.lower() or recherche.lower() in cat.lower():
                # Insertion propre (SANS icône dans la colonne pour ne pas fausser le tri)
                self.tableau.insert("", tk.END, values=(nom.strip().upper(), cat))

    def basculer_theme(self):
        self.mode_sombre = not self.mode_sombre
        self.utilisateur["mode_sombre"] = self.mode_sombre
        with open(self.config_file, "w") as f:
            json.dump(self.utilisateur, f)
        self.appliquer_theme()

    def reinitialiser_application(self):
        if messagebox.askyesno(
            "Réinitialisation", "Effacer votre profil et redémarrer ?"
        ):
            if os.path.exists(self.config_file):
                os.remove(self.config_file)
            self.root.destroy()
            os.system("python main.py")

    def nettoyer_recherche(self, event):
        if self.champ_recherche.get() == "Rechercher une commande ou une catégorie...":
            self.champ_recherche.delete(0, tk.END)

    def centrer_fenetre(self, f, largeur, hauteur):
        """Centre la fenêtre et applique les dimensions fixes"""
        # On s'assure que les dimensions sont des entiers
        l, h = int(largeur), int(hauteur)

        x = (f.winfo_screenwidth() // 2) - (l // 2)
        y = (f.winfo_screenheight() // 2) - (h // 2)

        # Application de la géométrie : "LargeurxHauteur+X+Y"
        f.geometry(f"{l}x{h}+{x}+{y}")

    def trier_colonne(self, col):

        # On inverse l'ordre
        self.ordre_tri[col] = not self.ordre_tri[col]

        # On récupère les données du tableau
        lignes = []
        for k in self.tableau.get_children(""):
            # On récupère la valeur et on la met en minuscule pour le tri
            valeur = str(self.tableau.set(k, col)).lower()
            lignes.append((valeur, k))

        # Tri alphabétique de la liste de tuples
        lignes.sort(reverse=self.ordre_tri[col])

        # On réorganise les lignes dans le Treeview
        for index, (val, k) in enumerate(lignes):
            self.tableau.move(k, "", index)

        # Mise à jour des flèches ↑ / ↓
        sym = " ↓" if self.ordre_tri[col] else " ↑"
        self.tableau.heading("cmd", text=f"COMMANDE{sym if col == 'cmd' else ' ↑'}")
        self.tableau.heading("cat", text=f"CATÉGORIE{sym if col == 'cat' else ' ↑'}")

    def gerer_clic_tableau(self, event):
        if not self.quiz_en_cours:
            self.afficher_details(None)

    def ouvrir_ajout(self):
        # --- 1. INITIALISATION DES VARIABLES ---
        self.icone_choisie_finale = None
        self.var_cat = tk.StringVar()

        # Filtrage des icônes pour ne pas proposer les doublons
        icones_reservees = list(self.icones.values())
        potentielles = [
            "🐧",
            "💻",
            "📟",
            "🌐",
            "📡",
            "🔗",
            "🔑",
            "🔐",
            "⚡",
            "📊",
            "🔍",
            "🕒",
            "🧪",
            "🚀",
            "🔥",
        ]
        emojis_tech = [e for e in potentielles if e not in icones_reservees]

        # --- 2. CONFIGURATION DE LA FENÊTRE ---
        fen = tk.Toplevel(self.root)
        fen.title("🐧 Nouvelle commande")

        # On rend la fenêtre NON REDIMENSIONNABLE
        fen.resizable(False, False)

        self.centrer_fenetre(fen, 500, 600)
        fen.configure(bg=self.c_card, padx=25, pady=15)
        fen.grab_set()
        fen.grab_set()

        # --- AJOUT DE L'ICÔNE ICI ---
        try:
            fen.iconbitmap(utils.ressource_path("favicon.ico"))
        except:
            pass

        # --- 3. PRÉPARATION DES WIDGETS ---
        cadre_saisie_cat = tk.Frame(fen, bg=self.c_card)

        ent_saisie_libre = tk.Entry(
            cadre_saisie_cat,
            font=("Segoe UI", 10),
            bg=self.c_bg,
            fg=self.c_fg,
            relief="solid",
            borderwidth=1,
        )

        cadre_custom_icon = tk.Frame(fen, bg=self.c_card)

        ent_cat_finale = tk.Entry(
            fen,
            font=("Segoe UI", 10, "bold"),
            bg="#F3F4F6",
            fg=self.c_accent,
            relief="flat",
            justify="center",
        )

        # --- 4. LOGIQUE INTERNE ---

        def actualiser_vue():
            cat_nom = self.var_cat.get()
            if not cat_nom:
                txt = "Sélectionnez une catégorie..."
            else:
                ico = self.icones.get(
                    cat_nom,
                    self.icone_choisie_finale if self.icone_choisie_finale else "📦",
                )
                txt = f"{ico}  {cat_nom}"

            ent_cat_finale.config(state="normal")
            ent_cat_finale.delete(0, tk.END)
            ent_cat_finale.insert(0, txt)
            ent_cat_finale.config(state="readonly")

        def selectionner_cat_existante(nom):
            # On vide le texte libre
            ent_saisie_libre.delete(0, tk.END)
            # On grise le bouton de création
            btn_valider_cat.config(state="disabled", bg="#D1D5DB")
            # On valide
            self.var_cat.set(nom)
            self.icone_choisie_finale = None
            cadre_custom_icon.pack_forget()
            actualiser_vue()

        def au_clic_saisie_libre(event):
            # On dégrise le bouton pour permettre la création
            btn_valider_cat.config(state="normal", bg=self.c_accent)
            # On reset la sélection précédente
            self.var_cat.set("")
            self.icone_choisie_finale = None
            cadre_custom_icon.pack_forget()
            actualiser_vue()

        def valider_nouvelle_cat():
            s = ent_saisie_libre.get().strip()
            if s:
                self.var_cat.set(s.capitalize())
                cadre_custom_icon.pack(fill="x", pady=5, after=cadre_saisie_cat)
                actualiser_vue()
                fen.focus_set()
            else:
                messagebox.showwarning(
                    "Attention", "Saisissez un nom de catégorie.", parent=fen
                )

        # --- 5. INTERFACE VISUELLE ---

        tk.Label(
            fen,
            text="1. CHOIX DE LA CATÉGORIE",
            font=("Segoe UI", 9, "bold"),
            bg=self.c_card,
            fg=self.c_accent,
        ).pack(anchor="w")

        cadre_badges = tk.Frame(fen, bg=self.c_card)
        cadre_badges.pack(fill="x", pady=5)

        row, col = 0, 0
        for c in self.categories:
            tk.Button(
                cadre_badges,
                text=c,
                font=("Segoe UI", 8),
                command=lambda x=c: selectionner_cat_existante(x),
                bg=self.c_bg,
                fg=self.c_fg,
                relief="flat",
            ).grid(row=row, column=col, padx=1, pady=1, sticky="we")
            col += 1
            if col > 4:
                col = 0
                row += 1

        tk.Label(
            fen,
            text="Ou créer une nouvelle catégorie :",
            font=("Segoe UI", 8),
            bg=self.c_card,
            fg="#6B7280",
        ).pack(anchor="w", pady=(10, 0))

        cadre_saisie_cat.pack(fill="x", pady=5)

        ent_saisie_libre.pack(side="left", fill="x", expand=True, ipady=3)
        ent_saisie_libre.bind("<FocusIn>", au_clic_saisie_libre)

        btn_valider_cat = tk.Button(
            cadre_saisie_cat,
            text="VALIDER ➔",
            command=valider_nouvelle_cat,
            bg="#D1D5DB",
            fg="white",
            font=("Segoe UI", 8, "bold"),
            state="disabled",
        )
        btn_valider_cat.pack(side="right", padx=5)

        # Zone des icônes
        tk.Label(
            cadre_custom_icon,
            text="Choisir une icône :",
            font=("Segoe UI", 8, "italic"),
            bg=self.c_card,
            fg=self.c_accent,
        ).pack(anchor="w")

        zone_emojis = tk.Frame(cadre_custom_icon, bg=self.c_card)
        zone_emojis.pack(pady=2)

        r_em, c_em = 0, 0
        for emo in emojis_tech:
            tk.Button(
                zone_emojis,
                text=emo,
                font=("Segoe UI", 10),
                command=lambda e=emo: [
                    setattr(self, "icone_choisie_finale", e),
                    actualiser_vue(),
                ],
                bg=self.c_bg,
                relief="flat",
                width=3,
            ).grid(row=r_em, column=c_em, padx=1, pady=1)
            c_em += 1
            if c_em > 6:
                c_em = 0
                r_em += 1

        ent_cat_finale.pack(fill="x", pady=10, ipady=5)
        ent_cat_finale.insert(0, "Sélectionnez une catégorie...")
        ent_cat_finale.config(state="readonly")

        # Détails de la commande
        tk.Label(
            fen,
            text="2. DÉTAILS DE LA COMMANDE",
            font=("Segoe UI", 9, "bold"),
            bg=self.c_card,
            fg=self.c_accent,
        ).pack(anchor="w", pady=(5, 5))

        ch = {}
        for lib, cl in [("Nom", "n"), ("Description", "d"), ("Exemple", "e")]:
            tk.Label(
                fen, text=lib, font=("Segoe UI", 8), bg=self.c_card, fg=self.c_fg
            ).pack(anchor="w")
            ch[cl] = tk.Entry(
                fen,
                font=("Segoe UI", 10),
                bg=self.c_bg,
                fg=self.c_fg,
                relief="solid",
                borderwidth=1,
            )
            ch[cl].pack(fill="x", pady=(0, 5), ipady=3)

        def sau():

            # 1. Récupération des données
            cat = self.var_cat.get().strip()
            nom = ch["n"].get().strip()
            des = ch["d"].get().strip()
            exe = ch["e"].get().strip()
            ico = self.icone_choisie_finale

            # 2. Préparation des erreurs
            erreurs = []

            # Vérification de la catégorie
            if not cat or "Sélectionnez" in cat:
                erreurs.append("• Catégorie manquante.")

            # Vérification de l'icône (seulement si nouvelle catégorie)
            if cat not in self.icones and ico is None:
                erreurs.append("• Choisissez une icône pour cette nouvelle catégorie.")

            if not nom:
                erreurs.append("• Nom manquant.")
            if not des:
                erreurs.append("• Description manquante.")
            if not exe:
                erreurs.append("• Exemple manquant.")

            # 3. Affichage des erreurs si besoin
            if erreurs:
                messagebox.showwarning("Incomplet", "\n".join(erreurs), parent=fen)
                return

            # 4. Détermination de l'icône finale
            # On prend l'icône déjà connue pour cette catégorie, sinon le choix de l'utilisateur
            icone_finale = self.icones.get(cat, ico)

            # 5. Enregistrement via utils.py
            if utils.ajouter_commande(nom.lower(), des, exe, cat, icone_finale):

                messagebox.showinfo(
                    "Succès ✨",
                    f"La commande '{nom.upper()}' est maintenant enregistrée dans votre base personnelle.",
                    parent=fen,
                )

                # Mise à jour de l'affichage
                self.actualiser_tableau()

                # IMPORTANT : On trie à nouveau pour placer la commande au bon endroit
                self.trier_colonne("cmd")

                fen.destroy()

            else:
                messagebox.showerror(
                    "Erreur ❌",
                    "Une erreur technique est survenue lors de l'enregistrement.",
                    parent=fen,
                )

        # --- LE BOUTON (Placé hors de la fonction sau) ---
        tk.Button(
            fen,
            text="ENREGISTRER LA COMMANDE 🐧",
            bg="#10B981",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            pady=12,
            command=sau,
            relief="flat",
        ).pack(fill="x", pady=(10, 0))

    def ouvrir_suppression(self):
        # On récupère uniquement ce qui est dans le fichier perso
        commandes_perso = utils.obtenir_commandes_perso()

        if not commandes_perso:
            messagebox.showinfo(
                "Suppression", "Vous n'avez aucune commande personnelle à supprimer."
            )
            return

        fen = tk.Toplevel(self.root)
        fen.title("🗑️ Supprimer mes commandes")
        self.centrer_fenetre(fen, 400, 500)
        fen.configure(bg=self.c_card, padx=20, pady=20)
        fen.grab_set()

        # --- AJOUT DE L'ICÔNE ICI ---
        try:
            fen.iconbitmap(utils.ressource_path("favicon.ico"))
        except:
            pass

        tk.Label(
            fen,
            text="MES COMMANDES PERSO",
            font=("Segoe UI", 12, "bold"),
            bg=self.c_card,
            fg="#EF4444",
        ).pack(pady=(0, 15))

        # Zone défilante pour la liste
        cadre_liste = tk.Frame(fen, bg=self.c_card)
        cadre_liste.pack(fill="both", expand=True)

        canvas = tk.Canvas(cadre_liste, bg=self.c_card, highlightthickness=0)
        scroll = ttk.Scrollbar(cadre_liste, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=self.c_card)

        scroll_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)

        canvas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        def confirmer_suppression(nom):
            if messagebox.askyesno(
                "Confirmation", f"Supprimer '{nom}' définitivement ?"
            ):
                if utils.supprimer_commande(nom):
                    # On rafraîchit l'interface
                    self.actualiser_tableau()
                    fen.destroy()
                    messagebox.showinfo("Succès", f"Commande '{nom}' supprimée.")

        # Affichage de chaque commande perso avec un bouton pour supprimer
        for nom in sorted(commandes_perso.keys()):
            f = tk.Frame(scroll_frame, bg=self.c_card, pady=5)
            f.pack(fill="x", expand=True)

            tk.Label(
                f,
                text=f"• {nom.upper()}",
                font=("Segoe UI", 10),
                bg=self.c_card,
                fg=self.c_fg,
            ).pack(side="left")

            tk.Button(
                f,
                text="❌",
                bg="#EF4444",
                fg="white",
                font=("Arial", 8, "bold"),
                command=lambda n=nom: confirmer_suppression(n),
            ).pack(side="right", padx=10)


if __name__ == "__main__":

    # 1. On s'assure que les fichiers JSON des commandes existent
    import utils

    utils.assurer_fichiers()

    root = tk.Tk()

    # On cache la fenêtre principale pendant la configuration du profil
    root.withdraw()

    # 2. On lance l'application.
    # Le tri sera fait AUTOMATIQUEMENT à l'intérieur de la classe.
    app = ApplicationLinux(root)

    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\n[!] Fermeture demandée par l'utilisateur.")
    except Exception as e:
        print(f"\n[!] Erreur critique : {e}")
