# 章节合并门控清单

本文件用于将 `paper/sections/` 中已确认的章节合并为完整论文草稿。

## 合并前检查

AI 合并前必须确认：

- 每个应写章节都存在。
- 每个章节都有对应的 `paper/reviews/section_review_*.md`。
- 没有未经用户确认的章节进入合并稿。
- 章节顺序符合 `paper/templates/paper_outline.md` 和本题实际问题数量。
- 第六章必须是 `paper/sections/90_model_validation.md`，第七章必须是 `paper/sections/91_model_evaluation_improvement.md`。
- 如果题目没有第四问，所有第四问章节和引用都已删除。

## 合并输出

合并稿输出到：

```text
paper/drafts/final_paper_draft.md
```

合并时应处理：

- 标题层级统一。
- 章节编号连续。
- 图表编号连续。
- 公式编号连续。
- 参考文献编号或格式统一。
- 附录代码文件路径与 `code/q*/` 对齐。

## 合并后第一轮核对

合并后立即生成：

```text
paper/reviews/final_review_round1.md
```

第一轮重点检查：

- 合并后是否出现重复段落。
- 前后文是否衔接自然。
- 问题编号、模型编号、图表编号是否错位。
- 每问结果是否回应该问任务。
- 正文是否引用了不存在的图、表、公式或附录。

第一轮核对完成后，才进入摘要二次优化。
