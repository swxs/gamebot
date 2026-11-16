# 大模型编写并自测流程的常见做法

只记录一手资料里的做法。范围是 Playwright Test Agents、Stagehand、browser-use、Anthropic computer use、OpenAI computer-using agent / Responses computer tool，以及微软 UFO 论文与文档、Windows Agent Arena 论文与仓库。没有采用二手综述。这些资料都谈浏览器或桌面 UI，没有一份把「游戏脚本」或「Python 节点函数」当作自己的对象；下面凡是问到游戏脚本或节点函数，都按资料实际写了什么、没写什么来记。

## 编写合同时常固定什么

各家固定的不是同一份合同，但重复出现的是：自然语言任务、可执行的动作原语、完成时要交回什么，以及谁来停。

Playwright 把编写拆成三份产物。Planner 收到明确请求、一个 seed test，可选再加 PRD；seed test 负责环境、fixture 和 hook，并当作后续测试的样例。计划写成 Markdown，每个场景要有标题、逐步说明、期望结果、起始状态假设，以及成功与失败条件；计划保存为 `specs/` 下的文件。Generator 再把计划收成 Playwright Test：一个场景一个文件，`describe` 对上计划的顶层条目，测试标题对上场景名，每步执行前写上该步原文，并优先采用实时执行日志里的写法。Healer 的输入是失败测试的名字，输出是通过的测试，或在它认为功能已坏时标成跳过。来源：<https://playwright.dev/docs/test-agents>，<https://github.com/microsoft/playwright/blob/main/packages/playwright/src/agents/playwright-test-planner.agent.md>，<https://github.com/microsoft/playwright/blob/main/packages/playwright/src/agents/playwright-test-generator.agent.md>，<https://github.com/microsoft/playwright/blob/main/packages/playwright/src/agents/playwright-test-healer.agent.md>。

Stagehand v3 的 `agent.execute` 固定一条自然语言 `instruction`。可选 `systemPrompt`、`mode`（`dom` / `hybrid` / `cua`）、模型、`maxSteps`，以及实验性的 `messages` 用来接上一次对话。`dom` 用 `act`、`fillForm`；`hybrid` 再加上坐标类工具，文档要求只用能可靠做坐标动作的模型。返回里有 `success`、`message`、`actions`、`completed`。来源：<https://docs.stagehand.dev/v3/references/agent>。v4 删掉了 `agent()`。官方迁移说明写：它是给当时不能自己稳定驱动浏览器的模型用的，每步选一个工具。替代有两条：code mode 让编程助手写一次脚本再运行，Browserbase 建议从这里开始；tool calling 则把模型留在运行循环里，工具是整份 Stagehand API。code mode 的生成约定是：选择器稳定就用 `page.locator()` 和 `page.goto()`，只有需要判断的步骤才调用 `act()` / `extract()`。来源：<https://docs.stagehand.dev/v4/migrations/v3>。

browser-use 1.0 的合同是一条非空 `task`，加上固定的核心系统提示；调用方只能用 `extend_system_message` 追加，不能替换核心提示。每一步模型写一个 Python cell，在持久 REPL 里跑，读输出，最后用交付结束。文档建议任务里写明起点、完成时长什么样、格式或 `output_model_schema`、失败时的退路，以及自定义工具何时调用。来源：<https://docs.browser-use.com/open-source/agent>。

Anthropic computer use 不让模型交一份脚本。应用在 `tools` 里放一个 `computer_toolset_20260801`，模型返回带 `toolset_name: computer` 的成员调用，例如 `screenshot`、`left_click`、`type`、`zoom`。应用按顺序执行，再把 `tool_result` 送回。官方提示建议把任务和每一步写清楚；若希望每批动作都以截图收尾，把这句话写进系统提示。来源：<https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool>。

OpenAI 的 Computer-Using Agent 说明是：用户给指令，模型看截图，用虚拟鼠标和键盘行动，直到它认为任务完成或需要用户输入；敏感动作要用户确认。来源：<https://openai.com/index/computer-using-agent/>。Responses 文档同时给出两条调用合同。一条是函数工具 `exec_py` 或 `exec_js`：模型提交一段代码，工具说明里限定可用对象（桌面路径是 `pyautogui`、`time`、`log`、`display`；浏览器路径是 Playwright 的 `browser` / `context` / `page`）。另一条是 `ComputerToolset`：驱动实现点击、输入、滚动、等待和 `screenshot`，应用拥有会话、权限和清理。来源：<https://developers.openai.com/api/docs/guides/tools-computer-use>。驱动文档写明：动作按顺序只执行一次，助手在这批动作之后抓最终截图，不重试驱动动作。来源：<https://developers.openai.com/api/docs/guides/tools-computer-use-sdk-drivers>。

