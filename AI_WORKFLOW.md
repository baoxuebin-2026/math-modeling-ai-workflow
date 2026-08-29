# AI 工作流总入口

当 AI 接手本工程时，必须把本文件作为唯一总入口读取。本工程目标是完成“写论文之前的所有工作”，即通过 AI 分阶段判断、解释、推荐和执行，产出可复核、可修改、可写入论文的建模素材包，而不是让 Python 流水线替代 AI 的建模决策。各阶段 skill 的职责和调用顺序以 `docs/workflow/skill_routing.md` 为准。

正式使用的 skill 位于 `skills/`；先读取 `skills/README.md`，再按路由加载最小必要模块。

## 总目标

建模阶段最终必须生成：

- `docs/paper_materials.md`

该文件应汇总题意、数据、模型、公式、算法、结果、图表说明、模型检验、敏感性分析和结论要点，为后续论文写作提供完整素材。

论文写作阶段从 `paper/README.md` 开始，目标是把 `docs/paper_materials.md` 转化为可反复修改的论文草稿。

## 核心原则：AI 决策门控

本工程不是“先自动跑完，再让用户看结果”。每个关键阶段必须由 AI 先给出判断、理由和可选方案，用户确认后才能进入下一阶段。所有判断都必须以最终论文是否逻辑完整、证据充分、表达清晰为准，而不是以代码是否跑通为准。

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
- 工作流状态记录：`docs/checkpoints.md`
- 跨阶段发现记录：`docs/findings.md`
- 实验与运行记录：`docs/experiment_log.md`
- 当前确认方案契约：`docs/active_solution_contract.md`
- 论文结论证据映射：`docs/claim_evidence_map.md`
- 工作流门控清单：`docs/workflow/*_gate.md`
- 论文写作工作流：`paper/`
- 分章节论文草稿：`paper/sections/`
- 合并后论文草稿：`paper/drafts/`
- 论文核对记录：`paper/reviews/`

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

1. 读取 `project_config.yaml`、`docs/checkpoints.md`、`docs/findings.md`、`docs/active_solution_contract.md` 与赛题/附件。
2. 读取 `docs/workflow/skill_routing.md`，锁定当前阶段的主 skill 和允许协作 skill，不得同时启动多个总流程。
3. AI 必须读取 `docs/workflow/national_prize_gate.md`，先从最终论文倒推题目主线、各问递进关系、隐含评分点、可创新位置和主要风险。
3. AI 解析题意，说明每一问可能的理解，生成 `docs/00_problem_extracted.md` 草稿。
4. AI 给出逐问任务对齐表，指出不确定点、前后问继承关系和论文主线位置，等待用户确认，确认后生成 `docs/01_task_alignment.md`。
5. AI 对每一问提出模型候选、优缺点、适配性评分、基线-改进-防守结构和推荐主线，等待用户确认，确认后生成 `docs/02_model_plan.md`。
6. AI 说明数据清洗策略、异常值处理、缺失值处理和变量口径，等待用户确认，确认后执行清洗并生成 `docs/03_data_report.md`。
7. AI 为每一问设计求解代码结构，说明输入、输出、算法步骤、基线对照、改进点和预期结果，等待用户确认，确认后写入或修改：
   - `code/q1/solve_q1.py`
   - `code/q2/solve_q2.py`
   - `code/q3/solve_q3.py`
8. AI 必须先按 `docs/workflow/figure_planning_gate.md` 为每一问生成“逐问图表证据链表”，说明论文要证明的结论、必画图、可选图、数据来源、论文放置位置和不画什么，等待用户确认。
9. 用户确认图表证据链后，AI 才能写入或修改可视化代码：
   - `code/q1/visualize_q1.py`
   - `code/q2/visualize_q2.py`
   - `code/q3/visualize_q3.py`
10. 在用户确认代码和图表方案后，才运行求解与可视化：
   - `code/q1/solve_q1.py` → `docs/results/q1_results.json`
   - `code/q1/visualize_q1.py` → `figures/q1/` 与 `docs/figures/q1_figures.md`
   - Q2、Q3 同理。
11. Python 生成图片后，AI 必须调用图片查看功能逐张打开 PNG，不得只看文件是否存在或代码是否运行成功。若发现空图、文字重叠、图例遮挡、标签越界、默认风格粗糙、数据缺失或结论不清，应优先修改 `code/q*/visualize_q*.py`，重新运行生成图片，并再次查看，直到达到论文可用质量。
12. AI 解读运行结果，说明结果是否合理、是否支撑论文主线、是否需要换模型、补实验或重画图，确认后生成 `docs/04_result_summary.md`，并更新 `docs/experiment_log.md` 与 `docs/findings.md`。
13. AI 设计验证与敏感性分析，等待用户确认，确认后执行并生成 `docs/06_validation_report.md`，并更新 `docs/claim_evidence_map.md`。
14. AI 汇总已经确认的全部内容，生成 `docs/paper_materials.md`。生成前必须确认 `docs/active_solution_contract.md` 与 `docs/claim_evidence_map.md` 已更新，并按 `docs/workflow/national_prize_gate.md` 检查论文主线、创新点和证据链是否足够。
15. 若用户进入论文写作阶段，读取 `paper/README.md` 和 `paper/workflow/paper_writing_workflow.md`，先生成章节队列，再逐章生成 `paper/sections/` 下的 Markdown 草稿。每章确认后才能进入下一章，全部章节确认后合并为 `paper/drafts/final_paper_draft.md`；生成该 Markdown 论文草稿后停止，不生成 Word、PDF 或其他排版文件。

