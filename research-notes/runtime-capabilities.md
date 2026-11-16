# 同类框架的常用运行时能力

只记录一手资料里的名称、它解决的问题，以及 gamebot 源码里今天有没有对应物。不决定哪些能力进入这次范围。启动参数从 `.env` 改入 `build_setup()` 是地图上已有的决定，本文不重开。

材料限定为官方文档、官方仓库文档或项目自身源码。起始集合是 Airtest、SikuliX、pywinauto、PyAutoGUI、Playwright Python、OpenCV `matchTemplate`、AutoHotkey v2。Poco 有独立官方文档，且与 Airtest 同属一套游戏界面自动化材料，因此单独记一节 UI 树。OpenCV 这一页是找图原语，不是整套桌面自动化框架。

「常见」在这里的意思是：同一项在多份上述文档里都有命名的运行时入口。只在一份文档里出现的，仍然记下，但不写成全体都有。

## gamebot 今天（源码）

对照基线是 `src/gamebot` 与 `src/gamebot/protocols`，当前工作树提交 `adfdf2c`。

| 已有实现 | 源码 |
| --- | --- |
| DAG：`Group` / `Node`，节点 `(ctx) -> bool`，`ctx.pkg` / `ctx.get` / `ctx.set`；CLI 按 `NUMBER` 循环 | `src/gamebot/dag.py`，`src/gamebot/cli.py` |
| 真实鼠键：移动、左键、右键、单键、`typewrite` | `src/gamebot/protocols/pointer_input.py`，`src/gamebot/protocols/keyboard_input.py`，`src/gamebot/handlers/packages/pyauto/pointer_direct.py` |
| 发给窗口的截图、鼠键、键盘，以及焦点 / 还原 / 最小化 | `src/gamebot/handlers/packages/win32/backend.py`，`src/gamebot/handlers/packages/win32/capture.py` |
| 按窗口标题或当前前台窗口绑定 hwnd；客户区坐标转屏幕坐标 | `src/gamebot/handlers/packages/win32/_bound.py`，`Win32CaptureHandler.client_to_screen` |
| OpenCV 模板匹配，以及截图后查找并点击 | `src/gamebot/handlers/packages/opencv/_cv.py`，`src/gamebot/handlers/packages/opencv/matcher.py` |
| 剪贴板读写 | `src/gamebot/protocols/clipboard_access.py`，`src/gamebot/handlers/packages/pyperclip/clipboard.py` |
| 本机 dashboard：DAG 图、快照、SSE | `src/gamebot/dashboard/server.py`，`src/gamebot/cli.py` |
| 浏览器只有契约：`goto`、`click_selector`。文档写明首期是 stub，实现留到后续 `playwright_chromium` 包。`handlers/packages` 下没有该包 | `src/gamebot/protocols/browser_automation.py` |

`TemplateMatcher.find` 的参数是整张画面、模板路径和 `sens`（默认 `0.8`）。协议里没有区域、超时、双击、拖拽、滚轮、组合键、OCR、像素色、断言或热键监听。

## 1. 截图

解决的问题：拿到当前屏幕、窗口或页面画面，供找图、记录或人工查看。