UFO 论文里，AppAgent 每步的输出合同是：对截图的 observation、thoughts、选中控件的 label 和 name、对该控件调用的 function 及参数、status、更细的 local plan、comment。status 取 `CONTINUE`、`FINISH`、`PENDING`、`SCREENSHOT`、`APP_SELECTION`。函数从固定列表里选，论文列出的是 Click、SetText、GetText、Scroll，以及自定义的 Annotate、Summary；执行后端是 pywinauto 和 Windows UI Automation，不是模型自由写的脚本。来源：<https://arxiv.org/html/2402.07939>。UFO² 文档把同一类动作收成具名命令，例如 `click_input`、`set_edit_text`，数据收集命令如 `capture_window_screenshot` 由框架调用，不由模型挑选。来源：<https://microsoft.github.io/UFO/ufo2/app_agent/commands/>。

Windows Agent Arena 的任务 JSON 固定 `instruction`、初始 `config`、`evaluator`。完成与否由 evaluator 函数对照 expected 计算奖励，论文写明沿用 OSWorld 的事后脚本，例如读设置、查文件或用动态函数。来源：<https://arxiv.org/html/2409.08264>，<https://github.com/microsoft/WindowsAgentArena/blob/main/docs/Develop-Tasks.md>。Navi 的提示词另固定每步输出：对屏幕的简短判断、下一步计划、`decision`（`DONE` / `FAIL` / `WAIT` / `COMMAND` 四选一）、一个 Python 代码块、可选的文本 memory。代码块被限制为调用提示词里列出的 `computer` 模块函数，并要求每步不要做超过一个动作。来源：<https://github.com/microsoft/WindowsAgentArena/blob/main/src/win-arena-container/client/mm_agents/navi/gpt/planner_messages.py>。

## 运行轨迹和截图怎样给模型看

Playwright 的生成与修复主路径看的是可访问性快照和测试日志，不是截图流。Planner 的工具列表里有 `browser_snapshot` 和 `browser_take_screenshot`，但指示写明不要截图，除非绝对必要，并先看 snapshot。Generator 对计划里的每一步用浏览器工具当场做一遍，意图用该步描述，然后 `generator_read_log`，立刻用日志里的写法调用 `generator_write_test`。Healer 的工具是 `test_run`、`test_debug`、`browser_snapshot`、console、network、`browser_evaluate`、`browser_generate_locator`；失败暂停后看错误和页面 snapshot，改测试代码再跑。来源同上三份 agent 定义与 <https://playwright.dev/docs/test-agents>。

Stagehand v3 的 CUA 模式把计算机使用模型放进 `execute`；`hybrid` 文档写明包含基于截图的坐标交互。`highlightCursor` 是执行选项。返回的 `actions` 是本轮各步工具数据，`messages` 可传给下一次 `execute` 以继续对话，文档标注为实验性且非 CUA。来源：<https://docs.stagehand.dev/v3/references/agent>，<https://docs.stagehand.dev/v3/basics/agent>。v4 code mode 不再把每步观察送回模型；模型在运行前写脚本。来源：<https://docs.stagehand.dev/v4/migrations/v3>。

browser-use 1.0 默认会把截图送给模型；只有 `use_vision=False` 时截图不到模型。页面上的橙色高亮给旁观者看，不会出现在模型自己的截图里，无障碍树、文本和点击也看不到它们。对话超过 `max_context_chars` 的 75% 时压缩历史。完整转录在 `result.messages`。0.x 的 `screenshots()` 等按步历史 API 在 1.0 已删除，迁移说明写：1.0 跑的是 Python cell，模型需要时自己截图。来源：<https://docs.browser-use.com/open-source/agent>，<https://docs.browser-use.com/open-source/migrating>。

Anthropic 要求 `screenshot` 和 `zoom` 的 `tool_result` 带图片，其他动作用短文本如 `OK` 即可。文档写 Claude 通常用 `screenshot` 结束一批动作，以便先看结果再决定下一步；若这批没有以截图结束，应用可以在最后一个结果上另附一张当前屏幕图。提示词原文建议每步截图后用一句话说明画面以及该步是否成功，没成功就重试，确认成功才进入下一步。坐标使用所返回截图的像素。长循环会堆积截图；单次请求超过 20 张图后，每张图适用更严的边长限制。文档给出的默认剪法是保留最近三张截图，每 25 轮剪一次，使两次剪枝之间的前缀保持逐字节相同。来源：<https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool>。

