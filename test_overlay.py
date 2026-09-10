# -*- coding: utf-8 -*-
"""最小自检：贴边/居中/自由定位数学 + 绘制不崩。运行：python test_overlay.py"""
import os
import sys
import tempfile

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import overlay as O  # noqa: E402
from PyQt5.QtGui import QPixmap  # noqa: E402
from PyQt5.QtWidgets import QApplication  # noqa: E402

O.CONFIG_PATH = os.path.join(tempfile.mkdtemp(), "overlay_config.json")
app = QApplication([])

win = O.Overlay({})
win.margin = 10
win.resize(60, 40)
geo = win._screen_geo()

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
assert not win.grab().isNull(), "绘制失败"

print("OK")
