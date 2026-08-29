# 数学建模赛前工作流工程

本工程用于把数学建模比赛中的赛题解析、数据处理、分问建模、代码求解、图表生成、模型检验和论文素材整理统一到一套可复现流程中。最终目标不是一次性生成完美论文，而是在 AI 分阶段给出判断、建议和取舍后，产出一份可靠的 `docs/paper_materials.md`，方便后续人工和 AI 共同打磨论文。

主流程不是“自动跑完再决策”，而是“AI 每一步先告诉你怎么判断、有哪些选项、推荐哪个，你确认后再执行”。

## 快速开始

1. 将赛题、附件和原始数据放入 `data/raw/`。
2. 如有外部补充数据，放入 `data/external/`，并在 `data/metadata/sources.json` 中记录来源。
3. 打开 `project_config.yaml`，填写比赛信息和问题数量；再与 AI 按 `AI_WORKFLOW.md` 分阶段推进。

4. 查看核心产物：
   - `docs/01_task_alignment.md`：逐问任务对齐
   - `docs/02_model_plan.md`：模型路线
   - `docs/active_solution_contract.md`：当前确认方案
   - `docs/experiment_log.md`：模型运行与检验记录
   - `docs/claim_evidence_map.md`：论文结论与证据映射
   - `docs/results/q*_results.json`：分问结果
   - `figures/q*/`：分问图表
   - `docs/06_validation_report.md`：检验报告
   - `docs/paper_materials.md`：写论文前素材包

注意：自动脚本只能复现已经确认的模型与图表，不能替代 AI 的建模判断和用户决策。

## 这个仓库需要哪些东西

公开仓库只保留运行工作流所需的轻量模板文件。

真正必须使用的是：

- `AI_WORKFLOW.md`：AI 决策门控主流程。
- `project_config.yaml`：路径和流程配置。
- `code/`：确认方案后的求解、可视化和验证代码骨架。
- `docs/`：题意、模型路线、决策日志、结果和论文素材模板。
- `paper/`：把 `docs/paper_materials.md` 转化为论文草稿的逐章写作工作流。
- `data/`：本地赛题和数据放置位置，仓库只保留空目录占位。
- `figures/`：本地图表输出位置，仓库只保留空目录占位。

## 阶段门控文件

`docs/workflow/` 中的文件是 AI 做阶段判断时必须遵守的 checklist：

- `data_preprocessing_gate.md`：数据预处理是否必要、如何处理、如何对比。
- `award_paper_insights.md`：获奖论文中可复用的建模递进、风险情景、对比验证和证据链思路。
- `modeling_decision_gate.md`：每问基础模型、创新模型、评分和用户确认。
- `validation_gate.md`：模型是否需要检验、检验方法、通过标准和改进建议。
- `materials_gate.md`：确认模型、结果、图表和检验足够汇总为论文素材包。
- `05_visualization_rules.md`：图表选择、命名、说明文字和论文位置。
- `code_contract.md`：`solve_qx.py` 与 `visualize_qx.py` 的职责边界。



## 目录原则

- `data/` 只放数据和数据元信息。
- `code/` 只放可运行代码。
- `figures/` 只放论文图表。
- `docs/` 放题意、模型、结果、验证和论文素材。
- `paper/` 放论文撰写流程、模板和草稿。

工作流主入口统一使用 `AI_WORKFLOW.md`。

建模阶段完成后，论文写作阶段从 `paper/README.md` 开始。

论文阶段不是一次性生成整篇，而是：

```text
章节队列确认 → 单章生成 → 单章核对 → 用户确认 → 下一章 → 合并全文 → 摘要二次优化 → 全文二次核对
```

分章节草稿放在 `paper/sections/`，合并后的整篇草稿放在 `paper/drafts/`，核对记录放在 `paper/reviews/`。

每一问按配置生成一组代码：

```text
code/q1/solve_q1.py
code/q1/visualize_q1.py
code/q2/solve_q2.py
code/q2/visualize_q2.py
code/q3/solve_q3.py
code/q3/visualize_q3.py
```

论文中引用代码、图表和结果时，应优先按问题编号定位。

比赛推进过程中还应维护：

- `docs/checkpoints.md`：每个等待用户确认的检查点。
- `docs/findings.md`：跨阶段发现和避坑记录。
- `docs/experiment_log.md`：每次运行、实验、检验和图表生成记录。
- `docs/active_solution_contract.md`：当前已经确认的模型主线。
- `docs/claim_evidence_map.md`：论文结论、结果、图表和检验之间的证据链。
