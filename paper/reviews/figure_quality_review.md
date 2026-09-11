# 图片质量验收记录

| 图号 | 文件 | 已查看 | 数据非空 | 无明显重叠 | 单位可读 | 采用 | 修改记录 |
|---|---|---|---|---|---|---|---|
| Q1图1 | `figures/q1/q1_fig01_dispatch_soc.png` | 是 | 是 | 是 | 是 | 正文 | 上移SOC下界标签 |
| Q1图2 | `figures/q1/q1_fig02_cost_comparison.png` | 是 | 是 | 是 | 是 | 正文 | 改为分组柱形图+节省费用折线图；插图检验通过 |
| Q2图1 | `figures/q2/q2_fig01_forecast_execution.png` | 是 | 是 | 是 | 是 | 正文 | 修复预测kWh重复除以6；执行线改为含紧急购电总量；重生成损坏PNG |
| Q2图2 | `figures/q2/q2_fig02_emergency_heatmap.png` | 是 | 是 | 是 | 是 | 正文 | 首轮通过 |
| Q3机制图 | `figures/q3.png` | 是 | 是 | 是 | 是 | 正文 | 用户定稿机制图；全文排版时统一复核分辨率与字号 |
| Q3图1 | `figures/q3/q3_fig01_plan_revisions.png` | 是 | 是 | 是 | 是 | 正文 | 增加净修正面板并移除空的下调图例 |
| Q3图2 | `figures/q3/q3_fig02_q2_q3_comparison.png` | 是 | 是 | 是 | 是 | 正文 | 改为双指标水平哑铃图，避免与时序折线重复 |
| Q4图1 | `figures/q4/q4_fig01_price_response.png` | 是 | 是 | 是 | 是 | 正文 | 首轮通过 |
| Q4图2 | `figures/q4/q4_fig02_q42_q43_comparison.png` | 是 | 是 | 是 | 是 | 正文 | 改为成本—风险二维迁移图，强化图型层次 |
| 验证图1 | `figures/validation/validation_fig01_calibration.png` | 是 | 是 | 是 | 是 | 正文/验证 | 扩大画布并调整图例位置；插图检验通过 |
| 验证图2 | `figures/validation/validation_fig02_physical_sensitivity.png` | 是 | 是 | 是 | 是 | 附录 | 去除效率柱状图，改为带节省率标注的点线图 |
| 验证图3 | `figures/validation/validation_fig03_update_ablation.png` | 是 | 是 | 是 | 是 | 正文/验证 | 首轮通过 |

除新增的`figures/q3.png`机制图外，其余程序生成PNG均经`check_contest_figure.py --strict --min-dpi 300`检查通过，像素尺寸均大于1700×970；新增机制图已完成内容与可读性检查，分辨率在全文排版时统一复核。

本轮已将全部正文图、验证图中的说明文字本地化为中文；仅保留Q1–Q4、PV、SOC、CVaR及kWh、MWh、h、min等题目编号、变量缩写和法定计量单位。绘图入口固定加载项目内置中文字体，避免跨环境重绘出现缺字。
