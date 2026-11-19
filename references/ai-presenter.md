# AI 数字主持人与 AI 视频（移植自 OpenMontage editorial-explainer-packaging）

**只在用户明确要求主持人时启用**；默认无主持人（真人口播模式优先用真人素材）。三条生成路：

| 路 | 脚本 | 适用呈现 | 输入 | 时长 | 钥匙（local.json / 环境变量） |
|---|---|---|---|---|---|
| Vidu S2-Avatar 非实时 | `scripts/vidu_avatar.py` | 角上圆窗 `host:'pip'`（只露脸） | 1 张单人图 + 音频（或 text） | 由音频实际时长决定 | `vidu_api_key` / `VIDU_API_KEY` |
| AutoDL H3 图+音频 | `scripts/autodl_video.py --presenter` | 房间全屏 `scene:'host'`、竖窗 `host:'window'`（头肩+上半身） | 参考图 URL + 参考音频 URL + 逐段提示词 | 每次 5–15 秒整数 | `autodl_token` / `AUTODL_COMFYUI_TOKEN`（权限组绑 H3） |
| AutoDL H3 文生视频 | `scripts/autodl_video.py` | 空镜/气氛镜/动态示意（AI 视频） | 文本提示词 | 按工作流 | 同上 |

旁白统一走 `scripts/tts_tokenplan.py`（qwen-audio-3.0-tts-plus / 默认 longanlingxin，key 复用 `qianwen_api_key`）。

## 选路与回退

- 圆窗 → Vidu（省提示词）；大画幅 → H3（这两类画幅易暴露镜头漂移和颈/肩变形，靠逐段提示词兜住）。
- H3 不可用/权限不足/工作流失败 → 大画幅改 Vidu；Vidu 积分不足（余额 <45 积分不能发起）或用户指定 → 小窗改 H3。**切换前告知用户并记录原因，不擅自换供应商。**
- 一次网络超时或单次失败 ≠ 服务不可用：先查已有 task_id 的状态，避免重复计费。

## 配音先行、形象固定

1. 先按句出旁白：`tts_tokenplan.py "<句>" voice/<id>.final.wav`（.wav 自动转好），听检后 `temp_voice.py script.json --asr` 真实对齐；估算时间线只用于预览。
2. 把**对应段音频**传给 `vidu_avatar.py --audio` / `autodl_video.py --ref-audio`；不要用 Vidu text 模式另配一套声音（用户明确要求除外）。
3. 同一形象全片**同一张角色图**；圆窗靠剪辑裁脸，不为小窗另生成形象（否则一支片里出现两个人）。
4. 参考图/音频给 H3 时**以流的方式**进 body：`ref_image_0`/`ref_audio_0` 接受 base64 data URI（脚本对本地文件自动编码，**实测通过，不需要公网上传去处**）；也可直传公网 URL。Vidu 本地素材自动 base64，解码后 ≤20MB，更大先传公网 URL。

## H3 口播镜头硬约束（写进每段 prompt，逐条，不能只写"镜头稳定"）

- **镜头**：禁止推、拉、摇、移、跟、升降、环绕；禁止重新构图、变焦、裁切变化；禁止背景变化（换景、元素漂移、明暗跳变、影子移动）；禁止画面抖动、呼吸式起伏、边缘闪动。
- **人体**：脖子、喉咙、下巴、肩膀、衣物、麦克风不得皮肤波动/液化/融化/拉伸/几何变形；不得颈部肌肉抽动/鼓起/脉动、下巴与脖子粘连、肩膀轮廓塌陷、衣领布料蠕动、麦克风/耳机弯曲/抖动/漂移/穿模。
- 只允许说话必要范围内的口型、眨眼和极轻微自然呼吸。
- 提示词结构按 `references/h3-prompt/README.md` 选 base-en / ref-en；**模型输出是概率性的，提示词不是保证，抽帧检查才是验收依据**。

## 验收（任一不合格就重生成，不靠剪辑掩盖）

| 部位 | 看什么 |
|---|---|
| 脖子/喉咙 | 抽动、鼓起、脉动、融化；说话吞咽时撕裂 |
| 下巴 | 与脖子粘连；下颌线抹平/拉长/扭曲 |
| 肩膀 | 轮廓塌陷/拉伸；左右突然不对称 |
| 衣物 | 衣领、布料纹理蠕动/扭曲/穿模 |
| 麦克风/耳机 | 弯曲/抖动/漂移/穿模 |
| 背景/构图 | 推拉摇移、重新构图、背景变化、整体抖动 |

