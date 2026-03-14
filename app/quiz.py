import random
import tkinter as tk
from tkinter import messagebox, Label, Button, Frame, Canvas
from tkinter import ttk

from data.data import enregistrer_score, obtenir_commandes_completes
from app.theme_utils import centrer_fenetre


def lancer_quiz_pre(self):
    data_globale = obtenir_commandes_completes()
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

    Label(
        self.cadre_quiz,
        text=f"Prêt pour le Quiz, {self.utilisateur['prenom'].capitalize()} ? 🐧",
        font=("Segoe UI", 13, "bold"),
        bg=self.c_card,
        fg=self.c_accent,
    ).pack(pady=20)

    Label(
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
            Button(
                self.cadre_quiz,
                text=texte,
                bg=couleur,
                fg="white",
                font=("Segoe UI", 10, "bold"),
                command=lambda n=nb, txt=texte: lancer_quiz_action(self, n, txt),
                relief="flat",
                pady=10,
            ).pack(fill="x", pady=5, padx=80)

    Button(
        self.cadre_quiz,
        text="ANNULER",
        command=lambda: quitter_quiz(self),
        bg="#6B7280",
        fg="white",
        pady=8,
    ).pack(pady=20)


def lancer_quiz_action(self, nb, quizz_type):
    self.score_q = 0
    self.index_q = 0
    self.reponses_donnees = []

    cles_disponibles = list(self.donnees.keys())
    self.questions = []
    nb = min(nb, len(cles_disponibles))

    for _ in range(nb):
        bonne_reponse = random.choice(cles_disponibles)
        cles_disponibles.remove(bonne_reponse)
        autres = [c for c in self.donnees.keys() if c != bonne_reponse]
        options = random.sample(autres, 3) + [bonne_reponse]
        random.shuffle(options)
        self.questions.append(
            {
                "d": self.donnees[bonne_reponse]["description"],
                "o": options,
                "a": bonne_reponse,
            }
        )

    self.current_quizz_type = quizz_type
    prochaine_question(self)


def prochaine_question(self):
    for w in self.cadre_quiz.winfo_children():
        w.destroy()

    # ── Écran de résultats ──────────────────────────────────────
    if self.index_q >= len(self.questions):
        enregistrer_score(self.score_q, len(self.questions), self.current_quizz_type)

        total = len(self.questions)
        pourcent = round((self.score_q / total * 100), 1) if total > 0 else 0

        if pourcent >= 90:
            msg = "PERFECT ! 🎉 Tu es un dieu du terminal !"
        elif pourcent >= 75:
            msg = "EXCELLENT ! 🔥 Tu maîtrises vraiment bien."
        elif pourcent >= 50:
            msg = "PAS MAL ! 💪 Continue comme ça."
        elif pourcent >= 25:
            msg = "Courage ! 📚 Il faut encore s'entraîner."
        else:
            msg = "On recommence ? 😅 Ça viendra !"

        # En-tête score (fixe, non scrollable)
        frame_score = Frame(self.cadre_quiz, bg=self.c_card)
        frame_score.pack(pady=15, fill="x")
        Label(
            frame_score,
            text=msg,
            font=("Segoe UI", 16, "bold"),
            bg=self.c_card,
            fg=self.c_accent,
        ).pack()
        Label(
            frame_score,
            text=f"Score : {self.score_q} / {total}  –  {pourcent}%",
            font=("Segoe UI", 22, "bold"),
            bg=self.c_card,
            fg="#10B981",
        ).pack(pady=8)

        # Bilan scrollable
        Label(
            self.cadre_quiz,
            text="Bilan des réponses :",
            font=("Segoe UI", 12, "bold"),
            bg=self.c_card,
            fg=self.c_fg,
        ).pack(pady=(10, 5))

        cadre_scroll = Frame(self.cadre_quiz, bg=self.c_card)
        cadre_scroll.pack(fill="both", expand=True, padx=10)

        canvas = Canvas(cadre_scroll, bg=self.c_card, highlightthickness=0)
        scrollbar = ttk.Scrollbar(cadre_scroll, orient="vertical", command=canvas.yview)
        inner = Frame(canvas, bg=self.c_card)
        inner.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        # Scroll molette cross-platform
        def _on_mousewheel(event):
            if event.delta:
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            elif event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")

        canvas.bind("<MouseWheel>", _on_mousewheel)
        canvas.bind("<Button-4>", _on_mousewheel)
        canvas.bind("<Button-5>", _on_mousewheel)

        for i, q in enumerate(self.questions):
            votre = self.reponses_donnees[i] if i < len(self.reponses_donnees) else "—"
            bonne = q["a"]
            resultat = "✅ Correct" if votre == bonne else "❌ Incorrect"
            couleur = "#10B981" if votre == bonne else "#EF4444"

            Label(
                inner,
                text=f"Q{i + 1}: {q['d']}",
                font=("Segoe UI", 10),
                bg=self.c_card,
                fg=self.c_fg,
                wraplength=520,
                anchor="w",
                justify="left",
            ).pack(anchor="w", padx=20, pady=(6, 0))

            Label(
                inner,
                text=f"Ta réponse : {votre}   |   Bonne : {bonne}   |   {resultat}",
                font=("Segoe UI", 10, "bold"),
                bg=self.c_card,
                fg=couleur,
                anchor="w",
            ).pack(anchor="w", padx=20, pady=(2, 6))

            Frame(inner, height=1, bg=self.c_border).pack(fill="x", padx=20)

        # Boutons (fixe, en bas)
        frame_boutons = Frame(self.cadre_quiz, bg=self.c_card)
        frame_boutons.pack(pady=15, fill="x")
        Button(
            frame_boutons,
            text="🔄 RECOMMENCER",
            command=lambda: lancer_quiz_pre(self),
            bg="#10B981",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            pady=12,
            padx=40,
            relief="flat",
        ).pack(side="left", padx=20)
        Button(
            frame_boutons,
            text="🚪 QUITTER LE QUIZ",
            command=lambda: quitter_quiz(self),
            bg="#EF4444",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            pady=12,
            padx=40,
            relief="flat",
        ).pack(side="right", padx=20)
        return

    # ── Question normale ─────────────────────────────────────────
    q = self.questions[self.index_q]

    Label(
        self.cadre_quiz,
        text=f"Question {self.index_q + 1} sur {len(self.questions)}",
        bg=self.c_card,
        fg="#6B7280",
        font=("Segoe UI", 10),
    ).pack(pady=(20, 5))

    Label(
        self.cadre_quiz,
        text=q["d"],
        font=("Segoe UI", 12),
        bg=self.c_card,
        fg=self.c_fg,
        wraplength=420,
        pady=20,
    ).pack()

    for opt in q["o"]:
        btn_bg = "#E5E7EB" if not self.mode_sombre else "#374151"
        Button(
            self.cadre_quiz,
            text=opt.upper(),
            bg=btn_bg,
            fg=self.c_fg,
            pady=12,
            relief="flat",
            font=("Segoe UI", 10),
            command=lambda v=opt: valider(self, v, q),
        ).pack(fill="x", pady=4, padx=50)


def valider(self, v, q):
    self.reponses_donnees.append(v)
    if v == q["a"]:
        self.score_q += 1
    self.index_q += 1
    prochaine_question(self)


def quitter_quiz(self):
    self.quiz_en_cours = False
    self.afficher_details(None)
