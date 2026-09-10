# -*- mode: python ; coding: utf-8 -*-

# 排掉本工具用不到的 Qt 组件（软件 OpenGL/ANGLE、Qml/Quick、Network 等），
# 以及除中文外的 Qt 翻译。改这里之后必须真跑一次 exe 确认能起来、能画出来。
EXCLUDED = (
    'opengl32sw', 'd3dcompiler', 'libGLESv2', 'libEGL',
    'Qt5Quick', 'Qt5Qml', 'Qt5Network', 'Qt5DBus', 'Qt5Svg', 'Qt5WebSockets',
    'qminimal', 'qoffscreen', 'qwebgl',
    'qsvg', 'qtiff', 'qicns', 'qtga', 'qwbmp',
    'libcrypto', 'libssl',
)


def keep(entry):
    name = entry[0].replace('\\', '/')
    if '/translations/' in name and 'zh_CN' not in name:
        return False
    return not any(key in name for key in EXCLUDED)


a = Analysis(
    ['overlay.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
a.binaries = [e for e in a.binaries if keep(e)]
a.datas = [e for e in a.datas if keep(e)]

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='screen-overlay',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico',
    contents_directory='.',  # 依赖跟 exe 同级，配置按 dirname(sys.executable) 解析
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='screen-overlay',
)
