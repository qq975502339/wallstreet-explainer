# 素材与证据

## 优先级

1. **当事公司的官方片**（YouTube 官方频道，1080p、干净、没有新闻条）：产线、机柜、数据中心、发布会集锦。
2. **大媒体的纪录片**（Bloomberg Originals 这类）：采访近景很漂亮，自带名牌，航拍可以当气氛镜。
3. **新闻台**（CNBC、Bloomberg TV 等）：底部有新闻条，只在两种情况下用：截当事人的原声，或者新闻条本身就是证据（比如“NVIDIA TO INVEST UP TO $100 BILLION IN OPENAI”）。
4. **新闻和报告原文截图**：用来证明可能被质疑的数。
5. **Pexels / Pixabay 免费图库**（`scripts/stock.py`）：只做空镜、气氛镜、通用画面（城市航拍、人群、机房、钞票、时钟这类），**不能当当事人/当事公司的证据**——图库里的“数据中心”不是英伟达的数据中心。两家都免费商用、无需署名，但出处照样写进简介。用法和限制见下面“图库空镜”一节。
6. **Wikimedia Commons**：只用来取 CC 许可的人物照片（做圆盘里的抠像）和 logo，要注明作者和许可。它上面的视频画质普遍太低。用脚本拿，不手工翻：
   - `python scripts/commons_photo.py search "Jensen Huang" --n 6`：列候选（许可/尺寸/作者/页面），只列 PD/CC0/CC BY/CC BY-SA（NC/ND 会裁切调色加字，不能用）；英文关键词结果更多。
   - `python scripts/commons_photo.py get "File:<标题>.jpg" <片子>/assets/img/jensen.jpg --width 2000`：下载+验许可（不自由直接拒），写 `<图>.json` 侧车（作者/许可/页面/现成中文署名行）。
   - `python scripts/commons_logo.py <片子>/assets/logos "NVIDIA=File:NVIDIA logo.svg" "Oracle=Oracle logo"`：Logo SVG 由 Commons 服务端渲染成 PNG，429 自动退避，追加 `CREDITS.txt`；MISSING 就换精确 File: 标题或官网 press kit。
   - 署名和许可抄进该片 CREDITS.md / 视频简介（规矩 16：不上屏）；CC 只管版权，不管商标和肖像权，Logo 只指称性使用、不改色不变形。
7. **生成图**（`scripts/gen_image.py`）：中性纹理；或者演一个拍不到的具体比喻物件（一枚币、一座楼、一条蛇吞大象），抠出来放进前后层，写实的标“AI生成”。不做电影感氛围大片。
   - `python scripts/gen_image.py "一枚金色硬币立在深蓝色细斜纹织物上，影棚柔光，写实产品摄影，暗背景" <片子>/assets/img/coin.png`：qwen-image 生成，默认 1664*928（16:9），`--size 宽*高` 改尺寸、`--ref <图>` 给参考图（可多个）。key 是 `local.json` 的 `qianwen_api_key`，按张计费，想好 prompt 再跑。
   - 侧车记 prompt/模型/AI生成标记；出处进 CREDITS.md。prompt 往 skill 的画风上靠：金色物件 + 深蓝织物 + 影棚光，和真素材同光同调色。

这些视频大多有版权，只做评论、解读性质的引用。**每条片都要把全部素材的出处写进简介**（格式参考 `examples/ai-burn-money/CREDITS.md`），并提醒用户存在被投诉的风险。

## 找片到抽帧（`scripts/footage.py`）

1. `search "关键词"`：带上公司名和 b-roll、keynote、official、data center 这类词，看频道名，挑官方的。
2. `get <id>`：下载 1080p。长视频（发布会全程、播客）只下需要的那一段：`--section 01:11:40-01:12:12`。被 403 拦住时，先 `pip install -U yt-dlp`。
3. `sheet <视频>`：拼一张带时间码的联系表，用眼睛挑镜头。挑的标准是这一镜能不能让人认出它说的是谁、是什么。
4. `scenes <视频> --from a --to b`：查镜头切点。入点和出点都要落在同一个镜头里，避开片头片尾、幻灯片和主持人（发布会集锦里人物前面常常是一张幻灯片）。
5. `extract clips.json`：抽成 30fps 帧序列。要裁掉台标、角标、原片烧进去的说明字时用 zoom/ax/ay 参数。抽完逐帧查一遍切点（相邻两帧差很多的地方）：第一帧和最后一帧不能是别的镜头，中间藏着的切点也要剪掉，或者留着当作底下实拍的一刀。
6. 把帧数登记进渲染代码（`counts.json` 里有）。漏登记的话会取到不存在的帧，出现黑屏或空框。

## 图库空镜（`scripts/stock.py`，Pexels / Pixabay）

官方片和新闻里没有、也不该冒充证据的通用画面（城市夜景航拍、人流、服务器机房、钞票、日历时钟），从免费图库下。

