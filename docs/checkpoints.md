# 工作流检查点

本文件用于记录 AI 工作流中等待用户确认的节点。每个关键阶段进入执行或落盘前，都必须有一个检查点。

## 状态说明

| 状态 | 含义 |
|---|---|
| `pending` | 尚未开始 |
| `running` | AI 正在分析或生成候选方案 |
| `waiting_user_decision` | 等待用户确认、修改或否决 |
| `approved` | 用户已确认，可以执行或落盘 |
| `rejected` | 用户否决，需要重新分析 |
| `completed` | 已执行并生成对应文件 |

## 检查点列表

| 编号 | 阶段 | 决策内容 | AI 推荐 | 用户回复 | 状态 | 关联文件 |
|---|---|---|---|---|---|---|
| CP-001 | 题意解析 | 每问任务拆分是否正确 | 待补充 | 待确认 | pending | `docs/01_task_alignment.md` |
| CP-002 | 模型选择 | 每问主模型和基线模型是否确认 | 待补充 | 待确认 | pending | `docs/02_model_plan.md` |
| CP-003 | 数据预处理 | 缺失、异常、编码、单位和清洗策略 | 待补充 | 待确认 | pending | `docs/03_data_report.md` |
| CP-004 | 代码实现 | 每问求解代码结构和输出字段 | 待补充 | 待确认 | pending | `code/q*/solve_q*.py` |
| CP-005 | 可视化 | 每张图服务哪个论文结论 | 待补充 | 待确认 | pending | `docs/05_visualization_plan.md` |
| CP-006 | 模型检验 | 检验方法、通过标准和补实验计划 | 待补充 | 待确认 | pending | `docs/06_validation_report.md` |
| CP-007 | 论文素材包 | 是否足够进入论文阶段 | 待补充 | 待确认 | pending | `docs/paper_materials.md` |
| CP-008 | 论文章节队列 | 每个章节文件、职责和素材来源 | 待补充 | 待确认 | pending | `paper/reviews/section_queue.md` |

## 使用规则

- AI 每到一个关键阶段，先新增或更新检查点。
- 用户确认后，将状态改为 `approved`，执行完成后改为 `completed`。
- 用户否决后，将状态改为 `rejected`，并在 `docs/findings.md` 或 `docs/decision_log.md` 中记录原因。
- 不允许跳过 `waiting_user_decision` 直接进入 `completed`。
