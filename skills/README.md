# 工作流 Skills

本目录是 `math-modeling-ai-workflow` 的正式 skill 集合。`AI_WORKFLOW.md` 负责阶段顺序、用户确认和最终停止条件；本目录中的 skill 负责各阶段专业执行。

## 已选模块

| Skill | 用途 | 默认阶段 |
|---|---|---|
| `math-hub` | 范围锁定、状态、阻塞和模块路由 | 全流程总控 |
| `math-problem-reader` | 题面、附件、分问和交付物解读 | 启动 |
| `math-literature` | 文献检索、来源和引用核验 | 可选 |
| `math-model` | 变量、假设、公式、约束、验证和代码交接 | 建模 |
| `math-code` | 计算复现、结果登记、数值诊断 | 代码 |
| `math-verifier` | 量纲、公式、边界、约束和可行性核验 | 独立门禁 |
| `math-figure` | 图表选择、证据链和视觉检查 | 可视化 |
| `math-table` | 符号表、结果表和表格一致性 | 结果整理 |
| `math-abstract` | 基于已验证证据生成摘要和关键词 | 论文写作 |
| `math-consistency` | 跨正文、表图、代码和登记表的一致性检查 | 结果/写作 |
| `math-review` | 评委视角风险、扣分点和最小修复 | 写作终检 |
| `math-templates` | Markdown 章节、段落和证据资产 | 论文写作 |
| `cumcm-c-problem` | 国赛本科组 C 题专项参考 | 条件加载 |

## 不纳入

- `math-modeling-skill`：旧版三角色总流程，职责与本工作流重复。
- `math-modeling-solver` / `math-modeling-paper`：旧版解题—写作总流程，阶段门控和产物协议不同。
- Word、DOCX、LaTeX、PDF 排版工具：本项目在 `paper/drafts/final_paper_draft.md` 生成后停止。

## 调用原则

一次只运行一个总控流程。先由 `math-hub` 锁定当前阶段，再调用对应主 skill；协作 skill 只能返回证据化意见，不能越权推进阶段或覆盖其他阶段产物。
