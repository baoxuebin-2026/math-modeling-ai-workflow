# Prompt 使用说明

`prompt/` 保存可复用提示词和方法库，但不作为主流程入口。主流程入口是根目录的 `AI_WORKFLOW.md`。

当前旧文件说明：

- `template.py`：来自 MMAgent 的提示词模板库，可作为阶段提示词来源。
- `constants.py`：模型方法库，可用于模型候选生成。
- `decompose_prompt.json`：任务拆解原则库。
- `PROMPT_FOLDER_GUIDE.md`：旧说明文件，存在编码显示问题，后续可按当前目录协议重写。

使用原则：

1. 先遵守 `AI_WORKFLOW.md` 的目录协议。
2. 再从 `template.py` 和 `constants.py` 中抽取具体提示词或模型库。
3. 输出必须落到 `docs/`、`code/`、`figures/`、`data/` 的对应位置。
