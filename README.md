# 数学建模赛前工作流工程

本工程用于把数学建模比赛中的赛题解析、数据处理、分问建模、代码求解、图表生成、模型检验和论文素材整理统一到一套可复现流程中。最终目标不是一次性生成完美论文，而是在 AI 分阶段给出判断、建议和取舍后，产出一份可靠的 `docs/paper_materials.md`，方便后续人工和 AI 共同打磨论文。

主流程不是“自动跑完再决策”，而是“AI 每一步先告诉你怎么判断、有哪些选项、推荐哪个，你确认后再执行”。

## 快速开始

1. 将赛题、附件和原始数据放入 `data/raw/`。
2. 如有外部补充数据，放入 `data/external/`，并在 `data/metadata/sources.json` 中记录来源。
3. 与 AI 按 `AI_WORKFLOW.md` 分阶段推进。需要检查骨架或运行已确认代码时，可以运行：

```bash
python code/run_all.py
```

4. 查看核心产物：
   - `docs/01_task_alignment.md`：逐问任务对齐
   - `docs/02_model_plan.md`：模型路线
   - `docs/results/q1_results.json` 等：分问结果
   - `figures/q1/` 等：分问图表
   - `docs/06_validation_report.md`：检验报告
   - `docs/paper_materials.md`：写论文前素材包

注意：`python code/run_all.py` 是检查与执行工具，不是替代 AI 决策的主流程。

## 这个仓库需要哪些东西

公开仓库只保留运行工作流所需的轻量模板文件。

真正必须使用的是：

- `AI_WORKFLOW.md`：AI 决策门控主流程。
- `project_config.yaml`：路径和流程配置。
- `code/`：确认方案后的求解、可视化和验证代码骨架。
- `docs/`：题意、模型路线、决策日志、结果和论文素材模板。
- `data/`：本地赛题和数据放置位置，仓库只保留空目录占位。
- `figures/`：本地图表输出位置，仓库只保留空目录占位。



## 目录原则

- `data/` 只放数据和数据元信息。
- `code/` 只放可运行代码。
- `figures/` 只放论文图表。
- `docs/` 放题意、模型、结果、验证和论文素材。

工作流主入口统一使用 `AI_WORKFLOW.md`。

每一问固定使用一组代码：

```text
code/q1/solve_q1.py
code/q1/visualize_q1.py
code/q2/solve_q2.py
code/q2/visualize_q2.py
code/q3/solve_q3.py
code/q3/visualize_q3.py
```

论文中引用代码、图表和结果时，应优先按问题编号定位。
