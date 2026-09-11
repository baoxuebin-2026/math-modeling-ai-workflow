# AI 工具使用记录

本文件用于后续生成比赛要求的 AI 工具使用详情；所有条目须由参赛队人工复核并补充实际修改情况。

| 日期 | 工具/模型 | 阶段 | 用途与交互摘要 | 生成或修改材料 | 人工核验状态 |
|---|---|---|---|---|---|
| 2026-09-10 | OpenAI Codex（具体模型版本由提交前界面记录补充） | 题意与数据审计 | 读取官方C题PDF及附件，核对题面转录、字段、维度、单位和模板 | `docs/00_problem_extracted.md`、`docs/findings.md`，修复`data/raw/C题.md`两处转录缺失 | 待参赛队逐项复核 |
| 2026-09-10 | OpenAI Codex（具体模型版本由提交前界面记录补充） | 任务与模型设计 | 比较基线、场景滚动与区间鲁棒路线；用户确认推荐组合后形成公式、参数网格和验证计划 | `docs/01_task_alignment.md`、`docs/02_model_plan.md`、`docs/model_handoff.md` | 用户已确认路线；公式、参数和敏感性已在后续运行中验证 |
| 2026-09-10 | OpenAI Codex（具体模型版本由提交前界面记录补充） | 数据预处理 | 编写并运行无损标准化程序，解析跨日时间、修复附件3结构日期并生成因果10分钟插值接口 | `code/common/prepare_data.py`、`data/processed/*.csv`、`docs/03_data_report.md` | 结构、缺失、负值、数值修改数与整点回代已复核 |
| 2026-09-10 | OpenAI Codex（具体模型版本由提交前界面记录补充） | 模型实现与求解 | 实现连续LP、严格因果预测、残差场景、48小时滚动及Q3/Q4调整结算；运行PoC、参数校准和全年回测 | `code/common/`、`code/q1/`至`code/q4/`、`docs/results/*.json`、年度CSV | 全部求解最优；逐格物理与费用独立复算通过 |
| 2026-09-10 | OpenAI Codex（具体模型版本由提交前界面记录补充） | 结果工作簿 | 按附件5模板生成5份副本并执行公式错误扫描与页面预览 | `data/processed/submission/result*.xlsx` | 5份工作簿公式错误0，关键区域与完整年度行列人工可视检查通过 |
| 2026-09-11 | OpenAI Codex（具体模型版本由提交前界面记录补充） | 结果解释与制图 | 根据用户确认的推荐组合生成总体、Q1–Q4共9张主图；修正首轮Q2展示快照重复单位换算 | `figures/q1/`至`figures/q4/`、`docs/04_result_summary.md`、`docs/05_visualization_plan.md` | 逐张查看且约300 DPI严格检查通过；展示错误未进入求解结果 |
| 2026-09-11 | OpenAI Codex（具体模型版本由提交前界面记录补充） | 验证与敏感性 | 执行物理/会计复算、预测对照、场景收敛、CVaR、末端SOC、效率、极端误差和更新消融 | `code/common/run_validation.py`、`docs/results/validation_results.json`、3张验证图、`docs/06_validation_report.md` | 总体通过；滚动消融有条件通过，限制已记录 |
| 2026-09-11 | OpenAI Codex（具体模型版本由提交前界面记录补充） | 论文素材汇总 | 回收已确认模型、结果、图表、验证与结论边界，生成论文写作唯一数值入口 | `docs/paper_materials.md`、更新后的证据映射和检查点 | 待参赛队在论文阶段逐章复核与记录人工修改 |
