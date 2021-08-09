# coding=utf-8
"""
    create by pymu
    on 2021/7/16
    at 16:39
"""
from typing import Tuple

from PyQt5.QtCore import QPoint, QRect, QBasicTimer, Qt
from PyQt5.QtGui import QPalette, QFont, QScreen
from PyQt5.QtWidgets import QWidget, QDialog, QLabel


class TooltipLabel(QLabel):
    triangle_width: int
    triangle_height: float
    label_radius: int
    top_left, top, top_right, bottom_left, bottom, bottom_right, \
    left_top, left, left_bottom, right_top, right, right_bottom = range(12)
    direct: int

    def setDirection(self, direct: int):
        self.direct = direct

    def set_triangle_width(self, width: int):
        ...


class ToolTip(QDialog):
    instance: ToolTip
    hideTimer: QBasicTimer
    expireTimer: QBasicTimer
    fadingOut: bool
    master: QWidget
    rect: QRect
    _text: str
    widget: TooltipLabel
    tip_pos_widget = Tuple[QPoint, QWidget]

    def __init__(self, text: str, widget: QWidget, msecDisplayTime: int):
        super().__init__(widget, Qt.ToolTip | Qt.BypassGraphicsProxyWidget)

    def place(self):
        ...

    def configure(self):
        ...

    def text(self) -> str:
        ...

    def setText(self, text: str):
        ...

    def reuseTip(self, text: str, msecDisplayTime: int):
        ...

    def show_(self, tip_position=None, tip_arrow_direction=None): ...

    def hideTip(self):
        ...

    def hideTipImmediately(self):
        ...

    def updateSize(self):
        ...

    def setTipRect(self, widget: QWidget, rect: QRect):
        ...

    def restartExpireTimer(self, msecDisplayTime: int):
        ...

    def placeTip(self, pos: QPoint, widget: QWidget):
        ...

    @staticmethod
    def getTipScreen(pos: QPoint, widget: QWidget) -> QScreen: ...


class CustomTooltip:
    """自定义的tooltip
    可以更换提示类型的
    """
    tooltip_palette: QPalette
    TOOLTIP_POSITION_KEY: str
    TOOLTIP_ARROW_DIRECTION_KEY: str

    # noinspection SpellCheckingInspection
    @staticmethod
    def showText(pos: QPoint, text: str, widget: QWidget = None, rect: QRect = QRect(), msecShowTime: int = -1):
        ...

    @staticmethod
    def _get_tip_attr(obj: QWidget) -> Tuple: ...

    @staticmethod
    def hideText(): ...

    @staticmethod
    def isVisible() -> bool: ...

    @staticmethod
    def text() -> str: ...

    @staticmethod
    def palette() -> QPalette: ...

    @staticmethod
    def setPalette(palette: QPalette): ...

    @staticmethod
    def font() -> QFont: ...

    @staticmethod
    def setFont(font: QFont): ...
