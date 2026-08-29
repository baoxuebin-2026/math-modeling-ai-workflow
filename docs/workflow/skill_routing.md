# Skill 路由与职责

本文件把项目工作流与专业 skill 对齐。`AI_WORKFLOW.md` 是唯一总入口；skill 只负责当前阶段的专业任务，不得改变阶段顺序、越权写入其他阶段产物或重新定义最终交付物。

## 总路由

| 工作流阶段 | 主 skill | 允许协作 skill | 核心输入 | 核心输出 |
|---|---|---|---|---|
| 启动与范围锁定 | `math-hub` | `math-problem-reader` | 赛题、附件、官方规则 | 状态、范围与阻塞项 |
| 题面解读 | `math-problem-reader` | `math-hub` | 题面、附件、交付要求 | `docs/00_problem_extracted.md`、`docs/01_task_alignment.md` |
| 文献与案例启发（可选） | `math-literature` | `math-hub` | 已锁定的问题和关键词 | 文献证据记录 |
| 模型设计 | `math-model` | `math-literature`、`math-verifier` | 题意锁定、数据、候选方法 | `docs/02_model_plan.md`、模型交接和验证计划 |
| 数据与代码 | `math-code` | `math-model`、`math-verifier` | 已确认模型交接、数据 | `docs/03_data_report.md`、代码、结果登记和运行记录 |
| 图表证据 | `math-figure` | `math-code`、`math-table` | 已确认结果和 claim | 图表、`docs/05_visualization_plan.md`、图表证据记录 |
| 数学与结果核验 | `math-verifier` | `math-consistency` | 公式、单位、约束、结果和边界案例 | `docs/06_validation_report.md`、核验记录 |
| 结果汇总与素材包 | `math-hub` | `math-consistency`、`math-review` | 结果、图表、验证和证据链 | `docs/04_result_summary.md`、`docs/paper_materials.md` |
| Markdown 论文写作 | `math-templates` | `math-abstract`、`math-consistency`、`math-review` | `docs/paper_materials.md` 和已确认证据 | `paper/sections/*.md`、`paper/drafts/final_paper_draft.md` |

## 统一规则

1. `math-hub` 负责状态、阻塞项和下一模块；不替代建模、代码或写作。
2. `math-problem-reader` 完成题意和交付物锁定后，才能进入 `math-model`。
3. `math-model` 必须先形成模型交接；`math-code` 不得凭空补公式、参数、单位或阈值。
4. `math-verifier` 是独立核验门，不参与模型发明；失败必须退回 `math-model` 或 `math-code`。
5. `math-figure` 只能使用真实结果和已登记 claim；检查失败时退回 `math-code` 或降级为诊断图。
6. `math-consistency`、`math-review` 只提出证据化修复意见，不直接改变主模型或强行推进阶段。
7. 论文阶段按章节确认，全部章节合并并完成 Markdown 全文核对后停止。
8. 本工作流不调用 Word、DOCX、LaTeX、PDF 排版或最终提交 skill。`math-compliance` 仅可在用户另行要求提交合规检查时单独调用。

## C 题专项

识别为国赛本科组 C 题时，可加载 `cumcm-c-problem` 作为领域参考。它必须服从本路由、统一证据链和 Markdown 终点，不得重新启用独立全流程或排版路径。

## 旧版兼容

`math-modeling-skill` 和 `math-modeling-solver` 的内容仅作兼容参考。启用本路由后，不同时启动它们的总流程，避免重复生成交付物或覆盖阶段状态。
