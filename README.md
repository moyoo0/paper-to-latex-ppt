# paper-to-latex-ppt

> 研究生应付组会专用：把一篇论文 PDF 尽快变成一份可以直接上阵的中文 PPT，自动生成逐页讲稿，并写进 PowerPoint 备注区。

研究生一边实习、上课或做项目，一边还要应付组会论文汇报。导师临时发来一篇 paper，真正需要准备的不只是摘要，而是一套包含背景、方法、公式、原图、实验和逐页讲稿的汇报材料。

这个 skill 的目标很直接：把一篇论文 PDF 变成一份 **能讲、像样、有备注** 的组会 PPT 初稿。

它不是论文摘要工具，而是一个面向“组会交付”的生成流程：

- `final_with_notes.pptx`：最终 PPT，备注区里有逐页讲稿，优先拿这个去讲。
- `speaker_notes.md`：独立讲稿，开讲前快速顺一遍。
- `slides.tex`：LaTeX 源文件，有时间还能继续精修。
- `slides.pdf`：由 LaTeX 编译出的视觉基准版本。

| 能力 | 作用 |
| --- | --- |
| 论文结构化阅读 | 抽取背景、动机、方法、公式、实验和局限性 |
| LaTeX Beamer 生成 | 保留公式质量，统一中文组会风格 |
| PDF 渲染检查 | 编译后逐页检查，避免溢出、太密、图糊 |
| PPTX 导出 | 每页高清插入 PPT，方便最终汇报 |
| 备注区讲稿 | 每页生成可照着讲的 speaker notes |

## 适合什么场景

适合需要在短时间内完成论文组会汇报的人：论文临时下发、准备时间很短，或者希望快速得到一份包含原图、公式和逐页讲稿的中文 PPT 初稿。

## 效果预览

一套端到端生成、零人工中间介入的组会 PPT 精选页：

![Paper to LaTeX PPT 工作流](docs/images/start.png)

![Slides grid](docs/images/example-grid.png)

## 它到底帮你省了什么

普通 AI 工具很容易做到“总结论文”，但组会真正需要的是一份能打开就讲的 PPT：

- 有背景、动机、输入输出、算法流程、实验和总结。
- 有 LaTeX 原生公式，看起来不像截图糊上去的。
- 有论文原图，显得你真动手读了。
- 有 PowerPoint 备注区讲稿，临场不至于卡壳。
- 有编译后的 PDF 页面检查，避免打开 PPT 才发现溢出、太密、图糊。

`paper-to-latex-ppt` 把流程固定成一条可检查的 pipeline：

```text
Paper PDF
  -> 结构化阅读：正文 / 公式 / 图片 / caption
  -> 15 页左右组会大纲
  -> LaTeX Beamer
  -> PDF 编译
  -> 页面渲染与自我检查
  -> LaTeX 回改
  -> PPTX 导出
  -> 逐页讲稿
  -> PPT 备注区注入
```

关键点：**不会只生成 `.tex` 就结束**。它要求实际编译 PDF、渲染页面截图、检查排版问题，再修正。否则“看起来生成了，打开全是溢出”这种事很容易发生在组会前十分钟。

## 安装方式

最推荐的方式是直接让 Codex、Claude Code 或其他支持 Agent Skill 的工具完成安装和环境检查。

复制下面这段话给 Agent：

```text
请安装这个 GitHub 仓库对应的 Skill：
https://github.com/moyoo0/paper-to-latex-ppt.git

请继续检查并安装运行环境：
1. 创建 Python 虚拟环境；
2. 安装 requirements.txt 中的依赖；
3. 检查 latexmk 和 xelatex；
4. 如果缺少 LaTeX，请根据我的操作系统给出安装方案；
5. 运行 scripts/check_environment.py，直到环境检查通过。
```

安装完成后，可以继续让 Agent 确认：

```text
请确认 paper-to-latex-ppt 的环境已经配置完成，并告诉我下一步如何用 paper.pdf 生成带讲稿的 PPTX。
```

### 手动安装方式

如果想自己执行命令，也可以使用下面的备用流程。完整生成 PPT 需要 Python 依赖和本地 LaTeX。

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

需要确保系统中存在：

```text
latexmk
xelatex
```

macOS 上可以用 TinyTeX：

```bash
curl -fsSL https://yihui.org/tinytex/install-bin-unix.sh | sh
```

并确保 TinyTeX 的 bin 目录在 `PATH` 中。

常见 macOS 路径是：

```bash
export PATH="$PATH:$HOME/Library/TinyTeX/bin/universal-darwin"
```

最后运行环境检查：

```bash
.venv/bin/python scripts/check_environment.py
```

## 怎么用

把论文放在当前目录，例如：

```text
paper.pdf
```

## 推荐提示词

```text
使用 $paper-to-latex-ppt 阅读 paper.pdf，帮我做一份明天组会能直接讲的中文 PPT。
```

## 默认汇报结构

默认生成 12-18 页，最佳约 15 页，目标是“组会上能顺着讲完”：

1. 标题页
2. 背景与任务
3. 动机与现有方法缺口
4. 问题定义：输入、输出、符号
5. 方法总览图
6. 模块/算法流程 1
7. 模块/算法流程 2
8. 核心公式或优化目标
9. 训练/推理流程
10. 实验设置
11. 主结果
12. 消融实验
13. 可视化、案例或误差分析
14. 局限性与讨论
15. 总结与 takeaways

具体页数会根据论文内容调整，但必须覆盖背景、动机、输入输出、算法流程、核心公式和实验。

## 输出文件

默认输出到按日期和论文名命名的独立目录，避免多次生成互相覆盖：

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

最常用的是：

- `final_with_notes.pptx`：优先拿这个去讲，备注区已有讲稿。
- `speaker_notes.md`：开讲前快速过一遍。
- `slides.tex`：有时间就继续改。
- `slides.pdf`：检查最终视觉效果。


它生成的是救急初稿，不是免读论文许可证。真正上场前仍建议自己通读 `speaker_notes.md`，至少确认公式解释、图表结论和实验细节没有偏离论文。
