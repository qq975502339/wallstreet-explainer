# <选题> 事实账本

每条上屏内容一条记录。分镜里的数字、原文、照片只能来自这里；编号写进导演表"需要的资料"列。
出处与署名进 CREDITS.md / 视频简介（规矩 16），**不上屏**。分级与查法见 `references/research.md`。
链接必须为完整 `https://` 地址；日期写 `YYYY-MM-DD`（年报发布日期可写 `YYYY` 或 `YYYY-MM`），不用"上周/今年"等相对时间。
下面 F01/F02 用《AI到底有多烧钱》的真记录做例，D01/P01/C01 是格式例。

## F01 四家 2026 年 AI 资本开支合计
- 上屏写法：$7250亿
- 原文（逐字，转述句）："Google, Microsoft, Meta, and Amazon capex spending to hit $725 billion in 2026"
- 来源：Tom's Hardware，汇总自各公司一季度财报指引
- 链接：https://www.tomshardware.com/tech-industry/big-tech/big-techs-ai-spending-plans-reach-725-billion
- 发布日期：2026-04-30；查阅日期：2026-05-01
- 级别：权威转述（一手为四家财报，找到后换一手并保留差异说明）
- 口径：多源汇总（若是单源或公司自述，写 `单源` / `当事方自述`）
- 原页核对：已开页，正文首段汇总表确认支持（承重核心数必填）
- 用在：镜 1（number）、镜 7（chart total）

## F02 每天烧多少（推算）
- 上屏写法：约 $20亿/天
- 推算方法：F01 ÷ 365 ≈ 19.86 → 约 20亿（算式存档）
- 输入：F01
- 来源：由 F01 一手/权威数据推算
- 链接：https://www.tomshardware.com/tech-industry/big-tech/big-techs-ai-spending-plans-reach-725-billion
- 发布日期：2026-04-30；查阅日期：2026-05-01
- 级别：推算
- 用在：镜 2（equation）

## D01 国务院关于渐进式延迟法定退休年龄的办法 第二条（docpage 原文）
- 原文（逐字）：
  > 第二条 从2030年1月1日起，将职工按月领取基本养老金最低缴费年限由十五年逐步提高至二十年，每年提高六个月。
- 高亮：由十五年逐步提高至二十年
- 来源：国务院《关于渐进式延迟法定退休年龄的办法》第二条
- 链接：https://www.gov.cn/zhengce/content/202409/content_6974294.htm
- 发布日期：2024-09-13；查阅日期：2026-05-01
- 原页核对：已开页，条款全文逐字核对一致
- 用在：镜 10（docpage marks[0]）

## P01 黄仁勋照片（圆盘用）
- 文件：assets/img/jensen.jpg（侧车 jensen.jpg.json 由 commons_photo.py 生成）
- 作者 / 许可：Anders Eidesvik / CC BY 4.0
- 页面：https://commons.wikimedia.org/wiki/File:Jensen_huang_stanford_2026-04-30_011.jpg
- 署名（进简介，不上屏）：Anders Eidesvik / CC BY 4.0 / Wikimedia Commons
- 用在：镜 4（discs photo）

## C01 反方证据 / 失效边界（中长片必填，须官方或权威转述）
- 结论/反例：四家云业务同期营收增速与自由现金流仍能覆盖部分资本开支，不能等同于全部纯亏损
- 来源：各公司 2026 Q1 10-Q 财报（示例格式，按实际替换）
- 链接：https://www.sec.gov/edgar/searchedgar/companysearch
- 发布日期：2026-04-30；查阅日期：2026-05-01
- 级别：一手
- 原页核对：已开页，现金流量表经营活动现金流栏确认支持
- 用在：第 4 章边界与风险段（平衡结论，不上绝对化铁论）

## 未验证（不上屏）
- 例：某年度调整幅度，只有自媒体说法，找不到官方通知——留在这里，不进任何镜头。
