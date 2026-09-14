# Skill 路由与职责

`AI_WORKFLOW.md` 是唯一总入口。本文件只决定当前阶段应加载哪个专业 skill；所有模块遵守同一比赛项目目录和同一结果登记协议。

## 启动必读

- `docs/workflow/competition_retrospective.md`
- 当前比赛的 `project_config.yaml`
- 当前项目的 `docs/hub_state.md`

## 路由表

| 阶段 | 主 skill | 协作 skill | 主要产物 |
|---|---|---|---|
| 范围与官方规则 | `math-hub` | `math-compliance` | `docs/hub_state.md`、`docs/submission_checklist.md` |
| 题面与交付物 | `math-problem-reader` | `math-hub` | `docs/problem_brief.md`、`docs/deliverable_matrix.csv` |
| 文献与来源 | `math-literature` | `math-hub` | 引用登记与 claim 映射 |
| 模型设计 | `math-model` | `math-verifier` | `docs/model_handoff.md`、验证等级 |
| 数据、代码与结果 | `math-code` | `math-model` | `code/qX/`、`results/qX/`、运行与结果登记 |
| 图表证据 | `math-figure` | `math-table` | `figures/qX/`、图表证据登记 |
| 数学与结果核验 | `math-verifier` | `math-consistency` | 数学验证与数值诊断 |
| 分章写作 | `math-templates` | `math-table`、`math-consistency` | `paper/sections/*.md` |
| 摘要与评委审查 | `math-abstract` | `math-review`、`math-consistency` | 摘要、全文风险清单 |
| 排版与提交 | `math-compliance` | `math-review`、`math-consistency` | 最终格式、页数、匿名与提交清单 |

识别为本科组 C 题时，可额外加载 `cumcm-c-problem`，但其规则不得覆盖当年官方题面、统一目录协议和证据冻结规则。

## 四个硬确认点

`rapid` 模式只保留：

1. 题意与官方规则锁定；
2. 主模型路线；
3. 正式结果、指定表和核心图；
4. 最终论文与提交包冻结。

局部、可逆、低风险操作不重复向用户索要确认；会改变题意、主模型、结果真源、指定交付或最终提交的操作必须停止确认。

## 统一返回原则

- 模块只修改自己负责的产物。
- 发现上游缺口时返回 `math-hub`，不得猜测补齐。
- `registries/result_registry.csv` 管数值，`registries/claim_ledger.csv` 管论文结论状态。
- 任何 `paper_ready` 结果发生变化，都必须新建结果 ID 并重新做一致性核验。

