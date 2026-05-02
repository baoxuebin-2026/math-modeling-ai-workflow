---
name: "pre-paper-workflow-orchestrator"
description: "数学建模写论文前总控流程：读取赛题与数据，分问求解、分问可视化、验证并生成 docs/paper_materials.md。Invoke when 用户希望完成写论文之前的全部建模、代码、图表和素材整理工作。"
---

# 写论文前工作流总控

## 目标

本技能是当前工程的唯一主流程入口。它负责通过 AI 分阶段决策，把赛题解析、数据处理、分问建模、代码求解、分问可视化、结果汇总和模型检验串联起来，最终生成：

- `docs/paper_materials.md`

该文件是后续论文写作与人工调稿的素材底座，不是最终论文。

## 核心原则：先 AI 判断，再执行

本技能不应直接用脚本替代 AI 回答。每个关键阶段必须先由 AI 输出：

- 当前阶段判断
- 2-3 个可选方案
- 推荐方案
- 推荐理由
- 风险与备选
- 需要用户确认的问题

用户确认后，才允许写入代码、运行脚本或进入下一阶段。

## 强制目录协议

- 赛题与原始附件：`data/raw/`
- 外部补充数据：`data/external/`
- 清洗数据：`data/processed/`
- 分问代码：`code/q1/`、`code/q2/`、`code/q3/`
- 公共代码：`code/common/`
- 分问图表：`figures/q1/`、`figures/q2/`、`figures/q3/`
- 验证图表：`figures/validation/`
- 结果文件：`docs/results/`
- 图表说明：`docs/figures/`
- 最终素材包：`docs/paper_materials.md`

不要在主流程中使用旧目录 `problem_files/`、`crawled_data/`、`paper_output/`。

## 脚本定位

`python code/run_all.py` 只用于运行已经确认的代码、检查目录完整性和生成占位素材。它不是主决策流程。

```bash
python code/run_all.py
```

当用户要求“完成整个任务”时，应先按 `AI_WORKFLOW.md` 的阶段门控推进，而不是立刻一键跑完。

## 分问代码契约

每一问必须拆成两个文件：

- `solve_qx.py`：求解模型，输出 `docs/results/qx_results.json`。
- `visualize_qx.py`：读取结果与数据，输出 `figures/qx/` 和 `docs/figures/qx_figures.md`。

论文位置与代码位置必须一一对应：

| 论文部分 | 求解代码 | 可视化代码 | 图表目录 |
|---|---|---|---|
| 问题一模型与结果 | `code/q1/solve_q1.py` | `code/q1/visualize_q1.py` | `figures/q1/` |
| 问题二模型与结果 | `code/q2/solve_q2.py` | `code/q2/visualize_q2.py` | `figures/q2/` |
| 问题三模型与结果 | `code/q3/solve_q3.py` | `code/q3/visualize_q3.py` | `figures/q3/` |

## 用户必须决策的内容

AI 可以给建议，但以下内容必须显式留给用户确认：

- 每问的题型判断。
- 每问的主模型选择。
- 模型复杂度是否值得增加。
- 核心创新点放在哪一问。
- 图表是否保留。
- 结果单位、精度与统计口径。
- 验证方法是否足够。

每次确认结果应记录到：

- `docs/decision_log.md`

## 完成标准

流程完成后至少应存在：

- `docs/01_task_alignment.md`
- `docs/02_model_plan.md`
- `docs/03_data_report.md`
- `docs/results/q1_results.json`
- `docs/results/q2_results.json`
- `docs/results/q3_results.json`
- `docs/figures/q1_figures.md`
- `docs/figures/q2_figures.md`
- `docs/figures/q3_figures.md`
- `docs/06_validation_report.md`
- `docs/paper_materials.md`

如果当前没有赛题或数据，可以生成占位模板，但必须标记为“待补充”。
