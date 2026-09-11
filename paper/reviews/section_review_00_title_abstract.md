# 章节验收记录：标题、摘要与关键词

## 章节文件

`paper/sections/00_title_abstract.md`

## 本章边界

- 论文位置：标题、摘要、关键词。
- 当前版本：正文完成前的可修改稿；全文合并后仍须按`paper/workflow/abstract_gate.md`二次优化。
- 引用内容：四问主模型、Q1单日基线对比、Q2年度基准、Q3/Q4滚动修正对比及两项综合验证指标。
- 不写入内容：正文公式推导、指定日明细、图表编号、参考文献编号、完整参数网格和未采用模型。
- 图表引用：本章不插图，因此不触发图片质量验收。

## 来源追溯

| 论文内容 | 直接来源 | 交叉核对 | 核对结果 |
|---|---|---|---|
| 标题中的“严格无前视、场景滚动、源—荷—储—价协同”及全文主线 | `docs/paper_materials.md`第1、13、18节；`docs/04_result_summary.md`第4节 | `docs/01_task_alignment.md`；`docs/02_model_plan.md` | 与已锁定主线一致 |
| 10 min步长、五倍紧急购电、储能及四问信息边界 | `data/raw/C题.md`；`docs/01_task_alignment.md` | `docs/02_model_plan.md` | 与题面和任务边界一致 |
| Q1确定性LP、词典序去退化及48,052.05→35,126.95元、节省26.90% | `docs/results/q1_results.json`；`docs/04_result_summary.md` | `code/q1/solve_q1.py`；`code/common/dispatch_lp.py`；V1/V6 | 原始值复算后按2位小数和百分比格式化一致 |
| Q2预测器、40场景、48 h滚动及334日结果 | `docs/results/q2_results.json`；`docs/paper_materials.md`第8节 | `code/q2/solve_q2.py`；`code/common/forecasting.py`；`code/common/scenarios.py` | 总费用13,703,782.97元、紧急购电347,701.03 kWh一致 |
| Q3四时次修正、分账模型及相对Q2变化 | `docs/results/q3_results.json`；`docs/paper_materials.md`第9节 | `code/q3/solve_q3.py`；C-002；V1/V8 | 总费用13,592,948.48元；费用与紧急购电分别下降0.81%和78.69%，一致 |
| Q4未来价格未知、联合残差场景及两策略对比 | `docs/results/q4_results.json`；`docs/paper_materials.md`第10节 | `code/q4/solve_q4.py`；C-003；V1/V8 | Q4-3总费用14,417,305.41元；紧急购电331,020.23→72,660.52 kWh，下降78.05%，一致 |
| 能量平衡、费用复算和40/60场景收敛 | `docs/results/validation_results.json`；`docs/06_validation_report.md` | C-005；`code/common/run_validation.py` | $6.82\times10^{-13}$ kWh、$2\times10^{-9}$元、0.32%和2.49%均一致 |
| 适用边界：连续控制、未计寿命与潮流 | `docs/04_result_summary.md`第5节；`docs/paper_materials.md`第17节 | `docs/06_validation_report.md`第10节 | 未夸大为完整工程控制模型 |

## 数值口径复核

- Q1为附件1对应的确定性单日结果；未与Q2—Q4的334日年度金额直接比较。
- Q3以Q2为比较基准，0.81%仅表述为小幅降费，78.69%用于表述紧急购电风险压缩。
- Q4仅比较同一未知波动电价信息集下的Q4-2与Q4-3；未把固定价与波动价差额作单因素因果解释。
- 正式年度方案的风险权重为0；摘要未把CVaR写成最终采用模型。
- 摘要只表述“完整滚动策略总体降低紧急购电暴露”，未声称每次预报更新均单调改善。

## 自检结果

- 结构完整性：通过。包含背景与统一主线、四问方法和核心结果、综合检验、创新与适用边界。
- 结果可追溯性：通过。全部数值均来自`docs/paper_materials.md`允许进入摘要的口径，并与结构化JSON交叉核对。
- 模型名称一致性：通过。使用“确定性日内线性规划”“48 h滚动场景线性规划”“多阶段滚动线性规划”和“源—荷—价联合残差场景”，未沿用早期未采用模型名称。
- 图表引用：无。
- 图片质量验收：不适用。
- 符号与单位：通过。费用按元、购电量按kWh，残差单位为kWh。
- 语言强度：通过。未使用“显著降低总成本”“CVaR最优”“每次更新均改善”等超出证据的结论。
- 与后续章节重复：未展开公式、算法步骤和图表解释，仅保留摘要所需信息。
- 章节范围：通过。仅生成第00章及本验收记录，未生成后续章节。

## 需要用户确认

1. 是否保留当前工作标题。
2. 是否接受摘要把Q3/Q4的核心价值概括为“压缩紧急购电暴露”，并同时披露不足1%的年度费用降幅。
3. 是否保留当前5个关键词。
4. 本章确认后，是否按队列进入`paper/sections/01_problem_restatement.md`。
