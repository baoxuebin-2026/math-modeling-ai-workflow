# 论文撰写阶段总工作流

本文件用于指导 AI 将 `docs/paper_materials.md` 转化为论文草稿。它属于论文阶段，不替代前面的建模、求解、检验工作。

核心要求：论文必须逐章生成、逐章核对、逐章确认。没有用户确认，不进入下一章；没有完成全文二次核对，不把草稿视为可提交终稿。

## 输入

必须读取：

- `docs/paper_materials.md`
- `docs/01_task_alignment.md`
- `docs/02_model_plan.md`
- `docs/03_data_report.md`
- `docs/04_result_summary.md`
- `docs/05_visualization_plan.md`
- `docs/06_validation_report.md`
- `docs/figures/`
- `docs/results/`
- `paper/templates/paper_outline.md`
- `paper/templates/section_queue.md`
- `paper/workflow/section_gate.md`
- `paper/workflow/merge_gate.md`
- `paper/workflow/final_review_gate.md`

如果上述文件缺失，AI 应先指出缺口，而不是凭空写论文。

## 输出

分章节草稿输出到 `paper/sections/`，建议队列如下：

- `paper/sections/00_title_abstract.md`
- `paper/sections/01_problem_restatement.md`
- `paper/sections/02_problem_analysis.md`
- `paper/sections/03_assumptions_notations.md`
- `paper/sections/04_q1_modeling_solution.md`
- `paper/sections/05_q2_modeling_solution.md`
- `paper/sections/06_q3_modeling_solution.md`
- `paper/sections/07_q4_modeling_solution.md`，仅在题目有第四问时保留。
- `paper/sections/90_model_evaluation_optimization.md`
- `paper/sections/91_references.md`
- `paper/sections/92_appendix.md`

核对与合并输出：

- `paper/reviews/section_review_*.md`
- `paper/drafts/final_paper_draft.md`
- `paper/reviews/final_review_round1.md`
- `paper/reviews/final_review_round2.md`

## 强制执行顺序

1. AI 先根据 `docs/01_task_alignment.md` 和 `paper/templates/paper_outline.md` 生成“章节队列”，说明每个章节读取哪些素材、解决什么写作任务、预计引用哪些图表和结果。
2. 用户确认章节队列后，AI 才开始写第一个章节。
3. AI 每次只写一个 `paper/sections/*.md` 文件。
4. 每写完一个章节，AI 必须按 `paper/workflow/section_gate.md` 做自检，生成对应 `paper/reviews/section_review_*.md`。
5. AI 把本章的主要内容、证据来源、待用户决策点列出来，等待用户确认或修改。
6. 用户确认后，AI 才进入下一章节。
7. 全部章节确认后，AI 按 `paper/workflow/merge_gate.md` 合并全文。
8. 合并后先做第一轮全文核对，修正文内引用、编号、符号、图表顺序和章节衔接。
9. 再按 `paper/workflow/abstract_gate.md` 重写标题、摘要和关键词。
10. 最后做第二轮全文核对，确认摘要中的每个数值、模型名、结论都能在正文找到。

## 章节写作原则

- 每一问的论文内容应对应 `code/qx/solve_qx.py` 和 `code/qx/visualize_qx.py`。
- 每一问的模型章节内部必须包含建模对象、变量、核心公式、求解步骤、结果、图表解释和检验说明。
- 数据预处理不强行单独成大章，除非题目本身以数据处理为核心；通常写进对应问题的模型建立小节。
- 小节标题应根据问题实际内容命名，不机械使用“模型构建/模型求解/结果分析”。
- 结果必须量化，避免“效果良好”“明显提升”等空话。
- 每个图表后必须有文字解读，并说明它支撑论文中的哪个结论。
- 不足要具体，但不能否定核心模型。

## 用户决策点

AI 在以下位置必须停下来让用户决策：

- 章节队列是否符合比赛格式。
- 是否需要按 `paper/templates/section_queue.md` 拆分、合并或重排章节文件。
- 每章是否保留、删减或调整标题。
- 每问模型章节是否把重点放在“模型原理”“求解过程”“结果解释”中的哪一侧。
- 图表是否放在正文、附录或删除。
- 摘要中哪些结果作为核心亮点。
- 全文二次核对后是否接受修改建议。

## 旧论文参考方式

已上传的旧论文只作为格式参考，主要参考：

- 标题、摘要、关键词的位置。
- 问题重述、问题分析、假设、符号、模型建立与求解、模型评价及优化、参考文献、附录的章节顺序。
- 图表编号和正文引用方式。
- 附录代码说明方式。

不要参考其中的空泛表达、错误代码、过度夸张结果或不严谨论证。