| 资料中的名称 | 出处 |
| --- | --- |
| `snapshot`：对目标设备截图并保存到文件，返回屏幕文件名与分辨率。支持 Android、iOS、Windows。`msg` 会显示在报告页 | [Airtest `snapshot`](https://airtest.readthedocs.io/en/latest/_modules/airtest/core/api.html)；README 将 `snapshot` 列为完全支持的模拟输入 API：[README_MORE](https://airtest.readthedocs.io/en/latest/README_MORE.html) |
| `screenshot` / `screenshot(region=(left, top, width, height))`：截主屏或一块区域，返回 Pillow 图像，也可存文件 | [PyAutoGUI Screenshot Functions](https://pyautogui.readthedocs.io/en/latest/screenshot.html) |
| `page.screenshot`、`full_page=True`、元素 `locator.screenshot` | [Playwright Screenshots](https://playwright.dev/python/docs/screenshots) |
| SikuliX 的找图与观察都在 `Region` 这块屏幕矩形上进行；文档把 `Screen` 定为继承 `Region` 的物理显示器 | [SikuliX Region](https://sikulix-2014.readthedocs.io/en/latest/region.html) |
| OpenCV 教程的输入是已经读入的图像，`matchTemplate` 本身不截屏 | [OpenCV Template Matching](https://docs.opencv.org/4.x/d4/dc6/tutorial_py_template_matching.html) |

gamebot 今天有：`Win32CaptureHandler.capture` 用 `BitBlt` 截已绑定窗口的客户区；`Win32BackendHandler.capture` 用 `WM_PRINT` 再 `BitBlt`。两者都返回 BGR 的 `numpy` 数组。没有「截整块主屏并保存成报告图片」的协议方法。Playwright 那种页面截图没有实现，浏览器协议里也没有截图方法。

## 2. 模板匹配找图

解决的问题：不依赖控件句柄，用一张小图在画面里定位按钮、图标或游戏物件。

| 资料中的名称 | 出处 |
| --- | --- |
| `cv.matchTemplate`：把模板滑过图像，按 `TemplateMatchModes` 写出每个位置的比较值。文档给出六种方法：`TM_SQDIFF`、`TM_SQDIFF_NORMED`、`TM_CCORR`、`TM_CCORR_NORMED`、`TM_CCOEFF`、`TM_CCOEFF_NORMED`。最好位置用 `minMaxLoc`（平方差取最小，其余取最大）。可选 `mask` | [教程](https://docs.opencv.org/4.x/d4/dc6/tutorial_py_template_matching.html)，[API](https://docs.opencv.org/4.x/df/dfb/group__imgproc__object.html) |
| `Template`：作为 `touch` / `swipe` / `wait` / `exists` 的图片目标。字段包括 `threshold`、`target_pos`（点模板上的哪个位置，默认 5）、`rgb`（是否用 RGB 三通道校验）、`scale_max` / `scale_step`（多尺度模板匹配） | [airtest.core.cv.Template](https://airtest.readthedocs.io/en/latest/all_module/airtest.core.cv.html) |
| `Region.find`：在区域内找图像或文字，返回相似度大于下限的最佳 `Match`；找不到抛 `FindFailed`。未设置时默认最小相似度 `0.7`。文档建议分数高于 `0.85` 或 `0.9`，以减少误匹配 | [SikuliX Region](https://sikulix-2014.readthedocs.io/en/latest/region.html) |
| `locateOnScreen` / `locateCenterOnScreen` / `locate`：返回第一个匹配的 `(left, top, width, height)` 或中心点。`confidence` 需要安装 OpenCV。`grayscale=True` 牺牲颜色换速度。找不到时抛 `ImageNotFoundException`（自 0.9.41 起） | [PyAutoGUI Screenshot Functions](https://pyautogui.readthedocs.io/en/latest/screenshot.html) |
| `ImageSearch`：在矩形区域内搜索图像，找到则返回左上角坐标。`*n` 允许每个像素 RGB 各偏离 n 个色阶（0–255，默认 0）。`*TransN` 指定一种颜色可以匹配任意屏幕颜色。文档写明用途包括 picture buttons、icons、web page links、game objects | [AutoHotkey v2 ImageSearch](https://www.autohotkey.com/docs/v2/lib/ImageSearch.htm) |

gamebot 今天有：`diff_image` 把画面转成灰度后调用 `cv2.matchTemplate(..., cv2.TM_CCOEFF_NORMED)`，再用 `np.where(result >= sens)`。`OpenCVMatcherHandler.find` 在所有不低于 `sens` 的位置里 `random.choice` 一个，返回 `MatchResult`（左上角与右下角）。没有 `mask`，没有多尺度，没有 `rgb` 三通道校验开关，也没有 `minMaxLoc` 取单一最优峰。

## 3. 搜索区域、全部匹配、等待与消失

解决的问题：缩小搜索范围、处理重复图标、以及画面还没出现时不要只查一次。

| 资料中的名称 | 出处 |
| --- | --- |
| 教程「Template Matching with Multiple Objects」：`TM_CCOEFF_NORMED` 加阈值（示例 `0.8`），`np.where` 取出全部位置。`minMaxLoc` 只给出一个极值 | [OpenCV 教程](https://docs.opencv.org/4.x/d4/dc6/tutorial_py_template_matching.html) |
| `exists`：找不到返回 `False`，找到返回坐标。`wait`：按间隔重试直到超时，超时抛 `TargetNotFoundError`，默认超时是 `ST.FIND_TIMEOUT`。`find_all`：返回全部出现，每项含 `result`、`rectangle`、`confidence`。`loop_find` 的参数里有 `timeout`、`threshold`、`interval` | [Airtest core API 源码页](https://airtest.readthedocs.io/en/latest/_modules/airtest/core/api.html)，[`loop_find`](https://airtest.readthedocs.io/en/latest/all_module/airtest.core.cv.html) |
| `find` 只查一次。`findAll` 返回全部 `Match`。`exists` 找不到返回 `None`。`wait` 等到出现或超时。`waitVanish` 等到消失。`onAppear` / `onVanish` / `onChange` 注册视觉事件，`observe` 开始观察，`stopObserver` 停止。`onChange` 看的是区域内像素内容变化 | [SikuliX Region](https://sikulix-2014.readthedocs.io/en/latest/region.html) |
| `locateAllOnScreen` / `locateAll` 返回所有位置。`region=(left, top, width, height)` 只搜一块 | [PyAutoGUI Screenshot Functions](https://pyautogui.readthedocs.io/en/latest/screenshot.html) |
| `ImageSearch` 的 `X1,Y1,X2,Y2` 就是搜索矩形 | [ImageSearch](https://www.autohotkey.com/docs/v2/lib/ImageSearch.htm) |
| `Template` 的 `record_pos` 与 `Predictor.get_predict_area`：用录制时的相对位置预测屏幕上的搜索范围 | [airtest.core.cv](https://airtest.readthedocs.io/en/latest/all_module/airtest.core.cv.html) |

gamebot 今天有单次 `find`：内部用阈值收集全部命中，但只随机返回其中一个，没有把列表交给调用方。`find` 没有区域参数、超时或重试。没有 `wait` / `exists` / `waitVanish` / `observe` 这些名字。

## 4. 鼠标

解决的问题：点、移、拖、滚画面上的某个位置。

| 资料中的名称 | 出处 |
| --- | --- |
| `touch`（`click` 是别名）：点 `Template` 或绝对坐标；`times` 连点。文档写 `duration` 可用于 Android 与 Windows，`right_click=True` 标注为 Windows。`double_click`。`swipe`：从一点滑到另一点，或沿向量滑；`duration` 与 `steps` 的示例标注为 Android 与 iOS。`touch` 与 `swipe` 的平台行是 Android、Windows、iOS。README 把二者列为完全支持的模拟输入 API | [core API 源码](https://airtest.readthedocs.io/en/latest/_modules/airtest/core/api.html)，[README_MORE](https://airtest.readthedocs.io/en/latest/README_MORE.html) |
| `click`、`doubleClick`、`rightClick`、`dragDrop`、`wheel`。`click` 可先按图像找到点击点 | [SikuliX Region](https://sikulix-2014.readthedocs.io/en/latest/region.html) |
| `moveTo` / `move`（可设 `duration`）、`dragTo` / `drag`、`click` / `doubleClick` / `tripleClick` / `rightClick`、`mouseDown` / `mouseUp`、`scroll`（垂直；`hscroll` 在文档中写明用于 OS X 与 Linux）。坐标是主屏笛卡尔坐标，原点在左上。缓动函数如 `easeInOutQuad` | [Mouse Control](https://pyautogui.readthedocs.io/en/latest/mouse.html)，首页示例亦有 `click('button.png')`：[Welcome](https://pyautogui.readthedocs.io/en/latest/) |
| `mouse.click`、`double_click`、`right_click`、`move`、`press`、`release`、`scroll`、`wheel_click` | [pywinauto.mouse](https://pywinauto.readthedocs.io/en/latest/code/pywinauto.mouse.html) |
| `Click`：可带坐标；默认相对活动窗口客户区，除非 `CoordMode` 改成 `Screen` 或 `Window`。文档写 `Click` 使用 `SendMode` 规定的发送方式 | [Click](https://www.autohotkey.com/docs/v2/lib/Click.htm)，[CoordMode](https://www.autohotkey.com/docs/v2/lib/CoordMode.htm) |
| `locator.click`、`locator.dblclick`、`locator.hover`、`locator.drag_to` | [Playwright Auto-waiting](https://playwright.dev/python/docs/actionability) |

gamebot 今天有：`PointerInput.move_to`、`click`、`right_click`。`PyAutoPointerDirectHandler.move_to` 调用 `pyautogui.moveTo`，并传入 `tween=pyautogui.easeInOutQuad`。协议和两个 handler 都没有双击、拖拽、滚轮、中键、`mouseDown` / `mouseUp`。

## 5. 键盘

解决的问题：向当前焦点或目标窗口输入文字、单键和组合键。

| 资料中的名称 | 出处 |
| --- | --- |
| `text`：向设备输入文字；默认随后再送 Enter（`enter=True`）。`keyevent`：平台按键。Windows 走 `pywinauto.keyboard`，示例 `keyevent("{DEL}")`、`keyevent("%{F4}")`。README 把 `text`、`keyevent` 列为完全支持 | [core API 源码](https://airtest.readthedocs.io/en/latest/_modules/airtest/core/api.html)，[README_MORE](https://airtest.readthedocs.io/en/latest/README_MORE.html) |
| `type`：对当前焦点或指定点击点逐键输入。文档建议可读文字用 `paste`，动作键（TAB、ENTER、ESC）用 `type`。`paste` 通过系统剪贴板快捷键粘贴，之后剪贴板里会留下这段文字 | [SikuliX Region](https://sikulix-2014.readthedocs.io/en/latest/region.html) |
| `write`、`press`、`hold`、`hotkey`（首页示例 `hotkey('ctrl', 'c')`）。FAQ：不能做按键记录，也不能检测某个键当前是否按下 | [Welcome](https://pyautogui.readthedocs.io/en/latest/) |
| `send_keys`：向活动窗口发送 Unicode 与特殊键；`+` Shift、`^` Ctrl、`%` Alt；`{键 down}` / `{键 up}` 表示按住与松开 | [pywinauto.keyboard](https://pywinauto.readthedocs.io/en/latest/code/pywinauto.keyboard.html) |
| `Send`：向活动窗口发送按键与文本，含修饰键与 `{Ctrl down}` 这类按下保持 | [Send](https://www.autohotkey.com/docs/v2/lib/Send.htm) |
| `locator.fill`、`locator.press`、`locator.press_sequentially` | [Playwright Auto-waiting](https://playwright.dev/python/docs/actionability) |

gamebot 今天有：`KeyboardInput.press` 与 `type_text`。pyauto 路径是 `pyautogui.press` 与 `pyautogui.typewrite`。win32 路径对单字符用 `WM_KEYDOWN` / `WM_KEYUP`，对字符串逐字 `WM_CHAR`。没有组合键、按住修饰键或 `hotkey` 方法。

## 6. 真实输入，以及发给窗口或控件的输入

解决的问题：有的程序只认真实光标；有的程序在后台、被挡住或没有标准控件时，需要把鼠标键盘消息直接送给 hwnd 或控件。

| 资料中的名称 | 出处 |
| --- | --- |
| 控件看不见时，仍可用 `mouse` 与 `keyboard` 模块产生鼠标键盘事件。`click_input`：在控件可见坐标上做更接近真实用户的点击，文档写明它和 `click` 不同，并且用户如果同时移动鼠标可能把光标移开。`drag_mouse_input`。`client_to_screen` | [Getting Started](https://pywinauto.readthedocs.io/en/latest/getting_started.html)，[BaseWrapper](https://pywinauto.readthedocs.io/en/stable/code/pywinauto.base_wrapper.html) |
| `ControlClick`：向窗口或控件发送鼠标键或滚轮事件，可以按客户区坐标，或按 ClassNN / 文本 / HWND。`NA` 选项避免把目标标成活动窗口。文档写明它最适合常见微软控件，自定义控件可能无效 | [ControlClick](https://www.autohotkey.com/docs/v2/lib/ControlClick.htm) |
| Airtest 连接 Windows 时使用 pywinauto 作为后端 | [README_MORE](https://airtest.readthedocs.io/en/latest/README_MORE.html) |
| PyAutoGUI 首页把能力写成控制其他应用窗口里的鼠标和键盘，坐标在屏幕上 | [Welcome](https://pyautogui.readthedocs.io/en/latest/) |

gamebot 今天两条路径都有。`PyAutoPointerDirectHandler` 调用 pyautogui，作用在真实光标和键盘上。`Win32BackendHandler` 用 `SendMessage` 发送 `WM_MOUSEMOVE`、`WM_LBUTTONDOWN` / `UP`、`WM_RBUTTONDOWN` / `UP`、`WM_KEYDOWN` / `UP`、`WM_CHAR`，并要求先绑定 hwnd。没有按控件 ClassNN 或 UI Automation 节点点击的接口。

## 7. 窗口绑定、等待窗口与坐标系

解决的问题：确定操作哪一个窗口，等到它出现，并分清客户区坐标和屏幕坐标。

| 资料中的名称 | 出处 |
| --- | --- |
| `connect_device` / `init_device`。Windows 示例：`Windows:///` 连接桌面，`Windows:///123456` 按句柄，`windows:///?title_re='.*explorer.*'` 按标题正则，`foreground=False` 连接时不把窗口置前。`set_current` 在已连接设备之间切换 | [core API 源码](https://airtest.readthedocs.io/en/latest/_modules/airtest/core/api.html)，[README_MORE](https://airtest.readthedocs.io/en/latest/README_MORE.html) |
| `Application.start` / 连接到已有进程，`Desktop` 跨进程。`window(title=...)`、`title_re`、`class_name`、`auto_id`、`control_type`、`best_match` 描述窗口。`wait('visible')` 等到窗口可用 | [Getting Started](https://pywinauto.readthedocs.io/en/latest/getting_started.html) |
| `WinWait`：等到指定窗口存在。`CoordMode` 的 `Pixel` 影响 `PixelGetColor`、`PixelSearch`、`ImageSearch`；`Mouse` 影响 `Click`、`MouseMove`、`MouseClick`、`MouseClickDrag`。相对目标可以是 `Screen`、`Window` 或 `Client`。文档写默认相对活动窗口客户区 | [WinWait](https://www.autohotkey.com/docs/v2/lib/WinWait.htm)，[CoordMode](https://www.autohotkey.com/docs/v2/lib/CoordMode.htm) |
| 首页列出一项 Windows-only 能力：定位应用窗口，并移动、缩放、最大化、最小化或关闭 | [PyAutoGUI Welcome](https://pyautogui.readthedocs.io/en/latest/) |
| SikuliX 动作用的是屏幕上的 `Region`，不是窗口句柄 | [Region](https://sikulix-2014.readthedocs.io/en/latest/region.html) |

gamebot 今天有：`bind` / `bind_from_env`。`NAME` 非空时按标题找 hwnd，否则绑定当前前台窗口。`WindowControl` 有 `focus`、`restore`、`minimize`，实现在 `Win32BackendHandler`（`SetForegroundWindow`、`SW_RESTORE`、`SW_MINIMIZE`）。`client_to_screen` 在截图 handler 上；`find_and_click` 在截图对象和点击对象不是同一个、且截图对象有该方法时做转换。没有按正则等待窗口出现的方法，也没有移动或缩放窗口的方法。

## 8. 控件树、无障碍定位，以及注入式 UI 树

解决的问题：标准 Win32 / UI Automation 控件，或游戏引擎导出的节点树，可以用名字和属性定位，而不必截图比对。

| 资料中的名称 | 出处 |
| --- | --- |
| 后端 `win32`（Win32 API）与 `uia`（MS UI Automation）。`print_control_identifiers` 打印控件树和可用的 best-match 名字。属性解析按标题、控件类型、auto_id 等查找 | [Getting Started](https://pywinauto.readthedocs.io/en/latest/getting_started.html) |
| Poco：跨引擎 UI 自动化。必须在主机安装 Python 库，并在游戏或应用里安装 poco-sdk。示例用 `poco('btn_start').click()`、`drag_to`、`get_text()`。`dump()` 导出统一格式的 UI 树（`name`、`type`、`visible`、`pos`、`size` 等）。文档列出的引擎包括 Unity3D、cocos2dx、Android/iOS 原生、Windows apps、Egret。查看层级的工具是 AirtestIDE 或 PocoHierarchyViewer | [Poco 文档](https://poco.readthedocs.io/en/latest/) |
| Playwright locator：`get_by_role`、`get_by_text`、`get_by_label`、`get_by_placeholder`、`get_by_alt_text`、`get_by_title`、`get_by_test_id`。每次动作前重新在 DOM 里查找。这是页面 DOM / 无障碍名，不是屏幕像素 | [Locators](https://playwright.dev/python/docs/locators) |
| `ControlClick` 的控件标识：ClassNN、文本或 HWND | [ControlClick](https://www.autohotkey.com/docs/v2/lib/ControlClick.htm) |

Airtest README 写的是用图像识别定位，从而不必往应用里注入代码：[README_MORE](https://airtest.readthedocs.io/en/latest/README_MORE.html)。Poco 文档写的是另一条路，需要 poco-sdk。

gamebot 今天没有控件树、UIA、DOM locator 或 Poco 式节点查询。

## 9. 像素颜色

解决的问题：目标没有稳定的小图，或只需要某个点的颜色是否匹配。

| 资料中的名称 | 出处 |
| --- | --- |
| `pixel(x, y)` 返回该点 RGB。`pixelMatchesColor` 可带 `tolerance` | [PyAutoGUI Screenshot Functions](https://pyautogui.readthedocs.io/en/latest/screenshot.html) |
| `PixelSearch`：在矩形里找指定颜色的像素，可设 `Variation`。搜索区域必须可见 | [PixelSearch](https://www.autohotkey.com/docs/v2/lib/PixelSearch.htm) |

本次读到的 Airtest core API、SikuliX Region 动作列表、pywinauto Getting Started、Playwright locators、OpenCV `matchTemplate` 页没有把「按颜色找一个像素」列成与模板匹配并列的入口。

gamebot 今天没有像素读取或按颜色搜索的协议方法。

## 10. OCR 与按画面文字定位

解决的问题：按钮上的字会变，或没有控件文本接口时，直接读屏幕上的字并按字定位。

| 资料中的名称 | 出处 |
| --- | --- |
| SikuliX 2.0.2 起类名是 `OCR`。三组能力：Tesseract 选项、从区域或图像读文字、在区域或图像里按字符串或正则找到文字的 `Match`。实现依赖 Tess4J / Tesseract。`find` 的参数也可以是普通文字 | [text and OCR](https://sikulix-2014.readthedocs.io/en/latest/textandocr.html)，[Region.find](https://sikulix-2014.readthedocs.io/en/latest/region.html) |
| PyAutoGUI FAQ 对「Does PyAutoGUI do OCR?」的回答是 No，并写明这在路线图上 | [Welcome](https://pyautogui.readthedocs.io/en/latest/) |

Airtest 的 `text()` 是键盘输入，不是 OCR（见第 5 节出处）。Poco 的 `get_text()` 读的是 UI 树节点上的文字。Playwright `get_by_text` 读的是 DOM 文本。这三处都不是屏幕 OCR。

gamebot 今天没有 OCR，模板查找的参数是图像路径。

## 11. 剪贴板

解决的问题：读出或写入系统剪贴板，用来粘贴长文本，或把游戏里复制出来的内容交给脚本。

| 资料中的名称 | 出处 |
| --- | --- |
| `get_clipboard`、`set_clipboard`、`paste`。文档标注平台 Android、iOS、Windows | [core API 源码](https://airtest.readthedocs.io/en/latest/_modules/airtest/core/api.html) |
| `A_Clipboard`：可读可写的文本剪贴板。`ClipWait` 等到剪贴板里有数据。示例是 `Send "^c"` 之后 `ClipWait` | [A_Clipboard](https://www.autohotkey.com/docs/v2/lib/A_Clipboard.htm) |
| SikuliX `paste` 会占用剪贴板来粘贴文字 | [Region](https://sikulix-2014.readthedocs.io/en/latest/region.html) |

本次读到的 PyAutoGUI 首页、截图页和鼠标页没有剪贴板 API。

gamebot 今天有：`ClipboardAccess.read` / `write`，由 `PyperclipHandler` 用 `pyperclip.paste` / `pyperclip.copy` 实现。

## 12. 断言

解决的问题：步骤之后明确判定目标是否出现、数值是否相等，失败时中断并留下记录。

| 资料中的名称 | 出处 |
| --- | --- |
| `assert_exists`、`assert_not_exists`、`assert_equal`、`assert_not_equal`，以及 `assert_true` 等。图像断言失败抛 `AssertionError`（README 写作 `AssertsionError`），`msg` 记入报告。README 把断言写成基本用法的一步 | [assertions](https://airtest.readthedocs.io/en/latest/all_module/airtest.core.assertions.html)，[README_MORE](https://airtest.readthedocs.io/en/latest/README_MORE.html) |
| `expect(locator).to_be_visible()` 等会自动重试直到条件成立或超时。同页还列出 `to_have_text`、`to_have_count`，以及 `expect(page).to_have_title()` / `to_have_url()` | [Auto-waiting 的 Assertions 表](https://playwright.dev/python/docs/actionability) |
| SikuliX 找不到图时 `find` 抛 `FindFailed`；`exists` 则返回空而不抛 | [Region](https://sikulix-2014.readthedocs.io/en/latest/region.html) |
| Poco 示例使用 Python `assert` 比较 `get_text()` | [Poco](https://poco.readthedocs.io/en/latest/) |

gamebot 今天没有断言 API。`find` 找不到时返回 `None`，`find_and_click` 返回 `False`。节点函数的 `bool` 返回值由 DAG 使用，源码里没有 `assert_exists` 这类名字。

## 13. 日志、报告、录屏，以及给人看的运行过程

解决的问题：失败后能看到当时的画面和步骤，而不是只剩一个退出码。

| 资料中的名称 | 出处 |
| --- | --- |
| core API 上的操作使用 `logwrap`。`snapshot(..., msg=...)` 的说明会显示在报告页。`sleep` 会记入报告。CLI：`airtest run` 的 `--log`、`--recording`（运行时录屏）、`--compress`、`--no-image`；`airtest report` 生成 HTML（默认 `log.html`），并可带上录屏文件 | [core API 源码](https://airtest.readthedocs.io/en/latest/_modules/airtest/core/api.html)，[README_MORE](https://airtest.readthedocs.io/en/latest/README_MORE.html) |
| Trace Viewer：`--tracing on` 或 `context.tracing.start(screenshots=True, snapshots=True, sources=True)`，事后用 `playwright show-trace` 按动作查看页面、日志和网络 | [Trace viewer](https://playwright.dev/python/docs/trace-viewer-intro) |
| `page.screenshot` 可存文件或字节，供事后像素对比 | [Screenshots](https://playwright.dev/python/docs/screenshots) |
| SikuliX 文档首页把 IDE 写成加载、编辑、保存、运行脚本并管理图像的编辑器 | [SikuliX 文档首页](https://sikulix-2014.readthedocs.io/en/latest/index.html) |

gamebot 今天有给人看的 dashboard：CLI 启动本机 HTTP，`/` 为页面，`/api/graph`、`/api/snapshot`、`/api/stream`（SSE）推送 DAG 快照；`DASHBOARD_OPEN` 为真时用浏览器打开。CLI 同时 `print` 当前 step。源码里没有 HTML 用例报告，也没有运行时录屏开关。

## 14. 失败保护与操作间隔

解决的问题：脚本失控时人还能夺回鼠标，并在每步之间留出界面反应时间。

| 资料中的名称 | 出处 |
| --- | --- |
| `FAILSAFE` 默认开启：调用 PyAutoGUI 函数时若鼠标在主屏四角，抛 `FailSafeException`。`PAUSE` 默认 `0.1` 秒，每次函数调用后等待。文档建议不要关掉 failsafe | [Welcome](https://pyautogui.readthedocs.io/en/latest/) |
| `timings.Timings`：`defaults`、`slow`（全局间隔约加倍）、`fast`（约减半）。`WindowSpecification.wait` / `wait_not`，以及 `wait_until` / `wait_until_passes` | [Waiting for Long Operations](https://pywinauto.readthedocs.io/en/latest/wait_long_operations.html) |
| Airtest 每个 `touch` / `keyevent` / `text` 等之后调用 `delay_after_operation()` | [core API 源码](https://airtest.readthedocs.io/en/latest/_modules/airtest/core/api.html) |

gamebot 源码没有自己的四角失败保护，也没有全局 `PAUSE` 配置。`PyAutoPointerDirectHandler` 直接调用 pyautogui，因此会走到 PyAutoGUI 库的默认 `FAILSAFE` 和 `PAUSE`。`Win32BackendHandler` 的 `SendMessage` 路径不经过 pyautogui。协议里没有等待方法。

## 15. 热键触发

解决的问题：人按下一个全局快捷键才启动一段鼠标键盘动作，或用热键中断。

AutoHotkey 文档把 Hotkeys 定义为由鼠标、手柄或键盘快捷键触发动作。示例 `#n::Run "notepad"`，以及热键里 `Send` 向当前窗口送字。[Hotkeys](https://www.autohotkey.com/docs/v2/Hotkeys.htm)

PyAutoGUI 的 `hotkey()` 是发出组合键，不是注册全局监听。同页 FAQ 写明不能检测某个键是否正被按下（见第 5 节）。

gamebot 今天没有热键或全局按键监听。CLI 的入口是直接 `run()` 执行 DAG。

## 16. 浏览器驱动

解决的问题：目标在网页里，用选择器和浏览器事件操作，而不是截客户区再模板匹配。

Playwright Python 文档写明：库可作为通用浏览器自动化工具，同步或异步均可；支持 Chromium、WebKit、Firefox，以及 headless 或有头。[Introduction](https://playwright.dev/python/docs/intro)

同套文档里的运行时入口包括：

- `page.goto`（简介中的示例）
- 第 8 节的 locators
- 动作前的自动等待：可见、稳定、能收到事件、启用、非 inert；超时则 `TimeoutError`。`force` 可跳过部分检查
- 第 12 节的 `expect`
- 第 4、5 节的点击、双击、悬停、拖拽、填写、按键
- 第 13 节的截图与 trace

[Auto-waiting](https://playwright.dev/python/docs/actionability)

gamebot 今天的 `BrowserAutomation` 只有 `goto(url)` 和 `click_selector(selector)` 两个方法，类文档写明是契约 stub。没有 Playwright 实现包，因此没有自动等待、locator、断言、截图或 trace。

## 17. 脚本怎么跑起来

这不是图像或鼠键原语，但上述文档都把它放在运行入口里。

| 资料中的名称 | 出处 |
| --- | --- |
| `airtest run <脚本.air> --device <URI>`，一个用例可配 Android、iOS 或 Windows 设备。`auto_setup` 连接设备并设置日志目录 | [README_MORE](https://airtest.readthedocs.io/en/latest/README_MORE.html)，[auto_setup 源码](https://airtest.readthedocs.io/en/latest/_modules/airtest/core/api.html) |
| Playwright Pytest 插件跑 `test_` 用例；不用 Pytest 时直接使用库 API | [Introduction](https://playwright.dev/python/docs/intro) |
| AutoHotkey 脚本由热键或脚本体启动，`Run` 可启动外部程序 | [Hotkeys](https://www.autohotkey.com/docs/v2/Hotkeys.htm) |
| pywinauto `Application.start('notepad.exe')` 启动进程并把它当作后续查找的边界 | [Getting Started](https://pywinauto.readthedocs.io/en/latest/getting_started.html) |

gamebot 今天的入口是 CLI 加载 `dags/<DAG>.py`，调用 `build_setup()`，再循环执行 `group`。次数来自 `core.NUMBER`（`.env` 的 `NUMBER`，`0` 表示一直跑）。窗口标题、模板子目录、dashboard 端口同样在 `src/gamebot/core/config.py` 从环境变量读取。本文不讨论把这些迁入 `build_setup()` 的决定。

## 对照摘要

多份文档都命名了这些运行时能力：截图、带阈值的模板找图、搜索区域、等待出现、全部匹配、鼠标点击与拖拽或滑动、滚轮、键盘文字与组合键、窗口或屏幕坐标系。断言、运行报告或录屏出现在 Airtest 与 Playwright。真实光标与「消息发给窗口/控件」成对出现在 pywinauto 与 AutoHotkey；Airtest 的 Windows 后端写明使用 pywinauto。

只在一部分文档里出现、因此不能写成全体标配的有：OCR（SikuliX 有；PyAutoGUI 明确写没有）、UI 树（pywinauto、Poco、Playwright DOM）、像素颜色（PyAutoGUI、AutoHotkey）、剪贴板 API（Airtest、AutoHotkey；SikuliX 的 `paste` 会使用剪贴板）、全局热键（AutoHotkey）、四角失败保护（PyAutoGUI）、浏览器驱动（Playwright）。

gamebot 今天对得上的是：窗口客户区截图、单次灰度 `TM_CCOEFF_NORMED` 匹配、找图并点击、真实鼠键与 `SendMessage` 鼠键、单键与打字、按标题或前台窗口绑定、焦点/还原/最小化、客户区转屏幕坐标、剪贴板、DAG 循环，以及给人看的 dashboard。浏览器只有契约。源码里没有双击、拖拽、滚轮、组合键、找图等待、返回全部匹配、搜索区域、OCR、像素色、控件树、断言、HTML 报告、录屏和热键监听。
