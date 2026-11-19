// story_from_film.mjs —— 从主片抽一个故事段工程（横屏 16:9，bighead 剪贴风）。
// 人物经历/创业故事/公司历史段走这里；其余段沿用 wallstreet kit。选段规则见 references/story-mode.md。
//
//   node scripts/story_from_film.mjs <片子目录> <故事名> <句id,句id,...>
//       建 <片子>/assets/story/<名>/：index.html + a/（横屏引擎+字体）+ scene.js 起点 + img/ +
//       timeline.json（主片时间线的子集，平移到本地 0 起点；aspect 16:9）
//       （--seq 渲的是 %04d.jpg 帧序列，与 kit 实拍帧惯例一致）
//   node scripts/story_from_film.mjs register <片子目录> <故事名>
//       数 assets/clips/story_<名>/ 的帧数，登记进 counts.json（footage 取帧靠它）
//
// 之后：写 scene.js（横屏坐标 1920×1080，安全区见 references/story-mode.md）→ 备 img/ 剪纸+锚点
// （python scripts/story_anchor.py img/x.png）→ 渲帧序列：
//   node vendor/bighead-collage/scripts/frames.mjs --dir <片子>/assets/story/<名> --seq <片子>/assets/clips/story_<名> --h 1080
// → register → 主片 film.js 加 {scene:'footage', clip:'story_<名>', from:0, until:<故事段下一句>, enter:...}。
// 字幕与旁白继续走主片管线（故事段不烧字幕、不带音轨），避免双字幕双音轨。
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const SK = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const VEN = path.join(SK, 'vendor', 'bighead-collage', 'scripts');
const a = process.argv.slice(2);

if (a[0] === 'register') {
  const [, film, name] = a;
  const seq = path.join(film, 'assets', 'clips', `story_${name}`);
  const n = fs.readdirSync(seq).filter(f => /^\d+\.jpg$/.test(f)).length;
  if (!n) { console.error('没有帧：', seq); process.exit(1); }
  const cp = path.join(film, 'assets', 'clips', 'counts.json');
  const counts = fs.existsSync(cp) ? JSON.parse(fs.readFileSync(cp, 'utf8')) : {};
  counts[`story_${name}`] = n;
  fs.writeFileSync(cp, JSON.stringify(counts, null, 1));
  console.log(`counts.story_${name} = ${n}`);
  process.exit(0);
}

const [film, name, idsArg] = a;
if (!film || !name || !idsArg) { console.error('用法见文件头'); process.exit(1); }
const ids = idsArg.split(',');
const T = JSON.parse(fs.readFileSync(path.join(film, 'timeline.json'), 'utf8'));
const beats = ids.map(id => {
  const b = T.beats.find(x => x.id === id);
  if (!b) { console.error('主片时间线没有这句：', id); process.exit(1); }
  return b;
});
const t0 = beats[0].start;
const local = {
  aspect: '16:9', fps: T.fps ?? 30, pre: 0,
  duration: +(beats[beats.length - 1].end - t0 + .3).toFixed(3),
  beats: beats.map(b => ({...b, start: +(b.start - t0).toFixed(3), end: +(b.end - t0).toFixed(3),
    chars: b.chars.map(([c, t]) => [c, +(t - t0).toFixed(3)])})),
};
const D = path.join(film, 'assets', 'story', name);
if (fs.existsSync(D)) { console.error('已存在，不覆盖：', D); process.exit(1); }
fs.mkdirSync(path.join(D, 'a'), {recursive: true});
fs.mkdirSync(path.join(D, 'img'), {recursive: true});
for (const f of ['stage.js', 'acts.js', 'look.css', 'landscape.js']) fs.copyFileSync(path.join(VEN, f), path.join(D, 'a', f));
for (const f of fs.readdirSync(path.join(VEN, 'fonts'))) fs.copyFileSync(path.join(VEN, 'fonts', f), path.join(D, 'a', f));
fs.writeFileSync(path.join(D, 'timeline.json'), JSON.stringify(local, null, 1));
fs.writeFileSync(path.join(D, 'index.html'), `<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="a/look.css"></head>
<body><script src="a/stage.js"></script><script src="a/acts.js"></script><script src="a/landscape.js"></script><script src="scene.js"></script></body></html>
`);
fs.writeFileSync(path.join(D, 'scene.js'), `// 横屏故事段（1920×1080）。时间一律从 timeline.json 取（at/beat），不手填秒数。
// 安全区：主体放 x 100–1820 / y 80–870；字幕由主片统一出，这里默认不烧字幕。
// 布局helper：STORY_LANDSCAPE.picture / caption / titleRow；动作语法 ACTS（drop/rise/slap/actor…）。
const {scene, word, row, sfx, TX, LOOK, at, beat, W, H, kf, spline, clamp} = STAGE;
const {person, actor, drop, rise, slap, dust, shakeOf, ring_, out, plus} = ACTS;
const {picture, caption, titleRow, SAFE} = STORY_LANDSCAPE;

// TODO: 按导演表写场景。例：
// const s1 = scene({t0: 0, t1: beat('s01').end, bg: '#20242c', cam: {z: [[0, 1.06], [beat('s01').end, 1, 'io']]}});
// picture(s1, {src: 'img/munger.png', x: 1400, y: 620, w: 520, t: at('s01', '芒格')});
// titleRow(s1, [['1924', at('s01', '1924')]], 480, 300);
`);
console.log('建好', D);
console.log('本地时间线', local.duration, '秒 /', beats.length, '句（主片', t0, 's 起）');
console.log('下一步：写 scene.js → 备 img/ 剪纸与锚点 → frames.mjs --seq 渲帧 → register → 主片加 footage 镜');
