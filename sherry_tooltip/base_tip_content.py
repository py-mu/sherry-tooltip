# coding=utf-8
"""
    create by pymu
    on 2021/8/10
    at 19:57
"""
import math

from PyQt5.QtWidgets import QWidget


class BaseTipLabel(QWidget):
    """
    tooltip基类 如果需要用custom tooltip 显示的自定义小部件
    则需要继承这个类 例如TooltipLabel
    """
    triangle_width = 10
    triangle_height = 8.66
    label_radius = 4
    top_left, top, top_right, bottom_left, bottom, bottom_right, \
    left_top, left, left_bottom, right_top, right, right_bottom = range(12)
    direct = top

    def setText(self, str_): ...

    def setWordWrap(self, on): ...

    def setDirection(self, direct):
        """
        设置箭头显示的方向

        Set the direction of the arrow.
        """
        self.direct = direct

    def set_triangle_width(self, width):
        """
        设置三角形宽度

        Set triangle width.
        """
        self.triangle_width = width
        self.triangle_height = math.sqrt(width ** 2 - (width / 2) ** 2)
