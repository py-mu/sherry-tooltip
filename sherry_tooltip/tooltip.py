# coding=utf-8
"""
    create by pymu
    on 2021/7/16
    at 16:39
"""
import math
from typing import Union

from PyQt5.QtCore import QPoint, QRect, QEvent, QBasicTimer, Qt, QSize, QCoreApplication
from PyQt5.QtGui import QGuiApplication, \
    QFontMetrics, QPainter, QPainterPath
from PyQt5.QtWidgets import QToolTip, QStyle, QStylePainter, QStyleOptionFrame, \
    QStyleHintReturnMask, QStyleOption, QApplication, QDialog, QHBoxLayout, QLabel


class TooltipLabel(QLabel):
    triangle_width = 10
    triangle_height = 8.66
    label_radius = 4
    top_left, top, top_right, bottom_left, bottom, bottom_right, \
    left_top, left, left_bottom, right_top, right, right_bottom = range(12)
    direct = top

    def setDirection(self, direct):
        self.direct = direct

    def set_triangle_width(self, width):
        self.triangle_width = width
        self.triangle_height = math.sqrt(width ** 2 - (width / 2) ** 2)

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


class ToolTip(QDialog):
    """单例"""
    instance = None
    hideTimer = QBasicTimer()
    expireTimer = QBasicTimer()
    fadingOut = False
    master = None
    widget = None
    rect = QRect()
    _text = ""
    tip_pos_widget = ()

    def __init__(self, text, widget, msecDisplayTime):
        super().__init__(widget, Qt.ToolTip | Qt.BypassGraphicsProxyWidget)
        self.place()
        self.configure()
        self.reuseTip(text, msecDisplayTime)

    def place(self):
        """放置布局"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(*[1] * 4)
        self.widget = TooltipLabel(self)
        layout.addWidget(self.widget)
        self.setLayout(layout)

    def configure(self):
        """配置"""
        app = QApplication.instance()  # type: Union[QApplication,  QCoreApplication]
        self.widget.setObjectName("tooltip_label")
        self.widget.setWordWrap(True)
        self.adjustSize()
        self.widget.adjustSize()
        self.hideTimer = QBasicTimer()
        self.expireTimer = QBasicTimer()
        app.installEventFilter(self)
        self.setMouseTracking(True)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.fadingOut = False
        app.setStyleSheet(app.styleSheet() + """
        ToolTip{border: 1px solid red;}
        ToolTip TooltipLabel#tooltip_label{
            border: none;
            background: #303133;
            padding-left: 10px;
            padding-top: 8px;
            padding-right: 7px;
            padding-bottom: 9px;
            margin: 10px;
            font-size: 12px;
            line-height: 1.2;
            font-weight: bold;
            color: #fefefe;
            /* font: bold italic 18px "Microsoft YaHei"; */
        }
        """)

    def text(self):
        """返回文本"""
        return self._text

    def setText(self, text):
        """获取文本"""
        self._text = text
        self.widget.setText(text)

    def reuseTip(self, text, msecDisplayTime):
        """复用tip，修改文本，显示时间，显示位置等"""
        self.setText(text)
        self.restartExpireTimer(msecDisplayTime)

    def showNormal(self):
        self.setVisible(True)
        self.updateSize()
        self._placeTip()

    def hideTip(self):
        """隐藏提示框"""
        if not self.hideTimer.isActive():
            self.hideTimer.start(300, self)

    def hideTipImmediately(self):
        """立即隐藏提tip"""
        self.hide()

    def updateSize(self):
        """更新位置及大小"""
        fm = QFontMetrics(self.font())
        sh = self.sizeHint()
        extra = QSize(1, 0)
        if fm.descent() == 2 and fm.ascent() >= 11:
            extra.setHeight(extra.height() + 1)
        self.resize(sh + extra)

    def setTipRect(self, widget, rect):
        if not rect.isNull() and widget:
            self.master = widget
            self.rect = rect

    def restartExpireTimer(self, msecDisplayTime):
        time_ = 10000 + 40 * max(0, len(self.text()) - 100)
        if msecDisplayTime > 0:
            time_ = msecDisplayTime
        self.expireTimer.start(time_, self)
        self.hideTimer.stop()

    def tipChanged(self, pos, text, obj):
        print(self.text(), text)
        if self.text() != text:
            return True
        if obj != self.master:
            return True
        if not self.rect.isNull():
            return not self.rect.contains(pos)
        return False

    def placeTip(self, pos, widget):
        """
        放置tip, 计算十二个边界，哪边的空位最大就显示在哪一边
        """
        self.tip_pos_widget = pos, widget

    def _placeTip(self):
        """
        在显示之后再进行移动

        Calculate the best display position.
        """
        pos, widget = self.tip_pos_widget
        screen = QGuiApplication.primaryScreen()
        max_y, max_x = screen.size().height(), screen.size().width()
        global_pos = widget.mapToGlobal(widget.pos())
        x, y = global_pos.x(), global_pos.y()
        top_left, top, top_right, bottom_left, bottom, bottom_right, \
        left_top, left, left_bottom, right_top, right, right_bottom = range(12)
        # 以tip显示结果作为key
        area = {
            # left_top: x * (y + widget.height()),  # 左边往上
            # left_bottom: x * (max_y - y),  # 左边往下
            # top_right: (x + widget.width()) * y,  # 上边往左
            # top_left: (max_x - x) * y,  # 上边往右
            # right_top: (max_x - x - widget.width()) * (y + widget.height()),  # 右边往上
            # right_bottom: (max_x - x - widget.width()) * (max_y - y),  # 右边往下
            # bottom_left: (max_y - y - widget.height()) * (max_x - x),  # 下边往右
            # bottom_right: (max_y - y - widget.height()) * (x + widget.width()),  # 下边往左
            # top: (max_x * y),
            bottom: ((max_y - y - widget.height()) * max_x),
            # left: (x * max_y),
            # right: ((max_x - x - widget.width()) * max_y)
        }
        # 排序得到空间最大的区域
        area_tag, area_size = sorted(area.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)[0]
        if widget.parent() and area_size > self.width() * self.height():
            # 相对坐标
            tooltip_height = self.widget.height()
            tooltip_width = self.widget.width()
            if tooltip_height == self.widget.triangle_width * 2:
                tooltip_height = widget.height()
                tooltip_width = widget.width()

            pos = widget.mapToGlobal(widget.pos()) - widget.pos()
            if area_tag == top:
                pos += QPoint(widget.width() / 2 - tooltip_width / 2, - tooltip_height)
            elif area_tag == top_left:
                pos += QPoint(- self.widget.triangle_width, - tooltip_height)
            elif area_tag == top_right:
                pos += QPoint(widget.width() - tooltip_width + self.widget.triangle_width, - tooltip_height)
            elif area_tag == bottom:
                pos += QPoint(widget.width() / 2 - tooltip_width / 2, widget.height())
            elif area_tag == bottom_left:
                pos += QPoint(- self.widget.triangle_width, widget.height())
            elif area_tag == bottom_right:
                pos += QPoint(widget.width() - tooltip_width + self.widget.triangle_width, widget.height())
            elif area_tag == right:
                pos += QPoint(widget.width(), - tooltip_height / 2 + widget.height() / 2)
            elif area_tag == right_top:
                pos += QPoint(widget.width(), - self.widget.triangle_width)
            elif area_tag == right_bottom:
                pos += QPoint(widget.width(), - tooltip_height + widget.height() + self.widget.triangle_width)
            elif area_tag == left:
                pos += QPoint(- tooltip_width, - tooltip_height / 2 + widget.height() / 2)
            elif area_tag == left_top:
                pos += QPoint(- tooltip_width, -self.widget.triangle_width)
            elif area_tag == left_bottom:
                pos += QPoint(- tooltip_width, - tooltip_height + widget.height() + self.widget.triangle_width)
        else:
            screen = screen.geometry()
            area_tag = 13
            pos += QPoint(5, -21)
            if pos.x() + self.width() > screen.x() + screen.width():
                pos.setX(pos.x() - 4 + self.width())
            if pos.y() + self.height() > screen.y() + screen.height():
                pos.setY(pos.y() - 24 + self.height())
            if pos.y() < screen.y():
                pos.setY(screen.y())
            if pos.x() + self.width() > screen.x() + screen.width():
                pos.setX(screen.x() + screen.width() - self.width())
            if pos.x() < screen.x():
                pos.setX(screen.x())
            if pos.y() + self.height() > screen.y() + screen.height():
                pos.setY(screen.y() + screen.height() - self.height())
        self.widget.setDirection(area_tag)
        self.move(pos)

    @staticmethod
    def getTipScreen(pos, widget):
        """获取提示屏幕"""
        guess = widget.screen() if widget else QGuiApplication.primaryScreen()
        exact = guess.virtualSiblingAt(pos)
        return exact or guess

    def timerEvent(self, event):
        """
        close delay.
        """
        event_time_id = event.timerId()
        if event_time_id == self.hideTimer.timerId() or event_time_id == self.expireTimer.timerId():
            self.hideTimer.stop()
            self.expireTimer.stop()
            self.hideTipImmediately()

    def mouseMoveEvent(self, event):
        """
        listen move event, hide tooltip.
        """
        if not self.rect.isNull():
            pos = event.globalPos()
            if self.master:
                pos = self.master.mapFromGlobal(pos)
            if not self.rect.contains(pos):
                self.hideTip()
        super(ToolTip, self).mouseMoveEvent(event)

    def resizeEvent(self, event):
        """
        build tooltip size, get from qss stylesheet.
        """
        frameMask = QStyleHintReturnMask()
        option = QStyleOption()
        option.initFrom(self)
        if self.style().styleHint(QStyle.SH_ToolTip_Mask, option, self, frameMask):
            self.setMask(frameMask.region)

        super(ToolTip, self).resizeEvent(event)

    def eventFilter(self, obj, event):
        """
        hook some Qt event when it hided.
        """
        event_type = event.type()
        if event_type in (QEvent.KeyPress, QEvent.KeyRelease):
            key = event.key()
            if key < Qt.Key_Shift or key > Qt.Key_ScrollLock:
                self.hideTipImmediately()
        elif event_type == QEvent.Leave:
            self.hideTip()
        elif event_type in (QEvent.WindowActivate, QEvent.FocusIn):
            return False
        elif event_type == QEvent.WindowDeactivate:
            if obj is not self:
                return False
            self.hideTipImmediately()
        elif event_type == QEvent.FocusOut:
            if obj is not self.windowHandle():
                return False
            self.hideTipImmediately()
        elif event_type == QEvent.Close:
            if obj is not self.windowHandle() and obj is not self:
                self.hideTipImmediately()
        elif event_type in (QEvent.MouseButtonPress,
                            QEvent.MouseButtonRelease,
                            QEvent.MouseButtonDblClick,
                            QEvent.Wheel):
            self.hideTipImmediately()
        elif event_type == QEvent.MouseMove:
            if obj == self.master and not self.rect.isNull() and not self.rect.contains(event.pos()):
                self.hideTip()
        return False


class CustomTooltip:
    """
    自定义的tooltip
    可以更换提示类型的

    custom tooltip, it is Variable.
    """
    tooltip_palette = QToolTip.palette()

    # noinspection SpellCheckingInspection
    @staticmethod
    def showText(pos, text, widget=None, rect=QRect(), msecShowTime=-1):
        """
        instance use ToolTip.instance or new.
        """
        instance = ToolTip.instance
        if not instance:
            instance = ToolTip.instance = ToolTip(text, widget, msecShowTime)
        if instance.isVisible():
            if not text:
                instance.hideTip()
                return
        elif text:
            instance.reuseTip(text, msecShowTime)
            instance.setTipRect(widget, rect)
            instance.placeTip(pos, widget)
            instance.setObjectName("qtooltip_label")
            instance.showNormal()

    @staticmethod
    def hideText():
        CustomTooltip.showText(QPoint(), "")

    @staticmethod
    def isVisible():
        return ToolTip.instance and ToolTip.instance.isVisible()

    @staticmethod
    def text():
        return ToolTip.instance.text() if ToolTip.instance else ""

    @staticmethod
    def palette():
        return CustomTooltip.tooltip_palette

    @staticmethod
    def setPalette(palette):
        CustomTooltip.tooltip_palette = palette
        instance = ToolTip.instance
        if instance:
            instance.setPalette(palette)

    @staticmethod
    def font():
        return QApplication.font("Tooltip")

    @staticmethod
    def setFont(font):
        QApplication.setFont(font, "Tooltip")
