# -*- coding: utf-8 -*-
"""最小自检：贴边/居中/自由定位数学 + 绘制不崩。运行：python test_overlay.py"""
import os
import sys
import tempfile

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import overlay as O  # noqa: E402
from PyQt5.QtCore import Qt  # noqa: E402
from PyQt5.QtGui import QPixmap  # noqa: E402
from PyQt5.QtWidgets import QApplication  # noqa: E402

O.CONFIG_PATH = os.path.join(tempfile.mkdtemp(), "overlay_config.json")
app = QApplication([])

win = O.Overlay({})
win.margin = 10
win.resize(60, 40)
geo = win._screen_geo()

# 定位用整块屏幕（含任务栏），不是 availableGeometry：任务栏不该把窗口顶偏
assert geo == QApplication.primaryScreen().geometry(), (geo, QApplication.primaryScreen().geometry())

cases = (
    ("tl", geo.left() + 10, geo.top() + 10),
    ("tr", geo.right() - 60 + 1 - 10, geo.top() + 10),
    ("bl", geo.left() + 10, geo.bottom() - 40 + 1 - 10),
    ("br", geo.right() - 60 + 1 - 10, geo.bottom() - 40 + 1 - 10),
    ("center", geo.x() + (geo.width() - 60) // 2, geo.y() + (geo.height() - 40) // 2),
)
for mode, expect_x, expect_y in cases:
    win.place(mode)
    assert (win.x(), win.y()) == (expect_x, expect_y), \
        "%s -> (%d,%d) 期望 (%d,%d)" % (mode, win.x(), win.y(), expect_x, expect_y)

# 自由模式恢复拖动坐标；屏外坐标回落到居中
win.config["pos"] = [123, 456]
win.place("free")
assert (win.x(), win.y()) == (123, 456), (win.x(), win.y())
win.config["pos"] = [-99999, -99999]
win.place("free")
assert win.mode == "center", win.mode

# 准星模式：缩放改准星尺寸，中心模式仍居中
win.place("center")
win._fit_to_content()  # 复位到准星尺寸（前面手工 resize 过）
before = win.width()
win.zoom(2.0)
assert win.width() == before * 2, (before, win.width())
assert (win.x(), win.y()) == (geo.x() + (geo.width() - win.width()) // 2,
                              geo.y() + (geo.height() - win.height()) // 2)

# 贴图模式：窗口尺寸 = 图片尺寸 × 缩放倍数
win.pixmap = QPixmap(40, 20)
win.pixmap.fill()
win.scale = 1.0
win._fit_to_content()
win.place("center")
assert (win.width(), win.height()) == (40, 20), (win.width(), win.height())
win.zoom(1.5)
assert (win.width(), win.height()) == (60, 30), (win.width(), win.height())
win.place("tl")
assert (win.x(), win.y()) == (geo.left() + 10, geo.top() + 10), (win.x(), win.y())

# 菜单项「原始大小（1:1）」：走菜单触发，4x4 的图就是 4x4 个像素
native_action = [a for a in win.menu.actions() if a.text().startswith("原始大小")][0]
win.pixmap = QPixmap(4, 4)
win.pixmap.fill()
win.scale = 3.7
native_action.trigger()
assert (win.width(), win.height()) == (4, 4), (win.width(), win.height())
win.place("center")
win.native_size()
assert (win.x(), win.y()) == (geo.x() + (geo.width() - 4) // 2,
                              geo.y() + (geo.height() - 4) // 2), (win.x(), win.y())
win.pixmap = None
win.native_size()
assert (win.width(), win.height()) == (24, 24), (win.width(), win.height())

# 全局快捷键：文本 → (修饰键, 虚拟键码)
assert O.parse_hotkey("Ctrl+Alt+H") == (0x0002 | 0x0001, 0x48)
assert O.parse_hotkey("ctrl+shift+space") == (0x0002 | 0x0004, 0x20)
assert O.parse_hotkey("F9") == (0, 0x78)
assert O.parse_hotkey("") == (0, 0)

# 载入图片后路径落盘，重启能原样恢复图片与参数
png = os.path.join(tempfile.mkdtemp(), "t.png")
pm = QPixmap(6, 5)
pm.fill(Qt.red)
assert pm.save(png), "测试图片没存下来"
win.pixmap = None
win.config["image"] = ""
win.scale = 1.0
assert win.load_image(png)
assert win.config["image"] == png, win.config["image"]
assert O.load_config()["image"] == png, O.load_config()
rebooted = O.Overlay(O.load_config())
assert rebooted.pixmap is not None, "重启后没恢复上次的图片"
assert (rebooted.width(), rebooted.height()) == (6, 5), (rebooted.width(), rebooted.height())

# 快捷键设置同样落盘
win.set_hotkey("Ctrl+Shift+F9")
assert O.load_config()["hotkey"] == "Ctrl+Shift+F9", O.load_config()

# 菜单「退出」必须先落盘（托盘退出不触发 closeEvent，老版本就丢在这里）
win.mode = "free"
win.move(321, 654)
win.quit_app()
assert O.load_config()["pos"] == [321, 654], O.load_config()

assert not win.grab().isNull(), "绘制失败"

print("OK")
