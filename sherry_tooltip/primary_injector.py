# coding=utf-8
"""
    create by pymu
    on 2021/7/28
    at 16:37
"""
from PyQt5.QtCore import QEvent, QRect
from PyQt5.QtWidgets import QWidget, QAbstractScrollArea

from sherry_tooltip.tooltip import CustomTooltip


class TooltipAgent:
    """反射器"""

    __agent__ = ('installer',)

    def __init__(self):
        for agent in self.__agent__:
            getattr(self, agent)()

    @staticmethod
    def _register_tooltip(obj):
        """替换内置的tooltip样式"""
        primeval_event_function = getattr(obj, 'event')

        def graft(widget, event):
            if event.type() == QEvent.ToolTip and widget.toolTip():
                CustomTooltip.showText(event.globalPos(), widget.toolTip(), widget, QRect(), widget.toolTipDuration())
                return True
            return primeval_event_function(widget, event)

        return graft

    @staticmethod
    def installer():
        setattr(QWidget, 'event', TooltipAgent._register_tooltip(QWidget))
        setattr(QAbstractScrollArea, 'event', TooltipAgent._register_tooltip(QAbstractScrollArea))