OpenAI CUA 说明把当前截图放进上下文，推理时同时看当前与过去的截图和动作。来源：<https://openai.com/index/computer-using-agent/>。API 侧，驱动的 `screenshot()` 返回 `computer_screenshot`，带 `image_url` 或 `file_id`。`exec_py` 的工具说明要求行动前 `display(pyautogui.screenshot())`，用截图坐标，一小段动作后再检查屏幕，并把截图留在内存里。来源：<https://developers.openai.com/api/docs/guides/tools-computer-use>，<https://developers.openai.com/api/docs/guides/tools-computer-use-sdk-drivers>。托管 Agents API 的 `include_screenshots` 默认不把截图放进 API 输出，文档写智能体仍能观察它们；设为 true 后，已完成的浏览器活动事件可在 `item.output` 带上最后一张图。来源：<https://developers.openai.com/api/docs/guides/agents-api/tools/computer-use>。

UFO 论文写，AppAgent 每步之前收到三张图：上一张把上次选中的控件用红框标出，用来看上一步有没有生效；一张无标注的干净截图；一张用 Set-of-Mark 给控件编号的标注图。observation 要描述当前窗口，并分析上一个动作是否生效。来源：<https://arxiv.org/html/2402.07939>。UFO² 系统配置里 `INCLUDE_LAST_SCREENSHOT` 默认 true，`SCREENSHOT_TO_MEMORY` 默认 true；步骤日志把 `screenshot_clean`、`screenshot_annotated` 等存成路径，响应字段含 observation、thought、action、status。来源：<https://microsoft.github.io/UFO/configuration/system/system_config/>，<https://microsoft.github.io/UFO/ufo2/evaluation/logs/step_logs/>。

Windows Agent Arena 论文写，Navi 的输入包括任务说明、动作空间描述、以往动作历史、剪贴板、一块可写文本 memory、带 Set-of-Marks 的标注图，以及上一状态的截图。上一张图用于理解当前画面，并判断任务是否已经完成。论文中的截图是 1440×900×3 的 RGB。来源：<https://arxiv.org/html/2409.08264>。仓库里的 Navi 提示词把输入列成：窗口标题、全部窗口名、剪贴板、OCR 文本、候选元素（ID、类型、文本、0–1 归一化框）、上一张原图、当前原图、标注图，以及「previous N actions」的代码块历史。提示词要求每步核对是否还在正轨。评测入口 `run.py` 的 `--observation_type` 可选 `screenshot`、`a11y_tree`、`screenshot_a11y_tree`、`som`，默认 `a11y_tree`；`--screen_width` / `--screen_height` 默认 1920 和 1200。论文里的 1440×900 与仓库默认分辨率不是同一个数，这里并列记录。来源：<https://github.com/microsoft/WindowsAgentArena/blob/main/src/win-arena-container/client/mm_agents/navi/gpt/planner_messages.py>，<https://github.com/microsoft/WindowsAgentArena/blob/main/src/win-arena-container/client/run.py>。`run.py` 还有 `--max_trajectory_length`，默认 3，但本次读到的 `NaviAgent(...)` 构造没有把该参数传进去；提示词只写 N，没有写死 N 等于 3。因此不能从这两处断定历史窗口就是 3。

## 有限次数如何约定

约定都在调用方或运行器，不在模型权重里。停的条件通常是模型自己宣布结束，或次数、时间用尽。

Playwright 文档写 healer 会重跑，直到测试通过，或直到 guardrails 停下循环。已发布的 healer agent 定义没有给出次数：它写继续到测试干净通过；若错误仍在且它高度确信测试是对的，就标 `test.fixme()` 并在失败步骤前加注释。这两份文本都没有写出 guardrail 的数字。来源：<https://playwright.dev/docs/test-agents>，<https://github.com/microsoft/playwright/blob/main/packages/playwright/src/agents/playwright-test-healer.agent.md>。

Stagehand v3 的 `maxSteps` 默认 20，表示停止前最多能做多少个动作。示例里写 15 步未完成即停，并用 `result.success === true` 区分成功与失败或未完成。来源：<https://docs.stagehand.dev/v3/references/agent>，<https://docs.stagehand.dev/v3/basics/agent>。v4 迁移表把 `execute({ maxSteps })` 对应成「你自己的循环上界，或脚本的长度」。来源：<https://docs.stagehand.dev/v4/migrations/v3>。

