# 验证图表说明

| 图 | 文件 | 论文位置 | 图型 | 数据来源 | 变量与单位 | 关键发现 | 验证用途 |
|---|---|---|---|---|---|---|---|
| 验证图1 | `figures/validation/validation_fig01_calibration.png` | 模型检验 | 双面板参数指数图 | `parameter_calibration.json` | 成本/紧急购电指数% | 40场景基本收敛；正CVaR权重以成本换取风险下降 | 场景数与风险权重 |
| 验证图2 | `figures/validation/validation_fig02_physical_sensitivity.png` | 敏感性分析 | 末端带宽折线+效率条形图 | `validation_results.json` | 相对变化%、费用千元 | 末端带宽扰动影响极小；效率提高降低成本 | 边界与物理参数 |
| 验证图3 | `figures/validation/validation_fig03_update_ablation.png` | 创新有效性检验 | 高风险日信息消融图 | `validation_results.json` | 紧急购电MWh | 完整更新总体降低风险，但中间步骤不严格单调且存在费用代价 | 滚动更新贡献 |
