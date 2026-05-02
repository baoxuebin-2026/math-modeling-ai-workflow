# 分问代码契约

## 基本结构

```text
code/q1/solve_q1.py
code/q1/visualize_q1.py
code/q2/solve_q2.py
code/q2/visualize_q2.py
code/q3/solve_q3.py
code/q3/visualize_q3.py
```

## solve_qx.py 负责

- 读取 `data/processed/` 中的数据。
- 实现该问的模型、算法和参数求解。
- 输出结构化结果到 `docs/results/qx_results.json`。
- 必要时输出中间表格到 `data/processed/` 或 `docs/results/`。
- 不直接负责最终论文文字。
- 只实现已经由 AI 解释并经用户确认的模型方案。

## visualize_qx.py 负责

- 读取 `docs/results/qx_results.json` 和必要数据。
- 生成该问所有图表到 `figures/qx/`。
- 写出图表说明到 `docs/figures/qx_figures.md`。
- 不重复实现核心求解逻辑。
- 只生成已经由 AI 说明用途并经用户确认保留的图表。

## JSON 最低字段

```json
{
  "question": "问题一",
  "status": "已完成/待补充",
  "paper_position": "问题一模型建立与求解",
  "code": "code/q1/solve_q1.py",
  "visualization_code": "code/q1/visualize_q1.py",
  "input_files": [],
  "model": {
    "baseline": "",
    "selected": "",
    "reason": ""
  },
  "outputs": {},
  "notes": []
}
```
