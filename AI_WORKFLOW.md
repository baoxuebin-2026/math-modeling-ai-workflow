# AI 工作流总入口

当 AI 接手本工程时，必须把本文件作为唯一总入口读取。本工程目标是完成“写论文之前的所有工作”，即通过 AI 分阶段判断、解释、推荐和执行，产出可复核、可修改、可写入论文的建模素材包，而不是让 Python 流水线替代 AI 的建模决策。

## 总目标

最终必须生成：

- `docs/paper_materials.md`

该文件应汇总题意、数据、模型、公式、算法、结果、图表说明、模型检验、敏感性分析和结论要点，为后续论文写作提供完整素材。

## 核心原则：AI 决策门控

本工程不是“先自动跑完，再让用户看结果”。每个关键阶段必须由 AI 先给出判断、理由和可选方案，用户确认后才能进入下一阶段。

AI 必须按以下模式工作：

```text
阶段输入 → AI 分析 → AI 给出 2-3 个可选方案 → AI 推荐一个方案 → 用户确认/修改 → 执行或落盘 → 进入下一阶段
```

如果用户没有确认，AI 可以继续解释和比较方案，但不应擅自把某个模型、图表或结果口径定为最终方案。

## 强制目录协议

- 原始赛题与附件：`data/raw/`
- 外部补充数据：`data/external/`
- 清洗后数据：`data/processed/`
- 数据来源与字典：`data/metadata/`
- 分问求解代码：`code/q*/solve_q*.py`
- 分问可视化代码：`code/q*/visualize_q*.py`
- 公共代码：`code/common/`
- 图表：`figures/q*/` 与 `figures/validation/`
- 结果 JSON：`docs/results/`
- 图表说明：`docs/figures/`
- 阶段文档：`docs/00_*.md` 至 `docs/06_*.md`
- 工作流门控清单：`docs/workflow/*_gate.md`

禁止新增 `problem_files/`、`crawled_data/`、`paper_output/` 作为主流程目录。旧资料中出现这些名称时，必须映射到本协议：

| 旧名称 | 新名称 |
|---|---|
| `problem_files/` | `data/raw/` |
| `crawled_data/` | `data/external/` |
| `paper_output/data_cleaned/` | `data/processed/` |
| `paper_output/figures/` | `figures/` |
| `paper_output/final_paper.md` | 后续论文阶段产物，当前阶段不生成 |
| `paper_output/tasks.json` | `docs/workflow/tasks.json` |

## 标准交互顺序

1. 读取 `project_config.yaml` 与赛题/附件。
2. AI 解析题意，说明每一问可能的理解，生成 `docs/00_problem_extracted.md` 草稿。
3. AI 给出逐问任务对齐表，指出不确定点，等待用户确认，确认后生成 `docs/01_task_alignment.md`。
4. AI 对每一问提出模型候选、优缺点、适配性评分和推荐主线，等待用户确认，确认后生成 `docs/02_model_plan.md`。
5. AI 说明数据清洗策略、异常值处理、缺失值处理和变量口径，等待用户确认，确认后执行清洗并生成 `docs/03_data_report.md`。
6. AI 为每一问设计求解代码结构，说明输入、输出、算法步骤和预期结果，等待用户确认，确认后写入或修改：
   - `code/q1/solve_q1.py`
   - `code/q2/solve_q2.py`
   - `code/q3/solve_q3.py`
7. AI 为每一问推荐图表清单，说明每张图服务论文哪个结论，等待用户确认，确认后写入或修改：
   - `code/q1/visualize_q1.py`
   - `code/q2/visualize_q2.py`
   - `code/q3/visualize_q3.py`
8. 在用户确认代码和图表方案后，才运行求解与可视化：
   - `code/q1/solve_q1.py` → `docs/results/q1_results.json`
   - `code/q1/visualize_q1.py` → `figures/q1/` 与 `docs/figures/q1_figures.md`
   - Q2、Q3 同理。
9. AI 解读运行结果，说明结果是否合理、是否需要换模型或补实验，确认后生成 `docs/04_result_summary.md`。
10. AI 设计验证与敏感性分析，等待用户确认，确认后执行并生成 `docs/06_validation_report.md`。
11. AI 汇总已经确认的全部内容，生成 `docs/paper_materials.md`。

## 阶段门控清单

AI 在对应阶段必须读取并遵守以下 checklist：

| 阶段 | 门控文件 | 用途 |
|---|---|---|
| 数据预处理 | `docs/workflow/data_preprocessing_gate.md` | 判断是否需要预处理、选择方法、记录前后对比 |
| 模型选择 | `docs/workflow/modeling_decision_gate.md` | 给出基础方案/创新方案、评分、推荐与用户确认点 |
| 模型检验 | `docs/workflow/validation_gate.md` | 判断检验必要性、选择检验方法、输出通过/未通过和改进建议 |
| 可视化 | `docs/workflow/05_visualization_rules.md` | 约束图表用途、命名、说明文字和论文位置 |
| 代码结构 | `docs/workflow/code_contract.md` | 保证每问求解代码与可视化代码职责分离 |

## 自动脚本的定位

`python code/run_all.py` 只用于快速检查目录、占位文件和已确认代码是否能跑通。它不是主决策流程。

主流程应由 AI 对话推进，阶段文档应记录 AI 的判断和用户确认。代码只有在方案确认后才负责复现计算与出图。

## 用户决策点

AI 必须显式暴露以下决策，不能擅自隐藏：

- 每一问的题型判断。
- 每一问的主模型选择。
- 是否采用复杂模型或组合模型。
- 每一问采用哪些图表。
- 结果单位、精度和统计口径。
- 验证方法是否足够。
- 论文主创新点应放在哪里。

每一次关键决策都应记录到：

- `docs/decision_log.md`

## 代码命名规则

每一问必须有：

- `solve_qx.py`：只负责求解，输出结构化结果。
- `visualize_qx.py`：只负责画图，读取结果和数据。

求解代码不得直接把图表散落到根目录；可视化代码不得重新实现核心模型逻辑。

## 完成标准

流程完成时至少应存在：

- `docs/01_task_alignment.md`
- `docs/02_model_plan.md`
- `docs/03_data_report.md`
- `docs/04_result_summary.md`
- `docs/05_visualization_plan.md`
- `docs/06_validation_report.md`
- `docs/paper_materials.md`
- 每个已启用问题的 `docs/results/qx_results.json`
- 每个已启用问题的 `docs/figures/qx_figures.md`

如果数据或赛题暂缺，允许生成占位模板，但必须在文档中明确标记 `待补充`。
