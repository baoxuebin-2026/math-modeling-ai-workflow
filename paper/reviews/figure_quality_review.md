# 图片质量验收记录

| 图号 | 文件 | 已查看 | 数据非空 | 无明显重叠 | 单位可读 | 采用 | 修改记录 |
|---|---|---|---|---|---|---|---|
| 总体图 | `figures/q1/q1_fig00_model_framework.png` | 是 | 是 | 是 | 不适用 | 正文 | 首轮通过 |
| Q1图1 | `figures/q1/q1_fig01_dispatch_soc.png` | 是 | 是 | 是 | 是 | 正文 | 上移SOC下界标签 |
| Q1图2 | `figures/q1/q1_fig02_cost_comparison.png` | 是 | 是 | 是 | 是 | 正文 | 首轮通过 |
| Q2图1 | `figures/q2/q2_fig01_forecast_execution.png` | 是 | 是 | 是 | 是 | 正文 | 修复预测kWh重复除以6；执行线改为含紧急购电总量；重生成损坏PNG |
| Q2图2 | `figures/q2/q2_fig02_emergency_heatmap.png` | 是 | 是 | 是 | 是 | 正文 | 首轮通过 |
| Q3图1 | `figures/q3/q3_fig01_plan_revisions.png` | 是 | 是 | 是 | 是 | 正文 | 增加净修正面板并移除空的下调图例 |
| Q3图2 | `figures/q3/q3_fig02_q2_q3_comparison.png` | 是 | 是 | 是 | 是 | 正文 | 增加总成本降幅标注 |
| Q4图1 | `figures/q4/q4_fig01_price_response.png` | 是 | 是 | 是 | 是 | 正文 | 首轮通过 |
| Q4图2 | `figures/q4/q4_fig02_q42_q43_comparison.png` | 是 | 是 | 是 | 是 | 正文 | 增加总成本降幅标注 |
| 验证图1 | `figures/validation/validation_fig01_calibration.png` | 是 | 是 | 是 | 是 | 正文/验证 | 首轮通过 |
| 验证图2 | `figures/validation/validation_fig02_physical_sensitivity.png` | 是 | 是 | 是 | 是 | 正文/验证 | 修复坐标偏移和效率标签拥挤 |
| 验证图3 | `figures/validation/validation_fig03_update_ablation.png` | 是 | 是 | 是 | 是 | 正文/验证 | 首轮通过 |

全部PNG经`check_contest_figure.py --strict --min-dpi 300`检查通过；像素尺寸均大于1700×970。
