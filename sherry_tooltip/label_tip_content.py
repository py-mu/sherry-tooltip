# coding=utf-8
"""
    create by pymu
    on 2021/8/10
    at 19:59
"""
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPainterPath
from PyQt5.QtWidgets import QLabel, QStylePainter, QStyleOptionFrame, QStyle

from sherry_tooltip.base_tip_content import BaseTipLabel


class TooltipLabel(QLabel, BaseTipLabel):
    """继承的类放在后面, 因为我们主要用的是前面的类"""

    def paintEvent(self, event):
        painter = QStylePainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        opt = QStyleOptionFrame()
        opt.initFrom(self)

        painter.drawPrimitive(QStyle.PE_PanelTipLabel, opt)
        painter.setPen(Qt.NoPen)
        painter.setBrush(opt.palette.color(self.backgroundRole()))

        triangle_height = self.triangle_height
        start_map = {
            self.bottom: self.width() / 2 - self.triangle_width / 2,
            self.bottom_left: self.triangle_width + self.triangle_width,
            self.bottom_right: self.width() - self.triangle_width * 3,
            self.left: self.height() / 2 - self.triangle_width / 2,
            self.left_top: self.triangle_width * 2,
            self.left_bottom: self.height() - self.triangle_width * 3,
        }
        temp = {
            self.top: start_map[self.bottom],
            self.top_left: start_map[self.bottom_left],
            self.top_right: start_map[self.bottom_right],
            self.right: start_map[self.left],
            self.right_top: start_map[self.left_top],
            self.right_bottom: start_map[self.left_bottom],
        }
        start_map.update(temp)
        p_path = []
        # 显示在上面 tips show on top.
        start = start_map.get(self.direct)
        if self.direct in (self.top_left, self.top_right, self.top):
            p_path.append((start, self.height() - self.triangle_width))
            p_path.append((start + self.triangle_width / 2, self.height() - self.triangle_width + triangle_height))
            p_path.append((start + self.triangle_width, self.height() - self.triangle_width))
        # 显示在下面 tips show on bottom.
        elif self.direct in (self.bottom, self.bottom_left, self.bottom_right):
            p_path.append((start, self.triangle_width))
            p_path.append((start + self.triangle_width / 2, self.triangle_width - triangle_height))
            p_path.append((start + self.triangle_width, self.triangle_width))
        # 显示在左边 tips show on left.
        elif self.direct in (self.left, self.left_top, self.left_bottom):
            p_path.append((self.width() - self.triangle_width, start))
            p_path.append((self.width() - self.triangle_width + triangle_height, start + self.triangle_width / 2))
            p_path.append((self.width() - self.triangle_width, start + self.triangle_width))
        # 显示在右边 tips show on right.
        elif self.direct in (self.right, self.right_top, self.right_bottom):
            p_path.append((self.triangle_width, start))
            p_path.append((self.triangle_width - triangle_height, start + self.triangle_width / 2))
            p_path.append((self.triangle_width, start + self.triangle_width))
        else:
            p_path = []

        if p_path:
            painter_path = QPainterPath()
            painter_path.moveTo(*p_path[0])
            for t_path in p_path[1:]:
                painter_path.lineTo(*t_path)
            painter_path.lineTo(*p_path[0])
            painter.drawPath(painter_path)

        return super(TooltipLabel, self).paintEvent(event)
