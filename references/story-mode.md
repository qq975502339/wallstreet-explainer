# 故事段模式（bighead-collage 横屏改造版）

**选段规则**：一条片里讲**人物经历、创业故事、公司历史**的段落（有人物与事件发展、适合故事化演绎）→ 用本模式做一段横屏剪贴风故事段插回主片；纯数据说明、图表、新闻证据、主持人口播 → 沿用 wallstreet kit。用户明确指定其他风格/画幅时按用户要求。

代码在 `vendor/bighead-collage/`（上游 HeyChengC/bighead-collage，MIT；字体 OFL 随附；参考图/素材权利按上游 README 与各自来源）。**已改造为横屏原生**，不是上游竖屏原版：

| 改造点 | 内容 |
|---|---|
| `scripts/stage.js` | 逻辑舞台 1080×1920 → **1920×1080**；颗粒画布 640×360；字幕默认 y=980、单条上限 22 字；irisOut 默认收圆半径 320 |
| `scripts/acts.js` | 离屏距离按舞台尺寸算（drop/rise/out 默认值），不写死竖屏像素 |
| `scripts/landscape.js` | 新增横屏 helper：`picture`（剪纸滑入）、`caption`（固定字幕，仅单独短片用）、`titleRow`（年份/人名橙黄行）、`SAFE` 安全区 |
| `scripts/new_film.py` | 脚手架默认 aspect 16:9、载入 landscape.js |
| `scripts/frames.mjs` | 新增 `--seq <dir>`：渲 JPG 帧序列（%04d.jpg 从 1 起，与 kit 实拍帧惯例一致），供主片当 footage 帧源 |

其余（look.css 颜色/字体、动作语法、转场 TX、sfx 登记、mix/verify 等）保持上游原样。

## 横屏编排规矩

- 坐标 1920×1080；**安全区 x 100–1820 / y 80–870**（与 kit 一致；y≥900 是字幕带）。
- 大头剪纸脚踩点用 `scripts/story_anchor.py` 写锚点（`ACTS.person` 读 `img/<名>.json`）。
- 一场一个小舞台 + 一台相机；参考片手感：一场 1–2 个大动作，动作之间停一停（`spline` 的 `'h'` 停点）；坏事从上砸（`drop`）、好事从下弹（`rise`）、贴条转着拍（`slap`）。
- **插入主片时故事段不烧字幕、不带音轨**：字幕与旁白继续走主片管线（`film_base` 字幕覆盖全片时间线），避免双字幕双音轨。单独横屏短片才用 `captions()`/`STORY_LANDSCAPE.caption`。
- 转场核验：iris/fromRect 的半径与框坐标按横屏重算；首末帧构图比对防漂移。

## 插入主片管线

```
node scripts/story_from_film.mjs <片子> <故事名> <句id,句id,…>   # 建 assets/story/<名>/ + 本地时间线（主片子集平移）
（写 scene.js；备 img/ 剪纸；python scripts/story_anchor.py img/x.png）
node vendor/bighead-collage/scripts/frames.mjs --dir <片子>/assets/story/<名> --seq <片子>/assets/clips/story_<名> --h 1080
node scripts/story_from_film.mjs register <片子> <故事名>        # 帧数进 counts.json
（主片 film.js：{scene:'footage', clip:'story_<名>', from:0, push:[1,1], until:<故事段后第一句>, enter:'whip'|'through'|…}）
```

- 故事段句子的**旁白就是主片旁白**（同一条音轨、同一音色）：主片 `temp_voice.py`/`host_timeline.py` 照常出时间线；故事段本地时间线只是它的子集平移，口型/动作挂在字上（`at/beat`）。
- 故事段自己的音效（`sfx()` 登记）可选合并：`sfxlist.mjs` 导出后把时刻加上故事段在主片里的起点偏移，并进主片 `sfx.json`。
- 承接按 kit 语法：进入用 `enter:'whip'/'through'`，离开接下一镜的 `enter`（故事段末帧构图留给下一镜接）。
- 验收：故事段抽帧（`frames.mjs --stills`）查安全区/可读性/转场；主片 `--check`/`--sheet`/720p 抽帧与 `frames_1fps.jpg` 并排；故事段画面是**演绎**，标"AI生成/演绎"按规矩 44，真实事件证据仍用 kit 的 article/footage 真素材。
- 主片 `--check` 会对长 footage 镜提醒"中间没有新落点"：故事段**内部场景切换就是落点**（iris/whip 在各句起点），答得上就留；想更碎可按故事场拆成多个 footage 镜（转场会叠加，慎用）。

## 与上游/fork 的差异说明

上游竖屏原版坐标不能直接沿用（fork 的 `--landscape` 只改常量、仍需手工重排）；本改造把舞台/字幕/离屏距离/颗粒全部横屏化，并提供布局 helper 与安全区，场景内容仍由导演表逐场设计（helper 不是现成模板）。合成不靠拼接 mp4（fork assemble-story 只硬切+补黑边），而是**帧序列进主片时间线**，转场/字幕/音频统一由主片管。