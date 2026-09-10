# -*- coding: utf-8 -*-
"""屏幕贴图 / 准星覆盖小工具（Windows）

无边框 + 全透明 + 置顶窗口：加载 PNG/JPG 贴图，或用内置准星；
支持贴边（左上/右上/左下/右下）与屏幕居中，可鼠标穿透。
"""
import ctypes
import json
import os
import sys

from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtGui import QColor, QIcon, QPainter, QPen, QPixmap
from PyQt5.QtWidgets import (QActionGroup, QApplication, QFileDialog, QMenu,
                             QSystemTrayIcon, QWidget)

POS_LABELS = (("tl", "左上"), ("tr", "右上"), ("bl", "左下"),
              ("br", "右下"), ("center", "居中"))
CROSS_COLORS = (("红", "#ff3b30"), ("绿", "#32ff5a"),
                ("青", "#00e5ff"), ("白", "#ffffff"))
OPACITIES = (100, 85, 70, 55, 40)
DEFAULT_MARGIN = 12
DEFAULT_CROSS = 24
MIN_SCALE, MAX_SCALE = 0.05, 20.0
MIN_CROSS, MAX_CROSS = 8, 400


def base_dir():
    """冻结成 exe 后配置放 exe 同级目录（PyInstaller onedir 约定）。"""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


CONFIG_PATH = os.path.join(base_dir(), "overlay_config.json")


def load_config():
    try:
        with open(CONFIG_PATH, encoding="utf-8") as fh:
            cfg = json.load(fh)
        return cfg if isinstance(cfg, dict) else {}
    except Exception:
        return {}


def save_config(cfg):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as fh:
            json.dump(cfg, fh, ensure_ascii=False, indent=2)
    except Exception:
        pass


