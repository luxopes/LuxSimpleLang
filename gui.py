'''
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, font
from code import SimpleLangInterpreter

class SimpleLangIDE:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1000x700")
        self.fullscreen = False

        # ----- Překlady -----
        self.translations = {
            'cs': {
                'title': "LuxSimpleLang IDE",
                'enter_code': "Zadej svůj LuxSimpleLang kód:",
                'run_code': "▶ Spustit kód",
                'undo': "↶ Zpět",
                'redo': "↷ Znovu",
                'output': "Výstup:",
                'menu_file': "Soubor",
                'menu_open': "Otevřít…",
                'menu_save': "Uložit",
                'menu_save_as': "Uložit jako…",
                'menu_exit': "Konec",
                'menu_edit': "Úpravy",
                'menu_help': "Nápověda",
                'menu_about': "O aplikaci",
                'menu_guide': "Návod k použití",
                'menu_language': "Jazyk",
                'menu_theme': "Motiv",
                'about_text': "LuxSimpleLang IDE\nVerze 0.0.1 BETA\nAutor: Antonín Tomeček\nLicence: Lux Development\nFormát souborů: .lsl",
                'guide_text': (
                    "📘 Návod k použití LuxSimpleLang IDE\n\n"
                    "- Do horního editoru napište svůj kód v jazyce LuxSimpleLang.\n"
                    "- Klikněte na tlačítko 'Spustit kód'.\n"
                    "- Výstup běžícího kódu se zobrazí v dolním okně.\n\n"
                    "Zkratky:\n"
                    " Ctrl+O – otevřít soubor\n"
                    " Ctrl+S – uložit soubor\n"
                    " Ctrl+Z – zpět\n"
                    " Ctrl+Y – znovu\n"
                    " F11 – fullscreen\n\n"
                    "Syntaxe jazyka: if/else/end, loop, while, function, call, print, append, remove, input, break, continue."
                ),
                'theme_dark': "Tmavý",
                'theme_light': "Světlý"
            },
            'en': {
                'title': "LuxSimpleLang IDE",
                'enter_code': "Enter your LuxSimpleLang code:",
                'run_code': "▶ Run code",
                'undo': "↶ Undo",
                'redo': "↷ Redo",
                'output': "Output:",
                'menu_file': "File",
                'menu_open': "Open…",
                'menu_save': "Save",
                'menu_save_as': "Save as…",
                'menu_exit': "Exit",
                'menu_edit': "Edit",
                'menu_help': "Help",
                'menu_about': "About",
                'menu_guide': "User Guide",
                'menu_language': "Language",
                'menu_theme': "Theme",
                'about_text': "LuxSimpleLang IDE\nVersion 0.0.1 BETA\nAuthor: Antonín Tomeček\nLicence: Lux Development\nFile format: .lsl",
                'guide_text': (
                    "📘 How to use LuxSimpleLang IDE\n\n"
                    "- Type your LuxSimpleLang code into the top editor.\n"
                    "- Click the 'Run code' button.\n"
                    "- Program output will appear in the bottom window.\n\n"
                    "Shortcuts:\n"
                    " Ctrl+O – open file\n"
                    " Ctrl+S – save file\n"
                    " Ctrl+Z – undo\n"
                    " Ctrl+Y – redo\n"
                    " F11 – fullscreen\n\n"
                    "Language syntax: if/else/end, loop, while, function, call, print, append, remove, input, break, continue."
                ),
                'theme_dark': "Dark",
                'theme_light': "Light"
            }
        }

        self.language = 'cs'
        self.theme = 'dark'

        self.build_gui()

    def t(self, key):
        return self.translations[self.language][key]

    def build_gui(self):
        self.root.title(self.t('title'))

        # --- Menubar ---
        self.menubar = tk.Menu(self.root)

        # File menu
        self.filemenu = tk.Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label=self.t('menu_open'), command=self.open_file, accelerator="Ctrl+O")
        self.filemenu.add_command(label=self.t('menu_save'), command=self.save_file, accelerator="Ctrl+S")
        self.filemenu.add_command(label=self.t('menu_save_as'), command=self.save_file_as)
        self.filemenu.add_separator()
        self.filemenu.add_command(label=self.t('menu_exit'), command=self.root.quit)
        self.menubar.add_cascade(label=self.t('menu_file'), menu=self.filemenu)

        # Edit menu
        self.editmenu = tk.Menu(self.menubar, tearoff=0)
        self.editmenu.add_command(label=self.t('undo'), command=lambda: self.code_input.edit_undo(), accelerator="Ctrl+Z")
        self.editmenu.add_command(label=self.t('redo'), command=lambda: self.code_input.edit_redo(), accelerator="Ctrl+Y")
        self.menubar.add_cascade(label=self.t('menu_edit'), menu=self.editmenu)

        # Language menu
        self.langmenu = tk.Menu(self.menubar, tearoff=0)
        self.langmenu.add_command(label="Čeština", command=lambda: self.change_language('cs'))
        self.langmenu.add_command(label="English", command=lambda: self.change_language('en'))
        self.menubar.add_cascade(label=self.t('menu_language'), menu=self.langmenu)

        # Theme menu
        self.thememenu = tk.Menu(self.menubar, tearoff=0)
        self.thememenu.add_command(label=self.t('theme_dark'), command=lambda: self.change_theme('dark'))
        self.thememenu.add_command(label=self.t('theme_light'), command=lambda: self.change_theme('light'))
        self.menubar.add_cascade(label=self.t('menu_theme'), menu=self.thememenu)

        # Help menu
        self.helpmenu = tk.Menu(self.menubar, tearoff=0)
        self.helpmenu.add_command(label=self.t('menu_guide'), command=self.show_guide)
        self.helpmenu.add_command(label=self.t('menu_about'), command=self.show_about)
        self.menubar.add_cascade(label=self.t('menu_help'), menu=self.helpmenu)

        self.root.config(menu=self.menubar)

        # Klávesové zkratky
        self.root.bind_all("<Control-o>", lambda e: self.open_file())
        self.root.bind_all("<Control-s>", lambda e: self.save_file())
        self.root.bind_all("<Control-z>", lambda e: self.code_input.edit_undo())
        self.root.bind_all("<Control-y>", lambda e: self.code_input.edit_redo())
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.exit_fullscreen)

        # Editor
        ttk.Label(self.root, text=self.t('enter_code')).pack(anchor="w", padx=10, pady=(10, 0))
        self.code_input = tk.Text(self.root, height=20, width=100, undo=True, wrap="none")
        self.code_input.pack(padx=10, pady=5, fill="both", expand=True)
        self.default_font = font.Font(family="Courier New", size=11)
        self.comment_font = font.Font(family="Courier New", size=11, slant="italic")
        self.code_input.configure(font=self.default_font)
        self.code_input.tag_configure("comment", foreground="#94a3b8", font=self.comment_font)
        self.code_input.tag_configure("keyword", foreground="#38bdf8", font=self.default_font)
        self.code_input.bind("<KeyRelease>", self.highlight_syntax)

        # Buttons
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=5)
        ttk.Button(button_frame, text=self.t('run_code'), command=self.run_code).pack(side="left", padx=5)
        ttk.Button(button_frame, text=self.t('undo'), command=lambda: self.code_input.edit_undo()).pack(side="left", padx=5)
        ttk.Button(button_frame, text=self.t('redo'), command=lambda: self.code_input.edit_redo()).pack(side="left", padx=5)

        ttk.Label(self.root, text=self.t('output')).pack(anchor="w", padx=10)
        self.output = tk.Text(self.root, height=10, width=100, wrap="none")
        self.output.pack(padx=10, pady=(0, 10), fill="x")

        self.current_file = None
        self.apply_theme()

    def apply_theme(self):
        if self.theme == 'dark':
            bg_code = "#0f172a"
            fg_code = "white"
            bg_out = "#1e3a8a"
            fg_out = "lime"
        else:  # light
            bg_code = "white"
            fg_code = "black"
            bg_out = "#f0f0f0"
            fg_out = "black"
        self.code_input.configure(bg=bg_code, fg=fg_code, insertbackground=fg_code)
        self.output.configure(bg=bg_out, fg=fg_out, insertbackground=fg_out)

    def change_language(self, lang):
        self.language = lang
        for widget in self.root.pack_slaves():
            widget.destroy()
        self.build_gui()

    def change_theme(self, theme):
        self.theme = theme
        self.apply_theme()

    def toggle_fullscreen(self, event=None):
        self.fullscreen = not self.fullscreen
        self.root.attributes("-fullscreen", self.fullscreen)

    def exit_fullscreen(self, event=None):
        self.fullscreen = False
        self.root.attributes("-fullscreen", False)

    def run_code(self):
        self.output.delete(1.0, tk.END)
        code = self.code_input.get("1.0", tk.END)
        interpreter = SimpleLangInterpreter(lambda text: self.output.insert(tk.END, text + "\n"))
        interpreter.run(code)

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("LuxSimpleLang soubory", "*.lsl"), ("All files", "*.*")])
        if file_path:
            with open(file_path, "r", encoding="utf-8") as f:
                self.code_input.delete(1.0, tk.END)
                self.code_input.insert(tk.END, f.read())
            self.current_file = file_path
            self.highlight_syntax()

    def save_file(self):
        if self.current_file:
            with open(self.current_file, "w", encoding="utf-8") as f:
                f.write(self.code_input.get("1.0", tk.END))
        else:
            self.save_file_as()

    def save_file_as(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".lsl",
                                                 filetypes=[("LuxSimpleLang soubory", "*.lsl"), ("All files", "*.*")])
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self.code_input.get("1.0", tk.END))
            self.current_file = file_path

    def show_about(self):
        messagebox.showinfo(self.t('menu_about'), self.t('about_text'))

    def show_guide(self):
        messagebox.showinfo(self.t('menu_guide'), self.t('guide_text'))

    def highlight_syntax(self, event=None):
        text = self.code_input.get("1.0", tk.END)
        self.code_input.tag_remove("comment", "1.0", tk.END)
        self.code_input.tag_remove("keyword", "1.0", tk.END)

        start = "1.0"
        while True:
            idx = self.code_input.search("#", start, tk.END)
            if not idx:
                break
            line_end = self.code_input.index(idx + " lineend")
            self.code_input.tag_add("comment", idx, line_end)
            start = line_end

        keywords = ["if", "else:", "end", "loop", "while", "function", "call",
                    "print", "append", "remove", "input", "break", "continue"]
        for kw in keywords:
            start = "1.0"
            while True:
                idx = self.code_input.search(r"\m"+kw+r"\M", start, tk.END, regexp=True)
                if not idx:
                    break
                end_idx = f"{idx}+{len(kw)}c"
                self.code_input.tag_add("keyword", idx, end_idx)
                start = end_idx
'''

