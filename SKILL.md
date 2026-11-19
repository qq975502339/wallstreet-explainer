---
name: wallstreet-explainer
description: 华尔街式的财经/科技解读短片（1–3 分钟、16:9，风格学自小Lin说），两种模式按有没有真人视频自动选：用户给了口播视频（真人或数字人，一个机位）就走真人口播模式——她是片子的"地面"，证据挂到她身后的墙上、关键词她身后换成织物舞台和巨字、讲证据时缩进圆窗或竖窗再长回全屏；没给就走无人动效包装模式——当事人实拍抠像站在巨字前面。两种模式共用：真实的人、新闻原文和官方画面作证据，图形（照片圆盘、金色大数字、柱子、图表、金价线、因果链）只演钱和关系，细斜纹深蓝织物底，克制的 2.5D，每一镜接住上一镜。模板档（镜头表 + render.mjs --check 自检）和手写档。工具：找片下片、图库搜下（Pexels/Pixabay 空镜）、比喻物件生图、新闻截图和荧光笔、逐帧抠像、口播逐字对齐、配音时间线、逐帧渲染、合成音效、混音。用户说"wallstreet-explainer""wallstreet-presenter""像《AI到底有多烧钱》那样""做一条财经/科技解读""真人口播财经""小Lin说那种""我有口播视频，帮我包装成财经解读""把一笔账讲清楚"时使用。
---

# 华尔街式财经解读（wallstreet-explainer）

**讲一笔账：真的人、真的新闻、真的画面作证据，图形把数字和关系演出来；每一镜都接住上一镜的东西往下走。**

## 先选模式：用户有没有给真人视频

| 用户给了 | 走哪个模式 | 先读 |
|---|---|---|
| 一条口播视频（真人或数字人，一个机位、不切） | **真人口播模式**：她是片子的"地面"，观众每离开她一会儿就回到她身边 | `references/presenter.md`，再读下面"真人口播模式" |
| 只有题目、文案、或者什么都没有 | **无人动效包装模式**：没有主持人，当事人实拍抠像来演"人站在巨字前面"，配音用临时语音或豆包 | 直接看下面"这份 skill 是什么"往后 |

拿不准就问一句"有没有口播视频"。两种模式画风、规则、场景、手法库、工具全一样，下面"这份 skill 是什么"往后的内容两种都适用。

## 真人口播模式

- 证据和图形不是盖掉她，而是挂进她的房间、或者把她带进图形的世界。
- 多出来的东西：
  - `references/presenter.md`：**先读这份**。真人怎么融进来：七种样子、之间怎么走、墙上挂东西放哪、景别、声音、量出来的数（四条小Lin说）。
  - `kit/host.js`：口播层。`scene:'host'`（房间全屏 / `items` 挂墙 / `swap` 身后换世界 / `zoom` 景别跳），任何场景加 `host:'pip'`（角上圆窗）或 `host:'window'`（竖窗 + 图形板），`enter:'grow'` / `'drop'` 回到房间。
  - `kit/scenes_plus.js`：`line`（真实日线走势）、`chain`（因果链：打仗 → 油价 → 通胀 → 利率）。
  - `scripts/host_timeline.py`（口播逐字对齐成时间线，口播就是配音）、`scripts/sfx_synth.py`（合成风声、低音撞击、轻响）；`mix.py` 认得口播原声。
  - 例子：`examples/gold-rates/`（《打仗了，黄金为什么反而跌》，28 秒）。
- 无人模式里"当事人抠像站在巨字前面"那一套：有了主持人，这些动作优先给她（`host` 的 `swap`）；当事人回到实拍、圆盘、原文里。`person` 场景照样能用。
- 没有真人口播、用户明确要数字主持人时：读 `references/ai-presenter.md`（圆窗走 Vidu、大画幅走 AutoDL H3、旁白走 Token Plan TTS）；产物走同一套 host 管线，标"AI生成"、不得称真人（规矩 44）。

### 真人口播片怎么做

