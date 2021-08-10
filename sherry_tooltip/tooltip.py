# coding=utf-8
"""
    create by pymu
    on 2021/7/16
    at 16:39
"""
import logging

from PyQt5.QtCore import QPoint, QRect
from PyQt5.QtWidgets import QToolTip, QApplication

from sherry_tooltip.base_tip_dialog import ToolTip


class CustomTooltip:
    """
    自定义的tooltip
    可以更换提示类型的


    ToolTip（QDialog） : tooltip的载体
    TooltipLabel（BaseTipLabel）： tooltip显示的内容（默认是这个）
    BaseTipLabel（QWidget）： tooltip显示的内容基类（如果需要用ToolTip来显示自定义的控件，则需要继承这个基类）

    可以在需要显示的控件中添加自定义属性如：

    class Custom(QPushButton):

        _sherry_tooltip_position = 1  # 指定tooltip显示的位置
        _sherry_tooltip_arrow_direction = 1  # 指定tooltip箭头的方向（0-12）13或者其他为不显示
        _sherry_tooltip_widget = CustomContent(QLabel, BaseTipLabel) # 一般在方法中设定要显示的内容，注意多态的继承先后秩序
                                                                     # 也可以不继承，这个不影响，只是为了约束这个渲染



    custom tooltip, it is Variable.
    """
    tooltip_cls = ToolTip

    # 通过给控件设置属性
    # 改变tooltip的显示内容，方向，位置的
    TOOLTIP_POSITION_KEY = '_sherry_tooltip_position'
    TOOLTIP_WIDGET_KEY = '_sherry_tooltip_widget'
    TOOLTIP_ARROW_DIRECTION_KEY = '_sherry_tooltip_arrow_direction'

    # noinspection SpellCheckingInspection
    @staticmethod
    def showText(pos, text, widget=None, rect=QRect(), msecShowTime=-1):
        """
        instance use ToolTip.instance or new.
        """
        tip_cls = CustomTooltip.tooltip_cls
        instance = tip_cls.instance
        if not instance:
            instance = tip_cls.instance = tip_cls(text, widget, msecShowTime)
        if instance.isVisible():
            if not text:
                instance.hideTip()
                return
        elif text:
            tip_position, tip_arrow_direct, tip_widget = CustomTooltip._get_tip_attr(widget)
            if not id(instance.content_widget) == id(tip_widget):
                if tip_widget:
                    instance.set_label(tip_widget)
                else:
                    instance.reset_label()
            instance.reuseTip(text, msecShowTime)
            instance.setTipRect(widget, rect)
            instance.placeTip(pos, widget)
            instance.setObjectName("qtooltip_label")
            instance.show_(tip_position, tip_arrow_direct)

    @staticmethod
    def _get_tip_attr(obj):
        """获取内联参数"""
        tip_position, tip_arrow_direct, tip_widget = None, None, None
        position_key, direction_key = CustomTooltip.TOOLTIP_POSITION_KEY, CustomTooltip.TOOLTIP_ARROW_DIRECTION_KEY
        if hasattr(obj, direction_key):
            tip_arrow_direct = getattr(obj, direction_key)
        if hasattr(obj, position_key):
            tip_position = getattr(obj, position_key)
            if not 0 <= tip_position <= 12:
                logging.warning('setter object {} ValueError "_sherry_tooltip_position". '
                                'The value should be between 0 and 12, but {}. '
                                'Currently assigned as None.'.format(obj, tip_position))
                tip_position = None
        if hasattr(obj, CustomTooltip.TOOLTIP_WIDGET_KEY):
            tip_widget = getattr(obj, CustomTooltip.TOOLTIP_WIDGET_KEY)
        return tip_position, tip_arrow_direct, tip_widget

    @staticmethod
    def hideText():
        CustomTooltip.showText(QPoint(), "")

    @staticmethod
    def isVisible():
        instance = CustomTooltip.tooltip_cls.instance
        return instance and instance.isVisible()

    @staticmethod
    def text():
        instance = CustomTooltip.tooltip_cls.instance
        return instance.text() if instance else ""

    @staticmethod
    def palette():
        instance = CustomTooltip.tooltip_cls.instance
        if instance:
            return QToolTip.palette()
        return QToolTip.palette()

    @staticmethod
    def setPalette(palette):
        instance = CustomTooltip.tooltip_cls.instance
        if instance:
            instance.setPalette(palette)

    @staticmethod
    def font():
        return QApplication.font("Tooltip")

    @staticmethod
    def setFont(font):
        QApplication.setFont(font, "Tooltip")
