"""
Calendário da Copa 2026 - versão melhorada
------------------------------------------
App desktop em PySide6 com visual 9:16/mobile e desktop responsivo.

Como rodar:
    pip install PySide6
    python main.py

O app cria estes arquivos ao lado do main.py:
    dados_copa.json      -> partidas editáveis
    favoritos.json       -> favoritos e alertas
    preferencias.json    -> fonte, janela e filtros
    calendario_copa_2026.ics -> exportação para calendário

Observação:
    Os dados iniciais são uma base demonstrativa atualizada para a Copa 2026.
    Para usar a tabela completa, edite/substitua dados_copa.json.
"""

from __future__ import annotations

import calendar
import csv
import json
import os
import platform
import subprocess
import sys
import webbrowser
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Optional

from PySide6.QtCore import QPointF, QRectF, QSize, Qt, QTimer
from PySide6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPainterPath, QPen, QPixmap, QPolygonF, QRadialGradient
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QSpinBox,
    QStyle,
    QSystemTrayIcon,
    QVBoxLayout,
    QWidget,
)

APP_DIR = Path(__file__).resolve().parent
DATA_FILE = APP_DIR / "dados_copa.json"
STATE_FILE = APP_DIR / "favoritos.json"
PREF_FILE = APP_DIR / "preferencias.json"
ICS_FILE = APP_DIR / "calendario_copa_2026.ics"
CSV_FILE = APP_DIR / "calendario_copa_2026.csv"


# ============================================================
# Dados
# ============================================================

# Lista de partidas demonstrativas. Nesta versão atualizada usamos nomes de estádios
# oficiais da Copa do Mundo 2026, conforme a lista de sedes divulgada pela FIFA e
# detalhada por fontes como o guia de sedes da Roadtrips【221844163382200†L116-L136】. Para personalizar
# sua base de dados basta editar o arquivo dados_copa.json após o primeiro
# lançamento do aplicativo.
DEFAULT_MATCHES: list[dict[str, Any]] = [
    {
        "id": "m001",
        "data": "2026-06-11",
        "hora": "19:00",
        "time_a": "México",
        "time_b": "África do Sul",
        "grupo": "Grupo A",
        "fase": "Grupos",
        "estadio": "Estadio Azteca",
        "cidade": "Cidade do México, México",
        "status": "encerrado",
        "placar": "2-0",
        "alerta": False,
        "destaque": "Jogo de abertura da Copa 2026.",
    },
    {
        "id": "m002",
        "data": "2026-06-11",
        "hora": "22:00",
        "time_a": "Coreia do Sul",
        "time_b": "Tchéquia",
        "grupo": "Grupo A",
        "fase": "Grupos",
        "estadio": "Estadio Akron",
        "cidade": "Guadalajara, México",
        "status": "encerrado",
        "placar": "2-1",
        "alerta": False,
        "destaque": "Segunda partida do Grupo A.",
    },
    {
        "id": "m003",
        "data": "2026-06-12",
        "hora": "16:00",
        "time_a": "Canadá",
        "time_b": "Bósnia e Herzegovina",
        "grupo": "Grupo B",
        "fase": "Grupos",
        "estadio": "BMO Field",
        "cidade": "Toronto, Canadá",
        "status": "encerrado",
        "placar": "1-1",
        "alerta": False,
        "destaque": "Estreia canadense como país-sede.",
    },
    {
        "id": "m004",
        "data": "2026-06-12",
        "hora": "22:00",
        "time_a": "Estados Unidos",
        "time_b": "Paraguai",
        "grupo": "Grupo D",
        "fase": "Grupos",
        "estadio": "SoFi Stadium",
        "cidade": "Los Angeles, EUA",
        "status": "encerrado",
        "placar": "4-1",
        "alerta": False,
        "destaque": "Estreia dos EUA como país-sede.",
    },
    {
        "id": "m005",
        "data": "2026-06-13",
        "hora": "13:00",
        "time_a": "Haiti",
        "time_b": "Escócia",
        "grupo": "Grupo C",
        "fase": "Grupos",
        "estadio": "Gillette Stadium",
        "cidade": "Boston, EUA",
        "status": "agendado",
        "placar": "",
        "alerta": False,
        "destaque": "Partida de abertura do Grupo C.",
    },
    {
        "id": "m006",
        "data": "2026-06-13",
        "hora": "16:00",
        "time_a": "Austrália",
        "time_b": "Turquia",
        "grupo": "Grupo D",
        "fase": "Grupos",
        "estadio": "BC Place",
        "cidade": "Vancouver, Canadá",
        "status": "agendado",
        "placar": "",
        "alerta": False,
        "destaque": "Duelo de estilos físicos e transição rápida.",
    },
    {
        "id": "m007",
        "data": "2026-06-13",
        "hora": "18:00",
        "time_a": "Brasil",
        "time_b": "Marrocos",
        "grupo": "Grupo C",
        "fase": "Grupos",
        "estadio": "MetLife Stadium",
        "cidade": "East Rutherford, EUA",
        "status": "agendado",
        "placar": "",
        "alerta": True,
        "destaque": "Jogo forte para acompanhar no app.",
    },
    {
        "id": "m008",
        "data": "2026-06-13",
        "hora": "21:00",
        "time_a": "Catar",
        "time_b": "Suíça",
        "grupo": "Grupo B",
        "fase": "Grupos",
        "estadio": "Levi's Stadium",
        "cidade": "Santa Clara, EUA",
        "status": "agendado",
        "placar": "",
        "alerta": False,
        "destaque": "Jogo noturno do Grupo B.",
    },
    {
        "id": "m009",
        "data": "2026-06-16",
        "hora": "16:00",
        "time_a": "França",
        "time_b": "Senegal",
        "grupo": "Grupo I",
        "fase": "Grupos",
        "estadio": "MetLife Stadium",
        "cidade": "East Rutherford, EUA",
        "status": "agendado",
        "placar": "",
        "alerta": True,
        "destaque": "Partida adicionada para testar alertas no dia atual.",
    },
    {
        "id": "m010",
        "data": "2026-06-22",
        "hora": "21:00",
        "time_a": "Noruega",
        "time_b": "Senegal",
        "grupo": "Grupo I",
        "fase": "Grupos",
        "estadio": "MetLife Stadium",
        "cidade": "East Rutherford, EUA",
        "status": "agendado",
        "placar": "",
        "alerta": False,
        "destaque": "Rodada decisiva para o grupo.",
    },
    {
        "id": "r32_01",
        "data": "2026-06-28",
        "hora": "18:00",
        "time_a": "1º Grupo A",
        "time_b": "3º melhor colocado",
        "grupo": "Mata-mata",
        "fase": "16 avos",
        "estadio": "A definir",
        "cidade": "A definir",
        "status": "agendado",
        "placar": "",
        "alerta": False,
        "destaque": "Nova fase com 32 seleções no mata-mata.",
    },
    {
        "id": "qf_01",
        "data": "2026-07-10",
        "hora": "21:00",
        "time_a": "Quartas 1",
        "time_b": "Quartas 2",
        "grupo": "Mata-mata",
        "fase": "Quartas",
        "estadio": "SoFi Stadium",
        "cidade": "Los Angeles, EUA",
        "status": "agendado",
        "placar": "",
        "alerta": False,
        "destaque": "Quartas de final.",
    },
    {
        "id": "sf_01",
        "data": "2026-07-14",
        "hora": "21:00",
        "time_a": "Semifinalista 1",
        "time_b": "Semifinalista 2",
        "grupo": "Mata-mata",
        "fase": "Semifinal",
        "estadio": "A definir",
        "cidade": "A definir",
        "status": "agendado",
        "placar": "",
        "alerta": True,
        "destaque": "Semifinal da Copa 2026.",
    },
    {
        "id": "final_2026",
        "data": "2026-07-19",
        "hora": "18:00",
        "time_a": "Finalista 1",
        "time_b": "Finalista 2",
        "grupo": "Mata-mata",
        "fase": "Final",
        "estadio": "MetLife Stadium",
        "cidade": "East Rutherford, EUA",
        "status": "agendado",
        "placar": "",
        "alerta": True,
        "destaque": "Final da Copa do Mundo 2026.",
    },
]

DEFAULT_PLAYERS: list[dict[str, Any]] = [
    {"pais": "Brasil", "nome": "Alisson", "posicao": "GOL", "camisa": 1},
    {"pais": "Brasil", "nome": "Marquinhos", "posicao": "ZAG", "camisa": 4},
    {"pais": "Brasil", "nome": "Bruno Guimarães", "posicao": "MEI", "camisa": 8},
    {"pais": "Brasil", "nome": "Vinícius Jr.", "posicao": "ATA", "camisa": 7},
    {"pais": "Marrocos", "nome": "Bono", "posicao": "GOL", "camisa": 1},
    {"pais": "Marrocos", "nome": "Hakimi", "posicao": "LAT", "camisa": 2},
    {"pais": "Marrocos", "nome": "Amrabat", "posicao": "MEI", "camisa": 4},
    {"pais": "Marrocos", "nome": "Ziyech", "posicao": "ATA", "camisa": 7},
    {"pais": "França", "nome": "Maignan", "posicao": "GOL", "camisa": 16},
    {"pais": "França", "nome": "Griezmann", "posicao": "MEI", "camisa": 7},
    {"pais": "Senegal", "nome": "Mané", "posicao": "ATA", "camisa": 10},
    {"pais": "México", "nome": "Ochoa", "posicao": "GOL", "camisa": 13},
]

