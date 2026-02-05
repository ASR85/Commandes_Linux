import tkinter as tk
from tkinter import ttk, messagebox, Frame, Canvas, Label, Button, Entry
import os
import json

from data.data import obtenir_commandes_perso, supprimer_commande, ajouter_commande, ressource_path, obtenir_categories, ajouter_categorie
from app.theme_utils import centrer_fenetre, appliquer_theme, basculer_theme, reinitialiser_application

def demander_profil(self):
    fen = tk.Toplevel(self.root)
    fen.title("🐧 Configuration")
    centrer_fenetre(self, fen, 400, 450)
    fen.configure(bg="#F9FAFB")
    fen.grab_set()
    try:
        fen.iconbitmap(ressource_path("favicon.ico"))
    except:
        pass
    self.profil_valide = False
    fen.protocol("WM_DELETE_WINDOW", lambda: fen.destroy())

    Label(fen, text="BIENVENUE", font=("Segoe UI", 18, "bold"), bg="#F9FAFB", fg="#312E81", pady=25).pack()
    Label(fen, text="Prénom :", bg="#F9FAFB", font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=50)
    ep = Entry(fen, font=("Segoe UI", 11), relief="solid", bd=1)
    ep.pack(pady=5, padx=50, fill="x")
    Label(fen, text="Nom :", bg="#F9FAFB", font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=50, pady=(10, 0))
    en = Entry(fen, font=("Segoe UI", 11), relief="solid", bd=1)
    en.pack(pady=5, padx=50, fill="x")

    def valider():
        p, n = ep.get().strip(), en.get().strip()
        if p and n:
            res = {"prenom": p, "nom": n, "mode_sombre": False}
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(res, f)
            self.profil_valide = True
            fen.destroy()
        else:
            messagebox.showwarning("Champs requis", "Veuillez entrer votre nom et prénom.")

    Button(fen, text="CRÉER MON PROFIL 🐧", bg="#312E81", fg="white",
           font=("Segoe UI", 10, "bold"), command=valider, pady=15, relief="flat").pack(pady=40, padx=50, fill="x")

    self.root.wait_window(fen)
    return self.charger_profil() if self.profil_valide else None

