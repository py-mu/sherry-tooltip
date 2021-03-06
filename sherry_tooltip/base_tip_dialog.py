# coding=utf-8
"""
    create by pymu
    on 2021/8/10
    at 20:01
"""
from typing import Union

from PyQt5.QtCore import QBasicTimer, QRect, Qt, QCoreApplication, QSize, QPoint, QEvent
from PyQt5.QtGui import QFontMetrics, QGuiApplication
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QApplication, QStyleHintReturnMask, QStyleOption, QStyle

from sherry_tooltip.base_tip_content import BaseTipLabel
from sherry_tooltip.label_tip_content import TooltipLabel


class ToolTip(QDialog):
    """单例"""
    instance = None
    hideTimer = QBasicTimer()
    expireTimer = QBasicTimer()
    master = None

    content_widget: BaseTipLabel = None  # Note: 要显示的tip控件
    _content_widget: BaseTipLabel = None
    _content_widget_cls = TooltipLabel
    rect = None
    _text = ""
    tip_pos_widget = ()

    def __init__(self, text, widget, msecDisplayTime):
        super().__init__(widget, Qt.ToolTip | Qt.BypassGraphicsProxyWidget)
        self.place()
        self.configure()
        self.reuseTip(text, msecDisplayTime)

    def place(self):
        """放置布局"""
        self.setLayout(QHBoxLayout())

        self.content_widget = self._content_widget = self._content_widget_cls(self)
        self.layout().addWidget(self.content_widget)

    def set_label(self, obj):
        # 删除控件
        # noinspection PyTypeChecker
        self.content_widget.setParent(None)
        self.layout().removeWidget(self.content_widget)
        self.layout().addWidget(obj)
        self.content_widget = obj

    def is_custom_widget(self):
        return not id(self.content_widget) == id(self._content_widget)

    def reset_label(self):
        if self.is_custom_widget():
            # 删除控件
            # noinspection PyTypeChecker
            self.content_widget.setParent(None)
            self.layout().addWidget(self._content_widget)
            self.content_widget = self._content_widget
            self.content_widget.show()

    def configure(self):
        """配置"""
        self.rect = QRect()
        app = QApplication.instance()  # type: Union[QApplication,  QCoreApplication]
        self.layout().setContentsMargins(*[1] * 4)
        self.content_widget.setObjectName("tooltip_label")
        if hasattr(self.content_widget, 'setWordWrap'):
            self.content_widget.setWordWrap(True)
        self.adjustSize()
        self.content_widget.adjustSize()
        self.hideTimer = QBasicTimer()
        self.expireTimer = QBasicTimer()
        app.installEventFilter(self)
        self.setMouseTracking(True)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlag(Qt.FramelessWindowHint)
        app.setStyleSheet("""
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
        """ + app.styleSheet())

    def text(self):
        """返回文本"""
        return self._text

    def setText(self, text):
        """获取文本, 非自定义控件时设置文本"""
        self._text = text
        if not self.is_custom_widget() and hasattr(self.content_widget, 'setText'):
            self.content_widget.setText(text)

    def reuseTip(self, text, msecDisplayTime):
        """复用tip，修改文本，显示时间，显示位置等"""
        self.setText(text)
        self.restartExpireTimer(msecDisplayTime)

    def show_(self, tip_position=None, tip_arrow_direction=None):
        """
        显示tooltip fixme 显示的过程会出现闪动是因为需要显示，才能知道内容的大小才进行计算

        :param tip_position: 要显示的方位(0-12)
        :param tip_arrow_direction: 显示的箭头类型(0-12/其它无箭头)
        """
        self.setVisible(True)
        self.updateSize()
        self._placeTip(tip_position, tip_arrow_direction)

    def hideTip(self):
        """隐藏提示框"""
        if not self.hideTimer.isActive():
            self.hideTimer.start(300, self)

    def hideTipImmediately(self):
        """立即隐藏提tip"""
        self.hide()

    def updateSize(self):
        """更新位置及大小"""
        if self.is_custom_widget():
            return
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

    def placeTip(self, pos, widget):
        """
        放置tip, 计算十二个边界，哪边的空位最大就显示在哪一边
        """
        self.tip_pos_widget = pos, widget

    def _get_move_pos(self, tip_position, widget):
        """
        通过计算剩余的边界面积，获得tip显示的最佳位置，
        如控件太靠右了，那他的tip应该显示在左边
        同理， 其他位置也是一样的

        首先获取tip的的长宽，（tip_height, tip_width） 用于比较其显示的位置会占用多大的地方
        其次生成一个对应各个方向的12向标记， 如top_left, top, top_right, bottom_left（代表箭头显示的位置）

        """
        top_left, top, top_right, bottom_left, bottom, bottom_right, \
        left_top, left, left_bottom, right_top, right, right_bottom = range(12)
        # tip 的长宽
        tip_height = self.content_widget.height()
        tip_width = self.content_widget.width()
        # 三角形的边长
        triangle_width = 0
        if hasattr(self.content_widget, 'triangle_width'):
            triangle_width = self.content_widget.triangle_width

        # 如果tip比控件箭头还要小，则需要使用widget的长宽作为比较，（注意这里有一个陷阱）
        # 如果你是需要显示比箭头还小的tip，那你就需要把这个判断条件去掉
        if tip_height == triangle_width * 2:
            tip_height = widget.height()
            tip_width = widget.width()

        pos = widget.mapToGlobal(widget.pos()) - widget.pos()
        if tip_position == top:
            pos += QPoint(widget.width() / 2 - tip_width / 2, - tip_height)
        elif tip_position == top_left:
            pos += QPoint(- triangle_width, - tip_height)
        elif tip_position == top_right:
            pos += QPoint(widget.width() - tip_width + triangle_width, - tip_height)
        elif tip_position == bottom:
            pos += QPoint(widget.width() / 2 - tip_width / 2, widget.height())
        elif tip_position == bottom_left:
            pos += QPoint(- triangle_width, widget.height())
        elif tip_position == bottom_right:
            pos += QPoint(widget.width() - tip_width + triangle_width, widget.height())
        elif tip_position == right:
            pos += QPoint(widget.width(), - tip_height / 2 + widget.height() / 2)
        elif tip_position == right_top:
            pos += QPoint(widget.width(), - triangle_width)
        elif tip_position == right_bottom:
            pos += QPoint(widget.width(), - tip_height + widget.height() + triangle_width)
        elif tip_position == left:
            pos += QPoint(- tip_width, - tip_height / 2 + widget.height() / 2)
        elif tip_position == left_top:
            pos += QPoint(- tip_width, - triangle_width)
        elif tip_position == left_bottom:
            pos += QPoint(- tip_width, - tip_height + widget.height() + triangle_width)
        return pos

    @staticmethod
    def get_tip_surplus_area(widget, screen):
        """获取tip剩余可展示的面积"""
        max_y, max_x = screen.size().height(), screen.size().width()
        global_pos = widget.mapToGlobal(widget.pos())
        x, y = global_pos.x(), global_pos.y()
        top_left, top, top_right, bottom_left, bottom, bottom_right, \
        left_top, left, left_bottom, right_top, right, right_bottom = range(12)
        # 以tip显示结果作为key
        area = {
            left_top: x * (y + widget.height()),  # 左边往上
            left_bottom: x * (max_y - y),  # 左边往下
            top_right: (x + widget.width()) * y,  # 上边往左
            top_left: (max_x - x) * y,  # 上边往右
            right_top: (max_x - x - widget.width()) * (y + widget.height()),  # 右边往上
            right_bottom: (max_x - x - widget.width()) * (max_y - y),  # 右边往下
            bottom_left: (max_y - y - widget.height()) * (max_x - x),  # 下边往右
            bottom_right: (max_y - y - widget.height()) * (x + widget.width()),  # 下边往左
            top: (max_x * y),
            bottom: ((max_y - y - widget.height()) * max_x),
            left: (x * max_y),
            right: ((max_x - x - widget.width()) * max_y)
        }
        # 排序得到空间最大的区域
        return sorted(area.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)[0]

    def _placeTip(self, tip_position=None, tip_arrow_direction=None):
        """
        在显示之后再进行移动

        Calculate the best display position.
        """
        pos, widget = self.tip_pos_widget
        screen = QGuiApplication.primaryScreen()
        # 排序得到空间最大的区域
        area_tag, area_size = self.get_tip_surplus_area(widget, screen)
        area_tag = tip_position or area_tag
        # 如果可显示的区域小于tip弹窗的面积（即widget太大）则使用随鼠标的位置
        if widget.parent() and area_size > self.width() * self.height():
            pos = self._get_move_pos(area_tag, widget)
        else:
            screen = screen.geometry()
            area_tag = 13
            pos += QPoint(5, -21)
            if pos.x() + self.width() > screen.x() + screen.width():
                pos.setX(pos.x() - self.width())
            if pos.y() + self.height() > screen.y() + screen.height():
                pos.setY(pos.y() - self.height())
            if pos.y() < screen.y():
                pos.setY(screen.y())
        if hasattr(self.content_widget, 'setDirection'):
            self.content_widget.setDirection(tip_arrow_direction or area_tag)
        self.move(pos)

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