DEFAULT_STATE = {"favoritos": ["m007", "m009", "final_2026"], "alertados": []}
DEFAULT_PREFS = {"font_scale": 100, "open_mode": "phone", "alert_minutes": 30, "favorite_team": ""}


@dataclass
class Match:
    id: str
    data: str
    hora: str
    time_a: str
    time_b: str
    grupo: str
    fase: str
    estadio: str
    cidade: str
    status: str = "agendado"
    placar: str = ""
    alerta: bool = False
    destaque: str = ""

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "Match":
        data = {**{f.name: getattr(cls, f.name, "") for f in []}, **value}
        return cls(
            id=str(data.get("id", "")),
            data=str(data.get("data", "")),
            hora=str(data.get("hora", "00:00")),
            time_a=str(data.get("time_a", "Time A")),
            time_b=str(data.get("time_b", "Time B")),
            grupo=str(data.get("grupo", "")),
            fase=str(data.get("fase", "Grupos")),
            estadio=str(data.get("estadio", "A definir")),
            cidade=str(data.get("cidade", "A definir")),
            status=str(data.get("status", "agendado")),
            placar=str(data.get("placar", "")),
            alerta=bool(data.get("alerta", False)),
            destaque=str(data.get("destaque", "")),
        )

    @property
    def title(self) -> str:
        score = f"  {self.placar}" if self.placar else ""
        return f"{self.time_a} x {self.time_b}{score}"

    @property
    def datetime_obj(self) -> datetime:
        try:
            return datetime.strptime(f"{self.data} {self.hora}", "%Y-%m-%d %H:%M")
        except ValueError:
            return datetime(2026, 6, 11, 0, 0)

    @property
    def is_past(self) -> bool:
        return self.datetime_obj < datetime.now() - timedelta(hours=3)

    @property
    def day_label(self) -> str:
        nomes = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
        d = self.datetime_obj
        return f"{nomes[d.weekday()]}, {d.day:02d}/{d.month:02d}"