```
node scripts/new_film.mjs <片子目录>
（口播抽 30fps 帧到 assets/clips/host/，counts.json 登记 "host": 帧数；ffmpeg -i 口播.mp4 -vf fps=30,scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2 assets/clips/host/%04d.jpg）
python scripts/matte.py <片子目录>/assets/clips/host <片子目录>/assets/cut/host      # 逐帧抠她（挂墙、换世界要用），然后 matte_clean.py
（写 script.json：lines 写她实际说的话，一句一个 id，字幕就用这份）
python scripts/host_timeline.py <口播.mp4> <片子目录>/script.json <片子目录>/timeline.json [--tail 1.0]
（写 film.js：FB.init → KIT.use → await KIT_HOST.use(K,{faceY:她脸中心在原片里的 y}) → K.film([...])）
node scripts/render.mjs --dir <片子目录> --check / --sheet / --video --h 720
python scripts/sfx_synth.py library/sfx/synth     # 一次就行
（写 sfx.json：配乐 + 音效卡在换样子的地方，见 references/presenter.md 的"声音"）
python scripts/mix.py <片子目录> --check
```

流程和原版一样每站停下来给用户看，区别在：
- **站 1 文案**：文案就是她的口播。拿到口播先转写（`host_timeline.py` 会打印识别结果），和用户核对她说的字（数字人常有读错、识别也会听错）；事实照样要查清、留链接。
- **站 2 导演表**：每一镜多一列"她在哪"：房间 / 挂墙 / 换世界 / 竖窗 / 圆窗 / 不在。先按 `presenter.md` 的"判断用这几句"排她的位置，再填画面。
- **站 4 时间线**：不用临时配音，`host_timeline.py` 从口播里逐字对齐；片子的 t 就是口播的 t。

## 这份 skill 是什么

- **是**：一套设计思路（每一镜放什么、为什么、凭什么接下一镜）、一套动效原理（从三条同类参考片逐帧量出来：为什么它不像 PPT、不像 AI，手法清单和量化目标）、一套风格语言（舞台、巨字、抠像、圆盘、数字、图表、原文高亮的具体做法，外加一份开头钩子菜单），以及一套工具。
- **两档做法，画风是同一个：**
  - **模板档（默认，先用这个）**：`kit/` 里 33 个场景（大数字、照片圆盘、新闻桌面、原文刷黄、人站在巨字前面、柱子、图表、地图……）。一条片 = 一张镜头表：每一镜选一个场景，填这一镜的字、数、图和“念到哪个字”。镜头怎么走、东西怎么出现、前后层、运动模糊、字号颜色，都由模板管。这样设计，是想让弱一些的模型也能稳定出片；这一点还没实测过。
  - **手写档（强模型，或者模板对不上的时候）**：底座 `film_base.js` + 手法库 `moves.js` + 2.5D 小工具 `stage25d.js`，逐镜手写。只有一镜对不上时，在镜头表里写 `scene:'custom'`，手写那一镜就行。
- **模板是词汇，不是镜头顺序**。每条片的画面都要从它自己的文案和素材里现想：每一镜先写 `says`（这一镜让观众多懂了什么），再找意思对得上的场景；只是差不多就换一个，或者手写。`examples/` 里的两条片记录的是片子怎么想出来、在哪里摔过跤，不要照搬它们的镜头。
- **画风的基准是成片，不是模板**：《AI到底有多烧钱》的每秒一帧（`examples/ai-burn-money/frames_1fps.jpg`）和 28 秒的《谷歌给苹果的两百亿》（`examples/google-apple-20b/`，真素材手写）。模板的默认样子就是照它们做的；做出来的片子要能和它们并排放而不突兀。
- **手写档能复用的有两样，都是为了质量稳定**：底座（`scripts/film_base.js`，每条片都一样的那层）和手法库（`scripts/moves.js`，磨过、逐帧查过的动作）。手法是词汇，不是镜头：先想这一镜要说什么，再找意思最对得上的手法；只是差不多就手写。不要为了用上手法去改画面，也不要为了出片去凑手法（选法见 `references/motion.md` 的手法库）。
- **慢推、数字滚动、实拍上压字，参考片都在用**。廉价的不是这些手法，是做法。判断用三句话：删掉它观众少懂了什么？是镜头在动、东西在换状态，还是元素自己在演入场？这一层是真的、具体的吗？

动手前先读 `references/thinking.md`、`references/motion.md` 和 `references/rules.md`；做模板档再读 `kit/README.md`。其他几份按需要读。

## 五条硬规矩（完整的在 `references/rules.md`，带编号、能检查）