## 阶段门控清单

AI 在对应阶段必须读取并遵守以下 checklist：

| 阶段 | 门控文件 | 用途 |
|---|---|---|
| 国奖导向 | `docs/workflow/national_prize_gate.md` | 从最终论文倒推建模主线、创新递进、证据链和风险防守 |
| 数据预处理 | `docs/workflow/data_preprocessing_gate.md` | 判断是否需要预处理、选择方法、记录前后对比 |
| 获奖论文启发 | `docs/workflow/award_paper_insights.md` | 提炼基线、递进、风险、对比和证据链思路 |
| 模型选择 | `docs/workflow/modeling_decision_gate.md` | 给出基础方案/创新方案、评分、推荐与用户确认点 |
| 模型检验 | `docs/workflow/validation_gate.md` | 判断检验必要性、选择检验方法、输出通过/未通过和改进建议 |
| 素材包生成 | `docs/workflow/materials_gate.md` | 确认结果、图表、检验和用户决策足够进入论文阶段 |
| 图表规划 | `docs/workflow/figure_planning_gate.md` | 按每问论文结论反推必画图、可选图和不画什么 |
| 可视化 | `docs/workflow/05_visualization_rules.md` | 约束图表用途、命名、说明文字和论文位置 |
| 图片质量 | `paper/workflow/figure_quality_gate.md` | 要求 Python 出图后逐张查看，发现问题回改代码并重生成 |
| 代码结构 | `docs/workflow/code_contract.md` | 保证每问求解代码与可视化代码职责分离 |
| 论文写作 | `paper/workflow/paper_writing_workflow.md` | 将建模素材包转为论文草稿 |
| 章节队列 | `paper/templates/section_queue.md` | 先确认每个章节文件的顺序、职责和素材来源 |
| 单章验收 | `paper/workflow/section_gate.md` | 每章生成后做来源追溯和用户确认 |
| 章节合并 | `paper/workflow/merge_gate.md` | 将已确认章节合并为整篇草稿 |
| 摘要优化 | `paper/workflow/abstract_gate.md` | 摘要、标题、关键词二次优化 |
| 论文草稿检查 | `paper/workflow/final_review_gate.md` | Markdown 全文一致性和逻辑检查；不执行排版验收 |

## 自动脚本的定位

`python code/run_all.py` 只用于快速检查目录、占位文件和已确认代码是否能跑通。它不是主决策流程。

主流程应由 AI 对话推进，阶段文档应记录 AI 的判断和用户确认。代码只有在方案确认后才负责复现计算与出图。

`code/01_initialize_docs.py` 默认只补齐缺失的初始模板，不覆盖已经确认的阶段文档。只有明确需要重置模板时，才使用 `--force`。

`docs/paper_materials.md` 生成前必须读取 `docs/workflow/materials_gate.md`。如果素材包仍包含大量 `待确认`、`待补充` 或 `待用户决策`，它只能作为过程草稿，不能进入论文阶段。

## 用户决策点

AI 必须显式暴露以下决策，不能擅自隐藏：

- 每一问的题型判断。
- 每一问的主模型选择。
- 是否采用复杂模型或组合模型。
- 国奖级创新点放在哪一层，以及是否真的服务题目。
- 每一问采用哪些图表。
- 结果单位、精度和统计口径。
- 验证方法是否足够。
- 论文主创新点应放在哪里。
- 论文每个章节是否通过单章验收。
- 摘要二次优化后是否接受全文第二轮核对建议。

每一次关键决策都应记录到：

- `docs/decision_log.md`
- `docs/checkpoints.md`

每一次模型运行、参数扰动、图表生成或检验实验都应记录到：

- `docs/experiment_log.md`

每一个会影响后续判断的发现都应记录到：

- `docs/findings.md`

每一个准备写入论文摘要或核心结论的说法都应记录到：

- `docs/claim_evidence_map.md`

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
- `docs/checkpoints.md`
- `docs/findings.md`
- `docs/experiment_log.md`
- `docs/active_solution_contract.md`
- `docs/claim_evidence_map.md`
- `docs/paper_materials.md`
- `paper/drafts/final_paper_draft.md`
- 每个已启用问题的 `docs/results/qx_results.json`
- 每个已启用问题的 `docs/figures/qx_figures.md`

如果数据或赛题暂缺，允许生成占位模板，但必须在文档中明确标记 `待补充`。
