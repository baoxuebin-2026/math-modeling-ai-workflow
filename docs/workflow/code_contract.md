# 分问代码与结果契约

## 唯一路径

每一问使用：

```text
code/qX/solve_qX.py
code/qX/visualize_qX.py
results/qX/
figures/qX/
```

`solve_qX.py` 读取 `data/processed/`，实现已确认模型并输出结构化结果到 `results/qX/`；不得生成论文文字或直接绘图。

`visualize_qX.py` 只读取正式结果和必要数据，输出 SVG 与 600 DPI PNG 到 `figures/qX/`；不得重新实现求解逻辑或覆盖 Markdown 文档。

## 正式结果条件

一个数值进入论文前，必须同时具有：

- `registries/run_record.csv` 中成功的正式运行；
- `registries/result_registry.csv` 中唯一结果 ID、值、单位、场景和来源；
- 对应验证等级和通过状态；
- 与工作簿、图表及正文一致的结果版本。

控制台输出、截图、旧 JSON、探索文件和失败运行只能作为诊断，不得成为论文真源。

## 变更规则

正式结果冻结后不得原地改值。需要修改时，新建结果 ID，标记旧行的 `superseded_by`，重跑受影响图表并重新进行全文一致性审查。