import sys, os, re
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget,
    QPushButton, QMenuBar, QMenu, QFileDialog, QMessageBox, QHBoxLayout
)
from PyQt6.QtGui import QIcon, QFont, QTextCharFormat, QColor, QAction, QKeySequence
from PyQt6.QtCore import Qt
from code import SimpleLangInterpreter  # tvůj interpretr

class LuxSimpleLangIDE(QMainWindow):
    def __init__(self):
        super().__init__()

        # ---------- Config ----------
        self.languages = ['cs', 'en']
        self.language = 'cs'
        self.theme = 'dark'
        self.fullscreen = False
        self.current_file = None

        self.translations = {
            'cs': {
                'title': "LuxSimpleLang IDE",
                'enter_code': "Zadej svůj LuxSimpleLang kód:",
                'run_code': "▶ Spustit kód",
                'undo': "↶ Zpět",
                'redo': "↷ Znovu",
                'output': "Výstup:",
                'menu_file': "Soubor",
                'menu_open': "Otevřít…",
                'menu_save': "Uložit",
                'menu_save_as': "Uložit jako…",
                'menu_exit': "Konec",
                'menu_edit': "Úpravy",
                'menu_help': "Nápověda",
                'menu_about': "O aplikaci",
                'menu_guide': "Návod k použití",
                'menu_language': "Jazyk",
                'menu_theme': "Motiv",
                'theme_dark': "Tmavý",
                'theme_light': "Světlý",
                'about_text': "LuxSimpleLang IDE\nVerze 0.0.1 BETA\nAutor: Antonín Tomeček\nLicence: Lux Development\nFormát souborů: .lsl",
                'guide_text': (
                    "📘 Návod k použití LuxSimpleLang IDE\n\n"
                    "- Do horního editoru napište svůj kód v jazyce LuxSimpleLang.\n"
                    "- Klikněte na tlačítko 'Spustit kód'.\n"
                    "- Výstup běžícího kódu se zobrazí v dolním okně.\n\n"
                    "Zkratky:\n"
                    " Ctrl+O – otevřít soubor\n"
                    " Ctrl+S – uložit soubor\n"
                    " Ctrl+Z – zpět\n"
                    " Ctrl+Y – znovu\n"
                    " F11 – fullscreen\n\n"
                    "Syntaxe jazyka: if/else/end, loop, while, function, call, print, append, remove, input, break, continue."
                )
            },
            'en': {
                'title': "LuxSimpleLang IDE",
                'enter_code': "Enter your LuxSimpleLang code:",
                'run_code': "▶ Run code",
                'undo': "↶ Undo",
                'redo': "↷ Redo",
                'output': "Output:",
                'menu_file': "File",
                'menu_open': "Open…",
                'menu_save': "Save",
                'menu_save_as': "Save as…",
                'menu_exit': "Exit",
                'menu_edit': "Edit",
                'menu_help': "Help",
                'menu_about': "About",
                'menu_guide': "User Guide",
                'menu_language': "Language",
                'menu_theme': "Theme",
                'theme_dark': "Dark",
                'theme_light': "Light",
                'about_text': "LuxSimpleLang IDE\nVersion 0.0.1 BETA\nAuthor: Antonín Tomeček\nLicence: Lux Development\nFile format: .lsl",
                'guide_text': (
                    "📘 How to use LuxSimpleLang IDE\n\n"
                    "- Type your LuxSimpleLang code into the top editor.\n"
                    "- Click the 'Run code' button.\n"
                    "- Program output will appear in the bottom window.\n\n"
                    "Shortcuts:\n"
                    " Ctrl+O – open file\n"
                    " Ctrl+S – save file\n"
                    " Ctrl+Z – undo\n"
                    " Ctrl+Y – redo\n"
                    " F11 – fullscreen\n\n"
                    "Language syntax: if/else/end, loop, while, function, call, print, append, remove, input, break, continue."
                )
            }
        }

        # ---------- Window ----------
        self.setWindowTitle(self.trans('title'))
        icon_path = os.path.join(os.path.dirname(sys.argv[0]), "icon.png")
        if not os.path.isfile(icon_path):
            icon_path = "/opt/luxsimplelang/icon.png"
        self.setWindowIcon(QIcon(icon_path))
        self.resize(1000, 700)

        # ---------- GUI ----------
        self.init_ui()
        self.apply_theme()

    def trans(self, key):
        return self.translations[self.language][key]

    # ---------- GUI ----------
    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Editor
        self.editor = QTextEdit()
        self.editor.setFont(QFont("Courier New", 11))
        layout.addWidget(self.editor)
        self.editor.textChanged.connect(self.highlight_syntax)

        # Buttons
        button_layout = QHBoxLayout()
        self.run_button = QPushButton(self.trans('run_code'))
        self.run_button.clicked.connect(self.run_code)
        self.undo_button = QPushButton(self.trans('undo'))
        self.undo_button.clicked.connect(self.editor.undo)
        self.redo_button = QPushButton(self.trans('redo'))
        self.redo_button.clicked.connect(self.editor.redo)
        button_layout.addWidget(self.run_button)
        button_layout.addWidget(self.undo_button)
        button_layout.addWidget(self.redo_button)
        layout.addLayout(button_layout)

        # Output
        self.output = QTextEdit()
        self.output.setFont(QFont("Courier New", 11))
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

        # Menus
        menubar = self.menuBar()
        self.create_menus(menubar)

        # Shortcuts
        self.create_shortcuts()

    def create_menus(self, menubar: QMenuBar):
        # File
        file_menu = menubar.addMenu(self.trans('menu_file'))
        open_action = QAction(self.trans('menu_open'), self)
        open_action.setShortcut(QKeySequence("Ctrl+O"))
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        save_action = QAction(self.trans('menu_save'), self)
        save_action.setShortcut(QKeySequence("Ctrl+S"))
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        save_as_action = QAction(self.trans('menu_save_as'), self)
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)

        exit_action = QAction(self.trans('menu_exit'), self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Help
        help_menu = menubar.addMenu(self.trans('menu_help'))
        guide_action = QAction(self.trans('menu_guide'), self)
        guide_action.triggered.connect(self.show_guide)
        help_menu.addAction(guide_action)

        about_action = QAction(self.trans('menu_about'), self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        # Language
        lang_menu = menubar.addMenu(self.trans('menu_language'))
        for lang in self.languages:
            act = QAction(lang.upper(), self)
            act.triggered.connect(lambda checked, l=lang: self.change_language(l))
            lang_menu.addAction(act)

        # Theme
        theme_menu = menubar.addMenu(self.trans('menu_theme'))
        dark_act = QAction(self.trans('theme_dark'), self)
        dark_act.triggered.connect(lambda: self.change_theme('dark'))
        theme_menu.addAction(dark_act)
        light_act = QAction(self.trans('theme_light'), self)
        light_act.triggered.connect(lambda: self.change_theme('light'))
        theme_menu.addAction(light_act)

    def create_shortcuts(self):
        self.editor.undo()  # enable undo stack
        self.editor.redo()
        self.run_button.setShortcut("F5")
        self.editor.setFocus()
        self.editor.setTabStopDistance(4*QFont("Courier New",11).pointSize())

    # ---------- File operations ----------
    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "LuxSimpleLang (*.lsl);;All Files (*)")
        if path:
            with open(path, "r", encoding="utf-8") as f:
                self.editor.setPlainText(f.read())
            self.current_file = path

    def save_file(self):
        if self.current_file:
            with open(self.current_file, "w", encoding="utf-8") as f:
                f.write(self.editor.toPlainText())
        else:
            self.save_file_as()

    def save_file_as(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "LuxSimpleLang (*.lsl);;All Files (*)")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.editor.toPlainText())
            self.current_file = path

    # ---------- Run code ----------
    def run_code(self):
        self.output.clear()
        code = self.editor.toPlainText()
        interpreter = SimpleLangInterpreter(lambda text: self.output.append(text))
        interpreter.run(code)

    # ---------- About / Guide ----------
    def show_about(self):
        QMessageBox.information(self, self.trans('menu_about'), self.trans('about_text'))

    def show_guide(self):
        QMessageBox.information(self, self.trans('menu_guide'), self.trans('guide_text'))

    # ---------- Language / Theme ----------
    def change_language(self, lang):
        self.language = lang
        self.setWindowTitle(self.trans('title'))
        self.init_ui()
        self.apply_theme()

    def apply_theme(self):
        if self.theme == 'dark':
            self.editor.setStyleSheet("background-color:#0f172a; color:white;")
            self.output.setStyleSheet("background-color:#1e3a8a; color:lime;")
        else:
            self.editor.setStyleSheet("background-color:white; color:black;")
            self.output.setStyleSheet("background-color:#f0f0f0; color:black;")

    def change_theme(self, theme):
        self.theme = theme
        self.apply_theme()

    # ---------- Fullscreen ----------
    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        self.setWindowState(Qt.WindowState.WindowFullScreen if self.fullscreen else Qt.WindowState.WindowNoState)

    # ---------- Syntax highlighting ----------
    def highlight_syntax(self):
        # Basic keyword coloring
        keywords = ["if", "else:", "end", "loop", "while", "function", "call",
                    "print", "append", "remove", "input", "break", "continue"]
        cursor = self.editor.textCursor()
        fmt_keyword = QTextCharFormat()
        fmt_keyword.setForeground(QColor("#38bdf8"))
        fmt_comment = QTextCharFormat()
        fmt_comment.setForeground(QColor("#94a3b8"))

        # Save cursor
        pos = cursor.position()
        text = self.editor.toPlainText()
        cursor.select(cursor.SelectionType.Document)
        cursor.setCharFormat(QTextCharFormat())  # clear formatting

        # Comments
        for match in re.finditer(r"#.*", text):
            cursor.setPosition(match.start())
            cursor.setPosition(match.end(), cursor.MoveMode.KeepAnchor)
            cursor.setCharFormat(fmt_comment)

        # Keywords
        for kw in keywords:
            for match in re.finditer(rf"\b{kw}\b", text):
                cursor.setPosition(match.start())
                cursor.setPosition(match.end(), cursor.MoveMode.KeepAnchor)
                cursor.setCharFormat(fmt_keyword)

        # Restore cursor
        cursor.setPosition(pos)
        self.editor.setTextCursor(cursor)

# ---------- Run ----------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LuxSimpleLangIDE()
    window.show()
    sys.exit(app.exec())

