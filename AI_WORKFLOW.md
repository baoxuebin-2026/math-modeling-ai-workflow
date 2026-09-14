# 数学建模 AI 工作流总入口

本仓库只保存可复用工作流，不直接承载某一场比赛的数据、代码、结果或论文。每场比赛必须通过初始化脚本创建独立项目目录或独立私有仓库，避免旧题状态、数值和路径污染新题。

开始任何任务前，先读取：

1. `docs/workflow/skill_routing.md`；
2. `docs/workflow/competition_retrospective.md`；
3. 当前比赛项目中的 `project_config.yaml`；
4. 当前项目的 `docs/hub_state.md` 与官方规则锁定记录。

## 一、唯一目录协议

比赛项目统一采用以下结构，其他 skill 不得自行发明第二套路径：

```text
contest-project/
├── project_config.yaml
├── data/
│   ├── raw/
│   ├── external/
│   ├── processed/
│   └── metadata/
├── code/qX/
│   ├── solve_qX.py
│   └── visualize_qX.py
├── results/qX/
├── figures/qX/
├── docs/
├── registries/
├── logs/
├── paper/
│   ├── sections/
│   ├── drafts/
│   └── reviews/
└── tmp/
```

- `data/raw/` 只读保存原题与附件。
- `results/qX/` 保存结构化数值结果和正式结果表。
- `figures/qX/` 保存论文候选图；探索图放 `tmp/`。
- `registries/result_registry.csv` 是计算结果的唯一权威登记表。
- `paper/` 只引用已冻结、已验证的登记结果。

## 二、工作模式

### rapid

适用于 72 小时正式比赛。只保留四个硬确认点：题意与官方规则锁定、模型路线、正式结果与图表、最终论文冻结。低风险的数据读取、格式转换和局部修复可连续执行，但必须记录。

### full

适用于赛前训练或时间充足的研究。可展开候选模型比较、文献路线、完整敏感性和多轮评审。

### local_repair

适用于单个公式、段落、图表或表格修复。不得借局部修改重新定义主模型、结果真源或已冻结结论。

## 三、标准阶段

### 0. 初始化与规则锁定

使用：

```bash
python scripts/init_contest.py <项目目录> --contest-name <比赛名> --year <年份> --problem-id <题号> --question-count <题数>
```

随后由 `math-hub` 和 `math-compliance` 锁定：官方规则来源、页数及计算范围、文件命名、匿名要求、支撑材料、AI 使用披露、最终格式和截止时间。规则未知时可以读题，但不得宣称最终提交就绪。

### 1. 题意与交付物

由 `math-problem-reader` 形成 `docs/problem_brief.md` 与 `docs/deliverable_matrix.csv`。每一问必须明确输入、输出、约束、指定表格/文件和前后依赖。

### 2. 模型路线

由 `math-model` 形成 `docs/model_handoff.md`。每问默认比较可解释基线与必要改进；若一种路线明显占优，可说明理由后免除机械双方案。模型必须给出变量、单位、目标、分组约束、边界、验证等级和结果 schema。

### 3. 数据与计算

由 `math-code` 按交接实现 `code/qX/`。正式运行必须写入 `registries/run_record.csv`、`registries/result_registry.csv` 和必要的数值诊断；控制台数字和旧 JSON 不能直接进入论文。

### 4. 图表与结果表

由 `math-figure`、`math-table` 建立“结论—数据源—图表—正文位置”映射。题目指定表是硬交付物，不受正文可选表数量控制。正式图片优先 SVG，同时导出 600 DPI PNG 备份，并按 Word/PDF 最终尺寸检查。

### 5. 验证与冻结

由 `math-verifier` 按 `direct-check`、`scenario-check`、`robustness-required` 或 `diagnostic-only` 分级检查。通过后将结果登记为 `paper_ready`；已冻结结果变更时新增结果 ID，不得原地覆盖。

### 6. 分章写作

由 `math-templates` 逐章写入 `paper/sections/`，每章核对后再进入下一章。模型章节在逐式解释后增加“目标函数 + 分组约束”的总括式；不强制巨大左大括号。压缩按章进行，单轮通常不超过 20%—30%，不得删除指定交付、核心约束、结果解释和验证证据。

### 7. 摘要与全文一致性

由 `math-abstract`、`math-consistency` 和 `math-review` 检查摘要、正文、图表、附件与登记表。摘要和结论只能使用 `paper_ready` 结果。

### 8. 排版与提交

Markdown 草稿完成后不再自动停止。根据 `project_config.yaml` 选择 Word、LaTeX 或 PDF 路线，由 `math-compliance` 检查页数、MathType/公式迁移、图表清晰度、编号、匿名性、文件命名、支撑材料和 AI 使用披露。只有官方规则与最终导出文件均核验后，才能标记 `submission_ready`。

## 四、证据冻结规则

论文结论必须满足：

```text
题目要求 → 模型/来源 → 正式运行 → 结果登记 → 数学/数值验证 → 图表或表格 → 论文表述
```

发生冲突时，优先级为：

1. 官方题面与当年规则；
2. `registries/result_registry.csv` 中已冻结的 `paper_ready` 行；
3. 对应正式运行及输出文件；
4. 图表、正文、摘要和结论。

不得用旧缓存、截图、控制台输出或未登记文件覆盖已冻结结果。

## 五、完成标准

一个比赛项目只有同时满足以下条件才算完成：

- 每一问的官方交付物均为 `provided`，或有明确批准的省略理由；
- 主模型、公式、单位、边界和算法一致；
- 正式结果可由 `run_record.csv` 复现；
- 摘要、正文、表图和附件数值一致；
- 图片在最终版面尺寸下清晰；
- 页数、匿名、文件命名、支撑材料和 AI 披露符合当年规则；
- 无开放的 P0/P1 阻塞项。

框架自身可运行：

```bash
python scripts/audit_workflow.py
```