1. **真东西是主角**：当事人实拍、新闻原文截图、官方发布会/财报/广告画面。图形只用来演钱和关系。示例片里的占位图（`kit/assets/ph/`）在正式片里一张都不能留。
2. **底只有一张细斜纹深蓝织物**。不要满屏 3D 物体，不要紫、青这类整屏底色，不要大团彩色光，不要浮尘。品牌色只在当事人身后出现；酒红底一条片最多一段（算总账那段）。
3. **每一镜写 `says`**，一镜一个主角；东西朴素地出现，镜头去找它。
4. **时刻挂在字上**（`'@b05:英伟达'`），不写死秒数；开头 0.5 秒内开口，第一帧就有东西。
5. **交片前**：`render.mjs --check` 没有错误；`--sheet` 自己看过；720p 抽帧和 `frames_1fps.jpg` 并排比过；关键动作看过连续帧。

## 素材一次使用与禁止循环（最高优先级）

找到或提供的外部画面素材必须遵守以下硬规则，适用于分镜、预览、正式片及转场：

- **同一段素材全片只能出现一次，绝不能循环播放。** 同一原视频的时间区间只能用一次；即使改名、裁切、缩放、调色、镜像、变速、转场或抽帧抠像，也不能再次使用相同或重叠的原始画面。不同且不重叠的原片区间可以各用一次，但要逐段标出起止时间。静态图片和截图也只能出现一次，不以裁切、放大或高亮变化作为新的素材。一个连续镜头内的镜头移动或连续高亮属于一次出现。
- **禁止循环、回放、重复拼接或用短片段来回填时长。** 素材不够长时，找新的不重叠镜头或另一份素材，或调整镜头与口播；不能靠循环凑长度。连续口播视频按原时间向前播放，切回主持人须使用尚未出现的后续画面，不得回放已播片段。
- 素材表和导演表逐镜记录来源、原片入点和出点、用途；图片记唯一来源。选片前检查所有时间区间没有重叠，剪辑与导出后复查全片，确认没有重复画面或循环。若来源区间无法核实，标为待核验，不当作已通过。
- 本规则优先于其他文件中关于素材复用、回到同一实拍或截图的示例；可承接数字、文字和图形，但不能因此重播素材。模板、组件、音乐及字幕不属于此处的画面素材限制。

## 流程：每一站停下来给用户看

审美由用户把关。不要一口气出成片；每站给出具体的东西，等他点头再往下走。

| 站 | 做什么 | 给用户看什么 |
|---|---|---|
| 0 选题 | 题目要同时满足“现在热”和“看完能带走点什么”；事实先查清、留链接；建事实账本 `<片子>/facts.md`（`references/facts_template.md`），来源分级见 `references/research.md` | 两三个题目，每个附一句钩子 |
| 1 文案 | 口语、第一人称，句句往下接；数字写成读法；**台词里的每个数字都要有账本编号**；插原声的地方先写铺垫句（`references/audio.md`） | 全文。点头之前不做正式配音 |
| 2 导演表 | 见下面“导演表”一节。模板档在“手法”一列写场景名；每一镜的素材从哪来也写上 | 要点：开头怎么抓人、每处怎么接、要不要加铺垫句、哪几处用当事人抠像 |
| 3 素材 | 官方高清片 → 新闻原文 → 当事人原声 → 当事人抠像用的整段实拍（没有切点、有对得上台词的动作）；空镜和气氛镜用 Pexels/Pixabay 图库（`stock.py`）。先拼联系表看过，再定入点，逐帧查切点；单段只截要用的几秒（`references/sourcing.md`） | 3–4 张关键样帧（真素材 + 版式），方向对了再做整片 |
| 4 配音和时间线 | 先用 `scripts/temp_voice.py` 出临时语音，或用 `scripts/timeline_stub.mjs` 按字数估出时间线，画面全部挂在字上；换正式配音后重新对齐 | — |
| 5 开头 | 先挑 3 个机制不同的钩子，各做 5–8 秒粗剪给用户选（`references/opening.md`）；选中的再做成从 0 秒到第一个换段处的小样（15–20 秒，带声音） | 3 个钩子粗剪 → 选中后的开头小样 |
| 6 全片 720p | 按导演表铺完。模板档：镜头表 → `--check` → `--sheet` → 720p；手写档：每写两三镜截静帧看，关键动作看连续帧（`strip.py`），再跑 `render.mjs --moves`。交片前跑 `motion_check.py`，720p 抽帧和 `frames_1fps.jpg` 并排比 | 720p 全片、抽帧图，再点出两三处请他重点看 |
| 7 成片 | 改到满意；换正式配音，`mix.py` 混音；出 1080p，只渲一次 | 1080p |