def ouvrir_aide(self):
    fen = tk.Toplevel(self.root)
    fen.title("🐧 Manuel d'Utilisation Complet")
    fen.resizable(False, False)
    centrer_fenetre(self, fen, 650, 800)
    fen.configure(bg=self.c_card)
    fen.grab_set()

    try:
        fen.iconbitmap(ressource_path("favicon.ico"))
    except:
        pass

    # Canvas scrollable
    canevas = tk.Canvas(fen, bg=self.c_card, highlightthickness=0)
    scrollbar = ttk.Scrollbar(fen, orient="vertical", command=canevas.yview)
    scrollbar.pack(side="right", fill="y")
    canevas.pack(side="left", fill="both", expand=True)

    scroll_frame = tk.Frame(canevas, bg=self.c_card)
    scroll_frame.bind("<Configure>", lambda e: canevas.configure(scrollregion=canevas.bbox("all")))
    canevas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canevas.configure(yscrollcommand=scrollbar.set)

    # Binding molette (seulement tant que la fenêtre existe)
    def on_mousewheel(event):
        if fen.winfo_exists():
            canevas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    fen.bind("<MouseWheel>", on_mousewheel)  # Binding sur la fenêtre, pas global

    # Bouton fermer en bas
    def fermer():
        fen.unbind("<MouseWheel>")
        fen.destroy()

    btn_fermer = tk.Button(
        fen,
        text="J'AI COMPRIS 🐧",
        command=fermer,
        bg=self.c_accent,
        fg="white",
        font=("Segoe UI", 11, "bold"),
        pady=15,
        relief="flat"
    )
    btn_fermer.pack(side="bottom", fill="x")

    # Titre
    tk.Label(
        scroll_frame,
        text="🐧 GUIDE COMPLET LINUX PRO",
        font=("Segoe UI", 16, "bold"),
        bg=self.c_card,
        fg=self.c_accent
    ).pack(pady=20, padx=40)

    # Fonction section
    def ajouter_section(titre, texte):
        f = tk.Frame(scroll_frame, bg=self.c_card, pady=10)
        f.pack(fill="x", padx=40)
        tk.Label(f, text=titre, font=("Segoe UI", 11, "bold"), bg=self.c_card, fg=self.c_fg,
                 wraplength=520, justify="left").pack(anchor="w")
        tk.Label(f, text=texte, font=("Segoe UI", 11), bg=self.c_card, fg=self.c_fg,
                 wraplength=520, justify="left").pack(anchor="w", pady=5)
        tk.Frame(scroll_frame, height=1, bg=self.c_border).pack(fill="x", padx=40, pady=5)

    # Contenu aide
    ajouter_section(
        "👤 GESTION DU PROFIL",
        "Au premier lancement, le logiciel vous demande votre Nom et Prénom. Ces informations servent à personnaliser votre expérience. Votre identifiant Linux (ex: jean.dupont) est généré automatiquement pour simuler le terminal dans les détails des commandes. Vous pouvez réinitialiser ce profil dans les Paramètres."
    )
    ajouter_section(
        "🌓 THÈMES ET APPARENCE",
        "Linux Pro dispose de deux modes : Clair et Sombre. Le mode sombre est conçu pour réduire la fatigue oculaire. Vous pouvez basculer entre les deux via le bouton 'PARAMÈTRES'. Votre choix est sauvegardé automatiquement dans le fichier de configuration."
    )
    ajouter_section(
        "🔍 NAVIGATION ET RECHERCHE",
        "La barre de recherche en haut vous permet de filtrer instantanément les commandes par leur nom ou par catégorie. Vous pouvez également cliquer sur les en-têtes du tableau pour trier la liste par ordre alphabétique (↑) ou inversé (↓)."
    )
    ajouter_section(
        "🎯 FONCTIONNEMENT DU QUIZ",
        "Le quiz teste vos connaissances sur les commandes Linux. \n1. Choisissez un défi (5 à 20 questions).\n2. Une description s'affiche, vous devez trouver la commande correspondante.\n3. À la fin, un score global s'affiche avec un message de félicitations.\n4. Vous pouvez recommencer ou quitter le quiz à tout moment."
    )
    ajouter_section(
        "➕ AJOUTER UNE COMMANDE",
        "Pour enrichir la base de données :\n1. Définissez la catégorie (Badge existant ou création d'une nouvelle via le bouton +).\n2. Remplissez tous les champs (Nom, Description, Exemple).\nIMPORTANT : Le logiciel formate automatiquement le nom et la catégorie avec une majuscule au début (ex: 'ssh' devient 'Ssh'). Les catégories ne doivent contenir que des lettres."
    )
    ajouter_section(
        "🎨 SYSTÈME D'ICÔNES ET VALIDATION",
        "Lors de la création d'une nouvelle catégorie, vous devez obligatoirement cliquer sur 'VALIDER' pour confirmer le nom. Cela fera apparaître une grille d'émojis tech. Sélectionnez l'icône de votre choix pour finaliser la création. Si vous sélectionnez une catégorie déjà existante, l'icône officielle sera utilisée automatiquement."
    )
    ajouter_section(
        "🗑️ SUPPRESSION ET SÉCURITÉ",
        "Le logiciel fait une distinction stricte entre deux types de commandes :\n• COMMANDES SYSTÈME : Les commandes de base (ls, cd, etc.) sont protégées. Elles ne peuvent pas être supprimées.\n• COMMANDES PERSONNELLES : Seules les commandes que vous avez créées via le bouton 'AJOUTER' apparaissent dans la liste de suppression et peuvent être retirées."
    )

    # Bind de fermeture propre
    fen.protocol("WM_DELETE_WINDOW", fermer)

def ouvrir_parametres(self):
    fen = tk.Toplevel(self.root)
    fen.title("🐧 Paramètres")
    centrer_fenetre(self, fen, 450, 400)
    fen.configure(bg=self.c_card, padx=30, pady=30)
    fen.grab_set()
    try:
        fen.iconbitmap(ressource_path("favicon.ico"))
    except:
        pass

    Label(fen, text="⚙️ RÉGLAGES", font=("Segoe UI", 13, "bold"), bg=self.c_card, fg=self.c_fg).pack(pady=(0, 25))
    txt = "PASSER AU MODE CLAIR ☀️" if self.mode_sombre else "PASSER AU MODE SOMBRE 🌙"
    Button(fen, text=txt, font=("Segoe UI", 10, "bold"), bg=self.c_accent, fg="white", pady=12, relief="flat",
           command=lambda: [basculer_theme(self), fen.destroy()]).pack(fill="x", pady=8)
    Button(fen, text="RÉINITIALISER LE PROFIL 🔄", font=("Segoe UI", 10, "bold"), bg="#F59E0B", fg="white", pady=12, relief="flat",
           command=lambda: reinitialiser_application(self)).pack(fill="x", pady=8)

