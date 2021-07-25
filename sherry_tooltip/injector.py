# coding=utf-8
"""
    create by pymu
    on 2021/7/15


    反射文件
"""
from PyQt5.QtCore import QEvent, QRect
from PyQt5.QtWidgets import QWidget, QAbstractScrollArea
from sherry.core.badge import Badge
from sherry.core.injector import BaseAgent
from sherry.core.reflex import ReflexCenter

from sherry_tooltip.tooltip import CustomTooltip


class TooltipAgent(BaseAgent):
    """反射器"""

    __agent__ = ('installer',)

    @staticmethod
    def _register_tooltip(obj):
        """替换内置的tooltip样式"""
        primeval_event_function = getattr(obj, 'event')

        def graft(widget, event):
            if event.type() == QEvent.ToolTip and widget.toolTip():
                tooltip = Badge(source=CustomTooltip, return_class=True)
                tooltip.showText(event.globalPos(), "这是重载后的 tooltip", widget, QRect(), widget.toolTipDuration())
                return True
            return primeval_event_function(widget, event)

        return graft

    @staticmethod
    def installer():
        ReflexCenter.hook(QWidget, 'event', TooltipAgent._register_tooltip(QWidget))
        ReflexCenter.hook(QAbstractScrollArea, 'event', TooltipAgent._register_tooltip(QAbstractScrollArea))