class Store:
    def __init__(self) -> None:
        self.matches: list[Match] = []
        self.players: list[dict[str, Any]] = []
        self.favorites: set[str] = set()
        self.alerted: set[str] = set()
        self.prefs: dict[str, Any] = DEFAULT_PREFS.copy()
        self.load()

    def ensure_files(self) -> None:
        if not DATA_FILE.exists():
            DATA_FILE.write_text(json.dumps({"partidas": DEFAULT_MATCHES, "jogadores": DEFAULT_PLAYERS}, indent=2, ensure_ascii=False), encoding="utf-8")
        if not STATE_FILE.exists():
            STATE_FILE.write_text(json.dumps(DEFAULT_STATE, indent=2, ensure_ascii=False), encoding="utf-8")
        if not PREF_FILE.exists():
            PREF_FILE.write_text(json.dumps(DEFAULT_PREFS, indent=2, ensure_ascii=False), encoding="utf-8")

    def load(self) -> None:
        self.ensure_files()
        try:
            raw = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except Exception:
            raw = {"partidas": DEFAULT_MATCHES, "jogadores": DEFAULT_PLAYERS}
        self.matches = [Match.from_dict(x) for x in raw.get("partidas", [])]
        self.matches.sort(key=lambda m: (m.data, m.hora, m.id))
        self.players = list(raw.get("jogadores", DEFAULT_PLAYERS))
        try:
            state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            state = DEFAULT_STATE.copy()
        self.favorites = set(state.get("favoritos", []))
        self.alerted = set(state.get("alertados", []))
        try:
            self.prefs.update(json.loads(PREF_FILE.read_text(encoding="utf-8")))
        except Exception:
            pass

    def save_data(self) -> None:
        DATA_FILE.write_text(
            json.dumps({"partidas": [asdict(m) for m in self.matches], "jogadores": self.players}, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def save_state(self) -> None:
        STATE_FILE.write_text(json.dumps({"favoritos": sorted(self.favorites), "alertados": sorted(self.alerted)}, indent=2, ensure_ascii=False), encoding="utf-8")

    def save_prefs(self) -> None:
        PREF_FILE.write_text(json.dumps(self.prefs, indent=2, ensure_ascii=False), encoding="utf-8")

    def toggle_favorite(self, match_id: str) -> bool:
        if match_id in self.favorites:
            self.favorites.remove(match_id)
            result = False
        else:
            self.favorites.add(match_id)
            result = True
        self.save_state()
        return result

    def toggle_alert(self, match_id: str) -> bool:
        for match in self.matches:
            if match.id == match_id:
                match.alerta = not match.alerta
                self.save_data()
                return match.alerta
        return False

    def set_favorite_team(self, team: str) -> None:
        """Define o time favorito e ajusta alertas para partidas desse time."""
        # armazena a preferência
        self.prefs["favorite_team"] = team
        self.save_prefs()
        # ativa o alerta em todas as partidas envolvendo o time favorito
        for m in self.matches:
            if team and (m.time_a == team or m.time_b == team):
                m.alerta = True
            # não desativa alertas existentes para outras partidas
        self.save_data()

    def reset_demo(self) -> None:
        DATA_FILE.write_text(json.dumps({"partidas": DEFAULT_MATCHES, "jogadores": DEFAULT_PLAYERS}, indent=2, ensure_ascii=False), encoding="utf-8")
        STATE_FILE.write_text(json.dumps(DEFAULT_STATE, indent=2, ensure_ascii=False), encoding="utf-8")
        self.load()

    def next_match(self) -> Optional[Match]:
        now = datetime.now()
        upcoming = [m for m in self.matches if m.datetime_obj >= now - timedelta(hours=2)]
        return upcoming[0] if upcoming else (self.matches[-1] if self.matches else None)

    def favorite_matches(self) -> list[Match]:
        return [m for m in self.matches if m.id in self.favorites]

    def players_by_country(self, country: str) -> list[dict[str, Any]]:
        return [p for p in self.players if str(p.get("pais", "")).lower() == country.lower()]

    def matches_on(self, iso: str) -> list[Match]:
        return [m for m in self.matches if m.data == iso]


# ============================================================
# Visual
# ============================================================

class Theme:
    BG = "#020b16"
    PANEL = "rgba(8, 28, 48, 0.86)"
    PANEL_2 = "rgba(11, 39, 66, 0.76)"
    BORDER = "rgba(82, 130, 173, 0.52)"
    BORDER_SOFT = "rgba(74, 101, 133, 0.36)"
    TEXT = "#f4f8ff"
    MUTED = "#b8c7dc"
    DIM = "#8092aa"
    GREEN = "#20df5a"
    BLUE = "#188cff"
    CYAN = "#2bd3ff"
    YELLOW = "#ffd044"
    RED = "#ff4f5d"
    PURPLE = "#b978ff"
    FONT = "Segoe UI"

    @staticmethod
    def css(font_scale: int = 100) -> str:
        base = max(11, int(13 * font_scale / 100))
        return f"""
        QWidget {{ font-family: '{Theme.FONT}'; font-size: {base}px; color: {Theme.TEXT}; }}
        QToolTip {{ background: #07182b; color: white; border: 1px solid {Theme.BLUE}; padding: 8px; border-radius: 8px; }}
        QLineEdit, QComboBox, QSpinBox {{
            background: rgba(4, 19, 35, 0.86); border: 1px solid rgba(72, 108, 143, 0.66);
            border-radius: 12px; padding: 9px 12px; color: {Theme.TEXT}; min-height: 28px;
        }}
        QLineEdit:focus, QComboBox:focus, QSpinBox:focus {{ border-color: {Theme.GREEN}; }}
        QCheckBox {{ color: {Theme.TEXT}; spacing: 8px; }}
        QCheckBox::indicator {{ width: 18px; height: 18px; border-radius: 5px; border: 1px solid {Theme.BLUE}; background: #06182b; }}
        QCheckBox::indicator:checked {{ background: {Theme.GREEN}; border-color: {Theme.GREEN}; }}
        QScrollArea {{ background: transparent; border: none; }}
        QScrollBar:vertical {{ background: rgba(4, 15, 28, 0.70); width: 10px; border-radius: 5px; margin: 2px; }}
        QScrollBar::handle:vertical {{ background: rgba(43, 211, 255, 0.55); border-radius: 5px; min-height: 40px; }}
        QScrollBar::handle:vertical:hover {{ background: rgba(32, 223, 90, 0.72); }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
        """

    @staticmethod
    def card(border: str | None = None, bg: str | None = None, radius: int = 20) -> str:
        return f"""
        QFrame {{
            background: {bg or Theme.PANEL}; border: 1px solid {border or Theme.BORDER_SOFT};
            border-radius: {radius}px;
        }}
        """

    @staticmethod
    def button(active: bool = False, color: str | None = None) -> str:
        if active:
            return f"""
            QPushButton {{ background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #0a7a36, stop:1 #17b84f);
                border: 1px solid #42f27b; border-radius: 14px; padding: 10px 14px; color: white; font-weight: 800; }}
            QPushButton:hover {{ background: #16c754; }}
            """
        return f"""
        QPushButton {{ background: rgba(8, 27, 46, 0.86); border: 1px solid rgba(75, 108, 142, 0.58);
            border-radius: 14px; padding: 10px 14px; color: {Theme.TEXT}; font-weight: 650; }}
        QPushButton:hover {{ border-color: {color or Theme.GREEN}; background: rgba(12, 46, 72, 0.98); color: white; }}
        """

    @staticmethod
    def ghost(color: str | None = None) -> str:
        return f"""
        QPushButton {{ background: rgba(5, 21, 38, 0.62); border: 1px solid rgba(72, 116, 156, 0.48);
            border-radius: 11px; padding: 7px 10px; color: {Theme.TEXT}; font-weight: 650; }}
        QPushButton:hover {{ border-color: {color or Theme.GREEN}; color: {color or Theme.GREEN}; }}
        """

COUNTRY_COLORS = {
    "Brasil": Theme.GREEN, "Marrocos": Theme.RED, "México": "#0aa858", "África do Sul": "#f0c52c", "Canadá": "#ff3434",
    "Estados Unidos": "#2d72ff", "França": "#4b7dff", "Senegal": "#1fc466", "Noruega": "#e44960", "Coreia do Sul": "#f4f4f4",
    "Tchéquia": "#e34c4c", "Haiti": "#3859ff", "Escócia": "#2b65d9", "Austrália": "#244b9e", "Turquia": "#df2432",
    "Catar": "#8f1336", "Suíça": "#d8212e",
}
PHASE_COLORS = {"Grupos": Theme.GREEN, "16 avos": Theme.CYAN, "Oitavas": Theme.BLUE, "Quartas": Theme.YELLOW, "Semifinal": Theme.RED, "Final": Theme.YELLOW}




def month_name_pt(month: int) -> str:
    nomes = ["", "janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
    return nomes[month] if 1 <= month <= 12 else str(month)

def fmt_date(iso: str) -> str:
    try:
        d = datetime.strptime(iso, "%Y-%m-%d")
    except ValueError:
        return iso
    meses = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
    dias = ["segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo"]
    return f"{dias[d.weekday()]}, {d.day:02d} de {meses[d.month-1]}"


def label(text: str, size: int = 13, color: str = Theme.TEXT, weight: int = QFont.Normal, align: Qt.AlignmentFlag = Qt.AlignLeft) -> QLabel:
    lb = QLabel(text)
    lb.setWordWrap(True)
    lb.setMinimumWidth(0)
    lb.setAlignment(align)
    lb.setFont(QFont(Theme.FONT, size, weight))
    lb.setStyleSheet(f"color: {color}; background: transparent; border: none;")
    lb.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
    return lb


def clear_layout(layout) -> None:
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        child = item.layout()
        if widget is not None:
            widget.deleteLater()
        elif child is not None:
            clear_layout(child)


def safe_open(path: Path) -> None:
    try:
        if platform.system() == "Windows":
            os.startfile(str(path))  # type: ignore[attr-defined]
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", str(path)])
        else:
            subprocess.Popen(["xdg-open", str(path)])
    except Exception:
        webbrowser.open(path.as_uri())


class Background(QWidget):
    def paintEvent(self, event) -> None:  # type: ignore[override]
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        r = self.rect()
        bg = QLinearGradient(0, 0, r.width(), r.height())
        bg.setColorAt(0.0, QColor(2, 8, 16))
        bg.setColorAt(0.45, QColor(4, 20, 39))
        bg.setColorAt(1.0, QColor(0, 7, 15))
        p.fillRect(r, bg)

        for cx, cy, radius, color in [
            (0.88, 0.10, 0.33, QColor(24, 145, 255, 70)),
            (0.12, 0.72, 0.26, QColor(32, 223, 90, 36)),
            (0.50, 1.02, 0.44, QColor(62, 30, 160, 42)),
        ]:
            grad = QRadialGradient(QPointF(r.width() * cx, r.height() * cy), max(r.width(), r.height()) * radius)
            grad.setColorAt(0, color)
            grad.setColorAt(1, QColor(0, 0, 0, 0))
            p.fillRect(r, grad)

        p.setPen(QPen(QColor(74, 145, 215, 42), 1))
        for i in range(18):
            y = int(60 + i * 13)
            p.drawArc(QRectF(-180, y, r.width() + 360, 170 + i * 9), 0, 180 * 16)

        p.setPen(QPen(QColor(43, 211, 255, 70), 1))
        spacing = 42
        for x in range(-spacing, r.width() + spacing, spacing):
            p.drawLine(x, r.height(), int(r.width() * 0.5), int(r.height() * 0.53))
        for y in range(int(r.height() * 0.55), r.height(), spacing):
            p.drawLine(0, y, r.width(), y)


class Card(QFrame):
    def __init__(self, border: str | None = None, bg: str | None = None) -> None:
        super().__init__()
        self.setStyleSheet(Theme.card(border=border, bg=bg))
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)


class HoverButton(QPushButton):
    def __init__(self, text: str, parent: Optional[QWidget] = None) -> None:
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(42)
        self.setStyleSheet(Theme.button())


class FlagBadge(QWidget):
    def __init__(self, country: str, size: int = 48) -> None:
        super().__init__()
        self.country = country
        self._size = size
        self.setFixedSize(size, size)
        self.setToolTip(country)

    def paintEvent(self, event) -> None:  # type: ignore[override]
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        s = min(self.width(), self.height()) - 4
        r = QRectF(2, 2, s, s)
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(0, 0, 0, 90))
        p.drawEllipse(r.adjusted(2, 4, 2, 4))
        color = QColor(COUNTRY_COLORS.get(self.country, "#2456a8"))
        grad = QLinearGradient(r.topLeft(), r.bottomRight())
        grad.setColorAt(0, color.lighter(128))
        grad.setColorAt(1, color.darker(130))
        p.setBrush(grad)
        p.drawEllipse(r)
        p.setPen(QPen(QColor(255, 255, 255, 120), 1.2))
        p.drawEllipse(r)
        initials = "".join([part[0] for part in self.country.replace("do", "").replace("de", "").replace("e", "").split()[:2]]).upper() or "?"
        p.setFont(QFont(Theme.FONT, max(9, int(s * 0.28)), QFont.Black))
        p.setPen(QColor(255, 255, 255) if color.lightness() < 190 else QColor(4, 16, 31))
        p.drawText(r, Qt.AlignCenter, initials[:2])


class TopHeader(Card):
    def __init__(self, title: str, subtitle: str, icon: str = "🏆", compact: bool = False) -> None:
        super().__init__(border="rgba(32, 223, 90, 0.42)", bg="rgba(6, 26, 45, 0.78)")
        self.setMinimumHeight(108 if compact else 132)
        box = QHBoxLayout(self)
        box.setContentsMargins(16 if compact else 24, 16, 16 if compact else 24, 16)
        box.setSpacing(14)
        badge = QLabel(icon)
        badge.setFixedSize(62 if compact else 76, 62 if compact else 76)
        badge.setAlignment(Qt.AlignCenter)
        badge.setStyleSheet(f"background: rgba(32,223,90,.12); border:1px solid rgba(32,223,90,.45); border-radius:{31 if compact else 38}px; font-size:{30 if compact else 38}px;")
        box.addWidget(badge)
        texts = QVBoxLayout()
        texts.addWidget(label(title, 21 if compact else 28, Theme.TEXT, QFont.Black))
        texts.addWidget(label(subtitle, 12 if compact else 14, Theme.MUTED))
        box.addLayout(texts, 1)
        live = QLabel("● AO VIVO")
        live.setAlignment(Qt.AlignCenter)
        live.setStyleSheet(f"color:{Theme.GREEN}; background:rgba(32,223,90,.10); border:1px solid rgba(32,223,90,.35); border-radius:14px; padding:8px 12px; font-weight:800;")
        if not compact:
            box.addWidget(live)


class StatCard(Card):
    def __init__(self, icon: str, title: str, value: str, sub: str, color: str, compact: bool = False) -> None:
        super().__init__(border=f"{color}66", bg="rgba(7, 27, 48, 0.78)")
        self.setMinimumHeight(96 if compact else 118)
        box = QVBoxLayout(self)
        box.setContentsMargins(14, 12, 14, 12)
        box.setSpacing(4)
        box.addWidget(label(icon, 22 if compact else 26, color, QFont.Bold, Qt.AlignLeft))
        box.addWidget(label(title.upper(), 9 if compact else 10, Theme.DIM, QFont.Bold))
        box.addWidget(label(value, 18 if compact else 24, Theme.TEXT, QFont.Black))
        box.addWidget(label(sub, 10 if compact else 12, Theme.MUTED))


class Section(Card):
    def __init__(self, title: str, icon: str = "") -> None:
        super().__init__()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 16, 16, 16)
        outer.setSpacing(12)
        head = QHBoxLayout()
        head.addWidget(label(title, 17, Theme.TEXT, QFont.Black))
        if icon:
            head.addWidget(label(icon, 20, Theme.GREEN, QFont.Bold, Qt.AlignRight))
        outer.addLayout(head)
        self.body = QVBoxLayout()
        self.body.setSpacing(10)
        outer.addLayout(self.body)


