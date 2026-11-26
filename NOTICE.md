# 第三方来源与许可说明

## 1 howoneai/xiaolin-explainer-packaging（MIT）

本项目下列内容改写/翻译自该仓库（https://github.com/howoneai/xiaolin-explainer-packaging ，MIT License，Copyright (c) 2026 howoneai）：

- `references/treatment.md`、`references/visual-checklist.md`、`references/research.md`、`references/layout-mapping.md`、`references/facts_template.md`（方法论文档，经本项目口径重写）
- `scripts/commons_photo.py`、`scripts/commons_logo.py`（移植）
- `kit/scenes.js` / `kit/scenes_plus.js` 中部分版式的布局数学（翻译为 vanilla JS，非原引擎代码）

按 MIT 保留版权与许可声明（全文见下）。**未合入**：对方 Remotion 引擎、主题底图、演示照片与道具、分镜 API、"来源上屏"做法（与规矩 16 冲突）、优设标题黑字体（再分发授权不明）、world110.json 当标准地图的用法（涉中国疆域须用有审图号地图）。

## 2 renzheng0415/zenskill-xiaolinshuo-video（无 LICENSE 文件）

该仓库**没有显式许可证**（仅 NOTICE 声明其部分文档源自 howoneai MIT）。因此本项目**只借鉴其规则思路与事实数据**（句型→镜头决策、节奏量值、参考片时间码观察、机位/手势语法），以自有表述重写于 `references/shot-grammar.md`、`references/reference-evidence.md`、`references/visual-checklist.md`、`references/layout-mapping.md`；**不逐字复制其原文表达**。其 NOTICE 中 howoneai MIT 部分按上节保留。

## 3 HeyChengC/bighead-collage（MIT + OFL）

`vendor/bighead-collage/` 为整份 vendoring（横屏改造），MIT 许可证与字体 OFL 许可证随附于该目录（LICENSE、scripts/fonts/OFL-*.txt）。参考图/素材权利按上游 README 与各自来源。

## 4 NBrangerF/xiao-lin-shuo-skill（MIT）

本项目 `references/scripting.md` 与 `references/brief_template.md` 借鉴并按本项目口径重写了该仓库（https://github.com/NBrangerF/xiao-lin-shuo-skill ，MIT License，Copyright (c) 2026）的解释型写稿方法论（问题压缩三件套、7 类财经机制库、5 类母题骨架、短/中长片结构与 8 维审稿维度）。**未合入**：其 Python 词频/语料脚本、固定口头禅示例、语料索引与剧集拆解全文。

## 5 Asaceoo/deep-research-plus-skills（MIT，仅限编排层）

本项目 `references/research.md`、`references/facts_template.md` 与 `scripts/facts_check.py` 借鉴并独立重写了该仓库编排层（https://github.com/Asaceoo/deep-research-plus-skills ，MIT License，Copyright (c) 2026 asaceoo）的证据防错机制（反方证据、承重结论开页留痕、单源/当事方自述标注、补搜上限、链接/日期/死链与 AI 腔检查）。**未合入**：其 5-YAML 调研报告流水线、发版/打包工具，以及其 `sub-skills/` 目录下未随附 MIT 许可的第三方子技能。

## 6 字体

kit 外部字体目录（scripts/local.json fonts_dir）：Bebas Neue / Montserrat（OFL）、MiSans（小米免费商用许可）、Alimama ShuHeiTi（阿里免费商用许可）——各自许可文本随字体来源；vendor/bighead 字体为 OFL（随附）。

## 7 本项目自有

kit 引擎其余部分、scripts 其余工具、references 其余文档为本项目自有创作。

---

MIT License

Copyright (c) 2026 howoneai

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
