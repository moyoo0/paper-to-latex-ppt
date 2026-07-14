---
name: paper-to-latex-ppt
description: Turn an academic paper PDF into a Chinese LaTeX Beamer presentation, rendered PDF, PPTX, and detailed speaker notes. Use when the user asks to convert/read/summarize a paper into slides/PPT/组会汇报/论文汇报/中文讲稿, especially when a local TeX/Beamer template should be used and the workflow must compile, inspect rendered PDF pages, and self-correct layout before producing PPT.
---

# Paper to LaTeX PPT

## 目标

将论文 PDF 转成适合中文组会汇报的 LaTeX Beamer 幻灯片，编译为 PDF，逐页渲染检查并自我纠正，最终生成 PPTX 和逐页讲稿。优先使用用户当前目录下提供的 `.tex`、`.sty`、`cls`、`theme`、图片和字体资源；只有没有本地模板时，才使用本 skill 的 `assets/beamer_template/`。

## 不可跳过的质量循环

不要把 LaTeX 源码视为最终质量证明。必须执行：

1. 通读论文 PDF，提取正文、候选图片、caption、公式候选和结构化大纲。
2. 规划汇报故事线和页级大纲，默认约 15 页，选择核心图片和核心公式。
3. 生成或修改 `slides.tex`。
4. 编译 LaTeX 得到 `slides.pdf`。
5. 将 `slides.pdf` 逐页渲染成高分辨率图片。
6. 读取页面图片和检查报告，判断是否存在排版、溢出、模糊、裁剪、内容过密、空白页、公式不可读等问题。
7. 根据检查结果回改 `slides.tex`，重新编译和检查。
8. 只有渲染后的 PDF 页面质量可接受，才转换为 PPTX、生成讲稿并写入 PPT 备注区。

默认至少执行 1 轮编译后视觉检查；如发现问题，继续迭代。通常最多 3-5 轮，除非用户明确要求继续打磨。

## 推荐入口

在任务目录运行：

```bash
python3 <skill>/scripts/extract_paper_assets.py paper.pdf
# 默认创建 output/YYYYMMDD_paper-name/；后续用该目录作为 RUN_DIR。
RUN_DIR=output/YYYYMMDD_paper-name
python3 <skill>/scripts/build_latex_pdf.py "$RUN_DIR/slides.tex"
python3 <skill>/scripts/inspect_pdf_pages.py "$RUN_DIR/slides.pdf"
python3 <skill>/scripts/pdf_to_pptx.py "$RUN_DIR/slides.pdf"
python3 <skill>/scripts/add_speaker_notes.py "$RUN_DIR/speaker_notes.md" --pptx "$RUN_DIR/final.pptx"
```

`<skill>` 是本 skill 目录。脚本可以单独使用，也可以按任务需要调整参数。一次论文转换必须使用独立运行目录，命名为 `output/YYYYMMDD_<paper-name>/`，不要把文件直接堆到 `output/` 根目录。

本地环境需要 LaTeX 编译器（优先 `latexmk` 或 `xelatex`）以及 Python 包 `pymupdf`、`python-pptx`。缺少依赖时先安装依赖，再继续流水线，不要跳过 PDF 渲染检查步骤。

## 论文理解与选材

先完整阅读论文，不要直接从摘要生成 PPT。输出中间理解时重点保留：

- 论文标题、作者、 venue 或 arXiv 信息。
- 研究问题、动机、已有方法缺口。
- 方法主线、关键假设、算法流程。
- 核心公式，包括目标函数、损失函数、推导关键式、理论结论。
- 核心图片，包括方法总览、模型结构、流程图、主要实验结果、消融实验。
- 局限性和适合组会讨论的问题。

选择图片时优先使用正文高频引用、caption 信息量高、与方法或主结果直接相关的图。不要为了页面丰富而使用装饰性或边缘结果图。

## 默认页数与内容结构

默认生成 15 页左右，适合 15-25 分钟中文组会汇报。除非用户指定页数，否则控制在 12-18 页之间，最佳约 15 页。必须覆盖：

