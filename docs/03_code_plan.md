# C题求解代码计划

状态：`locked`。用户确认 SciPy HiGHS、HistGradientBoostingRegressor 加季节基线、JSON/CSV 加独立模板生成器。

## 模块边界

| 模块 | 职责 | 禁止事项 |
|---|---|---|
| `code/common/prepare_data.py` | 原始附件到标准长表、单位与时间轴 | 不求解模型 |
| `code/common/data_io.py` | 读取并验证标准表 | 不填缺失、不修改数值 |
| `code/common/forecasting.py` | 季节基线、扩展窗HistGBR、严格因果特征 | 不接触未来实测 |
| `code/common/scenarios.py` | 联合残差块抽样、固定种子 | 不改变中心预测 |
| `code/common/dispatch_lp.py` | 确定性/场景LP、CVaR、残差诊断 | 不绘图、不写论文 |
| `code/q*/solve_q*.py` | 组装每问输入、运行、输出JSON/CSV | 不直接写Excel、不绘图 |
| `code/common/build_result_workbooks.mjs` | 读取结构化结果并填官方模板副本 | 不重新计算模型 |

采用逐层实施：Q1真实数据PoC → 公共场景LP → Q2指定日烟雾测试 → Q3预报更新测试 → Q4联合价格测试 → 全年运行。任一层失败就停在该层，不复用失败输出。

## 实现参数

- 连续LP：`scipy.optimize.linprog(method="highs")`，原始/对偶可行性容差 $10^{-7}$。
- 主预测：`HistGradientBoostingRegressor(max_iter=200, learning_rate=0.05, max_depth=6, l2_regularization=1.0, random_state=20260910)`；每7天扩展窗重训。
- 场景与末端参数使用 `docs/02_model_plan.md` 的网格；随机种子固定为20260910。
- JSON仅保存汇总与指定日完整数组；全年逐格明细保存CSV和最终工作簿，避免单文件过大。
- 工作簿电量4位小数、费用2位小数；模板构建器使用独立JS文件，原模板只读。

## 验证顺序

每次运行必须依次检查：求解状态 → 能量平衡 → 储能状态方程 → 容量/功率界 → 首末/跨日连续 → 同时充放电 → 费用分项复算 → 基线方向。未通过时结果状态保持 `diagnostic-only`。
