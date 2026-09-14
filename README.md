# 数学建模 AI 工作流

这是一个纯工作流仓库，用于管理数学建模竞赛中的题意锁定、模型设计、代码复现、图表证据、论文写作和最终提交核验。具体比赛的数据、代码、结果和论文应放在独立项目目录或独立私有仓库，不再写入本仓库根目录。

## 快速开始

```bash
python scripts/audit_workflow.py
python scripts/init_contest.py ../contest-2027-a --contest-name CUMCM --year 2027 --problem-id A --question-count 4
```

随后进入新项目，并让 AI 从本仓库的 `AI_WORKFLOW.md` 开始工作。

## 核心入口

- `AI_WORKFLOW.md`：唯一总流程和目录协议。
- `docs/workflow/skill_routing.md`：阶段与 skill 路由。
- `docs/workflow/competition_retrospective.md`：真实比赛复盘形成的硬经验。
- `project_config.example.yaml`：项目配置字段说明。
- `scripts/init_contest.py`：创建无旧题残留的新项目。
- `scripts/audit_workflow.py`：检查工作流断链、旧题状态和缺失 skill。
- `skills/`：按任务加载的专业技能。

## 核心原则

- 一场比赛一个独立项目，不在工作流仓库内反复清空数据。
- 先锁定官方规则和题目交付物，再建模。
- 代码服从模型，论文服从已验证结果。
- 指定结果表不得因压缩篇幅而省略。
- 正式图采用矢量优先并按最终版面检查。
- Markdown 完成后继续进行 Word/LaTeX/PDF 与提交合规核验。

本仓库不保存具体赛题的题面、数据、运行结果、论文草稿或已完成检查点。

