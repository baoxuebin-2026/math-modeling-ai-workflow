# 论文撰写工作流

`paper/` 用于承接前一阶段生成的 `docs/paper_materials.md`，把建模素材转化为可反复修改的论文草稿。

本目录不保存具体赛题论文原文，也不依赖私有提示词全文。它只保留通用写作流程、章节模板、逐章验收清单、摘要优化和全文复核清单。

## 使用顺序

1. 先完成建模工作流，得到 `docs/paper_materials.md`。
2. AI 读取 `paper/workflow/paper_writing_workflow.md` 和 `paper/templates/section_queue.md`，先列出本题实际章节队列。
3. AI 每次只生成一个章节文件，写入 `paper/sections/`。
4. 每生成一个章节，AI 必须使用 `paper/workflow/section_gate.md` 做本章核对，并等待用户确认。
5. 所有章节确认后，AI 使用 `paper/workflow/merge_gate.md` 合并为 `paper/drafts/final_paper_draft.md`。
6. AI 使用 `paper/workflow/abstract_gate.md` 回收全文结果，二次优化标题、摘要和关键词。
7. AI 使用 `paper/workflow/final_review_gate.md` 做 Markdown 全文一致性检查，输出最终 Markdown 草稿后停止；Word/PDF 排版由用户自行完成。

## 目录职责

- `paper/templates/`：论文结构和章节模板，只保存通用规则。
- `paper/workflow/`：逐章生成、逐章验收、合并、摘要优化、全文复核的门控清单。
- `paper/sections/`：比赛时生成的分章节草稿，一章一个 `.md`。
- `paper/drafts/`：由已确认章节合并出的整篇草稿。
- `paper/reviews/`：逐章核对记录和全文二次核对记录。
- `paper/reference_format/`：从参考论文中提炼出的写作和引用注意事项，不负责排版。

## 重要原则

- 论文写作必须基于 `docs/paper_materials.md`，不能凭空补结果。
- 一次只写一个章节，确认后再进入下一章。
- 摘要必须在正文主体确认后再次优化。
- 旧论文只能参考格式，不参考内容质量。
- 所有章节都要能追溯到模型、代码、图表或结果文件。
- 全文合并后必须做第二轮一致性核对，重点检查摘要、符号、公式、图表、结果和附录代码文件名。
