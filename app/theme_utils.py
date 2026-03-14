import json
import sys
import os
import tkinter as tk


def appliquer_theme(self):
    if self.mode_sombre:
        self.c_bg     = "#111827"
        self.c_fg     = "#F9FAFB"
        self.c_card   = "#1F2937"
        self.c_accent = "#4F46E5"
        self.c_border = "#374151"
    else:
        self.c_bg     = "#F3F4F6"
        self.c_fg     = "#111827"
        self.c_card   = "#FFFFFF"
        self.c_accent = "#312E81"
        self.c_border = "#D1D5DB"

    self.root.configure(bg=self.c_bg)
    self.entete.configure(bg=self.c_accent)
    self.lbl_titre.configure(bg=self.c_accent, fg="white")
    self.cadre_profil.configure(bg=self.c_accent)
    self.lbl_user.configure(bg=self.c_accent, fg="white")
    self.corps.configure(bg=self.c_bg)
    self.zone_recherche.configure(bg=self.c_bg)
    self.cadre_saisie.configure(bg=self.c_card, highlightbackground=self.c_border)
    self.lbl_loupe.configure(bg=self.c_card, fg="#64748B")
    self.champ_recherche.configure(bg=self.c_card, fg=self.c_fg, insertbackground=self.c_fg)
    self.cadre_details.configure(bg=self.c_card, highlightbackground=self.c_border)
    self.zone_affichage.configure(bg=self.c_card, foreground=self.c_fg)
    self.cadre_liste.configure(bg=self.c_card)
    self.bas_page.configure(bg=self.c_card, highlightbackground=self.c_border)

    # Tableau Canvas custom — thème + rechargement des lignes
    if hasattr(self, "tableau"):
        self.tableau.appliquer_theme(self.c_accent, self.c_border, self.c_card)
        if hasattr(self, "donnees"):
            self.actualiser_tableau()


def basculer_theme(self):
    from data.data import F_CONFIG
    self.mode_sombre = not self.mode_sombre
    self.utilisateur["mode_sombre"] = self.mode_sombre
    with open(F_CONFIG, "w", encoding="utf-8") as f:
        json.dump(self.utilisateur, f, ensure_ascii=False, indent=4)
    appliquer_theme(self)


def reinitialiser_application(self):
    from tkinter import messagebox
    from data.data import F_CONFIG, F_SCORES, F_CATEGORIES, F_COMMANDS_PER
    if not messagebox.askyesno("Réinitialisation", "Effacer votre profil et redémarrer ?"):
        return

    # Supprimer tous les fichiers runtime utilisateur (chemins corrects via runtime_path)
    for fichier in [F_CONFIG, F_SCORES, F_CATEGORIES, F_COMMANDS_PER]:
        if os.path.exists(fichier):
            try:
                os.remove(fichier)
            except OSError:
                pass

    self.root.destroy()

    # Relance cross-platform : fonctionne en dev ET dans l'exe PyInstaller
    if getattr(sys, "frozen", False):
        # Mode exe : relancer l'exécutable directement
        os.execv(sys.executable, [sys.executable])
    else:
        # Mode dev : relancer main.py via l'interpréteur Python
        script = os.path.normpath(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "main.py")
        )
        os.execv(sys.executable, [sys.executable, script])


def centrer_fenetre(self, f, largeur, hauteur):
    l, h = int(largeur), int(hauteur)
    f.update_idletasks()
    x = (f.winfo_screenwidth()  // 2) - (l // 2)
    y = (f.winfo_screenheight() // 2) - (h // 2)
    f.geometry(f"{l}x{h}+{x}+{y}")


def nettoyer_recherche(self, event):
    if self.champ_recherche.get() == "Rechercher une commande ou une catégorie...":
        self.champ_recherche.delete(0, tk.END)