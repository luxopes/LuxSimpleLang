import os
import sys
import tkinter as tk
from gui import SimpleLangIDE

def run_gui():
    root = tk.Tk()

    # Nastavíme titulek okna
    root.title("LuxSimpleLang IDE")

    # Nastavíme WM_CLASS pro window manager
    try:
        root.tk.call('wm', 'class', root._w, 'LuxSimpleLang')
    except tk.TclError:
        pass  # na Windows není potřeba

    # Najdeme cestu k ikoně
    # 1) současná složka (vývoj)
    icon_path = os.path.join(os.path.dirname(sys.argv[0]), "icon.png")
    # 2) při instalaci /opt
    if not os.path.isfile(icon_path):
        icon_path = "/opt/luxsimplelang/icon.png"

    # Nastavíme ikonku přímo v kódu
    try:
        icon_img = tk.PhotoImage(file=icon_path)
        root.iconphoto(False, icon_img)
    except Exception as e:
        print("Ikonu se nepodařilo načíst:", e)

    # Inicializace IDE
    app = SimpleLangIDE(root)

    # Spuštění hlavní smyčky
    root.mainloop()

if __name__ == "__main__":
    run_gui()