browser-use 的 `agent.run(max_steps=100, timeout=1700)`：`max_steps` 计的是模型请求次数，最后一次只允许交付，其后最多再有一次交付修补请求。`timeout` 是代理循环的秒数，不含浏览器启动和停止。触达任一预算时给一次交付轮：若交付了，`status` 为 `completed`，若智能体报告任务未完成则 `success` 为 false；若没有交付，`status` 为 `max_steps` 或 `timeout`，部分结果在 `result.partial`。`max_steps < 1` 或 `timeout <= 0` 在浏览器启动前抛 `ValueError`。迁移说明写：失败的 cell 在 `max_steps` 内由模型重试。来源：<https://docs.browser-use.com/open-source/agent>，<https://docs.browser-use.com/open-source/migrating>。官方 `llms.txt` 写：`result.is_done()` 表示运行 status 为 completed；`result.is_successful()` 是智能体 `finish(success)` 的自我判定，未给则为 None；重要的外部动作要另行核实。来源：<https://docs.browser-use.com/llms.txt>。

Anthropic 文档里的示例循环是 `max_iterations` 默认 10：Claude 不再请求工具，或次数用尽，循环结束。这是示例客户端代码，文档没有把它写成 API 强制上限。来源：<https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool>。

OpenAI 驱动文档写：用 `maxSteps` / `max_steps` 限制 API 请求，默认 20；最后一次允许的请求不能再开始新效果。SDK 的 HTTP 重试不会重试一次驱动动作。来源：<https://developers.openai.com/api/docs/guides/tools-computer-use-sdk-drivers>。同一指南里的 `exec_py` / `exec_js` 示例是手写 `for turn in range(20)`：没有函数调用且出现非 commentary 消息则返回；第 20 次仍未结束则抛错，文案是已达 20 次响应上限。取件示例把 `max_steps` 设为 6，并在模型回答之外用页面 DOM 检查细节是否打开。来源：<https://developers.openai.com/api/docs/guides/tools-computer-use>。CUA 产品说明没有给出用户侧的固定步数；它写模型一直做到自己认为完成或需要用户输入。OSWorld 评测写允许更多步时成绩上升。来源：<https://openai.com/index/computer-using-agent/>。Operator 系统卡里有一次自主复制评测「每个任务跑 10 次、最多 400 步」；这是该评测的预算，不是文档中的产品默认值。来源：<https://openai.com/index/operator-system-card/>。

UFO² 配置：`MAX_STEP` 默认 50，表示每个任务的最大步数；`MAX_ROUND` 默认 1，表示从起点重试整次任务的轮数，文档举例 `MAX_ROUND: 3` 即失败后整段任务最多再试到 3 轮。`JSON_PARSING_RETRY` 默认 3，只重试解析 LLM 的 JSON。来源：<https://microsoft.github.io/UFO/configuration/system/system_config/>。2024 论文描述循环直到请求完成或切应用，正文读到的部分没有给出步数数字。来源：<https://arxiv.org/html/2402.07939>。

Windows Agent Arena 论文把回合写成：模型给出动作，直到它输出终止动作 `DONE` 或 `FAIL`，或步数超过 `t_max`。来源：<https://arxiv.org/html/2409.08264>。仓库 `run.py` 的 `--max_steps` 默认 15。来源：<https://github.com/microsoft/WindowsAgentArena/blob/main/src/win-arena-container/client/run.py>。论文没有把 15 写成唯一的 `t_max`。Navi 提示词里 `DONE` 和 `FAIL` 都会结束 episode，`WAIT` 则睡到下一轮。来源：<https://github.com/microsoft/WindowsAgentArena/blob/main/src/win-arena-container/client/mm_agents/navi/gpt/planner_messages.py>。任务是否得分，论文与任务文档都写成 evaluator 脚本的事，与模型是否输出 `DONE` 分开。来源：<https://arxiv.org/html/2409.08264>，<https://github.com/microsoft/WindowsAgentArena/blob/main/docs/Develop-Tasks.md>。

