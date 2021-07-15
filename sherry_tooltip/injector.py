# coding=utf-8
"""
    create by pymu
    on 2021/7/15


    反射文件
"""
from PyQt5.QtCore import QEvent, QRect, Qt
from PyQt5.QtWidgets import QWidget, QAbstractScrollArea, QToolTip
from sherry.core.injector import register
from sherry.core.reflex import ReflexCenter


class Injector:
    """反射器"""

    @staticmethod
    def _register_tooltip(obj):
        """替换内置的tooltip样式"""
        primeval_event_function = getattr(obj, 'event')

        def graft(widget, event):
            if event.type() == QEvent.ToolTip and widget.toolTip():
                QToolTip.showText(event.globalPos(), "这是重载后的 tooltip", widget, QRect(),
                                  widget.toolTipDuration())
                return True
            return primeval_event_function(widget, event)

        return graft

    @staticmethod
    @register
    def installer():
        ReflexCenter.hook(QWidget, 'event', Injector._register_tooltip(QWidget))
        ReflexCenter.hook(QAbstractScrollArea, 'event', Injector._register_tooltip(QAbstractScrollArea))

    @staticmethod
    @register
    def install_enter_event():
        primeval_func = getattr(QWidget, "enterEvent")

        def enterEvent(widget, event):
            if not hasattr(widget, 'raw_cursor'):
                ReflexCenter.hook(widget, 'raw_cursor', Qt.ArrowCursor)
            if widget.parent():
                ReflexCenter.hook(widget, 'raw_cursor', widget.parent().cursor())
                if not widget.isEnabled():
                    widget.parent().setCursor(Qt.ForbiddenCursor)
            return primeval_func(widget, event)

        ReflexCenter.hook(QWidget, 'enterEvent', enterEvent)

    @staticmethod
    @register
    def install_leave_event():
        primeval_func = getattr(QWidget, "leaveEvent")

        def leaveEvent(widget, event) -> None:
            if not hasattr(widget, 'raw_cursor'):
                ReflexCenter.hook(widget, 'raw_cursor', Qt.ArrowCursor)
            if widget.parent():
                widget.parent().setCursor(widget.raw_cursor)
            return primeval_func(widget, event)

        ReflexCenter.hook(QWidget, 'leaveEvent', leaveEvent)

    #  设置动态修改属性会重载样式
    @staticmethod
    @register
    def install_set_property():
        primeval_func = getattr(QWidget, "setProperty")

        def setProperty(self, name, value):
            """在属性发生变化时刷新样式(不允许下划线开头)"""
            result = primeval_func(self, name, value)
            self.style().polish(self)
            return result

        ReflexCenter.hook(QWidget, 'setProperty', setProperty)
