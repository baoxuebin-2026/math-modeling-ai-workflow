# 绘图字体

论文图表使用 `NotoSansCJKsc-Regular.otf`（Noto Sans CJK SC，按当前图表文字生成的字体子集），由
`code/common/plot_utils.py` 在绘图时直接加载，避免不同运行环境缺少中文字体而产生方框字。

字体遵循 SIL Open Font License 1.1，许可文本见 `LICENSE-NotoSansCJK.txt`。