- 背景：领域问题、任务定义、关键术语。
- 动机：现有方法为什么不足，本文解决什么痛点。
- 输入输出：模型/算法输入是什么，输出是什么，训练和推理阶段分别是什么。
- 方法总览：核心思想、整体框架、关键模块关系。
- 算法流程：按步骤解释数据流、计算流或伪代码逻辑。
- 核心公式：目标函数、损失函数、关键变换或理论结论。
- 实验设置：数据集、baseline、指标和实现要点。
- 实验结果：主结果、消融、可视化或案例分析。
- 讨论：局限性、适用场景、可能改进和组会讨论点。

推荐 15 页结构：

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

## LaTeX 生成规则

默认生成中文 Beamer。使用 XeLaTeX 或 LuaLaTeX，优先支持 CJK 字体。每页只表达一个主点，避免长段落照搬论文。

若当前目录存在用户模板：

- 优先复用模板的导言区、主题、字号、颜色、页眉页脚和宏。
- 不要随意重写用户的主题风格。
- 将论文内容填入模板约定的 frame/block/macro。

若没有模板，使用 `assets/beamer_template/main.tex` 和 `assets/beamer_template/macros.tex`。

默认模板使用 Metropolis 主题和 `DeepBlue`/`AccentRed`/`LightGray` 颜色系统。生成内容时优先复用 `\primary{}`、`\primarybf{}`、`\accent{}`、`\accentbf{}`、`\paperterm{}`、`\paperaccent{}`、`\muted{}`、`\fullwidthimage{}`、`\columnimage{}` 以及 `pptbox`/`pptarrow` TikZ 样式，保持风格一致。不要在自动生成的正文里重新定义主题、颜色系统或全局字体，除非用户模板明确要求。

公式必须尽量用 LaTeX 原生公式，不要截图公式。图片可以从论文 PDF 中裁剪，但要保证清晰、比例正确，并保留必要 caption 或解释标签。

## PDF 检查标准

运行 `scripts/inspect_pdf_pages.py` 后，必须检查运行目录中的 `page_images/` 页面图和 `inspection.json`。重点判断：

- 是否有空白页、编译错误页或明显缺失内容。
- 标题、页脚、公式、图片是否越界。
- 图中文字、坐标轴、图例是否可读。
- 公式是否过长，需要拆行或缩放。
- 页面是否过密，需要拆页。
- 图片是否裁剪到关键区域，是否比例失真。
- 中文字体是否正常显示。

如检查失败，修改 `slides.tex` 后重新编译和检查。

## PPTX 输出规则

PPTX 是最终交付格式，但视觉权威来自 LaTeX PDF。使用 `scripts/pdf_to_pptx.py` 将最终确认的 PDF 每页渲染为高清图片并铺满 PPT 页面。若用户提供 PPT 模板，可以用作页面尺寸参考；若用户只提供 TeX 模板，这是更优先、更有效的模板来源。生成讲稿后，使用 `scripts/add_speaker_notes.py "$RUN_DIR/speaker_notes.md" --pptx "$RUN_DIR/final.pptx" --out "$RUN_DIR/final_with_notes.pptx"` 将讲稿写入 PPT 备注区。

## 讲稿规则

讲稿必须基于最终渲染后的页面内容，而不是早期大纲。每页讲稿应包含：

- 本页要讲的核心观点。
- 每个公式的符号含义、公式作用、和前后文关系。
- 每张图的模块、箭头、颜色、曲线、坐标轴、图例和结论。
- 可以口头讲出的过渡句。

讲稿默认写入运行目录中的 `speaker_notes.md`，并通过 `scripts/add_speaker_notes.py` 注入到同一目录的 `final_with_notes.pptx` 备注区。保留 `speaker_notes.md` 和 `speaker_notes.json` 作为可审计 sidecar 文件。

## 资源

- `scripts/extract_paper_assets.py`: 提取 PDF 文本、图片、caption 和公式候选。
- `scripts/build_latex_pdf.py`: 编译 LaTeX 并输出日志。
- `scripts/inspect_pdf_pages.py`: 渲染 PDF 页面并生成检查报告。
- `scripts/pdf_to_pptx.py`: 将 PDF 逐页高清插入 PPTX。
- `scripts/add_speaker_notes.py`: 将 Markdown 讲稿拆页，并写入 PPTX 备注区。
- `references/workflow.md`: 更详细的端到端执行准则。
