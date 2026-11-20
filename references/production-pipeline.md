# 视频制作清单、检查与交付（A 层）

这套工具补充现有 `script.json`、`timeline.json`、`film.js` 和渲染器：**不自动搜素材**（搜素材用 `fetch_footage.py`）、**不自动识别口型**（只量音轨偏移与逐句偏差）、**不自动验证事实**（facts_check + 人查）。所有时间以秒为单位；交片前仍按 `references/review.md` 逐镜逐声检查、过 `visual-checklist.md` 八问。

## 创建清单和镜头初稿

```powershell
python scripts/video_pipeline.py init <片子目录>     # production.json + PROGRESS.md（续做日志）
python scripts/video_pipeline.py draft <片子目录>    # draft_shots.json：按 B 表 12 句型+内容触发出候选，全标 needs_review
```

初稿只是候选，不绑定画面/时间，不改 film.js；已存在不覆盖。精修按 `references/shot-grammar.md`。

## 清单怎么填

`cuts` 是硬切/弱口型标记（人工或 `marks` 自动喂）；`overlays` 的 `coverage:'full'` 表示整幅遮住原画面（**pip 不算**）；`numbers` 手动记口播与屏幕文字；`media_usage` 的 source 是原片稳定标识（同原片不同文件名仍同 source），视频区间是**原片时间**；图片 `kind:'image'`；`media` 每条须 source+license（缺=fail）；`chapters` 不重叠；`final_video`/`sync_reference`（按成片时间轴对齐的正式配音）/`loudness_target:-14`/`true_peak_limit:-1.5`/`expected_frames` 可选。

空数据报 review 不装通过；工具不验证链接/许可真假、不检测改名后未统一 source 的重复。

## A1 A-roll 入库体检（口播抽帧前先跑）

```powershell
python scripts/video_pipeline.py aroll <口播.mp4> [--voice <配音.wav>] [--fps 30] [--json build/aroll.json] [--fix <修正副本.mp4>]
```

查恒定帧率（avg≠r 判 VFR）、帧率 vs 时间线、**首帧重复**（帧0=帧1→全片晚1帧；只判比特级相同，保守）、配音 vs 帧数差>1帧、16:9/分辨率提醒；6fps 灰度差自动检测疑似硬切写 `build/aroll.json.hard_cuts`（须人工确认）。`--fix` 出去首帧重复/转 fps 副本（防覆盖），用副本复检。有 fail 退出 1。

## A3 自动标记喂接缝表 + 覆盖门禁

```powershell
python vendor/bighead-collage/scripts/verify.py --sync <片子> --from <成片.mp4> --beat-json build/sync_beats.json
python scripts/video_pipeline.py marks <片子>
python scripts/video_pipeline.py audit <片子>
```

`--beat-json` 导出逐句口型偏差（**匹配率 gate 之前导出**：匹配率不足时更需要逐句数据）；`marks` 把硬切 + |偏差|>70ms 弱句合并进 `production.json.cuts`（标 origin、幂等、不删人工）；`audit` 的接缝覆盖检查逐条核"是否被全屏 B-roll 罩住前后 0.12s"，没盖=fail。

## A2 可商用实拍检索与署名登记

```powershell
python scripts/fetch_footage.py search "<中文>" "<english>" [--kind video|image] [--sources …] [--n 6] [--save hits.json]
python scripts/fetch_footage.py get <片子> --hits hits.json --pick 3 --id city_aerial
python scripts/fetch_footage.py add <片子> --id x --source Mixkit --author … --page … --license … --license-url … [--url … | --file …]
```

八源、中英双关键词、**ND/NC/Editorial 自动排除**；下载落 footage_raw/ 并登记 credits.json（author/page/license/license_url 齐全）；钥匙走 local.json/env；防覆盖。audit 缺来源/许可判 **fail**。下载后仍走单次使用/区间不重叠规则。

## A4 统一检查

```powershell
python scripts/video_pipeline.py audit <片子目录>
```

生成 production-report.md/json；有 fail 退出 1。检查：接缝覆盖、数字与口播、素材重复/循环、章节、素材入库（probe+尺寸+许可）、成片（完整解码+音轨+帧数）、响度+真峰值（ebur128）、**流式冻帧/黑帧/长静音**（freezedetect/blackdetect/silencedetect 单遍）、音轨偏移（互相关 3 窗口+置信度/歧义门禁）。pass 只表示登记信息过机械检查；review=未提供或需人判断；口型/画面/事实/许可真假仍人查。

## A5 分章节预览 / 封面 / 分享版

```powershell
python scripts/video_pipeline.py render-chapters <片子> --height 720   # 按 chapters 调 render.mjs --range，out/chapter-progress.json 记状态；每次从头重渲所列章节
python scripts/video_pipeline.py cover <成片.mp4> <横.png> --at 1.5     # 横=缩放留边；--portrait=中央裁切 1080x1920
python scripts/video_pipeline.py share <成片.mp4> <分享版.mp4> --height 720 --crf 24   # H.264/AAC；不保特定大小
```

输出防覆盖；封面只导出帧不设计标题；构图/字幕/人物须人查。

## C1 帧率对齐 / C5 细痕检查（已接的 C 层两项）

```powershell
python scripts/footage.py conform <源.mp4> <副本.mp4> speed|dup   # speed=变速使每源帧恰好一帧（改动作速度，慢镜头慎用）；dup=补帧（接受卡）；防覆盖；源=30fps 提示无需处理
python scripts/footage.py extract clips.json                    # 源≠30fps 会提醒先 conform
python scripts/video_pipeline.py audit <片子>                   # 报告含"细痕检查"：重复帧(stutter,逐帧差<0.5判fail)/疑似掉帧(突跳后回落,review人复核)/疑似咔哒(采样突跳>0.45,review人耳复核)
```

C5 与 A7 分工：A7 抓长坏（冻帧≥2s/黑帧≥0.5s/静音≥3s），C5 抓一瞬坏（0.03s 的顿/30ms 的啪）。掉帧/咔哒给 review+时间码供人复核（硬切也会突跳，机器不独断）。

## A7 流程件

```powershell
python scripts/selftest.py                       # 环境自检：node/playwright/chromium/ffmpeg/ffprobe/python依赖/字体/keys/kit文件；核心fail退出1
python scripts/music_candidates.py <片子> [--pick N]   # 列候选+试听命令；选定拷为 music/bed.* 并登记 SOURCES.md（许可须人工填全）
```

PROGRESS.md 由 init 创建：每完成一步追加一节，会话中断从它续做不重做。音乐床相对人声约 -18 dB（总响度仍 -14 LUFS）。

## 边界

不测口型好坏（只量音轨偏移/逐句偏差）；不宣称测了黑帧以外的画面质量（黑帧/冻帧/静音已测）；不自动决定镜头美观；事实/许可真假/字幕/口型仍人查。与 mix.py --check / facts_check / motion_check / review.md 配合使用，不替代。
