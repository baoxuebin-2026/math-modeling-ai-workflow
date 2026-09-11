# Q2图表说明

| 图 | 文件 | 论文位置 | 图型 | 数据来源 | 变量与单位 | 关键发现 | 验证用途 |
|---|---|---|---|---|---|---|---|
| Q2图1 | `figures/q2/q2_fig01_forecast_execution.png` | 问题二结果分析 | 预测—实测与执行双面板 | `forecast_snapshots.json`、`q2_results.json` | 净需求与购电量kWh/10min | 2025-03-20预测总体跟随实际，但局部低估对应高价紧急购电 | 预测误差传导 |
| Q2图2 | `figures/q2/q2_fig02_emergency_heatmap.png` | 问题二年度评价 | 月份×时段热力图 | `q2_full_detail.csv` | 紧急购电MWh | 风险并非均匀分布，而集中在部分月份及0时、11–12时、15–18时附近 | 年度风险结构 |