class Overlay(QWidget):
    """贴图/准星覆盖窗：右键菜单或托盘图标操作，滚轮缩放，左键拖动。"""

    def __init__(self, config=None):
        super().__init__(None)
        cfg = dict(config or {})
        self.config = cfg
        self.scale = float(cfg.get("scale") or 1.0)
        self.margin = int(cfg.get("margin") or DEFAULT_MARGIN)
        self.mode = cfg.get("mode") or "center"
        self.cross_color = cfg.get("cross_color") or "红"
        self.cross_size = int(cfg.get("cross_size") or DEFAULT_CROSS)
        self.top = bool(cfg.get("top", True))
        self.click_through = bool(cfg.get("click_through", False))
        self.pixmap = None
        self._drag = None

        flags = Qt.FramelessWindowHint | Qt.Tool | Qt.WindowDoesNotAcceptFocus
        if self.top:
            flags |= Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setWindowTitle("屏幕贴图 / 准星")
        self.setWindowOpacity(float(cfg.get("opacity") or 1.0))

        path = cfg.get("image") or ""
        if not (path and self.load_image(path, save=False)):
            self._fit_to_content()
        self.menu = self._build_menu()
        self.tray = self._build_tray()
        self.place()

    # ---------- 内容 ----------
    def load_image(self, path, save=True):
        pm = QPixmap(path)
        if pm.isNull():
            return False
        self.pixmap = pm
        self._fit_to_content()
        self.place()
        if save:
            self._save()
        return True

    def use_crosshair(self):
        self.pixmap = None
        self._fit_to_content()
        self.place()
        self.update()
        self._save()

    def _fit_to_content(self):
        if self.pixmap is not None:
            self.resize(max(1, round(self.pixmap.width() * self.scale)),
                        max(1, round(self.pixmap.height() * self.scale)))
        else:
            self.resize(self.cross_size, self.cross_size)

    # ---------- 位置 ----------
    def place(self, mode=None):
        """按模式贴到当前所在屏幕的角/中心；free 模式恢复拖动坐标。"""
        if mode:
            self.mode = mode
        if self.mode == "free":
            pos = self.config.get("pos") or []
            if len(pos) == 2 and self._on_any_screen(int(pos[0]), int(pos[1])):
                self.move(int(pos[0]), int(pos[1]))
                return
            self.mode = "center"  # 屏外坐标（拔过显示器）→ 回到居中

        geo = self._screen_geo()
        w, h = self.width(), self.height()
        if self.mode == "center":
            x = geo.x() + (geo.width() - w) // 2
            y = geo.y() + (geo.height() - h) // 2
        else:
            x = geo.left() + self.margin if self.mode in ("tl", "bl") \
                else geo.right() - w + 1 - self.margin
            y = geo.top() + self.margin if self.mode in ("tl", "tr") \
                else geo.bottom() - h + 1 - self.margin
        self.move(x, y)

    def _screen_geo(self):
        """整块屏幕，含任务栏区域——贴边/居中就是屏幕真实的角与中心。"""
        screen = QApplication.screenAt(self.frameGeometry().center()) or QApplication.primaryScreen()
        return screen.geometry()

    def _on_any_screen(self, x, y):
        cx, cy = x + self.width() // 2, y + self.height() // 2
        return any(s.geometry().contains(cx, cy) for s in QApplication.screens())

    def set_mode(self, key):
        self.place(key)
        self._save()

    def set_margin(self, value):
        self.margin = max(0, min(400, int(value)))
        self.place()
        self._save()

    # ---------- 大小 / 外观 ----------
    def zoom(self, factor):
        if self.pixmap is not None:
            self.scale = min(MAX_SCALE, max(MIN_SCALE, self.scale * factor))
        else:
            self.cross_size = int(min(MAX_CROSS, max(MIN_CROSS, self.cross_size * factor + 0.5)))
        self._fit_to_content()
        self.place()
        self.update()

    def set_cross_color(self, name):
        self.cross_color = name
        self.update()
        self._save()

    def native_size(self):
        """恢复到图片原生大小：4x4 的图就占 4x4 个屏幕像素。"""
        if self.pixmap is not None:
            # 高 DPI 屏上 Qt 按逻辑像素算，除以 dpr 才对得上物理像素
            self.scale = 1.0 / max(1.0, float(self.devicePixelRatioF()))
        else:
            self.cross_size = DEFAULT_CROSS  # 准星没有原生尺寸，回默认
        self._fit_to_content()
        self.place()
        self.update()

    def set_opacity(self, value):
        self.setWindowOpacity(max(0.1, min(1.0, float(value))))
        self._save()

    # ---------- 置顶 / 鼠标穿透 ----------
    def set_top(self, on):
        self.top = bool(on)
        was_visible = self.isVisible()
        self.setWindowFlag(Qt.WindowStaysOnTopHint, self.top)  # 会重建原生窗口
        if was_visible:
            self.show()
        self.apply_native()
        self._save()

    def set_click_through(self, on):
        self.click_through = bool(on)
        self.apply_native()
        self._save()

    def apply_native(self):
        """Windows 原生层：强制置顶 + 鼠标穿透（透明窗口默认已是 layered）。"""
        if sys.platform != "win32":
            return
        GWL_EXSTYLE, WS_EX_LAYERED, WS_EX_TRANSPARENT = -20, 0x80000, 0x20
        HWND_TOPMOST, HWND_NOTOPMOST = -1, -2
        SWP_NOSIZE_NOMOVE_NOACTIVATE = 0x0001 | 0x0002 | 0x0010
        try:
            hwnd = int(self.winId())
            user32 = ctypes.windll.user32
            style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE) | WS_EX_LAYERED
            style = (style | WS_EX_TRANSPARENT) if self.click_through else (style & ~WS_EX_TRANSPARENT)
            user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
            user32.SetWindowPos(hwnd, HWND_TOPMOST if self.top else HWND_NOTOPMOST,
                                0, 0, 0, 0, SWP_NOSIZE_NOMOVE_NOACTIVATE)
        except Exception:
            pass

    def showEvent(self, event):
        super().showEvent(event)
        self.apply_native()

    # ---------- 绘制 ----------
    def paintEvent(self, _event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
        if self.pixmap is not None:
            painter.drawPixmap(self.rect(), self.pixmap)
        else:
            self._paint_crosshair(painter)

    def _paint_crosshair(self, painter):
        w, h = self.width(), self.height()
        cx, cy = w / 2.0, h / 2.0
        color = QColor(dict(CROSS_COLORS)[self.cross_color])
        pen = QPen(color, 1.4)
        pen.setCapStyle(Qt.FlatCap)
        painter.setPen(pen)
        gap = max(2.0, min(w, h) * 0.18)  # 中心留空便于瞄准
        arm = min(w, h) / 2.0 - 1.0
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            painter.drawLine(QPointF(cx + dx * gap, cy + dy * gap),
                             QPointF(cx + dx * arm, cy + dy * arm))
        painter.setBrush(color)
        painter.drawEllipse(QPointF(cx, cy), 1.0, 1.0)

    # ---------- 交互 ----------
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag = event.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self._drag is not None and event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - self._drag)
            self.mode = "free"

    def mouseReleaseEvent(self, _event):
        if self._drag is not None:
            self._drag = None
            self._save()  # 拖动结束落盘一次，避免 moveEvent 逐像素写盘

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if delta:
            self.zoom(1.1 if delta > 0 else 1 / 1.1)

    def contextMenuEvent(self, event):
        self.menu.exec_(event.globalPos())

    def toggle_visible(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()

    def closeEvent(self, event):
        self._save()
        super().closeEvent(event)

    def _save(self):
        self.config.update({
            "image": "" if self.pixmap is None else self.config.get("image", ""),
            "mode": self.mode,
            "margin": self.margin,
            "scale": round(self.scale, 4),
            "cross_color": self.cross_color,
            "cross_size": self.cross_size,
            "top": self.top,
            "click_through": self.click_through,
            "opacity": round(self.windowOpacity(), 2),
            "pos": [self.x(), self.y()],
        })
        save_config(self.config)

    def _do(self, func, *args):
        func(*args)
        self._save()

    # ---------- 菜单 / 托盘 ----------
    def _build_menu(self):
        menu = QMenu(self)
        menu.addAction("载入图片…", self._pick_image)
        menu.addAction("使用内置准星", self.use_crosshair)
        menu.addSeparator()

        pos_menu = menu.addMenu("贴边位置")
        group = QActionGroup(pos_menu)
        group.setExclusive(True)
        for key, label in POS_LABELS:
            action = pos_menu.addAction(label)
            action.setCheckable(True)
            action.setChecked(self.mode == key)
            action.triggered.connect(lambda _checked=False, k=key: self.set_mode(k))
            group.addAction(action)

        menu.addAction("边距 +2", lambda: self._do(self.set_margin, self.margin + 2))
        menu.addAction("边距 -2", lambda: self._do(self.set_margin, self.margin - 2))
        menu.addAction("放大", lambda: self._do(self.zoom, 1.1))
        menu.addAction("缩小", lambda: self._do(self.zoom, 1 / 1.1))
        menu.addAction("原始大小（1:1）", lambda: self._do(self.native_size))

        color_menu = menu.addMenu("准星颜色")
        color_group = QActionGroup(color_menu)
        color_group.setExclusive(True)
        for name, _hex in CROSS_COLORS:
            action = color_menu.addAction(name)
            action.setCheckable(True)
            action.setChecked(self.cross_color == name)
            action.triggered.connect(lambda _checked=False, n=name: self.set_cross_color(n))
            color_group.addAction(action)

        opacity_menu = menu.addMenu("不透明度")
        for pct in OPACITIES:
            opacity_menu.addAction("%d%%" % pct,
                                   lambda _checked=False, p=pct: self.set_opacity(p / 100.0))

        menu.addSeparator()
        self.act_top = menu.addAction("窗口置顶")
        self.act_top.setCheckable(True)
        self.act_top.setChecked(self.top)
        self.act_top.triggered.connect(self.set_top)
        self.act_click = menu.addAction("鼠标穿透")
        self.act_click.setCheckable(True)
        self.act_click.setChecked(self.click_through)
        self.act_click.triggered.connect(self.set_click_through)
        menu.addSeparator()
        menu.addAction("显示 / 隐藏", self.toggle_visible)
        menu.addAction("退出", QApplication.quit)
        return menu

    def _build_tray(self):
        icon = QPixmap(32, 32)
        icon.fill(Qt.transparent)
        painter = QPainter(icon)
        painter.setPen(QPen(QColor("#ff3b30"), 3))
        painter.drawLine(16, 5, 16, 27)
        painter.drawLine(5, 16, 27, 16)
        painter.end()
        tray = QSystemTrayIcon(QIcon(icon), self)
        tray.setToolTip("屏幕贴图 / 准星")
        tray.setContextMenu(self.menu)
        tray.activated.connect(self._on_tray)
        tray.show()
        return tray

    def _on_tray(self, reason):
        if reason in (QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick):
            self.toggle_visible()

    def _pick_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择贴图", "", "图片 (*.png *.jpg *.jpeg *.bmp *.webp)")
        if path:
            self.load_image(path)


def main():
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # 隐藏后仍能从托盘恢复
    cfg = load_config()
    if len(sys.argv) > 1:  # overlay.py 贴图.png 可直接开图
        cfg["image"] = sys.argv[1]
    win = Overlay(cfg)
    win.show()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
