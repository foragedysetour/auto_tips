# auto_tips · seewo 一体机使用指北

一个极简的 Windows 桌面小工具：开机自动弹出一个窗口，用 Markdown 排版的「使用提示」把小字条贴在屏幕上，省去每次口头讲解。

基于 **PyQt5 + markdown2**，单文件源码、单文件 exe，不需要安装 Python 环境即可分发给使用者。

---

## 目录

- [项目简介](#项目简介)
- [功能特性](#功能特性)
- [运行环境](#运行环境)
- [快速开始](#快速开始)
- [内容文件在哪里](#内容文件在哪里)
- [开机自启](#开机自启)
- [打包成 exe](#打包成-exe)
- [Markdown 支持范围](#markdown-支持范围)
- [目录结构](#目录结构)
- [常见问题](#常见问题)
- [已知限制](#已知限制)
- [许可证](#许可证)

---

## 项目简介

「seewo 一体机使用指北」是一个纯展示型窗口：

1. 启动时读取一个 Markdown 文件；
2. 用 `markdown2` 把 Markdown 转成 HTML；
3. 交给 `QTextBrowser` 渲染显示（支持外部链接跳转到默认浏览器）。

窗口本身没有菜单、没有保存按钮，内容全部来自外部 Markdown 文件，所以**改内容不需要改代码、也不需要重新打包**。

程序名 `auto_tips` 取自「自动提示」：开机自启 + 自动展示。

## 功能特性

| 功能 | 说明 |
| --- | --- |
| Markdown 展示 | 读取 `readme.md` 渲染成富文本，支持标题、列表、代码块、脚注等 |
| 窗口居中 | 启动时按屏幕尺寸居中，默认 `800 × 600` |
| 开机自启 | 勾选底部「在开机时显示」，写入当前用户注册表 `Run` 项，无需管理员权限 |
| 一键编辑 | 「编辑显示内容」按钮用系统默认程序打开 Markdown 文件，改完保存即可 |
| 首次自动创建 | 文件不存在时自动生成带默认内容的 `readme.md`，不会空白出错 |
| 免安装分发 | `dist/auto_tips.exe` 为单文件、无控制台窗口，双击即用 |

## 运行环境

- **操作系统**：Windows（依赖 `winreg` 与 `os.startfile`，无法在 Linux / macOS 上运行）
- **Python**：3.12（开发环境为 3.12.10；3.8+ 理论可用，未逐一验证）
- **依赖**：

```text
PyQt5>=5.15.0
markdown2>=2.5.0
```

> 已打包好的使用方只需要 `auto_tips.exe`，无需安装以上任何东西。

## 快速开始

### 从源码运行

```powershell
# 1. 创建虚拟环境
python -m venv .venv

# 2. 激活虚拟环境
.\.venv\Scripts\Activate.ps1

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动
python auto_tips.py
```

用 `cmd` 时激活命令改为 `.\.venv\Scripts\activate.bat`。

### 直接使用 exe

双击 `dist\auto_tips.exe`。首次运行会在文档目录下生成 `auto_tips\readme.md`，点「编辑显示内容」开始写你的提示。

## 内容文件在哪里

程序**不会**读仓库里的这个 `README.md`，它读的是用户「文档」目录下另一个同名文件：

```text
%USERPROFILE%\Documents\auto_tips\readme.md
```

> ⚠️ 注意区分：仓库根目录的 `README.md` 是给开发者看的项目说明；`文档\auto_tips\readme.md` 才是窗口里显示的内容。

路径解析按以下优先级（见 `getMarkdownFilePath()`）：

| 优先级 | 条件 | 实际读取的文件 |
| --- | --- | --- |
| 1 | 环境变量 `AUTO_TIPS_DOC_DIR` 以 `.md` 结尾 | 该文件路径 |
| 2 | 环境变量 `AUTO_TIPS_DOC_DIR` 是目录 | 该目录下的 `readme.md` |
| 3 | 未设置环境变量 | Windows「文档」目录下的 `auto_tips\readme.md` |

「文档」目录通过 `SHGetFolderPathW(CSIDL_PERSONAL)` 获取，因此把文档文件夹移动 / 重定向到 `D:` 盘或 OneDrive 后依然能定位正确。

### 自定义存放位置

```powershell
# 只对当前窗口生效（临时测试用）
$env:AUTO_TIPS_DOC_DIR = "D:\Tips"
python auto_tips.py

# 也可以直接指向某个 .md 文件
$env:AUTO_TIPS_DOC_DIR = "D:\Tips\welcome.md"

# 永久写入用户环境变量（新开的进程才生效）
setx AUTO_TIPS_DOC_DIR "D:\Tips"
```

环境变量支持 `%USERPROFILE%` 这类变量展开和 `~` 写法。目录不存在时程序会自动创建。

## 开机自启

勾选窗口左下角的 **「在开机时显示」** 后：

- 写入注册表 `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run`，值名固定为 `AutoTips`；
- 运行 exe 时写入 `sys.executable`（exe 自身路径）；
- 以源码运行时写入 `"<python.exe>" "<auto_tips.py>"`（带引号，路径含空格也安全）。

取消勾选即删除该值。只写 `HKCU`，不需要管理员权限，也只对当前用户生效。

手动核对：

```powershell
Get-ItemProperty 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run' -Name AutoTips
```

手动删除：

```powershell
Remove-ItemProperty 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run' -Name AutoTips
```

启动时会读取该值并与「当前程序应有的命令」比对，一致才显示为已勾选。**所以移动过 exe 位置后，旧注册表值失效，勾选框会自动回到未勾选状态，重新勾一次即可。**

## 打包成 exe

```powershell
pip install pyinstaller
pyinstaller auto_tips.spec
```

产物为 `dist\auto_tips.exe`。`auto_tips.spec` 的关键配置：

| 配置 | 值 | 含义 |
| --- | --- | --- |
| 单文件模式 | `EXE(... a.binaries, a.datas ...)` 且无 `COLLECT` | 打包成一个 exe，运行时自解压到临时目录 |
| `console` | `False` | 不弹黑色控制台窗口（因此出错时也看不到报错） |
| `icon` | `icon.ico` | exe 图标 |
| `upx` | `True` | 装了 UPX 才会真正压缩，未安装则忽略 |

> `.gitignore` 默认忽略 `*.spec`、`build/`、`dist/`。若要把打包配置一起纳入版本管理，需要给 `auto_tips.spec` 加例外（`!auto_tips.spec`）。

## Markdown 支持范围

`markdown2.markdown(content)` 未传入 `extras`，因此走的是库的默认扩展集：**脚注（footnotes）** 与 **围栏代码块（fenced-code-blocks）**。

- 默认可用：标题、段落、粗体 / 斜体、有序 / 无序列表、引用、链接、图片、行内代码、围栏代码块、脚注、分割线；
- 默认**不可用**：表格（tables）、任务列表（task_list）、删除线（strike）、单换行即换行（break-on-newline）等。

需要更多语法时，修改 `loadMarkdown()` 中的一行即可：

```python
html_content = markdown2.markdown(
    markdown_content,
    extras=["tables", "task_list", "strike", "break-on-newline"],
)
```

## 目录结构

```text
auto_tips/
├─ auto_tips.py        # 主程序，全部逻辑（约 227 行）
├─ auto_tips.spec      # PyInstaller 打包配置
├─ icon.ico            # 窗口 / exe 图标
├─ requirements.txt    # 运行时依赖
├─ build/              # PyInstaller 中间产物（可安全删除）
└─ dist/
   └─ auto_tips.exe    # 打包结果，可直接分发
```

核心类 `AutoTipsApp(QMainWindow)` 的主要方法：

| 方法 | 职责 |
| --- | --- |
| `initUI()` | 构建窗口、`QTextBrowser`、复选框、按钮 |
| `getDefaultDocumentsFolder()` | 调用 `SHGetFolderPathW` 取真实「文档」目录 |
| `getMarkdownFilePath()` | 按优先级解析 Markdown 路径，必要时建目录 |
| `loadMarkdown()` | 读取文件 → `markdown2` 转 HTML → `setHtml()` |
| `getAutoStartCommand()` | 区分脚本 / exe 两种形态拼自启动命令行 |
| `loadAutoStartState()` | 读注册表并同步复选框状态 |
| `toggleAutoStart()` | 勾选 / 取消时写 / 删注册表值 |
| `openMarkdownFile()` | 用默认程序打开 Markdown 文件 |

## 常见问题

**Q：改了 `readme.md`，窗口里却没有变化？**
程序只在启动时读取一次文件，没有监听、也没有刷新按钮。关闭窗口重新打开即可。若需要热更新，可在 `openMarkdownFile()` 后补发信号再调用一次 `loadMarkdown()`，或加一个 `QFileSystemWatcher`。

**Q：中文变成乱码？**
文件必须存为 **UTF-8**。程序以 `encoding='utf-8'` 读取，用记事本另存为 ANSI 会显示乱码或触发「无法加载Markdown文件」提示。

**Q：勾了「在开机时显示」，重启后没弹出？**
依次排查：① 用上面的 `Get-ItemProperty` 确认注册表值存在；② 是否移动过 exe（路径变了会被判定为未勾选）；③ 杀毒 / 安全软件是否拦截了开机启动项；④ 从「任务管理器 → 启动」看是否被禁用。

**Q：双击 exe 没任何反应？**
exe 以 `console=False` 构建，异常不会显示在屏幕上。请先用源码 `python auto_tips.py` 运行，在控制台里看报错（例如缺 `markdown2`、文件被占用等）。

**Q：表格 / 任务列表不渲染？**
见 [Markdown 支持范围](#markdown-支持范围)，需要手动开启对应 `extras` 并重新打包。

**Q：窗口图标不见了？**
`QIcon('icon.ico')` 是相对路径，从其它工作目录启动脚本时找不到图标；打包后的 exe 已把图标嵌入，不受影响。

**Q：本地图片显示不出来？**
内容是通过 `setHtml()` 字符串注入的，没有设置文档基址，相对路径的本地图片可能无法解析。建议在 Markdown 里用 `http(s)://` 图片链接或绝对路径。

## 已知限制

- **仅 Windows**：`winreg`、`os.startfile` 均为 Windows 专有。
- **内容不自动刷新**：一次启动只加载一次 Markdown。
- **自启仅当前用户**：写 `HKCU`，同一台机器换用户登录需要各自勾选。
- **未签名**：exe 没有代码签名，首次运行可能触发 SmartScreen 提示，选择「仍要运行」即可。
- **`QDesktopWidget` 已弃用**：仅用于计算居中位置，当前不影响功能，后续可换成 `QScreen`。
- **`text_browser` 为只读**：窗口内不能编辑，编辑请走「编辑显示内容」按钮。

## 许可证

仓库当前未包含 `LICENSE` 文件。如需对外开源，请自行补充（例如 MIT / Apache-2.0）并在此处注明。
