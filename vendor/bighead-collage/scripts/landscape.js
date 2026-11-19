// landscape.js —— 横屏 16:9 布局 helper（wallstreet-explainer 改造新增；演进自 OpenMontage fork 的 story-landscape.js）。
// 舞台 1920×1080。安全区与 wallstreet kit 一致：主体 x 100–1820 / y 80–870（字幕带 y≥900 不放内容）。
// 插入主片时故事段不烧字幕（主片字幕统一覆盖）；caption 仅供单独横屏短片使用。
(function () {
  const {stage, overlays, LOOK, W, H, row} = STAGE;
  const SAFE = {x0: 100, x1: 1820, y0: 80, y1: 870};
  // 人物/道具剪纸：从 (fromX,fromY) 快进慢停滑到 (x,y)；w 是图宽（px），cutout 投影默认开
  function picture(sc, {src, x, y, w, t = 0, fromX = x, fromY = y, duration = .6, depth = 1, cutout = true, show} = {}) {
    if (!src || !Number.isFinite(x) || !Number.isFinite(y) || !Number.isFinite(w)) throw Error('picture requires src, x, y and w');
    return sc.add({img: src, w, x: [[t, fromX], [t + duration, x, 'out5']], y: [[t, fromY], [t + duration, y, 'out5']], depth, filter: cutout ? LOOK.CUT : undefined, show});
  }
  // 不随镜头缩放的固定字幕（单独短片用）；bottom 是距底边 px
  function caption(sc, text, {bottom = 60, size = 44} = {}) {
    const el = document.createElement('div'); el.textContent = String(text);
    Object.assign(el.style, {position: 'absolute', left: '0', right: '0', bottom: bottom + 'px', textAlign: 'center', fontFamily: 'CNHeavy', fontWeight: '800', fontSize: size + 'px', color: '#fff', textShadow: '3px 3px 0 #171717,-3px -3px 0 #171717', zIndex: '10000'});
    stage.appendChild(el); overlays.push(t => el.style.display = t >= sc.t0 && t < sc.t1 ? 'block' : 'none'); return el;
  }
  // 年份/人名一行（橙黄渐变窄粗字）：items=[[文字, 时刻, {opts}],…]；x 为整行中点（align center）
  function titleRow(sc, items, x, y, o = {}) {
    return row(sc, items.map(([txt, t, oo]) => [txt, t, Object.assign({cls: 'cn orange', size: undefined}, oo)]), x, y,
      Object.assign({align: 'center', gap: o.gap ?? 40}, o, {spec: Object.assign({css: {fontSize: (o.size ?? 120) + 'px'}, filter: LOOK.EXO}, o.spec || {})}));
  }
  window.STORY_LANDSCAPE = {picture, caption, titleRow, SAFE};
})();
