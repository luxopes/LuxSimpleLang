import os
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from gui_qt import SimpleLangIDE

def run_gui():
    app = QApplication(sys.argv)
    app.setApplicationName("LuxSimpleLang IDE")
    app.setApplicationDisplayName("LuxSimpleLang IDE")

    # Najdeme cestu k ikoně
    # 1) současná složka (vývoj)
    icon_path = os.path.join(os.path.dirname(sys.argv[0]), "icon.png")
    # 2) při instalaci /opt
    if not os.path.isfile(icon_path):
        icon_path = "/opt/luxsimplelang/icon.png"

    # Nastavíme ikonku
    if os.path.isfile(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # Inicializace IDE
    window = SimpleLangIDE()
    window.show()

    # Spuštění hlavní smyčky
    sys.exit(app.exec())

if __name__ == "__main__":
    run_gui()