每次交付都要做到：
- 用 `ffprobe` 验证文件能打开。
- 自己逐镜看过静帧和联系表，关键动作看过连续帧。
- 放进一个固定的审阅文件夹，用编号加中文名命名，旧版本加 `旧_` 前缀。
- 说清楚这版改了什么、哪些量过、哪些要用户自己听或看。
- 写清这条片实际用了哪一档、哪些脚本；版权素材标出来。

## 导演表

全片只有这一份计划。用户拿它核对画面，做的时候照它做，审片时拿它对照。每一镜写这几列：

| 镜 | 时间 | 文案 | 屏上是什么，在干什么 → 停下来时留下什么 | 观众多懂了什么 | 承担 | 读懂时刻 + 停留 | 承接 | 手法 |
|---|---|---|---|---|---|---|---|---|

- **观众多懂了什么**：一句具体的话，和上一镜的不一样。写不出来，这一镜就该删或者重想。模板档里，这一列就是这一镜的 `says`。
- **承担**：这一镜靠什么让人看懂。人物 / 实证（真素材、原文）/ 构造（圆盘、图表）/ 文字（大字、结论）/ 混合。
- **承接**：上一镜留下的哪样东西被这一镜接住，接法写成 `续 / 切 / 带过 / 推近 / 展开 / 换章` 加上那样东西。第一镜写 `—`。
- **手法**：模板档写场景名（`kit/README.md` 查）；手写档写 `moves.js` 里的手法名和它在这里说什么；都对不上写“手写”。先填前面几列，最后才填这一列。
- 在“屏上”一列里顺手写清**镜头怎么走**：每次移动的落点是谁（推到谁、摇去找谁、什么时候拉回看全），以及哪几镜用当事人抠像。
- 每一镜的素材从哪来（哪段实拍、哪篇原文、哪张照片）也记下来，交片时就是出处清单。
- **需要的资料**：每镜的数字/原文/照片写账本编号（F/D/P，`references/facts_template.md`）；不在账本里的先查或换场景（`references/research.md` 的回改表）。出处和署名进简介，不上屏（规矩 16）。
- 文案一字不改；一镜可以覆盖好几句话；时刻挂在词上（“说到‘七千’的那一刻”）。

写完做一次“读表”检查：遮住文案和“多懂了什么”两列，只读“屏上”一列，看还讲不讲得通。再查有没有连续好几处硬切、有没有停不够的镜头。示例见 `examples/ai-burn-money/director.md`。

## 模板档：一条片怎么做

```
node scripts/new_film.mjs <片子目录>                  # 建片子：lib/、assets/kit/、fonts/、script.json、film.js 起点
（写 script.json：每句 {id, text}；原声插段 bite、片名位置 title 的写法见 scripts/temp_voice.py 开头）
node scripts/timeline_stub.mjs <片子目录>/script.json  # 还没配音：按字数估时间线（之后换真配音重新对齐）
（写 film.js：await K.film([ {scene, until, says, enter, …场景参数}, … ])）
node scripts/render.mjs --dir <片子目录> --check        # 几秒：镜头表错误 + 提醒，改到没有错误
node scripts/render.mjs --dir <片子目录> --sheet        # 每镜开头/中间/末尾三帧拼成 out/sheet.png，自己先看
node scripts/render.mjs --dir <片子目录> --video --h 720
```

- 场景怎么选、每个场景的参数和例子：`kit/README.md`（“这句话在说什么 → 场景”的表在最前面）。
- 能跑的完整例子：`kit/demo/film.js`（前 22 个场景各用一次）、`kit/demo2/film.js`（后 11 个）。`new_film.mjs <目录> --demo` / `--demo2` 建出来就能渲。示例片用的是占位图，看写法，不看画面内容。
- `--check` 的提醒都要处理：要么改，要么能说出为什么不改。看不了图的模型，就靠 `--check` 的文字和 `rules.md` 的条目把关。
- 一镜对不上任何场景：`scene:'custom'` 手写这一镜（`render(c)` 里用 `stage25d.js` 的工具），也要写 `says`。

## 手写档：片子怎么搭（骨架，不是拿来抄的）

