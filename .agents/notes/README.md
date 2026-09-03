# Agent Notes

这里只存放一种设计文档。**Agent Note** 记录影响本代码库的决策或提案——那些代码和文档承载不了的 *为什么* 与 *我们放弃了什么*。本文定义 Agent Note 存放位置、何时书写，以及[文件格式](#文件格式)。

## 布局与命名

每篇 Agent Note 有两个维度，都编码在**路径**里——`{lifecycle}/{class}/yyyy-mm-dd-主题.md`：

- **生命周期**（顶层目录）是 Agent Note 的状态，随状态变化在目录间迁移：
  - **`proposed/`** —— 实现前评审的提案；尚未构建（或只构建了一部分）。
  - **`implemented/`** —— 决策已落地。文件记录决定的内容与否决的内容，并**与实际落地保持一致**：当代码后来移动文件、重命名包、或改变关键项/默认值时，Agent Note 在同一变更中同步更新（只更新事实——路径、名称、结构——不更新决策本身）。见 [implemented/AGENTS.md](implemented/AGENTS.md)。
  - **`rejected/`** —— 提案经过考虑后被否决。仅当其理由仍能阻止一个诱人而严重的错误时保留；否则删除整篇。
- **分类**（嵌套目录）是决策的*种类*——见[分类](#分类)。

文件名中的日期是主题**首次提出**的日期（按 git 历史）。Agent Note 之间的交叉引用使用相对 Markdown 链接（`[主题](../../implemented/architecture/2026-…-….md)`）——绝不使用裸文字或数字——以便机械可校验、迁移目录后仍然有效。

活跃生命周期树就是工作清单：浏览其 lifecycle/class 目录或在仓库中搜索即可。**不要**添加集中的 `INDEX.md`——中央索引是明确禁止的。低未来价值的 implemented 记录迁移到独立的冻结 [`archived/`](archived/AGENTS.md) 树。

## 分类

每篇 Agent Note 属于分类闭集中的一类（由 `scripts/agent-note-tree.ts` 强制校验）；分类门禁拒绝其他目录。新增分类必须同时更新规范集合与本节。

| Class | 覆盖内容 |
|---|---|
| `feature` | 新的用户或模型可见能力。 |
| `bug-fix` | 修正缺陷或填补事故复盘暴露的缺口。 |
| `simplification` | 不增加能力的前提下删除代码、行为或表面积。 |
| `architecture` | 关于**发布源码**的结构性决策——包如何关联、运行时词汇是什么。 |
| `process` | 代码**周边**的工具、策略或工作流——门禁、包管理器、vendoring——而非运行时行为。 |
| `testing` | 测试基建与策略。 |

`architecture` / `process` 的分界：**architecture** 是关于发布的源码；**process** 是周边的工具与工作流。（刻意没有 `refactor`——它与 `simplification` 重叠，后者的判别标准"可观察行为是否变化"已覆盖它。）

## 归档与删除

当已落地的决策已完成、且其理由不太可能指导未来工作时，将 implemented Agent Note 归档。以下情况保持活跃：其备选方案、所有权边界、否定性保证、持久化或线上语义、安全规则、或重新引入条件仍有指导价值时。**绝不**归档 proposed 笔记：过时的提案应否决。rejected 笔记仅在其能阻止一个可能发生的错误时保留；否则删除整篇。使用校准过的 [`dsh-archive-agent-notes`](../skills/dsh-archive-agent-notes/SKILL.md) 工作流判断，而非按字数、时长或配额目标。

归档路径编码为 `archived/{class}/yyyy-mm-dd-主题.md`；刻意没有 `implemented`，因为只有 implemented 笔记能进入归档。归档变更只允许：移动完整单文件、在 `Status: implemented` 正下方插入 `Archived: YYYY-MM-DD` 行、修复或删除入站链接。这是归档过程中唯一允许的内容变更。

一旦封存，每篇归档笔记**永久冻结**。不得编辑、重新格式化、更新、移动或删除，也不得将其作为当前行为的权威。文档门禁跳过归档来源（包括其出站链接）；活跃正文仍可在有意引用历史时链接进归档笔记。 [`verify-archived-agent-notes`](../../scripts/verify-archived-agent-notes.ts) 强制封闭分类树、归档元数据、manifest 哈希与 append-only 冻结内容清单。

## 何时写

每个非平凡变更**必须**在同一 PR 中新增或更新至少一篇 Agent Note。非平凡指：改变了行为、架构、跨文件或跨包共享的契约、流程或工具、测试策略、磁盘/线上/配置格式，或维护者可能合理回访的其他决策。重大未来工作的提案从 `proposed/` 开始；已定的决策直接进 `implemented/`。按决策匹配分类目录（见[分类](#分类)）。

更新已拥有该决策的 Agent Note 即满足规则；不要重复创建。只有纯机械或局部编辑（不改变行为、契约、结构、流程或理由）可豁免。Agent Note **绝不**被改写成*另一个决策*：用新笔记取代它，且除非旧笔记按下面规则被完全合并，否则两篇都要保留并交叉链接。编辑 `implemented/` 笔记以追踪其既有决策的新位置是**要求**而非禁止；见 [implemented/AGENTS.md](implemented/AGENTS.md)。

被完全取代的 implemented 笔记可合并进当前所有者笔记并删除。删除前，所有者必须保留每一条独有理由、备选方案、后果、必要验证与命名的覆盖缺口；修复每一条入站链接。部分取代不适用：两篇都保留并交叉链接，更新仍然有效的事实。合并不得把旧文件改写成其反面，也不得把 git 历史当作理由的唯一副本。

## 文件格式

每篇活跃 Agent Note 遵循同一种文件格式，由 `npm run verify-agent-note-format`（[scripts/verify-agent-note-format.ts](../../scripts/verify-agent-note-format.ts)）强制执行。归档笔记保留封存时的格式加上归档日期行。

### 头部块

每篇 Agent Note 的前三行必须精确为：

```markdown
# Agent Note: <标题>

Status: <status>
```

后接空行。`Status:` 取值有三种形式，且必须与所在生命周期目录一致——门禁会交叉校验：

- `Status: proposed`
- `Status: implemented`
- `Status: rejected — <为什么，一行>`

状态行不带日期、不带括号：文件名承载首次提出日期，git 承载其余一切；"以修正形式接受"是正文内容（在陈述决策处写明修正）。拒绝理由是唯一带内容的状态行，因为被否决笔记的裁决正是读者来此想看到的事实。

### 正文骨架

每篇 Agent Note 以 `## Problem` 开头——动机要写到脱离解决方案也能独立成立。后续取决于生命周期；重复出现的章节使用下列规范名称，其他真正定制的技术章节（包拓扑、线上契约、schema）可在必需章节之间自由书写。

#### `proposed/`

```markdown
## Problem
## Proposal
…定制章节…
## Alternatives considered
## Acceptance criteria
## Risks
```

`## Proposal` 是预期的变更，可以合理使用未来时态——计划、迁移步骤、开放问题在未构建时属于这里。`## Acceptance criteria` 定义可观察的完成状态。`## Risks` 覆盖可能出错的方面与明知放弃的方面。

#### `implemented/`

```markdown
## Problem
## Decision
…定制章节…
## Alternatives considered
## Consequences
```

`## Decision` 以现在时描述落地现实，整篇文件按 [implemented/AGENTS.md](implemented/AGENTS.md) 与其保持同步。`## Consequences` 记录权衡的代价**与**收益。提案式标题在这里是规范违规且被门禁拒绝：`## Proposal`、`## Plan`、`## Migration plan`、`## Acceptance criteria` 不得出现在 implemented 笔记中。`## Testing`、`## Deferred`、`## Related` 章节只要陈述现在时事实即可。

#### `rejected/`

被否决的笔记就是冻结的提案：保留其原有的提案期章节（包括 `## Acceptance criteria` 或 `## Plan`），裁决在 `Status:` 行上。只有头部块、`## Problem` 开头、`## Proposal` 章节与下面的 Alternatives 强制要求适用。

### Alternatives considered —— 必选

每篇 Agent Note 都带 `## Alternatives considered` 章节：每个真实备选方案及其落败原因，每个备选一段加粗引导，或每个有争议的方案用 `### Why not <X>?` 小节。没有记录击败对象的决策必然引来重新争论——这正是 Agent Note 要防止的失败。

备选方案是**记录的**，不是发明的。无法从记录重建备选方案的文件携带以下注释代替该章节：

```markdown
<!-- agent-note-format: alternatives-not-recorded (pre-format Agent Note) -->
```

### 生命周期迁移

在生命周期目录间移动文件意味着在同一变更中更新 `Status:` 行并重新满足该目录的骨架——否则门禁会拦截。具体而言：`proposed/` → `implemented/` 把 `## Proposal` 改写成现在时的 `## Decision`，把 `## Acceptance criteria` 与 `## Risks` 并入 `## Consequences`（或改写成现在时 `## Testing`/`## Verification` 章节描述现在钉住行为的东西），用落地现实替代计划。[implemented/AGENTS.md](implemented/AGENTS.md) 要求的改写由此变得机械化。`proposed/` → `rejected/` 只在 `Status:` 行加上理由并冻结文件。
