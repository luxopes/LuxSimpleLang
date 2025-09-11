import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QTextEdit, QMenuBar,
                           QMenu, QFileDialog, QMessageBox, QStatusBar, QSpinBox,
                           QPlainTextEdit, QSplashScreen)
from PyQt6.QtCore import Qt, QSize, QRect, QUrl, QTimer
from PyQt6.QtGui import (QFont, QKeySequence, QShortcut, QTextCharFormat, 
                        QSyntaxHighlighter, QColor, QPainter, QTextFormat, QDesktopServices,
                        QPixmap)
from code import SimpleLangInterpreter

class SimpleLangHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None, dark_theme=True):
        super().__init__(parent)
        self.dark_theme = dark_theme
        self.update_colors()

    def update_colors(self):
        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(QColor("#94a3b8"))
        self.comment_format.setFontItalic(True)

        self.keyword_format = QTextCharFormat()
        self.keyword_format.setForeground(QColor("#38bdf8"))

        self.keywords = ["if", "else:", "end", ";", "loop", "while", "function", "call",
                        "print", "append", "remove", "input", "break", "continue",
                        "readfile", "writefile", "appendfile", "createdir", "listdir",
                        "deletedir", "return", "for", "in", "upper", "lower"]

    def highlightBlock(self, text):
        # Zvýraznění komentářů
        if '#' in text:
            index = text.index('#')
            self.setFormat(index, len(text) - index, self.comment_format)

        # Zvýraznění klíčových slov
        for keyword in self.keywords:
            index = 0
            while index >= 0:
                index = text.find(keyword, index)
                if index >= 0:
                    # Kontrola, zda je klíčové slovo samostatné
                    if (index == 0 or not text[index-1].isalnum()) and \
                       (index + len(keyword) == len(text) or not text[index + len(keyword)].isalnum()):
                        self.setFormat(index, len(keyword), self.keyword_format)
                    index += len(keyword)

class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.editor.line_number_area_paint_event(event)

class CodeEditor(QPlainTextEdit):
    def __init__(self, theme='dark', parent=None):
        super().__init__(parent)
        self.theme = theme
        self.line_number_area = LineNumberArea(self)
        
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        
        self.update_line_number_area_width(0)
        self.highlight_current_line()

    def line_number_area_width(self):
        digits = 1
        count = max(1, self.blockCount())
        while count >= 10:
            count //= 10
            digits += 1
        space = 3 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(),
                                              self.line_number_area_width(), cr.height()))

    def line_number_area_paint_event(self, event):
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), Qt.GlobalColor.lightGray)

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        offset = self.contentOffset()
        top = self.blockBoundingGeometry(block).translated(offset).top()
        bottom = top + self.blockBoundingRect(block).height()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(Qt.GlobalColor.black)
                painter.drawText(0, int(top), self.line_number_area.width(), 
                               self.fontMetrics().height(),
                               Qt.AlignmentFlag.AlignRight, number)
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1

    def highlight_current_line(self):
        extra_selections = []
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            # Pro tmavý motiv použijeme tmavě modrou, pro světlý motiv světle modrou
            if self.theme == 'dark':
                line_color = QColor("#1e293b")  # tmavě modrá pro tmavý motiv
            else:
                line_color = QColor("#f0f9ff")  # světle modrá pro světlý motiv
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)
        self.setExtraSelections(extra_selections)

