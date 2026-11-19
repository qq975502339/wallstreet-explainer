# 道具画风目录（v1.5 接入，20 种）

数据：`kit/prop_styles.json`（提示词后缀 suffix + 公共结尾 tail + 阴影 shadow + 深/浅底旗标 + luma 标记）；小样：`kit/assets/prop_styles/<id>.png`（生成时当参考图喂，保一期统一）。

## 用法

1. 选画风（一期一种，或频道固定一种）；写进镜头表道具的 `look`。
2. 生图：`python scripts/gen_image.py "<主体描述> <suffix> <tail>" <片>/assets/props/<选题>/<名>.png --ref kit/assets/prop_styles/<id>.png`（suffix/tail 从 prop_styles.json 抄）。
3. 处理：`python scripts/prop_prep.py <生图.png> -o <片>/assets/props/<选题>/ [--luma]`（裁透明边、缩到 ≤800、白线稿用 --luma 把暗底变透明；打印不透明占比，<0.05 太细要换粗画风）。
4. 上屏：`K.prop({img,look,…})` / 场景插槽 / board `type:'prop'` 节点；白线稿可 `tint:'gold'` 染金。
5. 标注：道具是 AI 生成 → 规矩 40 标"AI生成"、进 CREDITS；事实账本记 P 条（prompt/模型/许可）。

## 20 种一览（shadow / 适用底）

| id | 画风 | 阴影 | 深底 | 浅底 | 本项目建议 |
|---|---|---|---|---|---|
| product_photo | 实物棚拍 | soft | ✓ | ✓ | **默认**：最贴华尔街"真东西"气质 |
| cutaway | 工程剖视 | soft | ✓ | ✓ | 讲结构/内部 |
| engraving | 老报纸版画 | paper | ✓ | ✓ | 讲历史 |
| sticker25d | 2.5D 贴纸 | soft | ✓ | ✓ | 年轻向/比喻角色 |
| papercut | 层叠剪纸 | paper | ✓ | ✓ | 农业/手工/地方 |
| clay | 黏土定格 | soft | ✓ | ✓ | 生活消费 |
| toy3d | 软胶玩具 | soft | ✓ | ✓ | 互联网产品 |
| vintage_ad | 复古广告 | soft | ✓ | ✓ | 年代感 |
| risograph | 孔版印刷 | paper | ✓ | ✓ | 纸感 |
| flat_editorial | 扁平杂志 | soft | ✓ | ✓ | 杂志感 |
| comic_pop | 波普 | paper | ✓ | ✓ | 夸张情绪 |
| watercolor | 水彩 | paper | ✓ | ✓ | 柔和 |
| woodcut | 木刻 | paper | ✓ | ✓ | 粗粝历史 |
| ink_wash | 水墨 | paper | ✓ | ✓ | 东方题材 |
| collage | 拼贴 | paper | ✓ | ✓ | 档案感 |
| mono_line | 单线 | none | ✗ | ✓ | 浅底才用 |
| lineart_white | 白线稿 | glow(白) | ✓ | ✗ | 深底+tint 染金 |
| chalk | 粉笔 | none | ✓ | ✗ | 黑板语境（本项目无黑板，慎用） |
| neon | 霓虹 | glow(粉) | ✓ | ✗ | **不推荐**：大团彩色光违反规矩 2 气质 |
| pixel16 | 16 位像素 | hard | ✓ | ✓ | **不推荐**：与织物质感撕扯 |

阴影配方在 `K.propShadow(look, lift)`（深底分支）：soft 浮空软影 / paper 贴纸片影 / hard 像素硬影 / glow 发光 / none 无。

## 边界

道具只演**比喻**（拍不到的具体物件/角色），不冒充真人、当事人、真实证据；证据镜头（article/desk/footage…）永远真素材。一期道具同一画风；相邻场景道具动作不重样（骑/切/开/流/堆 轮换）。
