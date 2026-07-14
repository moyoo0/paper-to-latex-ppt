# 工作流细则

## 输出目录

每次转换使用独立运行目录，默认由 `extract_paper_assets.py paper.pdf` 创建：

```text
output/
└── YYYYMMDD_paper-name/
    ├── paper_assets.json
    ├── slide_plan.json
    ├── slides.tex
    ├── slides.pdf
    ├── final.pptx
    ├── final_with_notes.pptx
    ├── speaker_notes.md
    ├── speaker_notes.json
    ├── figures/
    └── page_images/
```

不要把单次转换产物直接写到 `output/` 根目录。后续所有脚本都应继续使用同一个运行目录。

## 推荐迭代方式

1. 运行资产提取脚本。
2. 阅读 `paper_assets.json`，必要时直接查看原 PDF。
3. 生成 `slide_plan.json`，默认 15 页左右，列出每页标题、目的、公式、图片和讲稿要点。
4. 基于本地 TeX 模板生成 `slides.tex`。
5. 编译 PDF。
6. 渲染页面图，检查视觉结果。
7. 修复 LaTeX 问题并重复第 5-6 步。
8. 转 PPTX。
9. 按最终页面生成讲稿。
10. 将讲稿写入 PPT 备注区，输出 `final_with_notes.pptx`。

## 默认 15 页结构

除非用户指定页数，否则控制在 12-18 页之间，最佳约 15 页：

1. 标题页。
2. 背景与任务。
3. 动机与现有方法缺口。
4. 问题定义：输入、输出、符号。
5. 方法总览图。
6. 模块/算法流程 1。
7. 模块/算法流程 2。
8. 核心公式或优化目标。
9. 训练/推理流程。
10. 实验设置。
11. 主结果。
12. 消融实验。
13. 可视化、案例或误差分析。
14. 局限性与讨论。
15. 总结与 takeaways。

可以根据论文类型调整顺序，但必须覆盖背景、动机、输入输出、算法流程、核心公式和实验。

## 常见修正策略

- 公式过长：使用 `aligned`、`split`、`\resizebox{\linewidth}{!}{...}`，优先拆行。
- 图片不可读：改为裁剪关键子图，或拆成多页。
- 页面过密：删减背景文本，保留关键词和讲解放到讲稿。
- 中文缺字：改用本机可用 CJK 字体，或使用模板已声明字体。
- 图片比例失真：只设置宽度或高度之一，不同时强行指定。
- 结果图太复杂：加一句图上结论，不要逐项复刻 caption。

## 默认模板使用

默认模板采用 Metropolis 主题，正文只需要编写 frame，不要重写导言区。优先使用这些组件：

- 重点术语：`\primarybf{}`、`\accentbf{}`、`\paperterm{}` 或 `\paperaccent{}`。
- 次要说明：`\muted{}`。
- 单张大图：`\fullwidthimage{figures/name.png}`。
- 分栏图片：`\columnimage{figures/name.png}`。
- 流程图：TikZ 的 `pptbox`、`pptboxhighlight`、`pptarrow`、`pptarrowaccent`。

自动生成页面时保持简洁，一页只讲一个主点。模板不限制页面顺序，因此根据论文内容组织故事线。

## 讲稿检查

讲稿不要只是复述 slide bullet。每一页至少回答：

- 这页为什么出现？
- 公式或图如何支撑论文主张？
- 听众最容易误解哪里？
- 讲完这页如何自然进入下一页？

讲稿 Markdown 使用 `# Slide N` 或 `## Slide N` 作为每页分隔。运行：

```bash
python3 <skill>/scripts/add_speaker_notes.py "$RUN_DIR/speaker_notes.md" --pptx "$RUN_DIR/final.pptx" --out "$RUN_DIR/final_with_notes.pptx"
```

写入 PPT 备注区后，仍保留 `speaker_notes.md` 和 `speaker_notes.json`。
