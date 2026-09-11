# C题Markdown论文章节队列（已确认，逐章写作中）

工作标题：**基于严格无前视场景滚动优化的微网源—荷—储—价协同调度**

统一主线：以10分钟能量平衡和跨日SOC为物理地基，按“确定性调度→源荷不确定→多时次预报更新→未来电价未知”逐问扩展；核心价值表述为“以适度调整成本显著压缩高价紧急购电暴露”。

建议正文保留已确认的9张主图，并在综合验证中再放验证图1和验证图3；验证图2放附录。若最终页数紧张，优先压缩表格和算法流程文字，不先删除Q2风险热力图或两张跨方案对比图。

| 顺序 | 章节文件 | 论文位置 | 本章任务与写作侧重 | 主要来源 | 预计图表/结果 | 状态 |
|---|---|---|---|---|---|---|
| 00 | `paper/sections/00_title_abstract.md` | 标题、摘要、关键词 | 先写可修改版本；突出严格无前视、多时次更新、风险压缩和3组核心数值，正文完成后重写 | `docs/paper_materials.md`、`docs/claim_evidence_map.md` | Q1节省26.90%；Q3/Q4紧急购电下降78.69%/78.05%；不插图 | 已生成，待本章确认 |
| 01 | `paper/sections/01_problem_restatement.md` | 一、问题重述 | 用原创语言重述微网对象、四问任务、约束和交付，不复制题面、不提前报结果 | `docs/00_problem_extracted.md`、`docs/01_task_alignment.md` | 四问任务短表；不插图 | 待撰写 |
| 02 | `paper/sections/02_problem_analysis.md` | 二、问题分析 | 说明四问继承关系、信息集难点、跨日SOC与分账难点，给出全文技术路线 | `docs/01_task_alignment.md`、`docs/02_model_plan.md`、`docs/paper_materials.md` | 图1总体框架；不写最终费用 | 待撰写 |
| 03 | `paper/sections/03_assumptions_notations.md` | 三、模型假设；四、符号说明 | 只保留影响模型的6–7项假设，统一功率/电量、购电、SOC和场景符号 | `docs/paper_materials.md`第3–6节、`docs/02_model_plan.md` | 1张符号表；无结果图 | 待撰写 |
| 04 | `paper/sections/04_q1_modeling_solution.md` | 5.1 问题一 | 侧重物理机制和可解释最优调度：无储能基线、确定性LP、词典序去退化、结果和效率防守 | `docs/results/q1_results.json`、`docs/figures/q1_figures.md`、`code/q1/solve_q1.py`、`code/common/dispatch_lp.py` | 图2–3；Q1基线对比表；35,126.95元与26.90% | 待撰写 |
| 05 | `paper/sections/05_q2_modeling_solution.md` | 5.2 问题二 | 侧重严格因果信息集、预测器选择、残差场景和48小时滚动；解释误差到紧急购电的传播 | `docs/results/q2_results.json`、`docs/figures/q2_figures.md`、`code/q2/solve_q2.py` | 图4–5；Q2年度指标；13,703,782.97元 | 待撰写 |
| 06 | `paper/sections/06_q3_modeling_solution.md` | 5.3 问题三 | 侧重0/6/12/18时修正、上下调线性化和信息价值；诚实呈现小幅降费与显著降风险 | `docs/results/q3_results.json`、`docs/figures/q3_figures.md`、`code/q3/solve_q3.py` | 图6–7；Q2/Q3对比表；0.81%与78.69% | 待撰写 |
| 07 | `paper/sections/07_q4_modeling_solution.md` | 5.4 问题四 | 侧重未来电价未知的因果预测、源荷价场景与Q4-2/Q4-3公平对比；解释P95略升 | `docs/results/q4_results.json`、`docs/figures/q4_figures.md`、`code/q4/solve_q4.py` | 图8–9；Q4对比表；0.41%与78.05% | 待撰写 |
| 90 | `paper/sections/90_model_validation.md` | 六、模型检验 | 汇总物理/会计复算、预测对照、场景收敛、CVaR风险价格、末端SOC、效率、极端误差和更新消融 | `docs/06_validation_report.md`、`docs/results/validation_results.json` | 验证图1、验证图3；1张综合验证表；验证图2转附录 | 待撰写 |
| 91 | `paper/sections/91_model_evaluation_improvement.md` | 七、模型评价、改进与推广 | 写可执行性、统一性、可复现性优点；写终端带活跃、代表日消融、未含寿命/潮流等具体限制；提出72小时和寿命成本扩展 | `docs/paper_materials.md`第13、17节、`docs/06_validation_report.md` | 不新增结果图；引用验证结论 | 待撰写 |
| 92 | `paper/sections/92_references.md` | 参考文献与AI声明 | 只整理真实使用的题面、算法和软件来源；按当年格式在参考文献前设置AI工具使用声明 | 官方题面、最终实际引用来源、`docs/ai_usage_log.md` | 无图；不虚构参考文献 | 待撰写 |
| 93 | `paper/sections/93_appendix.md` | 附录与支撑材料 | 列补充验证图、结果表和核心代码文件说明，不粘贴大量不可读代码 | `code/`、`data/metadata/`、`docs/figures/`、`docs/poc_registry.csv` | 验证图2、补充参数表、程序清单 | 待撰写 |

## 推荐写作顺序与门控

1. 用户确认本队列、工作标题方向和图表去留。
2. 先生成`00_title_abstract.md`的可修改版本，并生成对应章节验收记录。
3. 每次只写一个章节；用户确认后才写下一章。
4. 全部章节通过后合并，再依据全文第二次改写标题、摘要和关键词。
5. 最终只交付`paper/drafts/final_paper_draft.md`，不在本流程生成Word或PDF。

## 队列确认记录

用户于2026-09-11接受推荐章节队列、图表安排、工作标题方向及逐章写作方式，并授权从`00_title_abstract.md`开始写作。

当前状态：

- 第00章标题、摘要和关键词已生成。
- 对应来源核对记录已生成。
- 在用户确认第00章前，不进入第01章。
