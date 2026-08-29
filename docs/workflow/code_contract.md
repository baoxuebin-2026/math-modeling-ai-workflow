# 分问代码契约

## 基本结构

```text
code/q1/solve_q1.py
code/q1/visualize_q1.py
...
```

问题数量和启用的问题由 `project_config.yaml` 与 `docs/workflow/tasks.json` 配置。AI 应先完成用户确认，再按配置新增或删减 `code/q*/`、`figures/q*/`、`docs/results/q*_results.json` 和 `docs/figures/q*_figures.md`。

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
- 不重复实现核心求解逻辑。
- 只生成已经由 AI 说明用途并经用户确认保留的图表。
- 严格遵守 `docs/workflow/05_visualization_rules.md` 中的默认论文图风格。
- 不写入或覆盖 `docs/*.md`；图表说明由 AI 使用人工式 patch 更新。

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