class MatchCard(Card):
    def __init__(self, match: Match, store: Store, refresh: Callable[[], None], details: Callable[[Match], None], export_one: Callable[[Match], None], compact: bool = False) -> None:
        # define borda base pela fase da partida
        border = PHASE_COLORS.get(match.fase, Theme.BLUE) + "66"
        # se o time favorito estiver presente nesta partida, usa cor púrpura para destacar
        # utilize o argumento "store" diretamente neste ponto, pois self.store ainda não foi definido
        try:
            fav_team = store.prefs.get("favorite_team", "")
        except Exception:
            fav_team = ""
        if fav_team and (match.time_a == fav_team or match.time_b == fav_team):
            border = Theme.PURPLE + "AA"
        super().__init__(border=border)
        self.match = match
        self.store = store
        self.refresh = refresh
        self.details = details
        self.export_one = export_one
        self.setMinimumHeight(142 if compact else 164)
        root = QVBoxLayout(self)
        root.setContentsMargins(14 if compact else 18, 14, 14 if compact else 18, 14)
        root.setSpacing(10)

        top = QHBoxLayout()
        top.addWidget(label(f"{match.day_label} • {match.hora}", 11 if compact else 12, Theme.GREEN, QFont.Bold), 1)
        status = match.status.upper() if match.status else "AGENDADO"
        color = Theme.DIM if match.status == "encerrado" else Theme.CYAN
        top.addWidget(label(status, 10, color, QFont.Black, Qt.AlignRight))
        root.addLayout(top)

        teams = QHBoxLayout()
        teams.setSpacing(10)
        teams.addWidget(FlagBadge(match.time_a, 42 if compact else 52))
        middle = QVBoxLayout()
        middle.addWidget(label(match.title, 16 if compact else 21, Theme.TEXT, QFont.Black, Qt.AlignCenter))
        middle.addWidget(label(f"{match.grupo} • {match.fase}", 11 if compact else 12, Theme.MUTED, QFont.Bold, Qt.AlignCenter))
        middle.addWidget(label(f"{match.estadio} — {match.cidade}", 10 if compact else 12, Theme.MUTED, align=Qt.AlignCenter))
        teams.addLayout(middle, 1)
        teams.addWidget(FlagBadge(match.time_b, 42 if compact else 52))
        root.addLayout(teams)

        actions = QHBoxLayout()
        fav = HoverButton("★" if match.id in store.favorites else "☆")
        fav.setToolTip("Adicionar/remover favorito")
        fav.setStyleSheet(Theme.ghost(Theme.YELLOW))
        fav.clicked.connect(self.on_fav)
        actions.addWidget(fav)
        alert = HoverButton("🔔" if match.alerta else "🔕")
        alert.setToolTip("Ativar/desativar alerta")
        alert.setStyleSheet(Theme.ghost(Theme.GREEN if match.alerta else Theme.DIM))
        alert.clicked.connect(self.on_alert)
        actions.addWidget(alert)
        details_btn = HoverButton("Detalhes")
        details_btn.setStyleSheet(Theme.ghost(Theme.CYAN))
        details_btn.clicked.connect(lambda: details(match))
        actions.addWidget(details_btn, 1)
        export_btn = HoverButton("Calendário")
        export_btn.setStyleSheet(Theme.ghost(Theme.BLUE))
        export_btn.clicked.connect(lambda: export_one(match))
        actions.addWidget(export_btn, 1)
        root.addLayout(actions)

    def on_fav(self) -> None:
        self.store.toggle_favorite(self.match.id)
        self.refresh()

    def on_alert(self) -> None:
        """Alterna o estado de alerta e, se ativado, exporta o evento para o calendário automaticamente."""
        # altera o estado de alerta da partida
        active = self.store.toggle_alert(self.match.id)
        # se o alerta foi ativado agora, exporta o evento e abre o .ics automaticamente
        if active:
            try:
                # export_one aponta para export_match_ics no contexto de uso
                self.export_one(self.match)
            except Exception:
                pass
        # atualiza a interface
        self.refresh()


class MiniPitch(QWidget):
    def __init__(self, a: list[dict[str, Any]], b: list[dict[str, Any]]) -> None:
        super().__init__()
        self.a = a
        self.b = b
        self.setMinimumHeight(245)

    def paintEvent(self, event) -> None:  # type: ignore[override]
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        r = QRectF(8, 8, self.width() - 16, self.height() - 16)
        grad = QLinearGradient(r.topLeft(), r.bottomRight())
        grad.setColorAt(0, QColor(5, 75, 45))
        grad.setColorAt(1, QColor(3, 38, 43))
        p.setPen(QPen(QColor(255, 255, 255, 155), 2))
        p.setBrush(grad)
        p.drawRoundedRect(r, 22, 22)
        p.drawLine(QPointF(r.center().x(), r.top()), QPointF(r.center().x(), r.bottom()))
        p.drawEllipse(r.center(), r.width() * .12, r.height() * .19)
        p.drawRect(QRectF(r.left(), r.top() + r.height() * .30, r.width() * .17, r.height() * .40))
        p.drawRect(QRectF(r.right() - r.width() * .17, r.top() + r.height() * .30, r.width() * .17, r.height() * .40))
        pos_a = [(0.15, .50), (0.30, .28), (0.34, .53), (0.31, .77)]
        pos_b = [(0.85, .50), (0.70, .28), (0.66, .53), (0.69, .77)]
        for player, (x, y) in zip(self.a[:4], pos_a):
            self.draw_player(p, r, x, y, player, QColor(32, 223, 90))
        for player, (x, y) in zip(self.b[:4], pos_b):
            self.draw_player(p, r, x, y, player, QColor(255, 79, 93))

    def draw_player(self, p: QPainter, r: QRectF, fx: float, fy: float, player: dict[str, Any], color: QColor) -> None:
        x, y = r.left() + r.width() * fx, r.top() + r.height() * fy
        p.setBrush(color)
        p.setPen(QPen(QColor(255, 255, 255, 220), 2))
        p.drawEllipse(QPointF(x, y), 18, 18)
        p.setPen(QColor(255, 255, 255))
        p.setFont(QFont(Theme.FONT, 9, QFont.Black))
        p.drawText(QRectF(x - 18, y - 11, 36, 22), Qt.AlignCenter, str(player.get("camisa", "")))
        p.setFont(QFont(Theme.FONT, 8, QFont.Bold))
        p.drawText(QRectF(x - 48, y + 20, 96, 18), Qt.AlignCenter, str(player.get("nome", "Jogador")).split()[0])


