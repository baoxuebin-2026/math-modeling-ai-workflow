# 工作流检查点

| 检查点 | 阶段 | 状态 | 已确认结论/当前门控 | 通过后产物 |
|---|---|---|---|---|
| CP-00 | 题意与信息集锁定 | `已通过` | 双向效率均为 0.9；严格无前视；跨日连续；允许弃光 | `docs/01_task_alignment.md` |
| CP-01 | 模型路线 | `已通过` | 场景滚动主线；未来电价未知；48小时滚动末端；保留LP基线 | `docs/02_model_plan.md` |
| CP-02 | 数据预处理 | `已通过` | 无损标准化；实际锚点线性插值；独立输出目录 | `docs/03_data_report.md` |
| CP-03 | 求解代码 | `已通过` | Q1–Q4真实数据PoC、全年回测、独立复算与5份结果工作簿均通过 | `code/q*/solve_q*.py`、`docs/results/`、`data/processed/submission/` |
| CP-04 | 图表证据链 | `已通过` | 用户确认推荐组合；9张图逐张查看并通过300 DPI严格检查 | `docs/05_visualization_plan.md`、`figures/q*/` |
| CP-05 | 结果解释 | `已通过` | 用户接受“成本小幅改善、紧急购电风险显著下降”的主线 | `docs/04_result_summary.md` |
| CP-06 | 验证与敏感性 | `已通过` | 推荐组合总体通过；滚动消融按成本—风险权衡有条件通过 | `docs/06_validation_report.md` |
| CP-07 | 论文素材包 | `已通过` | 所有引用路径存在；核心数值JSON复算一致；模型—结果—图表—验证闭环 | `docs/paper_materials.md` |
| CP-08 | Markdown 论文 | `章节队列待确认` | 章节顺序、写作侧重和正文/附录图表安排 | `paper/drafts/final_paper_draft.md` |
