# 版式速查：想要那种画面 → 用本项目哪个场景（B5）

> 对照 howoneai/xiaolin-explainer-packaging 版式库（MIT，见 NOTICE.md）与 zenskill layout_mapping 的思路；**本项目 42 场景比两者都富**，多数"对方做不到"的这里做得到。选完版式仍要过画法表（treatment.md）与句型表（shot-grammar.md）。

| 想要的画面 | 适用场合 | 本项目场景 | 备注 |
|---|---|---|---|
| 巨型数字 | 这句就在讲这一个数 | `number`（host 让位对侧） | text=口播原样 |
| 卡片墙跟拍 | 2–4 并列概念 | `cards3d` / board 连卡 | 跟拍+其余虚化已有 |
| 白卡柱/条形图 | 几年对比/多项比较 | `chart(kind:'bar')` / `bars` | 白卡是 kit 家族 ✓ |
| 原文荧光笔 | 法规/公报/合同条款 | `docpage` / `article hl` | 逐字原文；截不到用 mock |
| 真实网页+聚光 | 报道/官网/公示页 | `article`（真截图）+ hl | 图片社照片须模糊（sourcing） |
| 真实 Logo | 讲到具体产品/机构 | commons_logo + `board/discs` 节点 | 商标只指代不改色不背书 |
| 实体名片 | 国家/公司/机构 | `profile` / `discs` | 事实≤3 条按发布日核 |
| 大公式条 | 分步公式/因果链 | `equation` / `chain` | ≤3 步可 host 对侧 board 链 |
| 白底计算器 | "如果你…会怎样"测算 | `calc` | 上屏数字仍与口播一致 |
| 分段画线 | 走势/涨跌 | `line`（真实日线）/ `chart draw` | 边说边画=draw 区间或拆两镜；骑线头=rider |
| 时间轴 | 沿革/节点 | `timeline`（含 below 变体） | 沿轴平移=camSeq |
| 饼/环切照片 | 构成/占比 | `share`（pie/hole/legend/img） | img=真实照片切扇区 |
| 流程/循环 | 步骤/产业链 | `flow`（含 loop 回环） | 回环箭头已有 |
| 树状拆解 | 一项拆几项 | `tree` | 分支已有 |
| 地图航线/国家填色 | 产地/路线/分布 | `map`（dots/countries+vehicle） | 涉中国疆域用有审图号标准地图或不用 |
| 左右对比 | 两方对比 | `compare` / `versus` | 两侧配真画面/Logo；versus 面积比真 |
| 关系/资金流 | 持股/流向 | `network`（dot 道具流） | 边流小图标已有 |
| 象形堆/百格 | "每100个里有多少"/钞票堆 | `stack` / `grid` | 总数要数得清 |
| 观众想法气泡 | 误区/普遍说法 | `bubble` | 虚构昵称+普遍性证据 |
| 片名/目录/章节感 | 开场/章节 | `title` / `agenda` / `flash` | 参考片无数字章节卡（E9）→关键词目录卡 |
| 金句/结论 | 观点句 | `statement` | 判断须被账本支撑 |
| 故事段 | 人物经历/创业/公司历史 | story 段（bighead 横屏插回） | 见 story-mode.md |

| 从 X 变到 Y | 涨跌/翻倍/腰斩 | `change` | 倍数标"约" |
| 几个数并列 | 多指标一览 | `stats` | 同口径同单位 |
| 排名/前 N | 谁第一 | `ranking` | 主角单独色 |
| 人物站巨字前 | 人物+主题词 | `person` | 身份按发布日核 |
| 真人原话 | 引语 | `quote` | 逐字+hl 原样 |
| 钉住换实拍 | 实拍串 | `montage` | 成段 4–16s |
| 画框并列 | 多画面对比 | `frames` | 每框出处 |
| 新闻桌面圈注 | 圈注/盖章 | `desk` | 每张截图自带 hl/stamp |
| 反应窗 | 吐槽插话 | `popup` | 1–2s 核实报道 |
| 标题墙 | 多家报道 | `headlines` | 每条真出处 |
| 产品界面 | 操作演示 | `device` | 记版本/日期 |
| 主持人出镜 | 口播 A-roll | `host` | 五排布+zoom 机位 |
| 手写兜底 | 以上都不贴合 | `custom` | 上屏一切进账本 |

## 选版式两条规矩

1. **同一骨架不要连用两镜以上**（不要连着三张大数字卡）。
2. **每个图形场景至少一样本期专属物**（照片/道具/Logo/官方截图），见 treatment.md；`--check` 会提醒。