def ouvrir_statistiques(self):
    scores_file = "scores.json"
    if not os.path.exists(scores_file) or os.stat(scores_file).st_size == 0:
        messagebox.showinfo("Statistiques", "Aucun score enregistré pour le moment.")
        return
    with open(scores_file, "r", encoding="utf-8") as f:
        scores = json.load(f)

    fen = tk.Toplevel(self.root)
    fen.title("📊 Statistiques des Scores")
    centrer_fenetre(self, fen, 700, 550)
    fen.configure(bg=self.c_card)
    fen.grab_set()
    try:
        fen.iconbitmap(ressource_path("favicon.ico"))
    except:
        pass

    Label(fen, text="HISTORIQUE DES QUIZ", font=("Segoe UI", 14, "bold"), bg=self.c_card, fg=self.c_accent).pack(pady=15)

    tree = ttk.Treeview(fen, columns=("date", "type", "score"), show="headings", height=15)
    tree.heading("date", text="Date")
    tree.heading("type", text="Quiz")
    tree.heading("score", text="Résultat")
    tree.column("date", width=180, anchor="center")
    tree.column("type", width=300, anchor="w")
    tree.column("score", width=150, anchor="center")

    tree.pack(fill="both", expand=True, padx=30, pady=(0, 20))

    for s in sorted(scores, key=lambda x: x["date_complete"], reverse=True):
        score_text = f"{s['score']}/{s['total']} ({s['pourcentage']})"
        pourcent_num = int(s['pourcentage'].rstrip('%')) if '%' in s['pourcentage'] else 0
        tag = "good" if pourcent_num >= 70 else "medium" if pourcent_num >= 40 else "bad"
        tree.insert("", "end", values=(s["date_complete"], s["quizz_type"], score_text), tags=(tag,))

    tree.tag_configure("good", foreground="#10B981")
    tree.tag_configure("medium", foreground="#F59E0B")
    tree.tag_configure("bad", foreground="#EF4444")

    scrollbar = ttk.Scrollbar(fen, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

def ouvrir_ajout(self):
    self.icone_choisie_finale = None
    self.couleur_choisie_finale = None
    self.var_cat = tk.StringVar()

    icones_reservees = list(self.icones.values())
    potentielles = ["🐧", "💻", "📟", "🌐", "📡", "🔗", "🔑", "🔐", "⚡", "📊", "🔍", "🕒", "🧪", "🚀", "🔥"]
    emojis_tech = [e for e in potentielles if e not in icones_reservees]

    couleurs_potentielles = [
        "#E0F7FA", "#E8F5E9", "#FFF3E0", "#F3E5F5", "#E3F2FD",
        "#FEFCE8", "#FFE4E6", "#ECFDF5", "#F1F5F9", "#F0FDF4"
    ]
    categories_data = obtenir_categories()
    couleurs_utilisees = [data["couleur"] for data in categories_data.values()]
    couleurs_disponibles = [c for c in couleurs_potentielles if c not in couleurs_utilisees]

    fen = tk.Toplevel(self.root)
    fen.title("🐧 Nouvelle commande")
    fen.resizable(False, False)
    centrer_fenetre(self, fen, 500, 750)
    fen.configure(bg=self.c_card, padx=25, pady=15)
    fen.grab_set()
    try:
        fen.iconbitmap(ressource_path("favicon.ico"))
    except:
        pass

    cadre_saisie_cat = tk.Frame(fen, bg=self.c_card)
    ent_saisie_libre = tk.Entry(cadre_saisie_cat, font=("Segoe UI", 10), bg=self.c_bg, fg=self.c_fg, relief="solid", borderwidth=1)
    cadre_custom_icon = tk.Frame(fen, bg=self.c_card)
    cadre_custom_couleur = tk.Frame(fen, bg=self.c_card)
    ent_cat_finale = tk.Entry(fen, font=("Segoe UI", 10, "bold"), bg="#F3F4F6", fg=self.c_accent, relief="flat", justify="center")

    def actualiser_vue():
        cat_nom = self.var_cat.get()
        if not cat_nom:
            txt = "Sélectionnez une catégorie..."
        else:
            ico = self.icones.get(cat_nom, self.icone_choisie_finale or "📦")
            txt = f"{ico} {cat_nom}"
        ent_cat_finale.config(state="normal")
        ent_cat_finale.delete(0, tk.END)
        ent_cat_finale.insert(0, txt)
        ent_cat_finale.config(state="readonly")

    def selectionner_cat_existante(nom):
        ent_saisie_libre.delete(0, tk.END)
        btn_valider_cat.config(state="disabled", bg="#D1D5DB")
        self.var_cat.set(nom)
        self.icone_choisie_finale = None
        self.couleur_choisie_finale = None
        cadre_custom_icon.pack_forget()
        cadre_custom_couleur.pack_forget()
        actualiser_vue()

    def au_clic_saisie_libre(event):
        btn_valider_cat.config(state="normal", bg=self.c_accent)
        self.var_cat.set("")
        self.icone_choisie_finale = None
        self.couleur_choisie_finale = None
        cadre_custom_icon.pack_forget()
        cadre_custom_couleur.pack_forget()
        actualiser_vue()

    def valider_nouvelle_cat():
        s = ent_saisie_libre.get().strip()
        if s:
            self.var_cat.set(s.capitalize())
            cadre_custom_icon.pack(fill="x", pady=5, after=cadre_saisie_cat)
            cadre_custom_couleur.pack(fill="x", pady=5, after=cadre_custom_icon)
            actualiser_vue()
        else:
            messagebox.showwarning("Attention", "Saisissez un nom de catégorie.", parent=fen)

    tk.Label(fen, text="1. CHOIX DE LA CATÉGORIE", font=("Segoe UI", 9, "bold"), bg=self.c_card, fg=self.c_accent).pack(anchor="w")
    cadre_badges = tk.Frame(fen, bg=self.c_card)
    cadre_badges.pack(fill="x", pady=5)
    row, col = 0, 0
    for c in self.categories:
        tk.Button(cadre_badges, text=c, font=("Segoe UI", 8), command=lambda x=c: selectionner_cat_existante(x),
               bg=self.c_bg, fg=self.c_fg, relief="flat").grid(row=row, column=col, padx=1, pady=1, sticky="we")
        col += 1
        if col > 4:
            col = 0
            row += 1

    tk.Label(fen, text="Ou créer une nouvelle catégorie :", font=("Segoe UI", 8), bg=self.c_card, fg="#6B7280").pack(anchor="w", pady=(10, 0))
    cadre_saisie_cat.pack(fill="x", pady=5)
    ent_saisie_libre.pack(side="left", fill="x", expand=True, ipady=3)
    ent_saisie_libre.bind("<FocusIn>", au_clic_saisie_libre)
    btn_valider_cat = tk.Button(cadre_saisie_cat, text="VALIDER ➔", command=valider_nouvelle_cat,
                                bg="#D1D5DB", fg="white", font=("Segoe UI", 8, "bold"), state="disabled")
    btn_valider_cat.pack(side="right", padx=5)

    tk.Label(cadre_custom_icon, text="Choisir une icône :", font=("Segoe UI", 8, "italic"), bg=self.c_card, fg=self.c_accent).pack(anchor="w")
    zone_emojis = tk.Frame(cadre_custom_icon, bg=self.c_card)
    zone_emojis.pack(pady=2)
    r_em, c_em = 0, 0
    for emo in emojis_tech:
        tk.Button(zone_emojis, text=emo, font=("Segoe UI", 10),
               command=lambda e=emo: [setattr(self, "icone_choisie_finale", e), actualiser_vue()],
               bg=self.c_bg, relief="flat", width=3).grid(row=r_em, column=c_em, padx=1, pady=1)
        c_em += 1
        if c_em > 6:
            c_em = 0
            r_em += 1

    tk.Label(cadre_custom_couleur, text="Choisir une couleur :", font=("Segoe UI", 8, "italic"), bg=self.c_card, fg=self.c_accent).pack(anchor="w")
    zone_couleurs = tk.Frame(cadre_custom_couleur, bg=self.c_card)
    zone_couleurs.pack(pady=2)
    r_col, c_col = 0, 0
    for col in couleurs_disponibles:
        tk.Button(zone_couleurs, bg=col, width=5, height=2,
               command=lambda cl=col: setattr(self, "couleur_choisie_finale", cl),
               relief="flat").grid(row=r_col, column=c_col, padx=1, pady=1)
        c_col += 1
        if c_col > 6:
            c_col = 0
            r_col += 1

    ent_cat_finale.pack(fill="x", pady=10, ipady=5)
    ent_cat_finale.insert(0, "Sélectionnez une catégorie...")
    ent_cat_finale.config(state="readonly")

    tk.Label(fen, text="2. DÉTAILS DE LA COMMANDE", font=("Segoe UI", 9, "bold"), bg=self.c_card, fg=self.c_accent).pack(anchor="w", pady=(5, 5))
    ch = {}
    for lib, cl in [("Nom", "n"), ("Description", "d"), ("Exemple", "e")]:
        tk.Label(fen, text=lib, font=("Segoe UI", 8), bg=self.c_card, fg=self.c_fg).pack(anchor="w")
        ch[cl] = tk.Entry(fen, font=("Segoe UI", 10), bg=self.c_bg, fg=self.c_fg, relief="solid", borderwidth=1)
        ch[cl].pack(fill="x", pady=(0, 5), ipady=3)

    def sau():
        cat = self.var_cat.get().strip()
        nom = ch["n"].get().strip()
        des = ch["d"].get().strip()
        exe = ch["e"].get().strip()
        ico = self.icone_choisie_finale
        couleur = self.couleur_choisie_finale

        erreurs = []
        if not cat or "Sélectionnez" in cat:
            erreurs.append("• Catégorie manquante.")
        if cat not in self.categories:
            if ico is None:
                erreurs.append("• Choisissez une icône pour cette nouvelle catégorie.")
            if couleur is None:
                erreurs.append("• Choisissez une couleur pour cette nouvelle catégorie.")
        if not nom:
            erreurs.append("• Nom manquant.")
        if not des:
            erreurs.append("• Description manquante.")
        if not exe:
            erreurs.append("• Exemple manquant.")

        if erreurs:
            messagebox.showwarning("Incomplet", "\n".join(erreurs), parent=fen)
            return

        icone_finale = self.icones.get(cat, ico) if cat in self.icones else ico
        couleur_finale = couleur if cat not in self.categories else obtenir_categories().get(cat, {}).get("couleur", couleur)

        if cat not in self.categories:
            ajouter_categorie(cat, icone_finale, couleur_finale)

        if ajouter_commande(nom, des, exe, cat, icone_finale, couleur_finale):
            messagebox.showinfo("Succès ✨", f"La commande '{nom.upper()}' est enregistrée.", parent=fen)
            self.actualiser_tableau()
            self.trier_colonne("cmd")
            fen.destroy()
        else:
            messagebox.showerror("Erreur ❌", "Erreur lors de l'enregistrement.", parent=fen)

    tk.Button(fen, text="ENREGISTRER LA COMMANDE 🐧", bg="#10B981", fg="white", font=("Segoe UI", 10, "bold"),
           pady=12, command=sau, relief="flat").pack(fill="x", pady=(10, 0))

def ouvrir_suppression(self):
    commandes_perso = obtenir_commandes_perso()
    if not commandes_perso:
        messagebox.showinfo("Suppression", "Aucune commande personnelle à supprimer.")
        return

    fen = tk.Toplevel(self.root)
    fen.title("🗑️ Supprimer mes commandes")
    centrer_fenetre(self, fen, 400, 500)
    fen.configure(bg=self.c_card, padx=20, pady=20)
    fen.grab_set()
    try:
        fen.iconbitmap(ressource_path("favicon.ico"))
    except:
        pass

    tk.Label(fen, text="MES COMMANDES PERSO", font=("Segoe UI", 12, "bold"), bg=self.c_card, fg="#EF4444").pack(pady=(0, 15))

    cadre_liste = tk.Frame(fen, bg=self.c_card)
    cadre_liste.pack(fill="both", expand=True)
    canvas = tk.Canvas(cadre_liste, bg=self.c_card, highlightthickness=0)
    scroll = ttk.Scrollbar(cadre_liste, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas, bg=self.c_card)
    scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scroll.set)
    canvas.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")

    def confirmer_suppression(nom):
        if messagebox.askyesno("Confirmation", f"Supprimer '{nom}' définitivement ?"):
            if supprimer_commande(nom):
                self.actualiser_tableau()
                fen.destroy()
                messagebox.showinfo("Succès", f"Commande '{nom}' supprimée.")

    for nom in sorted(commandes_perso.keys()):
        f = tk.Frame(scroll_frame, bg=self.c_card, pady=5)
        f.pack(fill="x", expand=True)
        tk.Label(f, text=f"• {nom.upper()}", font=("Segoe UI", 10), bg=self.c_card, fg=self.c_fg).pack(side="left")
        tk.Button(f, text="❌", bg="#EF4444", fg="white", font=("Arial", 8, "bold"),
               command=lambda n=nom: confirmer_suppression(n)).pack(side="right", padx=10)