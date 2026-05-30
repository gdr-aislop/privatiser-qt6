#!/usr/bin/env python3
"""Privatiser — PyQt6 desktop GUI for the privatiser-engine library."""

import json
import re
import sys
from typing import Optional

from PyQt6.QtCore import QSettings, Qt, pyqtSignal
from PyQt6.QtGui import QAction, QFont, QKeySequence
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QFileDialog,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QStatusBar,
    QStyle,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from privatiser import Privatiser
from privatiser.patterns import PatternHandler

CATEGORY_KEYS = [
    ("secrets",     "Secrets & Keys"),
    ("network",     "Network (IPs, Domains)"),
    ("pii",         "PII (Phone, Cards)"),
    ("aws",         "AWS"),
    ("cloud",       "Cloud (Azure, GCP)"),
    ("identifiers", "Generic Identifiers"),
]

SAMPLE_TEXT = """\
server_ip    = "192.168.1.100"
password     = "super_secret_pass_123"
api_key      = "sk-proj-abc123xyz789"
email        = "john.smith@company.com"
aws_account  = "123456789012"
arn          = "arn:aws:iam::123456789012:role/admin"
phone        = "+1-555-123-4567"
credit_card  = "4111 1111 1111 1111"
db_url       = "postgresql://user:pass@prod-db.mycompany.com/mydb"
"""

DARK_STYLESHEET = """
    QMainWindow, QWidget {
        background-color: #1a1a1a;
        color: #e0e0e0;
    }
    QMenuBar {
        background-color: #141414;
        color: #e0e0e0;
        border-bottom: 1px solid #333;
    }
    QMenuBar::item:selected {
        background-color: #2d5a8e;
    }
    QMenu {
        background-color: #222;
        border: 1px solid #444;
        color: #e0e0e0;
    }
    QMenu::item:selected {
        background-color: #2d5a8e;
    }
    QTextEdit {
        background-color: #1e1e1e;
        color: #d4d4d4;
        font-family: "JetBrains Mono", "Fira Code", "Cascadia Code", "Courier New", monospace;
        border: none;
        padding: 8px;
        selection-background-color: #264f78;
    }
    QTextEdit:focus {
        border: 2px solid #4fc3f7;
    }
    QLineEdit {
        background-color: #2a2a2a;
        color: #e0e0e0;
        border: 1px solid #444;
        border-radius: 4px;
        padding: 4px 8px;
    }
    QLineEdit:focus {
        border: 2px solid #4fc3f7;
    }
    QPushButton {
        background-color: #2a2a2a;
        color: #e0e0e0;
        border: 1px solid #555;
        border-radius: 4px;
        padding: 4px 14px;
        min-height: 28px;
    }
    QPushButton:hover {
        background-color: #3a3a3a;
        border-color: #777;
    }
    QPushButton:pressed {
        background-color: #1a1a1a;
    }
    QPushButton:focus {
        border: 2px solid #4fc3f7;
        outline: none;
    }
    QPushButton:disabled {
        color: #555;
        border-color: #333;
    }
    QPushButton[class="primary"] {
        background-color: #1e3a5f;
        color: #ffffff;
        font-weight: bold;
        border: 1px solid #2d5a8e;
        font-size: 13pt;
        padding: 8px 28px;
        min-height: 40px;
    }
    QPushButton[class="primary"]:hover {
        background-color: #2d5a8e;
    }
    QPushButton[class="primary"]:focus {
        border: 2px solid #4fc3f7;
    }
    QPushButton[class="secondary"] {
        background-color: #252525;
        color: #e0e0e0;
        font-weight: bold;
        border: 1px solid #555;
        font-size: 13pt;
        padding: 8px 28px;
        min-height: 40px;
    }
    QPushButton[class="secondary"]:hover {
        background-color: #333;
    }
    QPushButton[class="secondary"]:focus {
        border: 2px solid #4fc3f7;
    }
    QPushButton[class="companion"] {
        background-color: #1a2e45;
        color: #a0c4e0;
        border: 1px solid #2a4a6a;
        font-size: 12pt;
        padding: 8px 16px;
        min-height: 40px;
    }
    QPushButton[class="companion"]:hover {
        background-color: #243d58;
        color: #d0e8f8;
    }
    QPushButton[class="companion"]:focus {
        border: 2px solid #4fc3f7;
    }
    QPushButton[class="danger"] {
        background-color: #2a2a2a;
        color: #e07070;
        border: 1px solid #555;
        font-size: 13pt;
        padding: 8px 20px;
        min-height: 40px;
    }
    QPushButton[class="danger"]:hover {
        background-color: #3a1a1a;
        border-color: #884444;
    }
    QCheckBox {
        spacing: 8px;
        min-height: 28px;
    }
    QCheckBox::indicator {
        width: 18px;
        height: 18px;
        border: 1px solid #555;
        border-radius: 3px;
        background-color: #2a2a2a;
    }
    QCheckBox::indicator:checked {
        background-color: #2d5a8e;
        border-color: #4fc3f7;
    }
    QCheckBox:focus {
        border: 2px solid #4fc3f7;
        border-radius: 3px;
    }
    QGroupBox {
        border: 1px solid #3a3a3a;
        border-radius: 4px;
        margin-top: 10px;
        padding-top: 6px;
        font-weight: bold;
        font-size: 9pt;
        color: #888888;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 4px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    QToolButton {
        background-color: #222;
        color: #bbbbbb;
        border: none;
        border-bottom: 1px solid #333;
        font-weight: bold;
        text-align: left;
        padding-left: 10px;
        font-size: 11pt;
        min-height: 36px;
    }
    QToolButton:hover {
        background-color: #2a2a2a;
        color: #e0e0e0;
    }
    QToolButton:focus {
        border: 2px solid #4fc3f7;
        outline: none;
    }
    QTableWidget {
        background-color: #1e1e1e;
        color: #d4d4d4;
        alternate-background-color: #232323;
        gridline-color: #2e2e2e;
        font-family: "JetBrains Mono", "Fira Code", "Cascadia Code", "Courier New", monospace;
        font-size: 10pt;
        border: 1px solid #333;
    }
    QTableWidget:focus {
        border: 2px solid #4fc3f7;
    }
    QHeaderView::section {
        background-color: #252525;
        color: #999999;
        padding: 4px 8px;
        border: none;
        border-bottom: 1px solid #3a3a3a;
        font-size: 9pt;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    QScrollBar:vertical {
        background: #1a1a1a;
        width: 10px;
        border: none;
    }
    QScrollBar::handle:vertical {
        background: #3a3a3a;
        border-radius: 5px;
        min-height: 20px;
    }
    QScrollBar::handle:vertical:hover {
        background: #4a4a4a;
    }
    QScrollBar:horizontal {
        background: #1a1a1a;
        height: 10px;
        border: none;
    }
    QScrollBar::handle:horizontal {
        background: #3a3a3a;
        border-radius: 5px;
        min-width: 20px;
    }
    QScrollBar::add-line, QScrollBar::sub-line {
        width: 0;
        height: 0;
    }
    QSplitter::handle {
        background-color: #2e2e2e;
    }
    QStatusBar {
        background-color: #141414;
        color: #777777;
        border-top: 1px solid #2a2a2a;
        font-size: 10pt;
    }
    QWidget#paneHeader {
        background-color: #222;
        border-bottom: 1px solid #2e2e2e;
    }
    QLabel#paneLabel {
        color: #666;
        background: transparent;
    }
    QLabel#fieldLabel {
        color: #888;
    }
    QLabel#hintLabel {
        color: #555;
    }
    QLabel#emptyState {
        color: #555;
        padding: 16px;
    }
    QPushButton#headerBtn {
        border: 1px solid #3a3a3a;
        border-radius: 3px;
        background: #2a2a2a;
        color: #ccc;
        padding: 2px 10px;
    }
    QPushButton#headerBtn:hover {
        background: #3a3a3a;
        color: #fff;
    }
    QPushButton#headerBtn:focus {
        border: 2px solid #4fc3f7;
    }
    QPushButton#headerBtn:disabled {
        color: #444;
    }
"""