- 最小的样子：`examples/google-apple-20b/film_index.html`，一个页面，只暴露 `window.ready` 和 `window.seek(t)`，`render.mjs` 直接渲。
- 完整的底座：也用 `new_film.mjs` 建片子目录。`index.html` 已经引好底座、手法库、2.5D 小工具和模板库，字体在 `lib/kit.css` 里声明；把 `film.js` 里的镜头表换成手写的镜头：`FB.init` 以后用 `shot()` 一镜一镜登记，最后 `return F.go()`。实拍帧放在 `assets/clips/<名>/`，抠像放在 `assets/cut/<名>/`。字体和素材都要在片子目录里：`render.mjs` 的服务器根目录就是片子目录，`../` 引用会 404。
- 底座（`film_base.js`）暴露 `window.ready` 和 `window.seek(t)`。`seek` 找到 t 所在的镜头（`shot(t0, t1, fn)`），调用 `fn(t)` 返回这一帧的 HTML，并等图片解码和字体加载完。同一个 t 永远画出同一帧，不依赖 CSS 动画和播放时钟。
- 时刻一律写成 `cue(句id, '词')`，从时间线里取，不写死秒数。换了配音，全片自动顺延。
- 实拍抽成帧序列，按 t 取帧，不用 `<video>`。帧数要登记，漏了会取到不存在的帧，出现黑屏或空框。
- 一镜 = 一个机位函数 + 几层画面：机位用 `camPath(t, 起点, 移动表)`，每层用 `L(机位, 上一帧机位, z, html)` 包起来，远的层 z 小，运动模糊自动算。
- 镜头之间要承接时，把上一镜的函数在它最后一刻的画面拿来做下一镜的开场（推过镜头、缩小挪走、撑开、横推出去）。这样上一镜的末态和下一镜的首态天然一致。手法库里的转场（`pushSwap`、`pushThrough`、`blurToBase`、`frameFill`）就是这样接的：`from` 传上一镜的函数。
- 手法在真片子里怎么用：`examples/ai-burn-money/film_lib.js`，第六版用底座和手法库重拼，和原版逐帧一致（素材不随仓库给，只用来读）。看它怎么在手写的画面里用手法、怎么写 why，不要照抄它的镜头。
- 720p 看效果，1080p 只在定稿后渲一次。

## 故事段（人物经历/创业故事/公司历史 → bighead 剪贴风横屏段）

含人物与事件发展的段落用 `vendor/bighead-collage`（横屏改造版）做一段插回主片；其余段沿用 kit。选段规则、横屏安全区、插入管线（帧序列进主片时间线，字幕/旁白统一走主片）见 `references/story-mode.md`。工具：`scripts/story_from_film.mjs`（抽段建工程 / register 登记帧数 / sfxmerge 音效合并 / resync 换配音后重对齐）、`scripts/story_anchor.py`（剪纸锚点）、`vendor/bighead-collage/scripts/frames.mjs --seq`（渲帧序列，重渲自动清旧帧）。含 AI 画面的片交片可渲 `render.mjs --ai-label` 烧角标；音画对齐用 `vendor/bighead-collage/scripts/verify.py --sync`（需 faster-whisper 模型，国内设 HF_ENDPOINT=https://hf-mirror.com）。

## 读哪份

| 在做什么 | 读 |
|---|---|
| 真人怎么融进来：七种样子、怎么走、挂墙、景别、声音 | `references/presenter.md`（先读） |
| 必须守的规则（编号、能检查）、“这句话 → 场景”决策表 | `references/rules.md` |
| 查资料、来源分级、写事实账本、查不到怎么回改 | `references/research.md` + `references/facts_template.md` |
| 数字主持人/AI 视频怎么生成、选路、验收 | `references/ai-presenter.md` + `references/h3-prompt/` |
| 故事段选段、横屏编排、插回主片 | `references/story-mode.md` + `vendor/bighead-collage/`（SKILL/style-card/references） |
| 模板档：场景、参数、镜头表写法、时刻、接法、颜色 | `kit/README.md`（图在 `kit/gallery/`） |
| 想一镜该放什么、为什么、凭什么接下一镜 | `references/thinking.md` |
| 动起来：为什么不像 PPT/AI、手法清单、手法 → 模板写法、手法库怎么选、量化目标、相机和抠像的代码手感 | `references/motion.md` |
| 画面长什么样：舞台、巨字、抠像、圆盘、数字、图表、片名、字幕、实拍画框 | `references/style.md` |
| 两镜之间怎么接、运镜和动作的手感、走法 → 模板写法 | `references/grammar.md` |
| 开头 | `references/opening.md` |
| 找片、下片、图库空镜、挑入点、抠人、新闻原文、原声 | `references/sourcing.md` |
| 文案、配音、原声剪口、音效、混音 | `references/audio.md` |
| 交付前自检 | `references/review.md` |
| 实践中踩过的坑 | `references/lessons.md` |
| 成片是怎么想出来的 | `examples/gold-rates/`（真人口播 28 秒）、`examples/ai-burn-money/`（77 秒，六个版本）、`examples/google-apple-20b/`（28 秒，真素材手写） |