class SimpleLangIDE(QMainWindow):
    def __init__(self):
        super().__init__()
        self.language = 'en'
        self.theme = 'dark'
        self.current_file = None
        self.fullscreen = False
        self.font_size = 11
        
        # Překlady
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
                'menu_manual': "Online manuál",
                'menu_language': "Jazyk",
                'menu_theme': "Motiv",
                'theme_dark': "Tmavý motiv",
                'theme_light': "Světlý motiv",
                'about_text': "LuxSimpleLang IDE\nVerze 0.0.3 Unstable\nAutor: Antonín Tomeček\nLicence: Lux Development\nKontakt: bambiliarda@gmail.com\nFormát souborů: .lsl",
                'guide_text': "📘 Návod k použití LuxSimpleLang IDE\n\n" +
                            "- Do horního editoru napište svůj kód v jazyce LuxSimpleLang.\n" +
                            "- Klikněte na tlačítko 'Spustit kód'.\n" +
                            "- Výstup běžícího kódu se zobrazí v dolním okně.\n\n" +
                            "Zkratky:\n" +
                            " Ctrl+O – otevřít soubor\n" +
                            " Ctrl+S – uložit soubor\n" +
                            " Ctrl+Z – zpět\n" +
                            " Ctrl+Y – znovu\n" +
                            " F11 – fullscreen\n\n" +
                            "Syntaxe jazyka:\n\n" +
                            "1. Základní příkazy:\n" +
                            "   - print <výraz> – vypíše hodnotu\n" +
                            "   - input \"prompt\" – načte vstup od uživatele\n" +
                            "   - var = <výraz> – přiřadí hodnotu do proměnné\n\n" +
                            "2. Řídící struktury:\n" +
                            "   - if <podmínka>: ... end\n" +
                            "   - if <podmínka>: ... else: ... end\n" +
                            "   - while <podmínka>: ... end\n" +
                            "   - for i from 0 to 10: ... end\n" +
                            "   - break – ukončí cyklus\n" +
                            "   - continue – přeskočí na další iteraci\n\n" +
                            "3. Funkce:\n" +
                            "   - function name(param1, param2): ... end\n" +
                            "   - call name(arg1, arg2)\n" +
                            "   - return <hodnota>\n\n" +
                            "4. Práce se soubory:\n" +
                            "   - writefile \"soubor.txt\", \"text\" – vytvoří/přepíše soubor\n" +
                            "   - appendfile \"soubor.txt\", \"text\" – přidá text na konec\n" +
                            "   - readfile \"soubor.txt\" – načte obsah souboru\n" +
                            "   - createdir \"slozka\" – vytvoří složku\n" +
                            "   - listdir \"slozka\" – vypíše obsah složky\n" +
                            "   - deletedir \"slozka\" – smaže prázdnou složku\n\n" +
                            "5. Práce s textem:\n" +
                            "   - upper(\"text\") – převede na velká písmena\n" +
                            "   - lower(\"text\") – převede na malá písmena\n\n" +
                            "6. Komentáře:\n" +
                            "   - # jednořádkový komentář\n" +
                            "   - /* víceřádkový\n" +
                            "      komentář */\n\n" +
                            "7. Blok kódu lze ukončit:\n" +
                            "   - end\n" +
                            "   - ; (středník)\n\n" +
                            "8. Další funkce:\n" +
                            "   - date – vrátí aktuální datum\n" +
                            "   - rand(min, max) – náhodné číslo\n" +
                            "   - len(seznam) – délka seznamu\n" +
                            "   - exists(\"cesta\") – test existence souboru/složky"
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
                'menu_manual': "Online Manual",
                'menu_language': "Language",
                'menu_theme': "Theme",
                'theme_dark': "Dark theme",
                'theme_light': "Light theme",
                'about_text': "LuxSimpleLang IDE\nVersion 0.0.3 Unstable\nAuthor: Antonín Tomeček\nLicence: Lux Development\nContact: bambiliarda@gmail.com\nFile format: .lsl",
                'guide_text': "📘 How to use LuxSimpleLang IDE\n\n" +
                            "- Type your LuxSimpleLang code into the top editor.\n" +
                            "- Click the 'Run code' button.\n" +
                            "- Program output will appear in the bottom window.\n\n" +
                            "Shortcuts:\n" +
                            " Ctrl+O – open file\n" +
                            " Ctrl+S – save file\n" +
                            " Ctrl+Z – undo\n" +
                            " Ctrl+Y – redo\n" +
                            " F11 – fullscreen\n\n" +
                            "Language syntax:\n\n" +
                            "1. Basic Commands:\n" +
                            "   - print <expression> – prints value\n" +
                            "   - input \"prompt\" – reads user input\n" +
                            "   - var = <expression> – assigns value to variable\n\n" +
                            "2. Control Structures:\n" +
                            "   - if <condition>: ... end\n" +
                            "   - if <condition>: ... else: ... end\n" +
                            "   - while <condition>: ... end\n" +
                            "   - for i from 0 to 10: ... end\n" +
                            "   - break – exits loop\n" +
                            "   - continue – skips to next iteration\n\n" +
                            "3. Functions:\n" +
                            "   - function name(param1, param2): ... end\n" +
                            "   - call name(arg1, arg2)\n" +
                            "   - return <value>\n\n" +
                            "4. File Operations:\n" +
                            "   - writefile \"file.txt\", \"text\" – creates/overwrites file\n" +
                            "   - appendfile \"file.txt\", \"text\" – appends text\n" +
                            "   - readfile \"file.txt\" – reads file content\n" +
                            "   - createdir \"folder\" – creates directory\n" +
                            "   - listdir \"folder\" – lists directory contents\n" +
                            "   - deletedir \"folder\" – deletes empty directory\n\n" +
                            "5. Text Operations:\n" +
                            "   - upper(\"text\") – converts to uppercase\n" +
                            "   - lower(\"text\") – converts to lowercase\n\n" +
                            "6. Comments:\n" +
                            "   - # single line comment\n" +
                            "   - /* multiline\n" +
                            "      comment */\n\n" +
                            "7. Block endings:\n" +
                            "   - end\n" +
                            "   - ; (semicolon)\n\n" +
                            "8. Additional Functions:\n" +
                            "   - date – returns current date\n" +
                            "   - rand(min, max) – random number\n" +
                            "   - len(list) – list length\n" +
                            "   - exists(\"path\") – tests file/folder existence"
            }
        }
        
        self.build_gui()

    def t(self, key):
        return self.translations[self.language][key]

    def build_gui(self):
        self.setWindowTitle(self.t('title'))
        self.setMinimumSize(QSize(1000, 700))

        # Hlavní widget a layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Editor
        header_layout = QHBoxLayout()
        
        self.editor_label = QLabel(self.t('enter_code'))
        self.editor_label.setObjectName("editor_label")
        header_layout.addWidget(self.editor_label)
        
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 72)
        self.font_size_spin.setValue(self.font_size)
        self.font_size_spin.valueChanged.connect(self.change_font_size)
        header_layout.addStretch()
        header_layout.addWidget(QLabel("Font size:"))
        header_layout.addWidget(self.font_size_spin)
        
        layout.addLayout(header_layout)

        self.code_input = CodeEditor(theme=self.theme)
        self.code_input.setFont(QFont("Courier New", self.font_size))
        layout.addWidget(self.code_input)

        # Zvýrazňovač syntaxe
        self.highlighter = SimpleLangHighlighter(self.code_input.document())

        # Menu
        self.create_menus()

        # Tlačítka
        button_layout = QHBoxLayout()
        self.run_button = QPushButton(self.t('run_code'))
        self.undo_button = QPushButton(self.t('undo'))
        self.redo_button = QPushButton(self.t('redo'))

        self.run_button.clicked.connect(self.run_code)
        self.undo_button.clicked.connect(self.code_input.undo)
        self.redo_button.clicked.connect(self.code_input.redo)

        button_layout.addWidget(self.run_button)
        button_layout.addWidget(self.undo_button)
        button_layout.addWidget(self.redo_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Výstup
        self.output_label = QLabel(self.t('output'))
        self.output_label.setObjectName("output_label")
        layout.addWidget(self.output_label)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setFont(QFont("Courier New", 11))
        layout.addWidget(self.output)

        # Klávesové zkratky
        open_shortcut = QShortcut(QKeySequence("Ctrl+O"), self)
        open_shortcut.activated.connect(self.open_file)
        
        save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        save_shortcut.activated.connect(self.save_file)
        
        fullscreen_shortcut = QShortcut(QKeySequence("F11"), self)
        fullscreen_shortcut.activated.connect(self.toggle_fullscreen)
        
        exit_fullscreen_shortcut = QShortcut(QKeySequence("Esc"), self)
        exit_fullscreen_shortcut.activated.connect(self.exit_fullscreen)

        # Status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")
        
        self.apply_theme()

    def change_font_size(self, size):
        self.font_size = size
        self.code_input.setFont(QFont("Courier New", size))
        self.output.setFont(QFont("Courier New", size))

    def create_menus(self):
        # File menu
        file_menu = self.menuBar().addMenu(self.t('menu_file'))
        
        open_action = file_menu.addAction(self.t('menu_open'))
        open_action.triggered.connect(self.open_file)
        open_action.setShortcut("Ctrl+O")
        
        save_action = file_menu.addAction(self.t('menu_save'))
        save_action.triggered.connect(self.save_file)
        save_action.setShortcut("Ctrl+S")
        
        save_as_action = file_menu.addAction(self.t('menu_save_as'))
        save_as_action.triggered.connect(self.save_file_as)
        
        file_menu.addSeparator()
        exit_action = file_menu.addAction(self.t('menu_exit'))
        exit_action.triggered.connect(self.close)

        # Edit menu
        edit_menu = self.menuBar().addMenu(self.t('menu_edit'))
        
        undo_action = edit_menu.addAction(self.t('undo'))
        undo_action.triggered.connect(self.code_input.undo)
        undo_action.setShortcut("Ctrl+Z")
        
        redo_action = edit_menu.addAction(self.t('redo'))
        redo_action.triggered.connect(self.code_input.redo)
        redo_action.setShortcut("Ctrl+Y")

        # Language menu
        lang_menu = self.menuBar().addMenu(self.t('menu_language'))
        
        cs_action = lang_menu.addAction("Čeština")
        cs_action.triggered.connect(lambda: self.change_language('cs'))
        
        en_action = lang_menu.addAction("English")
        en_action.triggered.connect(lambda: self.change_language('en'))

        # Theme menu
        theme_menu = self.menuBar().addMenu(self.t('menu_theme'))
        
        dark_action = theme_menu.addAction(self.t('theme_dark'))
        dark_action.triggered.connect(lambda: self.change_theme('dark'))
        
        light_action = theme_menu.addAction(self.t('theme_light'))
        light_action.triggered.connect(lambda: self.change_theme('light'))

        # Help menu
        help_menu = self.menuBar().addMenu(self.t('menu_help'))
        
        guide_action = help_menu.addAction(self.t('menu_guide'))
        guide_action.triggered.connect(self.show_guide)
        
        manual_action = help_menu.addAction(self.t('menu_manual'))
        manual_action.triggered.connect(self.open_manual)
        
        about_action = help_menu.addAction(self.t('menu_about'))
        about_action.triggered.connect(self.show_about)

    def apply_theme(self):
        if self.theme == 'dark':
            self.setStyleSheet("""
                QMainWindow, QWidget { background-color: #1a1a1a; color: white; }
                QTextEdit { 
                    background-color: #0f172a; 
                    color: white; 
                    border: 1px solid #2d2d2d;
                }
                QTextEdit#output { 
                    background-color: #1e3a8a; 
                    color: lime;
                }
                QPushButton {
                    background-color: #2d2d2d;
                    color: white;
                    border: 1px solid #3d3d3d;
                    padding: 5px 10px;
                }
                QPushButton:hover {
                    background-color: #3d3d3d;
                }
                QMenuBar {
                    background-color: #2d2d2d;
                    color: white;
                    border-bottom: 1px solid #3d3d3d;
                }
                QMenuBar::item {
                    padding: 4px 8px;
                    margin: 0;
                }
                QMenuBar::item:selected {
                    background-color: #3d3d3d;
                }
                QMenu {
                    background-color: #2d2d2d;
                    color: white;
                    border: 1px solid #3d3d3d;
                }
                QMenu::item {
                    padding: 4px 20px;
                }
                QMenu::item:selected {
                    background-color: #3d3d3d;
                }
                QStatusBar {
                    background-color: #2d2d2d;
                    color: #a0a0a0;
                    border-top: 1px solid #3d3d3d;
                }
                QSpinBox {
                    background-color: #2d2d2d;
                    color: white;
                    border: 1px solid #3d3d3d;
                    padding: 2px;
                }
                QSpinBox::up-button, QSpinBox::down-button {
                    background-color: #3d3d3d;
                    border: none;
                }
                QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                    background-color: #4d4d4d;
                }
                QLineNumberArea {
                    background-color: #1a1a1a;
                    color: #606060;
                    border-right: 1px solid #2d2d2d;
                }
            """)
        else:
            self.setStyleSheet("""
                QMainWindow, QWidget { background-color: white; color: black; }
                QTextEdit { 
                    background-color: white; 
                    color: black; 
                    border: 1px solid #d4d4d4;
                }
                QTextEdit#output { 
                    background-color: #f0f0f0; 
                    color: black;
                }
                QPushButton {
                    background-color: #f0f0f0;
                    color: black;
                    border: 1px solid #d4d4d4;
                    padding: 5px 10px;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
                QMenuBar {
                    background-color: #f0f0f0;
                    border-bottom: 1px solid #d4d4d4;
                }
                QMenuBar::item {
                    padding: 4px 8px;
                    margin: 0;
                }
                QMenuBar::item:selected {
                    background-color: #e0e0e0;
                }
                QMenu {
                    background-color: white;
                    border: 1px solid #d4d4d4;
                }
                QMenu::item {
                    padding: 4px 20px;
                }
                QMenu::item:selected {
                    background-color: #e0e0e0;
                }
                QStatusBar {
                    background-color: #f0f0f0;
                    color: #666666;
                    border-top: 1px solid #d4d4d4;
                }
                QSpinBox {
                    background-color: white;
                    color: black;
                    border: 1px solid #d4d4d4;
                    padding: 2px;
                }
                QSpinBox::up-button, QSpinBox::down-button {
                    background-color: #f0f0f0;
                    border: none;
                }
                QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                    background-color: #e0e0e0;
                }
                QLineNumberArea {
                    background-color: #f5f5f5;
                    color: #999999;
                    border-right: 1px solid #d4d4d4;
                }
            """)
        self.output.setObjectName("output")

    def change_language(self, lang):
        self.language = lang
        self.setWindowTitle(self.t('title'))
        
        # Aktualizace textů
        self.editor_label.setText(self.t('enter_code'))
        self.output_label.setText(self.t('output'))
        self.run_button.setText(self.t('run_code'))
        self.undo_button.setText(self.t('undo'))
        self.redo_button.setText(self.t('redo'))
        
        # Znovu vytvoříme menu
        menubar = self.menuBar()
        menubar.clear()
        self.create_menus()

    def change_theme(self, theme):
        self.theme = theme
        self.apply_theme()
        self.highlighter.dark_theme = (theme == 'dark')
        self.highlighter.update_colors()
        self.highlighter.rehighlight()
        # Aktualizujeme téma v editoru
        self.code_input.theme = theme
        # Aktualizujeme zvýraznění aktuálního řádku
        self.code_input.highlight_current_line()

    def toggle_fullscreen(self):
        if self.fullscreen:
            self.showNormal()
        else:
            self.showFullScreen()
        self.fullscreen = not self.fullscreen

    def exit_fullscreen(self):
        if self.fullscreen:
            self.showNormal()
            self.fullscreen = False

    def run_code(self):
        self.output.clear()
        self.statusBar.showMessage("Running code...")
        code = self.code_input.toPlainText()
        interpreter = SimpleLangInterpreter(lambda text: self.output.append(text))
        try:
            interpreter.run(code)
            self.statusBar.showMessage("Code execution completed")
        except Exception as e:
            self.statusBar.showMessage(f"Error: {str(e)}")
            self.output.append(f"[Error: {str(e)}]")

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            "",
            "LuxSimpleLang files (*.lsl);;All files (*.*)"
        )
        if file_path:
            with open(file_path, "r", encoding="utf-8") as f:
                self.code_input.setPlainText(f.read())
            self.current_file = file_path

    def save_file(self):
        if self.current_file:
            with open(self.current_file, "w", encoding="utf-8") as f:
                f.write(self.code_input.toPlainText())
        else:
            self.save_file_as()

    def save_file_as(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save File",
            "",
            "LuxSimpleLang files (*.lsl);;All files (*.*)"
        )
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self.code_input.toPlainText())
            self.current_file = file_path

    def show_about(self):
        QMessageBox.information(self, self.t('menu_about'), self.t('about_text'))

    def open_manual(self):
        QDesktopServices.openUrl(QUrl("https://lsl.netlify.app/"))

    def show_guide(self):
        QMessageBox.information(self, self.t('menu_guide'), self.t('guide_text'))

def create_splash_screen():
    # Vytvoření splash screenu s logem
    splash_pix = QPixmap("icon.png")
    splash_pix = splash_pix.scaledToWidth(200, Qt.TransformationMode.SmoothTransformation)  # Zvětšení ikony
    splash = QSplashScreen(splash_pix, Qt.WindowType.WindowStaysOnTopHint)  # Zajistí, že zůstane navrchu
    
    # Nastavení fontu pro text
    font = splash.font()
    font.setPixelSize(14)
    font.setBold(True)  # Tučný text pro lepší viditelnost
    splash.setFont(font)
    
    # Přidání textu pod logo
    splash.showMessage("Loading LuxSimpleLang IDE...",
                      Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter,
                      QColor(255, 255, 255))
    return splash

def main():
    app = QApplication(sys.argv)
    
    # Vytvoření a zobrazení splash screenu
    splash = create_splash_screen()
    splash.show()
    app.processEvents()  # Zajistí okamžité zobrazení splash screenu
    
    # Vytvoření hlavního okna
    window = SimpleLangIDE()
    
    # Použití QTimer pro zpoždění
    def show_main_window():
        window.show()
        splash.finish(window)
    
    QTimer.singleShot(3000, show_main_window)  # 3000 ms = 3 sekundy
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