谁判断「这一次真实运行走完了」，资料里是分开的两件事。Playwright 用测试运行器的通过或失败；healer 再决定改代码或 `fixme`。browser-use 把运行是否交付（`status`）和智能体自己的 `success` 分开，并要求重要外部动作另行核实。Anthropic 与 OpenAI CUA 以模型不再要工具、或模型给出最终文字，作为循环结束；OpenAI 的取件示例同时用宿主检查页面。Stagehand v3 同时返回 `success`（文档用语是任务是否成功完成）和 `completed`（文档用语是智能体是否认为已经完全完成），没有另写一个外部裁判。UFO 用模型的 `FINISH`。Windows Agent Arena 用模型的 `DONE`/`FAIL` 结束回合，用任务 evaluator 给分。

## 「直接写 Python 节点函数」是否被当作不稳

没有任何一份上述资料使用「Python 节点函数」这个说法，也没有讨论游戏 DAG 节点。就「让模型直接写 Python」而言，资料没有把它普遍写成不稳定而加以禁止。能对上的原话如下。

Stagehand v4 把「编程助手写一份脚本、然后运行」列为建议的起点，Python 示例与 TypeScript 并列。它认为不可靠的是旧的逐步 `agent()`：当时的模型不能自己稳定驱动浏览器，所以每步都是一次推理。v4 的写法是脚本里能确定的步骤不要推理。来源：<https://docs.stagehand.dev/v4/migrations/v3>。这是把「每次运行都由模型逐步驱动」视为已过时，不是把「写成 Python」视为不稳。

browser-use 1.0 把「每步写一个 Python cell」定为现行合同，并删掉了 0.x 的按步动作列表。文档没有把这种 cell 称为不稳。它写的风险是：模型写的代码能读到密钥和 cookie，密钥没有沙箱，不信任的任务应放在容器或虚拟机里。来源：<https://docs.browser-use.com/open-source/agent>，<https://docs.browser-use.com/open-source/migrating>，<https://docs.browser-use.com/skill.md>。

OpenAI 指南把 `exec_py` 写成正式示例：模型每轮提交 Python，用 `display(pyautogui.screenshot())` 看屏幕。同一页的另一条路径是结构化的 `ComputerToolset`，不提交任意代码。文档没有比较二者谁更不稳。来源：<https://developers.openai.com/api/docs/guides/tools-computer-use>。

Windows Agent Arena 论文同时提供两种动作空间：自由形式的 pyautogui/Python 执行，以及 `Computer` 类函数包装。讨论节的原意是：他们关注的是自由形式动作的全自主智能体，同时也看到更严的预定义动作函数或技能库有潜力；那样执行精度可以更高，因为错误会主要来自规划，以及把原语接起来的决策。来源：<https://arxiv.org/html/2409.08264>。Navi 提示词仍要求输出 Python，但把绝对坐标 `move_abs` 写成很少使用、高度不准确，把 `open_program` 写成比在任务栏、开始菜单或桌面图标上点选更可靠。来源：<https://github.com/microsoft/WindowsAgentArena/blob/main/src/win-arena-container/client/mm_agents/navi/gpt/planner_messages.py>。仓库评测入口的 `--action_space` 默认值是 `pyautogui`。来源：<https://github.com/microsoft/WindowsAgentArena/blob/main/src/win-arena-container/client/run.py>。

UFO 论文与 Anthropic computer use 都没有让模型写 Python 函数。UFO 从固定函数表里选一个，作用在已编号的控件上。Anthropic 使用命名的成员工具。这两处没有「写 Python 不稳」的判断。Playwright Test Agents 生成的是 Playwright Test 源码，官方示例是 TypeScript，生成前要先把每步用工具做一遍并从日志落笔；healer 改的是这份测试。它们没有讨论 Python 节点函数。

## 资料里没有的内容

- 没有一手资料讨论游戏脚本、模板匹配，或「Python 节点函数」这个合同。
- Playwright 公开文档里的 healer guardrails 没有数字；agent 定义也没有次数上限。
- Windows Agent Arena 仓库的 `--max_trajectory_length` 默认 3，与 Navi 提示词里的 N，本次没有在 `NaviAgent` 构造参数里对上。
- Stagehand v4 code mode 没有描述模型自动观看一次真实运行并自行判定走完；它写的是人再把助手用到已坏的那一步上。tool calling 的循环上界由调用方自己定，迁移文档没有再给一套完成判定。
- Anthropic 的 `max_iterations=10` 和 OpenAI 示例里的 20 次响应、取件示例的 6 步，都是文档中的客户端写法或该示例的参数。除 OpenAI 驱动助手「`max_steps` 默认 20」这一句外，不要把示例数字当成各产品统一的平台上限。