方法：整段播放核对口型与台词、听音色；`ffmpeg -i 片段 -vf fps=6` 抽帧拼接触表逐张看；比对首帧与末帧的构图/背景/麦克风位置，有位移即判未锁定。记录 task_id、duration、credits 进侧车与决定记录。

## Vidu 参数与失败处理

参数：`image`（必填单人图）、`audio`/`text`（至少一个，同传以 audio 为准）、`voice`（仅 text 模式）、`timeline`（`[{text,time_range:[s,e]}]`，不传服务自动生成）、`resolution` 720p/1080p/2k、`watermark`（脚本固定 false，下载无水印 creations[].url）。
err_code：`ImageCheckFaceFailed`/`ImageCheckBodyJointsFailed`/`ImageObjectsUndetected`/`MultiFaceDetected` → 换角色图；`CreditInsufficient` → 充值；`TooManyRequests` → 降轮询（脚本间隔 ≥2s 渐增到 8s）。
计费 1 积分/秒、1 积分 0.03125 元；出片约 40s–2min；creations URL 24h 过期，脚本立即下载。

## AutoDL 协议

`POST https://autodl.art/api/v1/comfyui/comfyui_workflow/{workflow_id}`（Header `Authorization: <token>` 原样）→ `data.task_id`；
`GET .../comfyui_workflow/result/{task_id}` → `data.status` SUCCESS 取 `results[0].url`（短效立即下载）/ FAILED 报 message。
body 透传：prompt/duration/resolution + `ref_image_0`/`ref_audio_0` + `--body` 额外字段；工作流 ID 可 `--workflow` 覆盖。

## 接进本项目 host 管线

1. 片段 mp4（带音轨）→ `footage.py extract` 抽 30fps 帧序列 → `counts.json` 登记；
2. 该片段音轨即口播原声：`host_timeline.py` 逐字对齐（或旁白 wav 走 `temp_voice.py --asr`），`mix.py` 认 host 原声；
3. 圆窗/竖窗/挂墙由 `kit/host.js` 现有裁切合成完成（Vidu/H3 输出不透明，不需要透明 WebM）；
4. 片段实际时长决定排布（不是申请值）；字幕/分镜按真实音频重对齐。

## 标注与配额（规矩 44）

- AI 数字人**不得称真人**；上屏标"AI生成"；不作当事人/真实证据；CREDITS 记 task_id/模型/积分/形象图来源。
- 用户指定出镜占比时：分母 = 最终成片实际总帧数；分子 = 约定形态可见区间并集（重叠只计一次）；**不得把生成片段溢出从分母扣除**；未指定不设配额。H3 短台词可检查口型后剪用其中一段，只按保留画面计占比。

## 实测记录与排坑（2026-11-19，本机）

- **Token Plan TTS / 生图：实测通过**（`tts_tokenplan.py` 出 wav、`gen_image.py` 出形象图）。
- **AutoDL H3 文生视频：实测通过**（5s / 1280×736 / 带 AAC 音轨；抽帧联系表无漂移）。
- **AutoDL H3 图+音频（presenter）：实测通过**（5s / 1344×768 H3 原生 / 带音轨；参考图+音频以 base64 流进 body，无需公网上传；fps=6 抽 31 帧身份/背景/构图锁定）。**resolution 枚举按工作流不同**：presenter 收 `768p横`，t2v 收 `736p横`；报 `RequestParameterIsWrong` 时按该工作流抽屉页 options 改，不要跨工作流套用。
- **Vidu：实测通过**（4s / 714×1288 竖屏随参考图比例 / 4 积分；fps=2 抽 8 帧身份与背景锁定）。曾把型号标签 `vidus2` 误拼进 key（key 实际以 `vda_` 开头）导致认证边缘 403 空响应。诊断法保留：不带 Authorization 请求 `/ent/v2/tasks/<数字id>/creations` 返回 **401 JSON**（网络与接口正常）；带 `Token <key>` 返回 **403 空 body** = key 被认证边缘拒绝（无效/过期/无权限/区域不对），去控制台查或重发，**不是代码或网络问题**。
- **大 base64  POST 曾触发 SSL EOF**（本机网络对大上传体不稳定）：参考图缩到 ≤512px 或改传公网 URL 可绕开；脚本对本地素材自动 base64，>20MB 直接拒。
- **AutoDL resolution 是严格枚举**：`736p横`（1280×736，H3 原生）等，`768p横` 不存在；报 `RequestParameterIsWrong` 时按目标工作流页面 options 改。

参考驱动与单段锁定已实测；正式制作前仍须**人工听口型对台词**、放大查颈/喉/下巴细节、多段时查跨片段身份一致性；权限不足/素材不可访问/服务不可用时如实报告阻碍，不擅自换工作流。