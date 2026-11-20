# 借鉴台账（borrow ledger）

> 每块能力：来源 / 提交 / 防什么 / 怎么验收 / 怎么回滚。蒙的时候查这张表；坏的时候 `git revert --no-edit <sha>` 只回滚那一块。
> 原则：一次一个痛点、一阶段一 commit、测试绿才提交、只新增少修改。

## 已在仓库的批次

| 提交 | 来源 | 内容 | 防什么 | 验收 | 回滚 |
|---|---|---|---|---|---|
| `3fd970a` | OpenMontage fork + 实测 | 事实查核体系；Vidu S2 / AutoDL H3 数字人；TokenPlan 配音/生图 | 数字无出处；主持人/第一人称无法生成 | facts_check；presenter_test 实片 | revert |
| `fc6cf21` | bighead-collage | 大头贴故事引擎 vendoring | 人物经历/创业/公司历史段无故事画面 | story 静帧/插片 | revert |
| `cedc642` | 审计+会话 | 缺陷1–10 修复；画廊39张；故事段管线（resync/sfxmerge/清旧帧/预检/resume/ai-label/facts_check/whisper缓存/sync接清单） | 字体丢失/旧帧/换配音漂移/付费盲提交/假通过 | tests/test_repairs.py；复现用例 | revert |
| `1502913` | 用户/审计修订 | verify 匹配率门槛、facts_check 诚实化、host_timeline 低匹配拒出、sfxmerge 替换、保比例抽帧、--check-fonts、check_clip/scene_diff | 检查器假通过/崩溃 | tests | revert |
| `8ad7ce0` | 用户 | 静态组件预览画廊 | 选场景看不到样张 | gallery/00_sheet | revert |
| `229bea5` | 用户 | 素材单次使用禁循环 | 重复画面/循环穿帮 | review 人查 | revert |
| `b96283b` | xiaolin v1.4/v1.5 + 审计收尾 | 道具通用层+四插槽+照片垫底+20画风+画法规矩；审计修复合批 | 每期像PPT模板；穿帮/侵权/假通过 | propdemo 五镜；tests | revert |
| **本 commit（B 层）** | zenskill 思路+数据（自有重写）；howoneai MIT 文档 lineage | shot-grammar / reference-evidence / visual-checklist / layout-mapping / research 补 / treatment 补 / NOTICE / 本台账 | 分镜靠感觉、节奏无尺子、规则无判例、审片无清单、许可声明缺失 | 文档审读；tests 全绿；git status 仅 md | revert |

## 被回滚 / 未接的备选池（不在仓库，按需重放）

| 项 | 来源 | 防什么 | 状态 |
|---|---|---|---|
| A1 A-roll 体检（CFR/首帧重复/配音vs帧数/硬切/--fix） | zenskill prepare_aroll | 全片错半拍 | 曾移植未提交→用户回滚；可重放 |
| A2 八源检索+ND/NC 门禁+credits | zenskill fetch_footage | 侵权/漏署名 | 同上 |
| A3 弱口型/硬切自动标记+覆盖门禁 | zenskill compile+verify | 穿帮裸奔 | 同上 |
| A4 交片检查包 / A5 交付便利 / A6 分镜草稿 / A7 流程件 | zenskill | 漏检/交付麻烦 | 同上 |
| C1–C10（conform/进度条/条目语法/拍点床/掉帧咔哒/封面嵌帧/聊天版/ChatCut/selftest/淡入） | zenskill engine | 各类 | 未接 |
| 环2（SyncNet 判弱+修口型/face-embedding 验收/ffmpeg 内置检测/FunClip/LLM 分镜/平台规范） | 调研方向 | AI 验收/黑帧冻帧 | 未接，需调研 |
| 最后一层（J/L-cut/匹配剪辑/音色表/语义断句/素材索引/时间码批注/光敏/增量渲染/完播回流） | 通用工程 | 更顺更省 | 未接，自建而非借鉴 |

## 不借清单（冲突或已覆盖）

24fps（咱们30）；-16 LUFS（咱们-14）；默认不加 AI 标（咱们规矩40/44必标）；Remotion 引擎（咱们 Playwright）；来源上屏（规矩16）；zenskill 图表组件（42场景已覆盖）；参考片换算数字写法（G2 原样）；粉紫配色/白斜卡设计/商标墙/新闻政要梗图素材/金属立体字书法字（许可或家族冲突）。

## 许可

见 `NOTICE.md`：howoneai MIT（保留声明）；zenskill 无 LICENSE→只借思路与数据、自有重写；bighead MIT+OFL 随附；字体各自许可。
