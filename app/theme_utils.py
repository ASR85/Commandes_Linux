import json
import tkinter as tk

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
    self.champ_recherche.configure(bg=self.c_card, fg=self.c_fg, insertbackground=self.c_fg)

    self.style.configure("Treeview", background=self.c_card, foreground=self.c_fg, fieldbackground=self.c_card)
    self.style.configure("Treeview.Heading", background=self.c_accent, foreground="white")

    self.cadre_details.configure(bg=self.c_card, highlightbackground=self.c_border)
    self.zone_affichage.configure(bg=self.c_card, foreground=self.c_fg)
    self.cadre_liste.configure(bg=self.c_card)
    self.bas_page.configure(bg=self.c_card, highlightbackground=self.c_border)

def basculer_theme(self):
    self.mode_sombre = not self.mode_sombre
    self.utilisateur["mode_sombre"] = self.mode_sombre
    with open(self.config_file, "w", encoding="utf-8") as f:
        json.dump(self.utilisateur, f)
    appliquer_theme(self)

def reinitialiser_application(self):
    from tkinter import messagebox
    if messagebox.askyesno("Réinitialisation", "Effacer votre profil et redémarrer ?"):
        import os
        files_to_delete = [self.config_file, "scores.json", "categories.json"]
        for file in files_to_delete:
            if os.path.exists(file):
                os.remove(file)
        self.root.destroy()
        os.system("python main.py")

def centrer_fenetre(self, f, largeur, hauteur):
    l, h = int(largeur), int(hauteur)
    x = (f.winfo_screenwidth() // 2) - (l // 2)
    y = (f.winfo_screenheight() // 2) - (h // 2)
    f.geometry(f"{l}x{h}+{x}+{y}")

def nettoyer_recherche(self, event):
    if self.champ_recherche.get() == "Rechercher une commande ou une catégorie...":
        self.champ_recherche.delete(0, tk.END)