# ── Collapsible section widget ─────────────────────────────────────────────────

class CollapsibleSection(QWidget):
    """Header toggle button + hidden/shown content area."""

    toggled = pyqtSignal(bool)  # emitted when expanded/collapsed via the header button

    def __init__(self, title: str, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._title = title
        self._expanded = True

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._toggle = QToolButton()
        self._toggle.setCheckable(True)
        self._toggle.setChecked(True)
        self._toggle.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._toggle.toggled.connect(self._on_toggled)
        self._update_toggle_text()
        root.addWidget(self._toggle)

        self._body = QWidget()
        body_layout = QVBoxLayout(self._body)
        body_layout.setContentsMargins(12, 10, 12, 10)
        body_layout.setSpacing(10)
        root.addWidget(self._body)

    def _on_toggled(self, checked: bool) -> None:
        self._expanded = checked
        self._body.setVisible(checked)
        self._update_toggle_text()
        state = "expanded" if checked else "collapsed"
        self._toggle.setAccessibleDescription(f"{self._title} section, {state}")
        self.toggled.emit(checked)

    def _update_toggle_text(self) -> None:
        arrow = "▼" if self._expanded else "▶"
        self._toggle.setText(f"  {arrow}   {self._title}")
        self._toggle.setAccessibleName(f"{self._title} section")
        self._toggle.setAccessibleDescription(
            f"{self._title} section, {'expanded' if self._expanded else 'collapsed'}"
        )

    def set_title(self, title: str) -> None:
        self._title = title
        self._update_toggle_text()

    def body_layout(self) -> QVBoxLayout:
        return self._body.layout()

    def set_expanded(self, expanded: bool) -> None:
        self._toggle.setChecked(expanded)


# ── Drop-aware input editor ────────────────────────────────────────────────────

class DropTextEdit(QTextEdit):
    """QTextEdit that accepts file drops and emits a signal to add selected text as a custom word."""

    word_selected = pyqtSignal(str)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setAcceptDrops(True)

    def contextMenuEvent(self, event) -> None:
        menu = self.createStandardContextMenu()
        selection = self.textCursor().selectedText().strip()
        if selection:
            menu.addSeparator()
            action = menu.addAction(f'Add "{selection[:40]}" to Custom Words')
            action.setStatusTip(
                "Add the selected text to the Custom Words to Redact list in Settings"
            )
            action.triggered.connect(lambda: self.word_selected.emit(selection))
        menu.exec(event.globalPos())

    def dragEnterEvent(self, event) -> None:
        if event.mimeData().hasUrls() or event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event) -> None:
        if event.mimeData().hasUrls() or event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event) -> None:
        if event.mimeData().hasUrls():
            url = event.mimeData().urls()[0]
            path = url.toLocalFile()
            if path:
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        self.setPlainText(f.read())
                    event.acceptProposedAction()
                    return
                except Exception:
                    pass
        super().dropEvent(event)


