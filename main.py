import tkinter as tk
from data.data import assurer_fichiers
from app.application import ApplicationLinux

if __name__ == "__main__":
    assurer_fichiers()
    root = tk.Tk()
    root.withdraw()
    app = ApplicationLinux(root)
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\n[!] Fermeture demandée par l'utilisateur.")
    except Exception as e:
        print(f"\n[!] Erreur critique : {e}")