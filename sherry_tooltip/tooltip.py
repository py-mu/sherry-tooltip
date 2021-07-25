# coding=utf-8
"""
    create by pymu
    on 2021/7/16
    at 16:39
"""

from PyQt5.QtCore import QPoint, QRect, QEvent, QObject, QTimerEvent, QBasicTimer, Qt
from PyQt5.QtGui import QPalette, QFont, QScreen, QPaintEvent, QMouseEvent, QResizeEvent, QKeyEvent, QGuiApplication
from PyQt5.QtWidgets import QWidget, QToolTip, QStyle, QStylePainter, QStyleOptionFrame, \
    QStyleHintReturnMask, QStyleOption, QApplication, QDialog


class ToolTip(QDialog):
    """单例"""
    instance = None
    hideTimer: QBasicTimer
    expireTimer: QBasicTimer
    fadingOut: bool = False

    styleSheetParent: QWidget
    widget: QWidget = QWidget()
    rect: QRect = QRect()
    _text = ""

    def __init__(self, text: str, pos: QPoint, widget: QWidget, msecDisplayTime: int):
        super().__init__(widget, Qt.ToolTip | Qt.BypassGraphicsProxyWidget)
        self.hideTimer = QBasicTimer()
        self.expireTimer = QBasicTimer()
        # self.setForegroundRole(QPalette.ToolTipText)
        # self.setBackgroundRole(QPalette.ToolTipBase)
        # self.setPalette(QToolTip.palette())
        # 给自己发送QEvent::Polish事件，同时递归调用子类的ensurePolished()函数
        self.ensurePolished()
        QApplication.instance().installEventFilter(self)
        # self.setWindowOpacity(self.style().styleHint(QStyle.SH_ToolTipLabel_Opacity, None, self) / 255.0)
        self.setMouseTracking(True)

        self.fadingOut = False
        self.reuseTip(text, msecDisplayTime, pos)
        self.resize(200, 300)

    def text(self):
        """返回文本"""
        return self._text

    def setText(self, text: str):
        """获取文本"""
        self._text = text

    def reuseTip(self, text: str, msecDisplayTime: int, pos: QPoint):
        """复用tip，修改文本，显示时间，显示位置等"""
        self.setText(text)
        self.restartExpireTimer(msecDisplayTime)

    def hideTip(self):
        """隐藏提示框"""
        if not self.hideTimer.isActive():
            self.hideTimer.start(300, self)

    def hideTipImmediately(self):
        """立即隐藏提tip"""
        self.hide()
        # self.deleteLater()
        # ToolTip.instance = None

    def setTipRect(self, widget: QWidget, rect: QRect):
        if not rect.isNull() and widget:
            self.widget = widget
            self.rect = rect

    def restartExpireTimer(self, msecDisplayTime: int):
        time = 10000 + 40 * max(0, len(self.text()) - 100)
        if msecDisplayTime > 0:
            time = msecDisplayTime
        self.expireTimer.start(time, self)
        self.hideTimer.stop()

    def tipChanged(self, pos: QPoint, text: str, obj: QObject) -> bool:
        if ToolTip.instance.text() != text:
            return True
        if obj != self.widget:
            return True
        if not self.rect.isNull():
            return not self.rect.contains(pos)
        return False

    def placeTip(self, pos: QPoint, widget: QWidget):
        """放置tip"""
        screen = self.getTipScreen(pos, widget)

        # if screen:
        #     platformScreen = screen.handle()

    @staticmethod
    def getTipScreen(pos: QPoint, widget: QWidget) -> QScreen:
        """获取提示屏幕"""
        guess = widget.screen() if widget else QGuiApplication.primaryScreen()
        exact = guess.virtualSiblingAt(pos)
        return exact or guess

    def timerEvent(self, event: QTimerEvent) -> None:
        event_time_id = event.timerId()
        if event_time_id == self.hideTimer.timerId() or event_time_id == self.expireTimer.timerId():
            self.hideTimer.stop()
            self.expireTimer.stop()
            self.hideTipImmediately()

    def paintEvent(self, event: QPaintEvent) -> None:
        p = QStylePainter(self)
        opt = QStyleOptionFrame()
        opt.initFrom(self)
        p.drawPrimitive(QStyle.PE_PanelTipLabel, opt)
        p.end()
        super(ToolTip, self).paintEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if not self.rect.isNull():
            pos = event.globalPos()
            if self.widget:
                pos = self.widget.mapFromGlobal(pos)
            if not self.rect.contains(pos):
                self.hideTip()
        super(ToolTip, self).mouseMoveEvent(event)

    def resizeEvent(self, event: QResizeEvent) -> None:
        frameMask = QStyleHintReturnMask()
        option = QStyleOption()
        option.initFrom(self)
        if self.style().styleHint(QStyle.SH_ToolTip_Mask, option, self, frameMask):
            self.setMask(frameMask.region)

        super(ToolTip, self).resizeEvent(event)

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        event_type = event.type()
        if event_type in (QEvent.KeyPress, QEvent.KeyRelease):
            event: QKeyEvent
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
            event: QMouseEvent
            if obj == self.widget and not self.rect.isNull() and not self.rect.contains(event.pos()):
                self.hideTip()
        return False


class CustomTooltip:
    """自定义的tooltip
    可以更换提示类型的
    """
    tooltip_palette = QToolTip.palette()

    # noinspection SpellCheckingInspection
    @staticmethod
    def showText(pos: QPoint, text: str, widget: QWidget = None, rect: QRect = QRect(), msecShowTime: int = -1):
        # instance use ToolTip.instance or new.
        instance: ToolTip = ToolTip.instance
        if not instance:
            instance = ToolTip.instance = ToolTip(text, pos, widget, msecShowTime)
        if instance.isVisible():
            if not text:
                instance.hideTip()
                return
            elif instance.fadingOut:
                localPos = pos
                if widget:
                    localPos = widget.mapFromGlobal(pos)
                if instance.tipChanged(localPos, text, widget):
                    instance.reuseTip(text, msecShowTime, pos)
                    instance.setTipRect(widget, rect)
                    instance.placeTip(pos, widget)
                return
        elif text:
            instance.reuseTip(text, msecShowTime, pos)
            instance.setTipRect(widget, rect)
            instance.placeTip(pos, widget)
            instance.setObjectName("qtooltip_label")
            instance.showNormal()

    @staticmethod
    def hideText():
        CustomTooltip.showText(QPoint(), "")

    @staticmethod
    def isVisible() -> bool:
        return ToolTip.instance and ToolTip.instance.isVisible()

    @staticmethod
    def text() -> str:
        return ToolTip.instance.text() if ToolTip.instance else ""

    @staticmethod
    def palette() -> QPalette:
        return CustomTooltip.tooltip_palette

    @staticmethod
    def setPalette(palette: QPalette):
        CustomTooltip.tooltip_palette = palette
        instance: ToolTip = ToolTip.instance
        if instance:
            instance.setPalette(palette)

    @staticmethod
    def font() -> QFont:
        return QApplication.font("QTipLabel")

    @staticmethod
    def setFont(font: QFont):
        QApplication.setFont(font, "QTipLabel")