# ── Read-only output editor with whitelist context menu ───────────────────────

class OutputTextEdit(QTextEdit):
    """Read-only output pane that emits a signal to add selected text to the whitelist."""

    word_selected = pyqtSignal(str)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setReadOnly(True)

    def contextMenuEvent(self, event) -> None:
        menu = self.createStandardContextMenu()
        selection = self.textCursor().selectedText().strip()
        if selection:
            menu.addSeparator()
            action = menu.addAction(f'Add "{selection[:40]}" to Whitelist')
            action.setStatusTip(
                "Add the selected text to the Whitelist (Never Redact) in Settings"
            )
            action.triggered.connect(lambda: self.word_selected.emit(selection))
        menu.exec(event.globalPos())


# ── Main window ────────────────────────────────────────────────────────────────

class MainWindow(QMainWindow):

    def __init__(self) -> None:
        super().__init__()
        self._mapping: Optional[dict] = None
        self._settings = QSettings("Privatiser", "PrivatiserGUI")

        self.setWindowTitle("Privatiser")
        self.setMinimumSize(860, 580)
        self.resize(
            self._settings.value("window/width",  1100, int),
            self._settings.value("window/height", 760,  int),
        )

        self._system_font_size = QApplication.font().pointSize()

        self._build_menu()
        self._build_ui()
        self._build_statusbar()
        self._restore_settings()  # restores _dark_action.setChecked → triggers _apply_theme

    # ── Menu bar ───────────────────────────────────────────────────────────────

    def _build_menu(self) -> None:
        mb = self.menuBar()
        mb.setAccessibleName("Main menu bar")
        style = self.style()
        SI = QStyle.StandardPixmap

        # File
        fm = mb.addMenu("&File")
        self._add_action(fm, "&Open Input File…",    "Ctrl+O",       self._open_file,
                         "Open a text file into the input pane",
                         style.standardIcon(SI.SP_DialogOpenButton))
        self._add_action(fm, "&Save Output As…",     "Ctrl+Shift+S", self._save_output,
                         "Save the output pane to a file",
                         style.standardIcon(SI.SP_DialogSaveButton))
        fm.addSeparator()
        self._add_action(fm, "Save &Mapping As…",    "Ctrl+Shift+M", self._save_mapping,
                         "Save the anonymization mapping to JSON",
                         style.standardIcon(SI.SP_DialogSaveButton))
        self._add_action(fm, "&Load Mapping…",       "Ctrl+Shift+L", self._load_mapping,
                         "Load a previously saved mapping for deanonymization",
                         style.standardIcon(SI.SP_DialogOpenButton))
        fm.addSeparator()
        self._add_action(fm, "&Quit",                "Ctrl+Q",       self.close,
                         icon=style.standardIcon(SI.SP_TitleBarCloseButton))

        # Edit
        em = mb.addMenu("&Edit")
        self._add_action(em, "Copy &Output",         "Ctrl+Shift+C", self._copy_output,
                         "Copy the output pane to the clipboard")
        self._add_action(em, "&Paste into Input",    "Ctrl+Shift+V", self._paste_input,
                         "Paste clipboard text into the input pane")
        em.addSeparator()
        self._add_action(em, "Load &Sample Text",    "Ctrl+Shift+E", self._load_sample,
                         "Fill the input pane with sample sensitive text")
        self._add_action(em, "C&lear All",           "",             self._clear_all,
                         "Clear both panes and the mapping table",
                         style.standardIcon(SI.SP_TrashIcon))
        self._add_action(em, "Focus &Input",         "Ctrl+L",       self._focus_input,
                         "Select all text in the input pane and focus it")

        # View — use set_expanded so the header toggle button stays visible when
        # the section is collapsed; sync the action back when the user clicks the
        # header toggle directly.
        vm = mb.addMenu("&View")
        self._settings_toggle = QAction("&Settings Panel", self, checkable=True, checked=True)
        self._settings_toggle.setShortcut(QKeySequence("Ctrl+,"))
        vm.addAction(self._settings_toggle)

        self._mapping_toggle = QAction("&Mapping Table", self, checkable=True, checked=True)
        self._mapping_toggle.setShortcut(QKeySequence("Ctrl+T"))
        vm.addAction(self._mapping_toggle)

        vm.addSeparator()
        self._dark_action = QAction("&Dark Mode", self, checkable=True)
        self._dark_action.setStatusTip("Switch between dark and system-native theme")
        self._dark_action.toggled.connect(self._apply_theme)
        vm.addAction(self._dark_action)

        vm.addSeparator()
        self._add_action(vm, "Increase Font Size", "Ctrl+=", self._increase_font)
        self._add_action(vm, "Decrease Font Size", "Ctrl+-", self._decrease_font)
        self._add_action(vm, "Reset Font Size",    "Ctrl+0", self._reset_font)

        # Help
        hm = mb.addMenu("&Help")
        self._add_action(hm, "&About Privatiser", triggered=self._show_about,
                         icon=style.standardIcon(SI.SP_MessageBoxInformation))

    @staticmethod
    def _add_action(menu, label: str, shortcut: str = "", triggered=None,
                    status_tip: str = "", icon=None) -> QAction:
        action = QAction(label, menu.parent() if hasattr(menu, 'parent') else None)
        if icon is not None:
            action.setIcon(icon)
        if shortcut:
            action.setShortcut(QKeySequence(shortcut))
        if status_tip:
            action.setStatusTip(status_tip)
        if triggered:
            action.triggered.connect(triggered)
        menu.addAction(action)
        return action

    # ── Central UI ─────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # Editor panes
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(6)
        splitter.addWidget(self._build_input_pane())
        splitter.addWidget(self._build_output_pane())
        splitter.setSizes([1, 1])
        layout.addWidget(splitter, stretch=4)

        # Action row
        layout.addLayout(self._build_action_row())

        # Settings
        self._settings_sec = self._build_settings_section()
        layout.addWidget(self._settings_sec)

        # Mapping table
        self._mapping_sec = self._build_mapping_section()
        layout.addWidget(self._mapping_sec)

        # View menu ↔ collapsible sections: use set_expanded so the header
        # toggle button stays visible when the section is collapsed.
        self._settings_toggle.toggled.connect(self._settings_sec.set_expanded)
        self._mapping_toggle.toggled.connect(self._mapping_sec.set_expanded)

        def _sync_action(action: QAction, checked: bool) -> None:
            action.blockSignals(True)
            action.setChecked(checked)
            action.blockSignals(False)

        self._settings_sec.toggled.connect(
            lambda v: _sync_action(self._settings_toggle, v)
        )
        self._mapping_sec.toggled.connect(
            lambda v: _sync_action(self._mapping_toggle, v)
        )

    def _build_input_pane(self) -> QFrame:
        frame, layout = self._pane_frame()

        header, hl = self._pane_header("INPUT")
        for label, tip, slot in [
            ("Open File…", "Open a file  (Ctrl+O)",       self._open_file),
            ("Paste",      "Paste from clipboard  (Ctrl+Shift+V)", self._paste_input),
            ("Sample",     "Load sample text  (Ctrl+Shift+E)",     self._load_sample),
        ]:
            btn = self._header_btn(label, tip)
            btn.clicked.connect(slot)
            hl.addWidget(btn)
        layout.addWidget(header)
        layout.addWidget(self._hline())

        self._input_edit = DropTextEdit()
        self._input_edit.setTabChangesFocus(True)
        self._input_edit.setPlaceholderText(
            "Paste config files, .env files, logs, or any text containing sensitive data…\n"
            "You can also drag and drop a file here."
        )
        self._input_edit.setAccessibleName("Input text")
        self._input_edit.setAccessibleDescription(
            "Editable pane. Enter or paste text to anonymize. "
            "Drag and drop text files onto this area. "
            "Right-click a selection to add it to Custom Words."
        )
        self._input_edit.word_selected.connect(self._add_to_custom_words)
        layout.addWidget(self._input_edit)
        return frame

    def _build_output_pane(self) -> QFrame:
        frame, layout = self._pane_frame()

        header, hl = self._pane_header("OUTPUT")

        self._redact_sel_btn = self._header_btn(
            "Redact Selection",
            "Manually redact the selected text in the output pane"
        )
        self._redact_sel_btn.setEnabled(False)
        self._redact_sel_btn.setAccessibleName("Redact selected text in output")
        self._redact_sel_btn.clicked.connect(self._redact_selection)
        hl.addWidget(self._redact_sel_btn)

        for label, tip, slot in [
            ("Copy",     "Copy output to clipboard  (Ctrl+Shift+C)", self._copy_output),
            ("Save As…", "Save output to file  (Ctrl+Shift+S)",      self._save_output),
        ]:
            btn = self._header_btn(label, tip)
            btn.clicked.connect(slot)
            hl.addWidget(btn)

        layout.addWidget(header)
        layout.addWidget(self._hline())

        self._output_edit = OutputTextEdit()
        self._output_edit.setTabChangesFocus(True)
        self._output_edit.setPlaceholderText("Anonymized output appears here…")
        self._output_edit.setAccessibleName("Output text")
        self._output_edit.setAccessibleDescription(
            "Read-only pane showing the anonymized or deanonymized result. "
            "Right-click a selection to add it to the Whitelist."
        )
        self._output_edit.selectionChanged.connect(self._on_output_selection_changed)
        self._output_edit.word_selected.connect(self._add_to_whitelist)
        layout.addWidget(self._output_edit)
        return frame

    def _build_action_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(8)

        def _main_btn(label, shortcut, tip, slot, cls="secondary"):
            b = QPushButton(label)
            b.setProperty("class", cls)
            b.setMinimumHeight(40)
            if shortcut:
                b.setShortcut(QKeySequence(shortcut))
            b.setToolTip(f"{tip}  ({shortcut})" if shortcut else tip)
            b.clicked.connect(slot)
            return b

        def _companion_btn(label, shortcut, tip, slot):
            b = QPushButton(label)
            b.setProperty("class", "companion")
            b.setMinimumHeight(40)
            b.setShortcut(QKeySequence(shortcut))
            b.setToolTip(f"{tip}  ({shortcut})")
            b.clicked.connect(slot)
            return b

        self._anon_btn = _main_btn(
            "Anonymize", "Ctrl+Shift+A",
            "Anonymize the input text",
            self._run_anonymize, cls="primary",
        )
        self._anon_btn.setAccessibleName("Anonymize")

        anon_copy_btn = _companion_btn(
            "&& Copy", "Ctrl+Return",
            "Anonymize then copy the result to the clipboard",
            self._run_anon_and_copy,
        )
        anon_copy_btn.setAccessibleName("Anonymize and copy")
        anon_copy_btn.setAccessibleDescription(
            "Anonymize the input text and copy the result to the clipboard. "
            "Keyboard shortcut: Ctrl+Return"
        )

        paste_deanon_btn = _companion_btn(
            "Paste &&", "Ctrl+Shift+Return",
            "Paste clipboard text into the output pane then deanonymize it",
            self._paste_and_deanon,
        )
        paste_deanon_btn.setAccessibleName("Paste and deanonymize")
        paste_deanon_btn.setAccessibleDescription(
            "Paste clipboard text into the output pane and deanonymize it. "
            "Keyboard shortcut: Ctrl+Shift+Return"
        )

        self._deanon_btn = _main_btn(
            "Deanonymize", "Ctrl+Shift+D",
            "Restore anonymized output to original using the current mapping",
            self._run_deanonymize,
        )
        self._deanon_btn.setAccessibleName("Deanonymize")

        clear_btn = _main_btn("Clear All", "", "Clear input, output, and mapping", self._clear_all)
        clear_btn.setProperty("class", "danger")
        clear_btn.setAccessibleName("Clear all")

        row.addStretch()
        row.addWidget(self._anon_btn)
        row.addSpacing(2)
        row.addWidget(anon_copy_btn)
        row.addSpacing(24)
        row.addWidget(paste_deanon_btn)
        row.addSpacing(2)
        row.addWidget(self._deanon_btn)
        row.addSpacing(24)
        row.addWidget(clear_btn)
        row.addStretch()
        return row

    # ── Settings section ───────────────────────────────────────────────────────

    def _build_settings_section(self) -> CollapsibleSection:
        sec = CollapsibleSection("Settings")
        bl = sec.body_layout()
        bl.setSpacing(12)

        # Detection categories
        cat_group = QGroupBox("Detection Categories")
        cat_group.setAccessibleName("Detection categories")
        cat_layout = QVBoxLayout()
        cat_layout.setSpacing(4)
        self._cat_checks: dict[str, QCheckBox] = {}

        pairs = CATEGORY_KEYS
        for i in range(0, len(pairs), 3):
            row_layout = QHBoxLayout()
            row_layout.setSpacing(24)
            for key, display in pairs[i:i + 3]:
                cb = QCheckBox(display)
                cb.setChecked(True)
                cb.setMinimumHeight(30)
                cb.setAccessibleName(f"{display} detection")
                cb.setAccessibleDescription(
                    f"Enable or disable detection of {display} patterns"
                )
                self._cat_checks[key] = cb
                row_layout.addWidget(cb)
            row_layout.addStretch()
            cat_layout.addLayout(row_layout)

        cat_group.setLayout(cat_layout)
        bl.addWidget(cat_group)

        # Custom words
        bl.addWidget(self._field_label("Custom Words to Redact"))
        self._custom_words_edit = self._settings_lineedit(
            placeholder="mycompany, john.smith, prod-server-1",
            accessible_name="Custom words to redact",
            accessible_desc="Comma-separated words that are always redacted regardless of pattern",
        )
        bl.addWidget(self._custom_words_edit)
        bl.addWidget(self._hint("Comma-separated. Always redacted, regardless of pattern."))

        # Whitelist
        bl.addWidget(self._field_label("Whitelist (Never Redact)"))
        self._allowlist_edit = self._settings_lineedit(
            placeholder="localhost, example.com",
            accessible_name="Whitelist — never redact",
            accessible_desc="Comma-separated values that will never be redacted",
        )
        bl.addWidget(self._allowlist_edit)
        bl.addWidget(self._hint("Comma-separated. These values will never be redacted."))

        return sec

    # ── Mapping table section ──────────────────────────────────────────────────

    def _build_mapping_section(self) -> CollapsibleSection:
        sec = CollapsibleSection("Mapping Table  (0 items)")
        bl = sec.body_layout()

        self._mapping_empty = QLabel(
            "No replacements yet — run Anonymize to populate this table."
        )
        self._mapping_empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._mapping_empty.setObjectName("emptyState")
        self._mapping_empty.setAccessibleName("Empty mapping table notice")
        bl.addWidget(self._mapping_empty)

        self._mapping_table = QTableWidget(0, 2)
        self._mapping_table.setHorizontalHeaderLabels(["Original", "Replacement"])
        self._mapping_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._mapping_table.setAlternatingRowColors(True)
        self._mapping_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._mapping_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._mapping_table.setMinimumHeight(160)
        self._mapping_table.setTabKeyNavigation(True)
        self._mapping_table.setAccessibleName("Mapping table")
        self._mapping_table.setAccessibleDescription(
            "Two-column table listing every original value and its anonymized replacement."
        )
        self._mapping_table.setVisible(False)
        bl.addWidget(self._mapping_table)

        return sec

    # ── Status bar ─────────────────────────────────────────────────────────────

    def _build_statusbar(self) -> None:
        sb = QStatusBar()
        self.setStatusBar(sb)
        self._status_msg = QLabel("Ready")
        self._status_msg.setAccessibleName("Status message")
        sb.addWidget(self._status_msg, 1)
        self._status_count = QLabel("")
        self._status_count.setAccessibleName("Replacement count")
        sb.addPermanentWidget(self._status_count)

    # ── Core operations ────────────────────────────────────────────────────────

    def _make_privatiser(self) -> Privatiser:
        enabled = {k: cb.isChecked() for k, cb in self._cat_checks.items()}
        allowlist = self._parse_csv(self._allowlist_edit.text())
        custom_words = self._parse_csv(self._custom_words_edit.text())

        extra: list[PatternHandler] = []
        for i, word in enumerate(custom_words, start=1):
            tag = f"REDACTED_CUSTOM_{i}"
            extra.append(PatternHandler(
                name=f"custom_word_{i}",
                category="custom",
                regex=re.compile(re.escape(word), re.IGNORECASE),
                pseudonym_fn=lambda n, t=tag: t,
                priority=90,
            ))

        return Privatiser(
            enabled_categories=enabled,
            allowlist=allowlist,
            extra_patterns=extra or None,
        )

    def _run_anonymize(self) -> None:
        text = self._input_edit.toPlainText()
        if not text.strip():
            self._status("No input text to anonymize.", error=True)
            return
        try:
            result, mapping = self._make_privatiser().anonymize(text)
        except Exception as exc:
            self._status(f"Anonymization failed: {exc}", error=True)
            return

        self._mapping = mapping
        self._output_edit.setPlainText(result)
        self._populate_mapping(mapping)
        n = len(mapping)
        self._status(f"Anonymized — {n} replacement{'s' if n != 1 else ''}.")

    def _run_deanonymize(self) -> None:
        text = self._output_edit.toPlainText()
        if not text.strip():
            self._status("Output pane is empty — nothing to deanonymize.", error=True)
            return
        if not self._mapping:
            self._status(
                "No mapping available. Run Anonymize first, or load a mapping via "
                "File → Load Mapping…",
                error=True,
            )
            return
        try:
            result = self._make_privatiser().deanonymize(text, self._mapping)
        except Exception as exc:
            self._status(f"Deanonymization failed: {exc}", error=True)
            return

        self._input_edit.setPlainText(result)
        self._status("Deanonymized — original text restored to input pane.")

    def _run_anon_and_copy(self) -> None:
        text = self._input_edit.toPlainText()
        if not text.strip():
            self._status("No input text to anonymize.", error=True)
            return
        try:
            result, mapping = self._make_privatiser().anonymize(text)
        except Exception as exc:
            self._status(f"Anonymization failed: {exc}", error=True)
            return
        self._mapping = mapping
        self._output_edit.setPlainText(result)
        self._populate_mapping(mapping)
        QApplication.clipboard().setText(result)
        n = len(mapping)
        self._status(f"Anonymized and copied to clipboard — {n} replacement{'s' if n != 1 else ''}.")

    def _paste_and_deanon(self) -> None:
        text = QApplication.clipboard().text()
        if not text:
            self._status("Clipboard is empty.", error=True)
            return
        if not self._mapping:
            self._status(
                "No mapping available. Run Anonymize first, or load a mapping via "
                "File → Load Mapping…",
                error=True,
            )
            return
        self._output_edit.setPlainText(text)
        try:
            result = self._make_privatiser().deanonymize(text, self._mapping)
        except Exception as exc:
            self._status(f"Deanonymization failed: {exc}", error=True)
            return
        self._input_edit.setPlainText(result)
        self._status("Pasted and deanonymized — original text restored to input pane.")

    def _redact_selection(self) -> None:
        cursor = self._output_edit.textCursor()
        if not cursor.hasSelection():
            return
        selected = cursor.selectedText()
        tag = f"[REDACTED]"
        self._output_edit.setReadOnly(False)
        cursor.insertText(tag)
        self._output_edit.setReadOnly(True)
        if self._mapping is None:
            self._mapping = {}
        self._mapping[tag] = selected
        self._populate_mapping(self._mapping)
        preview = selected[:40] + ("…" if len(selected) > 40 else "")
        self._status(f'Manually redacted: “{preview}”')

    def _clear_all(self) -> None:
        if self._input_edit.toPlainText() or self._output_edit.toPlainText():
            reply = QMessageBox.question(
                self, "Clear All",
                "Clear input, output, and mapping table?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        self._input_edit.clear()
        self._output_edit.clear()
        self._mapping = None
        self._mapping_table.setRowCount(0)
        self._mapping_table.setVisible(False)
        self._mapping_empty.setVisible(True)
        self._mapping_sec.set_title("Mapping Table  (0 items)")
        self._status_count.setText("")
        self._status("Cleared.")

    # ── File I/O ───────────────────────────────────────────────────────────────

    def _open_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Input File", "",
            "Text files (*.txt *.log *.conf *.env *.tf *.json *.yaml *.yml *.ini *.toml);;"
            "All files (*)"
        )
        if not path:
            return
        try:
            with open(path, encoding="utf-8") as f:
                self._input_edit.setPlainText(f.read())
        except Exception as exc:
            self._status(f"Could not open file: {exc}", error=True)
            return
        self.setWindowTitle(f"Privatiser — {path.split('/')[-1]}")
        self._status(f"Opened: {path}")

    def _save_output(self) -> None:
        text = self._output_edit.toPlainText()
        if not text:
            self._status("Output pane is empty — nothing to save.", error=True)
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Output As", "", "Text files (*.txt);;All files (*)"
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
        except Exception as exc:
            self._status(f"Could not save: {exc}", error=True)
            return
        self._status(f"Output saved to: {path}")

    def _save_mapping(self) -> None:
        if not self._mapping:
            self._status("No mapping to save — run Anonymize first.", error=True)
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Mapping As", "mapping.json", "JSON files (*.json);;All files (*)"
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self._mapping, f, indent=2, ensure_ascii=False)
        except Exception as exc:
            self._status(f"Could not save mapping: {exc}", error=True)
            return
        self._status(f"Mapping saved to: {path}")

    def _load_mapping(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Load Mapping", "", "JSON files (*.json);;All files (*)"
        )
        if not path:
            return
        try:
            with open(path, encoding="utf-8") as f:
                mapping = json.load(f)
        except Exception as exc:
            self._status(f"Could not load mapping: {exc}", error=True)
            return
        if not isinstance(mapping, dict):
            self._status("Invalid mapping file — expected a JSON object.", error=True)
            return
        self._mapping = mapping
        self._populate_mapping(mapping)
        self._status(f"Loaded {len(mapping)} mapping entries from {path.split('/')[-1]}")

    # ── Clipboard ──────────────────────────────────────────────────────────────

    def _copy_output(self) -> None:
        text = self._output_edit.toPlainText()
        if not text:
            self._status("Output pane is empty — nothing to copy.", error=True)
            return
        QApplication.clipboard().setText(text)
        self._status("Output copied to clipboard.")

    def _paste_input(self) -> None:
        text = QApplication.clipboard().text()
        if not text:
            self._status("Clipboard is empty.", error=True)
            return
        self._input_edit.setPlainText(text)
        self._status("Pasted from clipboard.")

    def _load_sample(self) -> None:
        self._input_edit.setPlainText(SAMPLE_TEXT)
        self._status("Sample text loaded.")

    def _focus_input(self) -> None:
        self._input_edit.setFocus()
        self._input_edit.selectAll()

    def _add_to_custom_words(self, word: str) -> None:
        word = word.strip()
        if not word:
            return
        existing = self._parse_csv(self._custom_words_edit.text())
        if word in existing:
            self._status(f'"{word}" is already in Custom Words.')
            return
        existing.append(word)
        self._custom_words_edit.setText(", ".join(existing))
        # Make sure the settings panel is visible and expanded so the user sees the change
        self._settings_sec.setVisible(True)
        self._settings_toggle.setChecked(True)
        self._settings_sec.set_expanded(True)
        preview = word[:40] + ("…" if len(word) > 40 else "")
        self._status(f'Added "{preview}" to Custom Words.')

    def _add_to_whitelist(self, word: str) -> None:
        word = word.strip()
        if not word:
            return
        existing = self._parse_csv(self._allowlist_edit.text())
        if word in existing:
            self._status(f'"{word}" is already in the Whitelist.')
            return
        existing.append(word)
        self._allowlist_edit.setText(", ".join(existing))
        self._settings_sec.setVisible(True)
        self._settings_toggle.setChecked(True)
        self._settings_sec.set_expanded(True)
        preview = word[:40] + ("…" if len(word) > 40 else "")
        self._status(f'Added "{preview}" to Whitelist.')

    # ── Mapping table ──────────────────────────────────────────────────────────

    def _populate_mapping(self, mapping: dict) -> None:
        self._mapping_table.setRowCount(0)
        if not mapping:
            self._mapping_table.setVisible(False)
            self._mapping_empty.setVisible(True)
            self._mapping_sec.set_title("Mapping Table  (0 items)")
            self._status_count.setText("")
            return

        self._mapping_empty.setVisible(False)
        self._mapping_table.setVisible(True)

        for replacement, original in mapping.items():
            row = self._mapping_table.rowCount()
            self._mapping_table.insertRow(row)
            self._mapping_table.setItem(row, 0, QTableWidgetItem(str(original)))
            self._mapping_table.setItem(row, 1, QTableWidgetItem(str(replacement)))

        n = len(mapping)
        label = f"Mapping Table  ({n} item{'s' if n != 1 else ''})"
        self._mapping_sec.set_title(label)
        self._status_count.setText(f"{n} replacement{'s' if n != 1 else ''}")

    # ── Font scaling ───────────────────────────────────────────────────────────

    def _increase_font(self) -> None:
        self._set_font_size(min(QApplication.font().pointSize() + 1, 24))

    def _decrease_font(self) -> None:
        self._set_font_size(max(QApplication.font().pointSize() - 1, 8))

    def _reset_font(self) -> None:
        self._settings.remove("font_size")
        font = QApplication.font()
        font.setPointSize(self._system_font_size)
        QApplication.setFont(font)

    def _set_font_size(self, size: int) -> None:
        font = QApplication.font()
        font.setPointSize(size)
        QApplication.setFont(font)
        self._settings.setValue("font_size", size)

    # ── Settings persistence ───────────────────────────────────────────────────

    def _restore_settings(self) -> None:
        if self._settings.contains("font_size"):
            font = QApplication.font()
            font.setPointSize(self._settings.value("font_size", type=int))
            QApplication.setFont(font)

        for key, cb in self._cat_checks.items():
            cb.setChecked(self._settings.value(f"cat/{key}", True, bool))

        self._custom_words_edit.setText(self._settings.value("custom_words", "", str))
        self._allowlist_edit.setText(self._settings.value("allowlist", "", str))

        # Restore theme — blockSignals so we only call _apply_theme once at the end
        self._dark_action.blockSignals(True)
        self._dark_action.setChecked(self._settings.value("theme/dark", False, bool))
        self._dark_action.blockSignals(False)
        self._apply_theme()

    def _save_settings(self) -> None:
        self._settings.setValue("window/width",  self.width())
        self._settings.setValue("window/height", self.height())
        for key, cb in self._cat_checks.items():
            self._settings.setValue(f"cat/{key}", cb.isChecked())
        self._settings.setValue("theme/dark",    self._dark_action.isChecked())
        self._settings.setValue("custom_words",  self._custom_words_edit.text())
        self._settings.setValue("allowlist",    self._allowlist_edit.text())

    def closeEvent(self, event) -> None:
        self._save_settings()
        event.accept()

    # ── Misc ───────────────────────────────────────────────────────────────────

    def _apply_theme(self) -> None:
        self.setStyleSheet(DARK_STYLESHEET if self._dark_action.isChecked() else "")

    def _on_output_selection_changed(self) -> None:
        self._redact_sel_btn.setEnabled(
            self._output_edit.textCursor().hasSelection()
        )

    def _status(self, message: str, *, error: bool = False) -> None:
        self._status_msg.setText(message)
        # Red for errors is universal; clear to native for normal messages
        self._status_msg.setStyleSheet("color: red;" if error else "")

    def _show_about(self) -> None:
        QMessageBox.about(
            self, "About Privatiser",
            "<b>Privatiser</b> — desktop GUI<br><br>"
            "Anonymizes IPs, API keys, secrets, PII, and cloud identifiers from any text. "
            "Fully reversible. Everything runs locally — nothing leaves this machine.<br><br>"
            "Built on the freemium "
            "<a href='https://privatiser.net/'>Privatiser</a> library. "
            "If you find it useful, consider purchasing a licence to support its development.<br><br>"
            "<i>This application is not affiliated with or endorsed by Privatiser.</i>",
        )

    # ── Widget helpers ─────────────────────────────────────────────────────────

    @staticmethod
    def _pane_frame() -> tuple[QFrame, QVBoxLayout]:
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        return frame, layout

    @staticmethod
    def _pane_header(label_text: str) -> tuple[QWidget, QHBoxLayout]:
        header = QWidget()
        header.setObjectName("paneHeader")
        hl = QHBoxLayout(header)
        hl.setContentsMargins(10, 4, 8, 4)
        lbl = QLabel(label_text)
        lbl.setObjectName("paneLabel")
        font = QFont()
        font.setPointSize(9)
        font.setBold(True)
        lbl.setFont(font)
        lbl.setAccessibleName(f"{label_text} pane label")
        hl.addWidget(lbl)
        hl.addStretch()
        return header, hl

    @staticmethod
    def _header_btn(label: str, tip: str = "") -> QPushButton:
        btn = QPushButton(label)
        btn.setObjectName("headerBtn")
        btn.setFlat(True)
        font = QFont()
        font.setPointSize(9)
        btn.setFont(font)
        if tip:
            btn.setToolTip(tip)
        return btn

    @staticmethod
    def _hline() -> QFrame:
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        return line

    @staticmethod
    def _field_label(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setObjectName("fieldLabel")
        font = QFont()
        font.setPointSize(9)
        font.setBold(True)
        lbl.setFont(font)
        return lbl

    @staticmethod
    def _hint(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setObjectName("hintLabel")
        font = QFont()
        font.setPointSize(9)
        lbl.setFont(font)
        return lbl

    @staticmethod
    def _settings_lineedit(placeholder: str = "", accessible_name: str = "",
                            accessible_desc: str = "") -> QLineEdit:
        edit = QLineEdit()
        edit.setMinimumHeight(34)
        if placeholder:
            edit.setPlaceholderText(placeholder)
        if accessible_name:
            edit.setAccessibleName(accessible_name)
        if accessible_desc:
            edit.setAccessibleDescription(accessible_desc)
        return edit

    @staticmethod
    def _parse_csv(text: str) -> list[str]:
        return [w.strip() for w in text.split(",") if w.strip()]


# ── Entry point ────────────────────────────────────────────────────────────────

def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("Privatiser")
    app.setOrganizationName("Privatiser")

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