## 工具（scripts/）

| 脚本 | 干什么 |
|---|---|
| `new_film.mjs` | 建片子：`<目录>` 新片，`--demo` / `--demo2` 示例片，`--sync` 只把 `lib/` 和 `assets/kit/` 更新到最新版 |
| `timeline_stub.mjs` | 没有配音时按字数估时间线（和 `temp_voice.py` 同格式，带 `stub:true`） |
| `footage.py` | `search` 搜片 / `get` 下载（可只下一段、只下音频）/ `sheet` 带时间码的联系表 / `scenes` 镜头切点 / `extract` 抽 30fps 帧序列 / `wave` 看原声剪口的响度 |
| `stock.py` | Pexels/Pixabay 免费图库 `search` 搜 / `get` 下（视频+图片，视频默认 ≤1080p，`--4k` / `--size original` 取全画质），写作者/许可/页面侧车 `.json`；key 写 `local.json`。只做空镜、气氛镜、通用画面，不当当事人证据（`references/sourcing.md`） |
| `gen_image.py` | 生成图（规矩 40）：只演拍不到的具体比喻物件或中性纹理，qwen-image 走 token-plan 网关，`--ref` 参考图、`--size` 默认 16:9；侧车记 prompt/模型/AI生成标记；key 写 `local.json` 的 `qianwen_api_key` |
| `snap_news.mjs` | 新闻和报告原文截图：拦广告、去浮层、等字体加载完再量关键词的框（荧光笔用，坐标写进 `docs/news.json`） |
| `commons_photo.py` | Commons 自由许可照片 search/get：验许可（只 PD/CC0/BY/BY-SA）、下载、写作者/许可/中文署名侧车 `.json` |
| `commons_logo.py` | Commons 真实 Logo → PNG（SVG 服务端渲染）、429 退避重试、追加 `CREDITS.txt`；MISSING 换精确标题或 press kit |
| `vidu_avatar.py` | Vidu S2-Avatar 数字主持人（圆窗）：单图+音频→说话视频；轮询/下载/侧车；err_code 处理见 ai-presenter.md |
| `autodl_video.py` | AutoDL 托管 ComfyUI：默认 H3 文生视频（AI 空镜）；`--presenter` 切图+音频工作流（大画幅数字主持人，5–15s） |
| `tts_tokenplan.py` | Token Plan 旁白（qwen-audio-3.0-tts-plus / longanlingxin）；.wav 自动转好喂 --asr；数字主持人驱动音频按句出 |
| `matte.py` | 实拍逐帧抠人（GPU 上 ISNet 约 0.25 秒/帧），提示藏着的切点，只存人物外框那一块。没有显卡：`examples/google-apple-20b/matte_full.py`（CPU，同一个模型） |
| `matte_clean.py` | 抠像后处理：去细线零碎、整列抹掉贴着的椅背、写出每帧头肩中心（放人时跟住他） |
| `matte_despill.py` | 抠像去色边：原片背景色（比如会场蓝幕）渗进软边，换底后一圈蓝光。软边换色、收边、压溢色，写到新目录，先 `--check` 看单帧 |
| `stage25d.js` | 页面里用的小工具：分层相机 `camPath`/`L`、关键帧机位 `camKeys`、3D 桌面 `desk3d`、方向运动模糊、景深、抠像跟人 `cutP`、巨字 `mega`、眉题、实拍退成底、按十亿取整。只是工具函数，不是镜头 |
| `film_base.js` | 底座：读时间线、`cue(句,'词')` 取时刻、实拍取帧、`shot()` 登记镜头、按时刻找镜头、字幕、预加载。镜头有空档、实拍没登记、找不到字时直接报错。模板档也搭在它上面 |
| `moves.js` | 手法库：横推换人、人身后换背景、巨字随话翻、卡片冒出来、画框推满屏、甩进来、倒成桌面、钉住换实拍、证据小卡、虚化当底、推过镜头、累加滚数。只管动作，画面由片子传。手写档直接调用，调用要写 `why`；模板档的接法也是用它做的 |
| `temp_voice.py` | `script.json` → 临时配音（edge-tts）和 `timeline.json`（每个字的时刻、原声插段、片名位置）；有正式配音时自动换上，`--asr` 重新对齐 |
| `render.mjs` | 逐帧渲染：`--check` 查镜头表（模板档，几秒，不渲染）、`--sheet` 每镜三帧拼图、`--stills` 看帧、`--video --range` 渲一段、`--h 1080` 出成片（渲完自动报“第几秒画面是空的”）；`--moves [--prev 上一条/out/moves.json]` 查手法用量 |
| `strip.py` | 连续帧拼图：一个动作 8 张，查静帧看不出来的穿帮；也用来拆参考片的动作 |
| `audit.py` | 成片像素质检：视频抽帧 vs 同时刻静帧逐块比差，抓"静帧正常视频坏"；flagged 必须 0 或每条能解释，并排图 out/audit/flagged.jpg |
| `motion_check.py` | 镜头运动自检：画面完全不动的时间、定住次数、镜头在动的时间、前后层、推拉比，和参考片的区间比 |
| `mix.py` | 配音、原声、音效、配乐（配乐给人声让路）→ -14 LUFS；`--check` 量各段响度。时间线里有 `host` 就把口播原声整条当人声 |
| `host_timeline.py` | 真人口播 → `timeline.json`：faster-whisper 逐词识别，逐字对齐到 script.json 的正文（同音字识别错不影响时刻），`--tail` 片尾多留几秒 |
| `sfx_synth.py` | 合成四样音效：软风声、上扬风声、低沉撞击、轻响（没有版权问题） |
| `kit/host.js` `kit/scenes_plus.js` | 口播层（host、pip、window、grow、drop）和新场景（line、chain），`new_film.mjs` 会拷进片子的 `lib/` |

