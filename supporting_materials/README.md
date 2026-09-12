# 支撑材料

本目录汇总论文复核所需的代码、计算结果和图表，内容与仓库根目录中的源文件保持一致。

## 目录

- `code/`：问题一至问题四求解、可视化、公共模型和测试代码。
- `results/`：年度 JSON 结果、校准结果和验证结果。
- `data/`：年度逐时/逐格明细、调整明细和结果工作簿。
- `figures/`：论文正文使用的全部图表。

## 复核入口

从仓库根目录运行：

```powershell
py -m unittest code.tests.test_adjustment_settlement -v
py code/q3/solve_q3.py --full --scenarios 40 --risk-weight 0 --terminal-half-width 600
py code/q4/solve_q4.py --full --scenarios 40 --risk-weight 0 --terminal-half-width 600
py code/q3/visualize_q3.py
py code/q4/visualize_q4.py
```

`build_result_workbooks.mjs` 依赖特定运行环境，普通本地环境不要直接运行。