- **key**：[pexels.com/api](https://www.pexels.com/api/) 和 [pixabay.com/api/docs](https://pixabay.com/api/docs/) 免费申请，写进 `scripts/local.json` 的 `pexels_api_key` / `pixabay_api_key`（或环境变量 `PEXELS_API_KEY` / `PIXABAY_API_KEY`）。没 key 时脚本会直接提示去哪申请。
- `python scripts/stock.py search pexels "city night aerial" -n 8 --min-dur 5 --max-dur 20`：列候选（id / 时长 / 尺寸 / 作者 / 页面）。`--orientation landscape|portrait|square`；pixabay 另有 `--category business`、`--type film|animation`（图片 `--type photo|illustration|vector`、`--color blue`）。英文关键词结果多。
- `python scripts/stock.py get pexels <id或页面url> <片子>/assets/clips_src/city.mp4`：下载，写 `<文件>.json` 侧车（作者/许可/页面/中文署名行）。视频默认挑 ≤1080p 的 hd（片子就是 1080p 出的），要 4K 加 `--4k`；pixabay 视频用 `--quality large|medium|small|tiny`。
- 照片加 `--photo`：`get pexels <id> <片子>/assets/img/money.jpg --photo --size original`（默认 large2x）；pixabay 标准 API 图片最大 1280px，够圆盘和画框用，不够就换 pexels。
- 下完的视频接 `footage.py` 的老流程：`sheet` 挑镜头 → `scenes` 查切点 → `extract` 抽帧。图库片一般一整个镜头没有切点，但还是要查一遍。
- 署名行抄进该片 CREDITS.md / 简介（规矩 16：不上屏）。两家许可都禁止原样转售、禁止暗示画面里的人/品牌代言；可识别的人物画面别用在敏感语境。
- 候选看一遍再挑，别闭眼拿第一条：第一条大家都用，容易和别的片子撞画面。

已知限制：Pexels 约 200 次请求/小时、Pixabay 约 100 次/分钟（429 脚本自动退避重试）；Pixabay 下载链接带会过期的 token，搜到就立刻下，别存链接以后用；Pixabay 视频通常 1080p（个别有 4K 的 large），保证要 4K 就用 Pexels `--4k`。

## 当事人的抠像（`scripts/matte.py` → `matte_clean.py`）

人和图形一起动的那些手法（人站在巨字前面、身后换背景、横推换人、卡片在旁边冒出来），都要当事人的实拍抠像。

- **挑一段没有切点的实拍**，比这一镜要用的时长长一点。发布会的台上、采访的近景都好用；纯色或暗的背景抠得最干净。挑有动作的那一段对上台词（说“全世界最值钱”时他正好张开双手）。原片不够长可以放慢到 0.8 倍，再慢就看得出来了。
- 抽帧以后先看切点：`matte.py` 会打印“可疑切点”。采访片常常前几帧还是采访者，用 `--from` 跳过，不然横推换人的那一下会露出别人。
- 模型：`isnet-general-use` 在 GPU 上约 0.25 秒/帧，边缘够用；`birefnet-portrait` 头发更干净，但在 8GB 显存的卡上要 10 秒以上一帧。用 GPU 版 onnxruntime 时先 `preload_dlls()`，不然会悄悄跑在 CPU 上。
- `matte_clean.py`：去掉台上的线、小块；贴着人的椅背去不掉时用 `--cut-left` 整列抹掉；写出每帧头肩的中心（`box.json:cx`），放人时按它对齐，人在原片里走动，画面里就钉住了。
- 名牌、台标不用管，抠的时候自然就去掉了。抠像也是引用的画面，出处照样写进清单。

## 新闻原文（`scripts/snap_news.mjs`）

- 用英文搜真实报道。优先找能直接打开的页面：通讯社的转载页、科技媒体、财经门户。有的站会拦截自动访问，或者弹验证码。
- 截图流程：
  - 拦掉广告和同意弹窗的域名（不要拦掉所有第三方，会把网页字体也拦掉）；
  - 去掉所有 fixed/sticky 浮层；
  - 把标题滚到离顶部约 140px；
  - 等字体加载完；
  - 先量关键词的框，再截图。
- 折行的关键词会给出两个框，荧光笔要按行一段一段刷。
- 被拦住时不要硬截。用核实过的文字自己排一个通用样式的效果图，不仿任何真实网站。

## 当事人原声

- **找原话**：`yt-dlp --skip-download --write-auto-subs --sub-langs en` 拿自动字幕，在字幕里搜关键词定位大概时间；只下那一段，再用 faster-whisper 识别出每个词的时间。
- **剪口以波形为准**（`footage.py wave 文件 起 止`），Whisper 给的时间会偏零点几秒：
  - 开口前留 0.05 秒；
  - 句尾要等最后一个字的能量完全落下去，砍掉半个词听起来就是一声“异响”；
  - 中间如果有数字静音（低于 -75dB），说明原片在这里剪过，不要截进来，否则会突然“断电”再猛地进人声。
- 分段下载的音轨偶尔会解码出错（ffmpeg 报 `aac decode_band_types`）。用 `get --audio` 单独再下一次音频，按画面对齐（两条音轨做互相关，算出偏移）。
- 一段原声里跳着剪几句可以接受，接缝要落在停顿处。
- 原声画面用全屏；当成反应梗时，放在压暗背景上的小窗里。

## 下载踩坑（做《谷歌给苹果的两百亿》时碰到的）

- YouTube 只要一小段：`--download-sections` 和 HLS（m3u8）格式直连都会断。先 `yt-dlp -F` 找 https dash 格式（1080p 一般是 137），`yt-dlp -f 137 -g URL 2>/dev/null` 拿直链，再 `ffmpeg -ss 起点 -i 直链 -t 秒数 -c copy out.mp4`。不用 cookies。
- 镜像下大模型会断：`curl -C -` 续传可能把文件拼坏（比该有的还大、加载报 protobuf 错）。先 `curl -sIL` 看 `X-Linked-Size`，循环续传到大小对上，再对 sha256。