依赖：ffmpeg、yt-dlp、Python（edge-tts、numpy、opencv-python、Pillow；可选 faster-whisper；抠人要 onnxruntime-gpu 和 rembg 下载的模型）、Node 和 Playwright。安装方法见 README。

字体不随仓库给，要自己下（清单见 README）：Bebas Neue、阿里妈妈数黑体、MiSans、Montserrat，文件名以 `kit/kit.css` 里的 `@font-face` 为准。下好放进一个文件夹，在 `scripts/local.json` 里写 `fonts_dir`；`new_film.mjs` 建的片子里，`fonts/` 是指向这个文件夹的联接，联接建不了就拷过去。Playwright、ffmpeg、yt-dlp 不在默认位置时，也写在 `local.json`（`playwright_from`、`ffmpeg`、`ffprobe`、`yt_dlp`；后三个写 exe 路径或所在目录都行，py 脚本经 `scripts/local_bins.py` 统一解析）。`yt_dlp` 指到目录时取其中的 `yt-dlp.exe`：它的便携配置 `yt-dlp.conf` 和 cookies 放在 exe 同目录会自动生效。这个文件只放本机配置，不进仓库。Pexels/Pixabay 图库（`stock.py`）要免费 key：[pexels.com/api](https://www.pexels.com/api/) 和 [pixabay.com/api/docs](https://pixabay.com/api/docs/) 申请，写进 `local.json` 的 `pexels_api_key` / `pixabay_api_key`（或环境变量 `PEXELS_API_KEY` / `PIXABAY_API_KEY`）。生成图（`gen_image.py`）用 `qianwen_api_key`（或 `QIANWEN_API_KEY`），按张计费。

## 配音：先用临时语音

- 先用 `temp_voice.py` 出 edge-tts 临时配音，排出时间线，画面照它做。
- 文案和画面都定了，再换正式配音（任何 TTS、克隆音色或真人录音都可以）：每句存成 `voice/<id>.final.wav`，跑 `temp_voice.py script.json --asr`。
- 配音一律：切掉首尾静音、保持原速、句间停顿只由 `gap` 决定。不要事后用 atempo 加速，切掉静音以后再加速会很急促。