class DetailsDialog(QDialog):
    def __init__(self, match: Match, store: Store, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(match.title)
        self.resize(430, 700)
        self.setMinimumSize(360, 540)
        self.setStyleSheet(Theme.css(store.prefs.get("font_scale", 100)))
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        box = QVBoxLayout(content)
        box.setSpacing(12)
        box.addWidget(TopHeader(match.title, f"{fmt_date(match.data)} • {match.hora} • {match.estadio}", "⚽", compact=True))

        info = Section("Resumo da partida", "▣")
        rows = [
            ("Fase", match.fase), ("Grupo", match.grupo), ("Cidade", match.cidade), ("Status", match.status),
            ("Placar", match.placar or "Ainda não informado"), ("Destaque", match.destaque or "Sem observações."),
        ]
        for k, v in rows:
            row = QHBoxLayout()
            row.addWidget(label(k, 12, Theme.MUTED, QFont.Bold), 0)
            row.addWidget(label(v, 12, Theme.TEXT, align=Qt.AlignRight), 1)
            info.body.addLayout(row)
        box.addWidget(info)

        tactical = Section("Mapa tático demonstrativo", "⚽")
        pitch = MiniPitch(store.players_by_country(match.time_a), store.players_by_country(match.time_b))
        tactical.body.addWidget(pitch)
        tactical.body.addWidget(label("O mapa usa jogadores cadastrados em dados_copa.json. Se não houver elenco, o campo fica vazio.", 11, Theme.MUTED))
        box.addWidget(tactical)

        players = Section("Figurinhas rápidas", "🃏")
        grid = QGridLayout()
        plist = store.players_by_country(match.time_a) + store.players_by_country(match.time_b)
        if not plist:
            players.body.addWidget(label("Nenhum jogador cadastrado para essas seleções.", 12, Theme.MUTED, align=Qt.AlignCenter))
        else:
            for i, player in enumerate(plist[:8]):
                c = Card(border="rgba(43,211,255,.38)", bg="rgba(8,30,52,.72)")
                c.setMinimumHeight(72)
                cb = QHBoxLayout(c)
                cb.setContentsMargins(10, 8, 10, 8)
                cb.addWidget(label(str(player.get("camisa", "")), 18, Theme.GREEN, QFont.Black, Qt.AlignCenter), 0)
                cb.addWidget(label(f"{player.get('nome')}\n{player.get('pais')} • {player.get('posicao')}", 11, Theme.TEXT), 1)
                grid.addWidget(c, i // 2, i % 2)
            players.body.addLayout(grid)
        box.addWidget(players)
        box.addStretch()
        scroll.setWidget(content)
        root.addWidget(scroll, 1)
        close = HoverButton("Fechar")
        close.setStyleSheet(Theme.button(True))
        close.clicked.connect(self.accept)
        root.addWidget(close)


# ============================================================
# Janela principal
# ============================================================

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.store = Store()
        self.current_page = "home"
        self.current_phase = "Todos"
        self.search_text = ""
        self.only_alerts = False
        self.only_favorites = False
        self.calendar_year = 2026
        self.calendar_month = 6
        self.selected_date = "2026-06-16"
        self._mode = ""

        self.setWindowTitle("Calendário da Copa 2026")
        self.setMinimumSize(390, 660)
        self.resize(432, 768)
        self.setStyleSheet(Theme.css(self.store.prefs.get("font_scale", 100)))

        self.root = Background()
        self.setCentralWidget(self.root)
        self.root_layout = QVBoxLayout(self.root)
        self.root_layout.setContentsMargins(14, 10, 14, 0)
        self.root_layout.setSpacing(10)

        self.page_scroll = QScrollArea()
        self.page_scroll.setWidgetResizable(True)
        self.page = QWidget()
        self.page.setStyleSheet("background: transparent;")
        self.page_layout = QVBoxLayout(self.page)
        self.page_layout.setContentsMargins(0, 0, 0, 0)
        self.page_layout.setSpacing(14)
        self.page_scroll.setWidget(self.page)
        self.root_layout.addWidget(self.page_scroll, 1)

        self.nav = QHBoxLayout()
        self.nav.setContentsMargins(0, 0, 0, 8)
        self.nav.setSpacing(8)
        self.nav_buttons: dict[str, QPushButton] = {}
        self.root_layout.addLayout(self.nav)
        self.build_nav()

        self.setup_tray()
        self.setup_timer()
        self.apply_open_mode()
        self.update_responsive_metrics()
        self.navigate("home")

    # ---------- responsividade ----------

    def mode(self) -> str:
        if self.width() <= 640:
            return "phone"
        if self.width() <= 1040:
            return "tablet"
        return "desktop"

    def is_phone(self) -> bool:
        return self.mode() == "phone"

    def cols(self, phone: int = 1, tablet: int = 2, desktop: int = 3) -> int:
        return {"phone": phone, "tablet": tablet, "desktop": desktop}[self.mode()]

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        super().resizeEvent(event)
        new = self.mode()
        if hasattr(self, "page_layout") and new != self._mode:
            self.update_responsive_metrics()
            self.navigate(self.current_page)

    def update_responsive_metrics(self) -> None:
        self._mode = self.mode()
        if self._mode == "phone":
            self.root_layout.setContentsMargins(12, 10, 12, 0)
            self.page_layout.setSpacing(12)
        elif self._mode == "tablet":
            self.root_layout.setContentsMargins(24, 16, 24, 0)
            self.page_layout.setSpacing(16)
        else:
            self.root_layout.setContentsMargins(42, 22, 42, 0)
            self.page_layout.setSpacing(18)
        self.build_nav()

    def apply_open_mode(self) -> None:
        mode = self.store.prefs.get("open_mode", "phone")
        if mode == "desktop":
            QTimer.singleShot(80, self.showMaximized)
        elif mode == "phone":
            QTimer.singleShot(80, lambda: self.apply_preset("phone"))

    def apply_preset(self, preset: str) -> None:
        screen = self.screen() or QApplication.primaryScreen()
        geom = screen.availableGeometry() if screen else self.geometry()
        if preset == "desktop":
            self.showNormal()
            self.setMinimumSize(390, 660)
            self.move(geom.topLeft())
            self.resize(geom.width(), geom.height())
            self.showMaximized()
        else:
            self.showNormal()
            h = min(768, geom.height() - 50)
            w = int(h * 9 / 16)
            w = max(390, w)
            h = max(660, h)
            self.resize(w, h)
            self.move(geom.x() + (geom.width() - w) // 2, geom.y() + (geom.height() - h) // 2)
        self.store.prefs["open_mode"] = preset
        self.store.save_prefs()
        self.update_responsive_metrics()
        self.navigate(self.current_page)

    # ---------- navegação ----------

    def build_nav(self) -> None:
        clear_layout(self.nav)
        items = [("home", "🏠", "Início"), ("games", "⚽", "Jogos"), ("calendar", "📅", "Calendário"), ("favorites", "★", "Favoritos"), ("table", "📊", "Tabela"), ("more", "☰", "Mais")]
        self.nav_buttons = {}
        for key, icon, name in items:
            txt = icon if self.is_phone() else f"{icon}  {name}"
            b = HoverButton(txt)
            b.setMinimumHeight(50 if self.is_phone() else 48)
            b.clicked.connect(lambda checked=False, k=key: self.navigate(k))
            self.nav.addWidget(b, 1)
            self.nav_buttons[key] = b
        self.set_active_nav()

    def set_active_nav(self) -> None:
        for key, btn in self.nav_buttons.items():
            btn.setStyleSheet(Theme.button(key == self.current_page, Theme.GREEN))

    def navigate(self, page: str) -> None:
        self.current_page = page
        self.set_active_nav()
        clear_layout(self.page_layout)
        if page == "home":
            self.build_home()
        elif page == "games":
            self.build_games()
        elif page == "calendar":
            self.build_calendar()
        elif page == "favorites":
            self.build_favorites()
        elif page == "table":
            self.build_table()
        else:
            self.build_more()
        self.page_scroll.verticalScrollBar().setValue(0)

    def responsive_layout(self) -> QVBoxLayout | QHBoxLayout:
        layout = QVBoxLayout() if self.mode() in {"phone", "tablet"} else QHBoxLayout()
        layout.setSpacing(14 if self.is_phone() else 18)
        return layout

    # ---------- dados filtrados ----------

    def filtered_matches(self) -> list[Match]:
        data = self.store.matches[:]
        if self.current_phase != "Todos":
            data = [m for m in data if m.fase == self.current_phase or m.grupo == self.current_phase]
        if self.only_alerts:
            data = [m for m in data if m.alerta]
        if self.only_favorites:
            data = [m for m in data if m.id in self.store.favorites]
        q = self.search_text.strip().lower()
        if q:
            data = [m for m in data if q in " ".join([m.time_a, m.time_b, m.fase, m.grupo, m.estadio, m.cidade, m.status]).lower()]
        return data

    # ---------- páginas ----------

    def build_home(self) -> None:
        phone = self.is_phone()
        self.page_layout.addWidget(TopHeader("Calendário da Copa 2026", "Jogos, alertas, favoritos e exportação para calendário", "🏆", compact=phone))
        next_match = self.store.next_match()
        stats = QGridLayout()
        stats.setSpacing(12)
        values = [
            ("⚽", "Jogos no app", str(len(self.store.matches)), "base editável", Theme.GREEN),
            ("🔔", "Alertas", str(len([m for m in self.store.matches if m.alerta])), "ativos", Theme.YELLOW),
            ("★", "Favoritos", str(len(self.store.favorites)), "salvos", Theme.BLUE),
            ("📍", "Sedes", "3", "Canadá • México • EUA", Theme.PURPLE),
        ]
        for i, args in enumerate(values):
            stats.addWidget(StatCard(*args, compact=phone), i // self.cols(2, 4, 4), i % self.cols(2, 4, 4))
        self.page_layout.addLayout(stats)

        body = self.responsive_layout()
        left = QVBoxLayout()
        left.setSpacing(14)
        if next_match:
            s = Section("Próximo jogo em destaque", "▶")
            s.body.addWidget(MatchCard(next_match, self.store, lambda: self.navigate("home"), self.open_details, self.export_match_ics, compact=phone))
            left.addWidget(s)
        today = Section("Jogos do dia selecionado", "📅")
        today.body.addWidget(label(f"Data: {fmt_date(self.selected_date)}", 12, Theme.MUTED, QFont.Bold))
        day_matches = self.store.matches_on(self.selected_date)
        if not day_matches:
            today.body.addWidget(label("Não há partidas cadastradas para este dia.", 12, Theme.MUTED, align=Qt.AlignCenter))
        else:
            for m in day_matches[:3]:
                today.body.addWidget(MatchCard(m, self.store, lambda: self.navigate("home"), self.open_details, self.export_match_ics, compact=True))
        left.addWidget(today)
        body.addLayout(left, 2)

        right = QVBoxLayout()
        right.setSpacing(14)
        quick = Section("Ações rápidas", "✦")
        actions = [
            ("Ver jogos", lambda: self.navigate("games")), ("Abrir calendário", lambda: self.navigate("calendar")),
            ("Exportar .ICS", self.export_all_ics), ("Modo desktop", lambda: self.apply_preset("desktop")),
        ]
        for text, cb in actions:
            b = HoverButton(text)
            b.setStyleSheet(Theme.button(False, Theme.CYAN))
            b.clicked.connect(cb)
            quick.body.addWidget(b)
        right.addWidget(quick)
        facts = Section("Informações do torneio", "ⓘ")
        for line in ["48 seleções", "104 partidas", "12 grupos", "Canadá, México e Estados Unidos", "11/06 a 19/07/2026"]:
            facts.body.addWidget(label("• " + line, 12, Theme.TEXT))
        right.addWidget(facts)
        body.addLayout(right, 1)
        self.page_layout.addLayout(body)
        self.page_layout.addStretch()

    def build_games(self) -> None:
        phone = self.is_phone()
        self.page_layout.addWidget(TopHeader("Jogos", "Busca, filtros, favoritos, alertas e detalhes", "⚽", compact=phone))
        filters = Section("Filtros", "🔎")
        form = QVBoxLayout() if phone else QHBoxLayout()
        self.search = QLineEdit(self.search_text)
        self.search.setPlaceholderText("Procurar por seleção, estádio, fase ou cidade...")
        self.search.textChanged.connect(self.on_search)
        self.search.returnPressed.connect(lambda: self.navigate("games"))
        form.addWidget(self.search, 2)
        apply_btn = HoverButton("Buscar")
        apply_btn.setStyleSheet(Theme.button(False, Theme.GREEN))
        apply_btn.clicked.connect(lambda: self.navigate("games"))
        form.addWidget(apply_btn)
        phase = QComboBox()
        phase.addItems(["Todos", "Grupos", "16 avos", "Oitavas", "Quartas", "Semifinal", "Final"])
        phase.setCurrentText(self.current_phase)
        phase.currentTextChanged.connect(self.on_phase)
        form.addWidget(phase, 1)
        alerts = QCheckBox("Só alertas")
        alerts.setChecked(self.only_alerts)
        alerts.toggled.connect(self.on_alert_filter)
        form.addWidget(alerts)
        favs = QCheckBox("Só favoritos")
        favs.setChecked(self.only_favorites)
        favs.toggled.connect(self.on_favorite_filter)
        form.addWidget(favs)
        filters.body.addLayout(form)
        self.page_layout.addWidget(filters)

        matches = self.filtered_matches()
        grid = QGridLayout()
        grid.setSpacing(14)
        col_count = self.cols(1, 2, 2)
        if not matches:
            empty = Section("Nenhum jogo encontrado", "⚠")
            empty.body.addWidget(label("Tente limpar a busca ou mudar os filtros.", 13, Theme.MUTED, align=Qt.AlignCenter))
            self.page_layout.addWidget(empty)
        else:
            for i, m in enumerate(matches):
                grid.addWidget(MatchCard(m, self.store, lambda: self.navigate("games"), self.open_details, self.export_match_ics, compact=phone), i // col_count, i % col_count)
            self.page_layout.addLayout(grid)
        self.page_layout.addStretch()

    def build_calendar(self) -> None:
        phone = self.is_phone()
        self.page_layout.addWidget(TopHeader("Calendário", "Navegação mensal com marcação de dias e jogos", "📅", compact=phone))
        top = QHBoxLayout()
        prev = HoverButton("‹")
        nxt = HoverButton("›")
        for b in (prev, nxt):
            b.setFixedWidth(48)
            b.setStyleSheet(Theme.button(False, Theme.CYAN))
        prev.clicked.connect(lambda: self.change_month(-1))
        nxt.clicked.connect(lambda: self.change_month(1))
        top.addWidget(prev)
        top.addWidget(label(f"{month_name_pt(self.calendar_month).capitalize()} de {self.calendar_year}", 20 if phone else 24, Theme.TEXT, QFont.Black, Qt.AlignCenter), 1)
        top.addWidget(nxt)
        self.page_layout.addLayout(top)

        stats = QGridLayout()
        stats.setSpacing(12)
        month_matches = [m for m in self.store.matches if m.data.startswith(f"{self.calendar_year}-{self.calendar_month:02d}")]
        stats_items = [
            ("▣", "Jogos no mês", str(len(month_matches)), "partidas", Theme.CYAN),
            ("🔔", "Alertas", str(len([m for m in month_matches if m.alerta])), "ativos", Theme.YELLOW),
            ("📆", "Dias com jogos", str(len({m.data for m in month_matches})), "dias", Theme.GREEN),
            ("★", "Favoritos", str(len([m for m in month_matches if m.id in self.store.favorites])), "no mês", Theme.BLUE),
        ]
        for i, args in enumerate(stats_items):
            stats.addWidget(StatCard(*args, compact=phone), i // self.cols(2, 4, 4), i % self.cols(2, 4, 4))
        self.page_layout.addLayout(stats)

        body = self.responsive_layout()
        cal_card = Section("Mês", "▦")
        week_line = QGridLayout()
        week_line.setSpacing(6)
        for i, w in enumerate(["DOM", "SEG", "TER", "QUA", "QUI", "SEX", "SÁB"]):
            week_line.addWidget(label(w, 9 if phone else 11, Theme.DIM, QFont.Bold, Qt.AlignCenter), 0, i)
        cal_card.body.addLayout(week_line)
        grid = QGridLayout()
        grid.setSpacing(6 if phone else 8)
        weeks = calendar.Calendar(firstweekday=6).monthdatescalendar(self.calendar_year, self.calendar_month)
        today_iso = date.today().isoformat()
        for r, week in enumerate(weeks):
            for c, d in enumerate(week):
                iso = d.isoformat()
                count = len(self.store.matches_on(iso))
                btn = QPushButton(f"{d.day}\n{'⚽ ' + str(count) if count else ''}")
                btn.setCursor(Qt.PointingHandCursor)
                outside = d.month != self.calendar_month
                selected = iso == self.selected_date
                today = iso == today_iso
                border = Theme.GREEN if selected else (Theme.YELLOW if today else "rgba(75,108,142,.45)")
                bg = "rgba(32,223,90,.23)" if selected else ("rgba(255,208,68,.14)" if today else "rgba(8,27,46,.72)")
                if outside:
                    bg = "rgba(4,13,24,.40)"
                btn.setStyleSheet(f"QPushButton {{ background:{bg}; border:1px solid {border}; border-radius:12px; color:{Theme.TEXT if not outside else Theme.DIM}; padding:8px 2px; font-weight:800; }} QPushButton:hover {{ border-color:{Theme.CYAN}; }}")
                btn.setMinimumHeight(56 if phone else 72)
                btn.clicked.connect(lambda checked=False, day=iso: self.select_day(day))
                grid.addWidget(btn, r, c)
        cal_card.body.addLayout(grid)
        body.addWidget(cal_card, 2)

        day = Section("Jogos do dia", "⚽")
        day.body.addWidget(label(fmt_date(self.selected_date), 13, Theme.GREEN, QFont.Bold))
        selected_matches = self.store.matches_on(self.selected_date)
        if not selected_matches:
            day.body.addWidget(label("Nenhum jogo cadastrado nesta data.", 12, Theme.MUTED, align=Qt.AlignCenter))
        else:
            for m in selected_matches:
                day.body.addWidget(MatchCard(m, self.store, lambda: self.navigate("calendar"), self.open_details, self.export_match_ics, compact=True))
        body.addWidget(day, 1)
        self.page_layout.addLayout(body)
        self.page_layout.addStretch()

    def build_favorites(self) -> None:
        phone = self.is_phone()
        self.page_layout.addWidget(TopHeader("Favoritos", "Jogos salvos para acompanhar mais rápido", "★", compact=phone))
        favs = self.store.favorite_matches()
        top = QGridLayout()
        top.setSpacing(12)
        top_items = [("★", "Favoritos", str(len(favs)), "partidas", Theme.YELLOW), ("🔔", "Com alerta", str(len([m for m in favs if m.alerta])), "ativos", Theme.GREEN)]
        next_fav = favs[0] if favs else self.store.next_match()
        top_items.append(("▶", "Próximo", next_fav.hora if next_fav else "--", next_fav.title if next_fav else "sem jogos", Theme.CYAN))
        for i, args in enumerate(top_items):
            top.addWidget(StatCard(*args, compact=phone), i // self.cols(1, 3, 3), i % self.cols(1, 3, 3))
        self.page_layout.addLayout(top)
        if not favs:
            empty = Section("Ainda sem favoritos", "☆")
            empty.body.addWidget(label("Vá em Jogos e toque na estrela de uma partida para salvar aqui.", 13, Theme.MUTED, align=Qt.AlignCenter))
            self.page_layout.addWidget(empty)
        else:
            grid = QGridLayout()
            grid.setSpacing(14)
            cc = self.cols(1, 2, 2)
            for i, m in enumerate(favs):
                grid.addWidget(MatchCard(m, self.store, lambda: self.navigate("favorites"), self.open_details, self.export_match_ics, compact=phone), i // cc, i % cc)
            self.page_layout.addLayout(grid)
        self.page_layout.addStretch()

    
    def build_table(self) -> None:
        """Construir tabela de classificação por grupo com base nas partidas encerradas."""
        phone = self.is_phone()
        self.page_layout.addWidget(TopHeader("Tabela de grupos", "Classificação por grupo baseada em partidas encerradas", "📊", compact=phone))
        # Calcula a classificação a partir dos resultados
        standings: dict[str, dict[str, dict[str, int]]] = {}
        for m in self.store.matches:
            # considere somente partidas da fase de grupos com placar informado
            if not m.placar or not (m.fase == "Grupos" or m.grupo.startswith("Grupo")):
                continue
            try:
                goals_a, goals_b = [int(x) for x in m.placar.split("-")]
            except Exception:
                continue
            group = m.grupo.strip()
            standings.setdefault(group, {})
            # atualiza estatísticas para time A e B
            for team, gf, ga in [(m.time_a, goals_a, goals_b), (m.time_b, goals_b, goals_a)]:
                team_stats = standings[group].setdefault(team, {"P": 0, "J": 0, "V": 0, "E": 0, "D": 0, "GP": 0, "GC": 0, "SG": 0})
                team_stats["J"] += 1
                team_stats["GP"] += gf
                team_stats["GC"] += ga
                team_stats["SG"] = team_stats["GP"] - team_stats["GC"]
            # vitória/empate/derrota
            if goals_a > goals_b:
                standings[group][m.time_a]["V"] += 1
                standings[group][m.time_a]["P"] += 3
                standings[group][m.time_b]["D"] += 1
            elif goals_b > goals_a:
                standings[group][m.time_b]["V"] += 1
                standings[group][m.time_b]["P"] += 3
                standings[group][m.time_a]["D"] += 1
            else:
                standings[group][m.time_a]["E"] += 1
                standings[group][m.time_b]["E"] += 1
                standings[group][m.time_a]["P"] += 1
                standings[group][m.time_b]["P"] += 1
        # constrói a interface para cada grupo
        if standings:
            for group_name, teams in sorted(standings.items()):
                sec = Section(group_name, "📋")
                grid = QGridLayout()
                grid.setSpacing(6 if phone else 8)
                headers = ["Seleção", "J", "V", "E", "D", "GP", "GC", "SG", "Pts"]
                for col, h in enumerate(headers):
                    grid.addWidget(label(h, 9 if phone else 11, Theme.MUTED, QFont.Bold, Qt.AlignCenter), 0, col)
                # ordena por pontos, saldo de gols e gols marcados
                sorted_teams = sorted(teams.items(), key=lambda x: (-x[1]["P"], -x[1]["SG"], -x[1]["GP"]))
                for row, (team, stats) in enumerate(sorted_teams, start=1):
                    values = [team, stats["J"], stats["V"], stats["E"], stats["D"], stats["GP"], stats["GC"], stats["SG"], stats["P"]]
                    for col, val in enumerate(values):
                        color = Theme.TEXT if row <= 2 else Theme.DIM
                        weight = QFont.Bold if col == 0 else QFont.Normal
                        grid.addWidget(label(str(val), 9 if phone else 11, color, weight, Qt.AlignCenter), row, col)
                sec.body.addLayout(grid)
                self.page_layout.addWidget(sec)
        else:
            empty = Section("Sem dados", "🔍")
            empty.body.addWidget(label("Nenhuma partida concluída para calcular a classificação.", 12, Theme.MUTED, align=Qt.AlignCenter))
            self.page_layout.addWidget(empty)
        # adiciona uma legenda explicando cada coluna
        legend = Section("Legenda", "🛈")
        legend_grid = QGridLayout()
        legend_grid.setSpacing(6 if phone else 8)
        legend_rows = [
            ("J", "Jogos disputados"),
            ("V", "Vitórias"),
            ("E", "Empates"),
            ("D", "Derrotas"),
            ("GP", "Gols pró"),
            ("GC", "Gols contra"),
            ("SG", "Saldo de gols"),
            ("Pts", "Pontos"),
        ]
        for r, (abbr, expl) in enumerate(legend_rows):
            legend_grid.addWidget(label(abbr, 9 if phone else 11, Theme.TEXT, QFont.Bold), r, 0)
            legend_grid.addWidget(label(expl, 9 if phone else 11, Theme.MUTED), r, 1)
        legend.body.addLayout(legend_grid)
        self.page_layout.addWidget(legend)
        self.page_layout.addStretch()
    def build_more(self) -> None:
        phone = self.is_phone()
        self.page_layout.addWidget(TopHeader("Mais", "Configurações, exportação e manutenção do projeto", "☰", compact=phone))
        body = self.responsive_layout()
        left = QVBoxLayout()
        left.setSpacing(14)
        view = Section("Visual e janela", "🖥")
        for text, cb in [("📱 Celular 9:16", lambda: self.apply_preset("phone")), ("🖥 Desktop tela cheia", lambda: self.apply_preset("desktop"))]:
            b = HoverButton(text)
            b.setStyleSheet(Theme.button(False, Theme.CYAN))
            b.clicked.connect(cb)
            view.body.addWidget(b)
        font_row = QHBoxLayout()
        font_row.addWidget(label("Tamanho da fonte", 12, Theme.MUTED, QFont.Bold))
        spinner = QSpinBox()
        spinner.setRange(85, 135)
        spinner.setSingleStep(5)
        spinner.setValue(int(self.store.prefs.get("font_scale", 100)))
        spinner.valueChanged.connect(self.change_font_scale)
        font_row.addWidget(spinner)
        view.body.addLayout(font_row)
        left.addWidget(view)

        data = Section("Dados e calendário", "⇩")
        buttons = [
            ("Exportar todos para .ICS", self.export_all_ics), ("Exportar CSV", self.export_csv),
            ("Importar JSON", self.import_json), ("Abrir pasta do projeto", lambda: safe_open(APP_DIR)),
            ("Resetar demo", self.reset_demo_confirm),
        ]
        for text, cb in buttons:
            b = HoverButton(text)
            b.setStyleSheet(Theme.button(False, Theme.GREEN))
            b.clicked.connect(cb)
            data.body.addWidget(b)
        left.addWidget(data)
        # configura temporizador de alerta personalizado
        # Criamos a linha com um rótulo, um esticador e o spinbox para melhorar a aparência.
        alert_row = QHBoxLayout()
        # texto que explica o que o spinbox controla
        label_minutes = label("Minutos antes do alerta", 12, Theme.MUTED, QFont.Bold)
        alert_row.addWidget(label_minutes)
        # adiciona um esticador para empurrar o spinbox para o lado direito
        alert_row.addStretch()
        # spinner com range customizado; ele se ajusta à largura do modo atual
        alert_spinner = QSpinBox()
        alert_spinner.setRange(5, 120)
        alert_spinner.setSingleStep(5)
        alert_spinner.setValue(int(self.store.prefs.get("alert_minutes", 30)))
        # define uma largura máxima que depende se estamos no modo celular ou desktop
        max_w = 90 if self.is_phone() else 120
        alert_spinner.setMaximumWidth(max_w)
        alert_spinner.valueChanged.connect(self.change_alert_minutes)
        alert_row.addWidget(alert_spinner)
        # adiciona a linha à seção "Dados e calendário"
        data.body.addLayout(alert_row)
        # adiciona seção para escolher time favorito
        fav_section = Section("Time favorito", "💙")
        fav_layout = QHBoxLayout()
        fav_layout.setSpacing(10)
        # rótulo da combobox
        fav_layout.addWidget(label("Seu time", 12, Theme.MUTED, QFont.Bold))
        team_combo = QComboBox()
        # obtém lista de seleções únicas dos jogos
        teams = sorted({m.time_a for m in self.store.matches}.union({m.time_b for m in self.store.matches}))
        # adiciona opção em branco para nenhum favorito
        team_combo.addItem("")
        for t in teams:
            team_combo.addItem(t)
        # seleciona o valor atual, se houver
        current_team = self.store.prefs.get("favorite_team", "")
        if current_team:
            idx = team_combo.findText(current_team)
            if idx >= 0:
                team_combo.setCurrentIndex(idx)
        team_combo.currentTextChanged.connect(self.change_favorite_team)
        fav_layout.addWidget(team_combo, 1)
        fav_section.body.addLayout(fav_layout)
        left.addWidget(fav_section)
        # adiciona o layout da coluna esquerda ao layout principal
        body.addLayout(left, 1)

        # monta a coluna da direita com estatísticas e fases da competição
        right = QVBoxLayout()
        right.setSpacing(14)
        # estatísticas gerais
        stats_section = Section("Estatísticas", "📊")
        stats_grid = QGridLayout()
        stats_grid.setSpacing(14 if self.is_phone() else 18)
        # calcula totais: partidas totais, favoritos e alertas
        total_games = len(self.store.matches)
        fav_matches = [m for m in self.store.matches if m.id in self.store.favorites]
        alert_matches = [m for m in self.store.matches if m.alerta]
        stats = [
            ("⚽", "Jogos Totais", str(total_games), "partidas", Theme.CYAN),
            ("★", "Favoritos", str(len(fav_matches)), "partidas", Theme.YELLOW),
            ("🔔", "Alertas", str(len(alert_matches)), "ativos", Theme.GREEN),
        ]
        for i, (ic, title, value, sub, color) in enumerate(stats):
            stats_grid.addWidget(StatCard(ic, title, value, sub, color, compact=self.is_phone()), 0, i)
        stats_section.body.addLayout(stats_grid)
        right.addWidget(stats_section)
        # fases da competição
        phases_section = Section("Fases da competição", "🏆")
        phase_grid = QGridLayout()
        phase_grid.setSpacing(14 if self.is_phone() else 18)
        # define dados fictícios para fases da Copa 2026
        phases_data = [
            ("Grupos", "48 seleções", "16 grupos", Theme.GREEN),
            ("16 avos", "32 seleções", "16 jogos", Theme.CYAN),
            ("Oitavas", "16 seleções", "8 jogos", Theme.BLUE),
            ("Quartas", "8 seleções", "4 jogos", Theme.YELLOW),
            ("Semifinal", "4 seleções", "2 jogos", Theme.RED),
            ("Final", "2 seleções", "1 jogo", Theme.YELLOW),
        ]
        # distribui as fases em duas linhas de até três colunas cada
        for idx, (name, line1, line2, col) in enumerate(phases_data):
            row = idx // 3
            col_idx = idx % 3
            phase_card = StatCard("🏅", name, line1, line2, col, compact=self.is_phone())
            phase_grid.addWidget(phase_card, row, col_idx)
        phases_section.body.addLayout(phase_grid)
        right.addWidget(phases_section)
        # adiciona a coluna da direita ao layout principal
        body.addLayout(right, 1)
        # adiciona o layout completo na página
        self.page_layout.addLayout(body)
        # espaço extra para empurrar conteúdo para cima
        self.page_layout.addStretch()

    # ---------- callbacks ----------

    def on_search(self, text: str) -> None:
        self.search_text = text

    def on_phase(self, text: str) -> None:
        self.current_phase = text
        self.navigate("games")

    def on_alert_filter(self, state: bool) -> None:
        self.only_alerts = state
        self.navigate("games")

    def on_favorite_filter(self, state: bool) -> None:
        self.only_favorites = state
        self.navigate("games")

    def change_favorite_team(self, team: str) -> None:
        """Callback para alteração do time favorito via combobox."""
        # atualiza a preferência no store
        self.store.set_favorite_team(team)
        # recarrega a página atual para refletir cores e alertas
        self.navigate(self.current_page)

    def change_month(self, delta: int) -> None:
        m = self.calendar_month + delta
        y = self.calendar_year
        if m < 1:
            m = 12; y -= 1
        elif m > 12:
            m = 1; y += 1
        self.calendar_year, self.calendar_month = y, m
        self.navigate("calendar")

    def select_day(self, iso: str) -> None:
        self.selected_date = iso
        self.navigate("calendar")

    def change_font_scale(self, value: int) -> None:
        self.store.prefs["font_scale"] = value
        self.store.save_prefs()
        self.setStyleSheet(Theme.css(value))

    
    def change_alert_minutes(self, value: int) -> None:
        """Atualiza o intervalo (em minutos) para receber alertas dos jogos."""
        self.store.prefs["alert_minutes"] = int(value)
        self.store.save_prefs()
    def reset_demo_confirm(self) -> None:
        result = QMessageBox.question(self, "Resetar dados", "Isso vai substituir dados_copa.json pela base demonstrativa. Continuar?")
        if result == QMessageBox.Yes:
            self.store.reset_demo()
            self.navigate(self.current_page)

    def open_details(self, match: Match) -> None:
        DetailsDialog(match, self.store, self).exec()

    # ---------- exportação ----------

    def event_to_ics(self, match: Match) -> str:
        start = match.datetime_obj
        end = start + timedelta(hours=2)
        uid = f"{match.id}@calendario-copa-2026.local"
        desc = f"{match.grupo} - {match.fase} - {match.estadio} - {match.cidade}".replace("\n", " ")
        return "\n".join([
            "BEGIN:VEVENT", f"UID:{uid}", f"DTSTAMP:{datetime.utcnow():%Y%m%dT%H%M%SZ}",
            f"DTSTART:{start:%Y%m%dT%H%M%S}", f"DTEND:{end:%Y%m%dT%H%M%S}",
            f"SUMMARY:Copa 2026 - {match.time_a} x {match.time_b}", f"LOCATION:{match.estadio}, {match.cidade}",
            f"DESCRIPTION:{desc}", "END:VEVENT",
        ])

    def write_ics(self, matches: list[Match]) -> Path:
        content = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Calendario Copa 2026//PT-BR", "CALSCALE:GREGORIAN", "METHOD:PUBLISH"]
        for m in matches:
            content.append(self.event_to_ics(m))
        content.append("END:VCALENDAR")
        ICS_FILE.write_text("\n".join(content) + "\n", encoding="utf-8")
        return ICS_FILE

    def export_match_ics(self, match: Match) -> None:
        path = self.write_ics([match])
        QMessageBox.information(self, "Calendário exportado", f"Arquivo criado:\n{path}\n\nAbra esse .ics para adicionar ao calendário do Windows, Google Calendar, Outlook ou celular.")
        safe_open(path)

    def export_all_ics(self) -> None:
        path = self.write_ics(self.store.matches)
        QMessageBox.information(self, "Calendário exportado", f"Todos os jogos cadastrados foram exportados para:\n{path}")
        safe_open(path)

    def export_csv(self) -> None:
        with CSV_FILE.open("w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(["data", "hora", "time_a", "time_b", "placar", "grupo", "fase", "estadio", "cidade", "status", "alerta"])
            for m in self.store.matches:
                writer.writerow([m.data, m.hora, m.time_a, m.time_b, m.placar, m.grupo, m.fase, m.estadio, m.cidade, m.status, "sim" if m.alerta else "não"])
        QMessageBox.information(self, "CSV exportado", f"Arquivo criado:\n{CSV_FILE}")
        safe_open(CSV_FILE)

    def import_json(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Importar dados_copa.json", str(APP_DIR), "JSON (*.json)")
        if not path:
            return
        try:
            raw = json.loads(Path(path).read_text(encoding="utf-8"))
            if "partidas" not in raw:
                raise ValueError("O JSON precisa ter a chave 'partidas'.")
            DATA_FILE.write_text(json.dumps(raw, indent=2, ensure_ascii=False), encoding="utf-8")
            self.store.load()
            self.navigate(self.current_page)
            QMessageBox.information(self, "Importado", "JSON importado com sucesso.")
        except Exception as exc:
            QMessageBox.warning(self, "Erro ao importar", str(exc))

    # ---------- alertas/notificações ----------

    def setup_tray(self) -> None:
        self.tray: Optional[QSystemTrayIcon] = None
        if QSystemTrayIcon.isSystemTrayAvailable():
            icon = self.style().standardIcon(QStyle.SP_MessageBoxInformation)
            self.tray = QSystemTrayIcon(icon, self)
            self.tray.setToolTip("Calendário da Copa 2026")
            self.tray.show()

    def setup_timer(self) -> None:
        self.timer = QTimer(self)
        self.timer.setInterval(60_000)
        self.timer.timeout.connect(self.check_alerts)
        self.timer.start()
        QTimer.singleShot(1200, self.check_alerts)

    def notify(self, title: str, message: str) -> None:
        if self.tray:
            self.tray.showMessage(title, message, QSystemTrayIcon.Information, 8000)
        else:
            QMessageBox.information(self, title, message)

    def check_alerts(self) -> None:
        now = datetime.now()
        minutes = int(self.store.prefs.get("alert_minutes", 30))
        for m in self.store.matches:
            if not m.alerta or m.id in self.store.alerted:
                continue
            delta = m.datetime_obj - now
            if timedelta(minutes=0) <= delta <= timedelta(minutes=minutes):
                self.store.alerted.add(m.id)
                self.store.save_state()
                self.notify("Jogo da Copa começando", f"{m.title}\n{m.hora} • {m.estadio}")


def main() -> None:
    # Qt6 automatically habilita ajuste de DPI; as flags AA_EnableHighDpiScaling e AA_UseHighDpiPixmaps
    # estão depreciadas e foram removidas
    app = QApplication(sys.argv)
    app.setApplicationName("Calendário da Copa 2026")
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()