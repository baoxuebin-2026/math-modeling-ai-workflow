# 论文章节队列模板

本文件用于论文阶段开始前，由 AI 根据当前赛题和 `docs/paper_materials.md` 生成实际写作队列。队列必须先让用户确认，确认后才开始写第一章。

建议输出路径：

```text
paper/reviews/section_queue.md
```

## 队列生成规则

- 章节顺序以 `paper/templates/paper_outline.md` 为准。
- 问题数量以 `docs/01_task_alignment.md` 为准。
- 每个问题原则上对应一个独立的模型建立与求解章节文件。
- 如果某一问内容特别长，可以拆成“模型建立”“结果与验证”两个文件，但必须先说明理由并让用户确认。
- 如果某一问只是前一问的扩展，仍应保留独立文件，方便论文中定位该问。
- 只保留数学建模论文正文、参考文献和附录所需章节。

## 队列表格式

| 顺序 | 章节文件 | 论文位置 | 本章任务 | 主要来源 | 预计图表/结果 | 状态 |
|---|---|---|---|---|---|---|
| 00 | `paper/sections/00_title_abstract.md` | 标题、摘要、关键词 | 先写可修改摘要草稿，最终再二次优化 | `docs/paper_materials.md` | 各问核心结果 | 待确认 |
| 01 | `paper/sections/01_problem_restatement.md` | 一、问题重述 | 重述题意、任务和约束 | `docs/00_problem_extracted.md`、`docs/01_task_alignment.md` | 无 | 待确认 |
| 02 | `paper/sections/02_problem_analysis.md` | 二、问题分析 | 逐问说明难点、建模动机和验证思路 | `docs/01_task_alignment.md`、`docs/02_model_plan.md` | 技术路线图，如有 | 待确认 |
| 03 | `paper/sections/03_assumptions_notations.md` | 三、模型假设；四、符号说明 | 写假设依据、影响和符号表 | `docs/02_model_plan.md`、`docs/paper_materials.md` | 符号表 | 待确认 |
| 04 | `paper/sections/04_q1_modeling_solution.md` | 5.1 问题一模型的建立与求解 | 写问题一的基线模型、改进模型、求解、结果和检验 | `docs/results/q1_results.json`、`docs/figures/q1_figures.md`、`code/q1/` | Q1 图表和结果 | 待确认 |
| 05 | `paper/sections/05_q2_modeling_solution.md` | 5.2 问题二模型的建立与求解 | 写问题二如何继承问题一，并加入风险、误差、情景或约束变化 | `docs/results/q2_results.json`、`docs/figures/q2_figures.md`、`code/q2/` | Q2 图表和结果、与Q1对比 | 待确认 |
| 06 | `paper/sections/06_q3_modeling_solution.md` | 5.3 问题三模型的建立与求解 | 写问题三如何加入现实因素、多因素、相关性、替代互补或综合评价 | `docs/results/q3_results.json`、`docs/figures/q3_figures.md`、`code/q3/` | Q3 图表和结果、与Q2对比 | 待确认 |
| 90 | `paper/sections/90_model_evaluation_optimization.md` | 六、模型的评价及优化 | 写优点、缺点、推广和优化 | `docs/06_validation_report.md`、`docs/paper_materials.md` | 验证结果、敏感性分析 | 待确认 |
| 91 | `paper/sections/91_references.md` | 参考文献 | 整理真实引用 | 已确认参考资料 | 无 | 待确认 |
| 92 | `paper/sections/92_appendix.md` | 附录 | 列数据说明、补充图表和核心代码文件 | `code/`、`data/metadata/`、`docs/figures/` | 附录图表和代码列表 | 待确认 |

## 用户确认格式

AI 生成实际队列后，应向用户确认：

```text
请确认：
1. 这些章节是否符合本次数模比赛格式。
2. 哪些章节需要拆分或合并。
3. 哪些图表必须放正文，哪些放附录。
4. 是否可以开始生成第一个章节。
```
