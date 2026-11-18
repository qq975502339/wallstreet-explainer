# 更新记录

- v2.3（2026-11-18）：加免费图库工具 `scripts/stock.py`（Pexels/Pixabay 搜+下，视频和图片，视频默认 ≤1080p、可 `--4k` / `--size original`，写作者/许可/页面侧车，429 自动退避；做法借鉴 OpenMontage 的 pexels/pixabay 工具，改成本 skill 的纯标准库两段式）。加生成图工具 `scripts/gen_image.py`（qwen-image 走 token-plan 网关，做法借鉴 OpenMontage 的 token_plan_image；规矩 40 内置提醒，侧车记 prompt/模型/AI生成标记，`--ref` 参考图），key 用 `local.json` 的 `qianwen_api_key`。key 写 `scripts/local.json`；`references/sourcing.md` 加图库空镜一节和优先级定位（只做空镜气氛镜，不当当事人证据）。
- v2.2（2026-11-04）：加真人口播模式，一个 skill 两种模式（给了口播视频走真人口播，没给走无人动效包装）。新增口播层 `kit/host.js`（房间、挂墙、身后换世界、圆窗、竖窗、长回、掉落）、`line` 和 `chain` 场景、口播逐字对齐 `host_timeline.py`、合成音效 `sfx_synth.py`；`mix.py` 认口播原声；`references/presenter.md`；例子《打仗了，黄金为什么反而跌》。
- v2.1（2026-10-31）：`render.mjs --check` 补漏：改了文案没重算时间线直接提醒重跑 `timeline_stub`；参数名写错直接报错并猜正确写法（比如 `lable` → `label`）；只用占位图的镜头不算真素材；报错去掉程序内部字样。`timeline_stub` 把"〇"按汉字算时长；`new_film` 打印完整步骤；chart 标题下的英文小字参数改叫 `en`（`sub` 仍可用）。
- v2.0（2026-10-31）：加模板档 `kit/`（31 个场景、镜头表、`render.mjs --check` 文字自检）、`references/rules.md`、新建片子的 `new_film.mjs`；新例子《谷歌给苹果的两百亿》；找素材、渲染踩的坑补进文档。
