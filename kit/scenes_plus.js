// scenes_plus.js —— 真人口播版新加的场景（载入顺序：scenes.js → scenes_plus.js → host.js）
(()=>{
const K=KIT,{C,IO,E,lerp,f1,f3,col,mixc,alpha,fit,camSeq,bignum,brow,appear,FAM}=K;
const {L}=S25;
const A=v=>v==null?[]:Array.isArray(v)?v:[v];
const arr=A;

// =====================================================================================
// line：一条真实的价格走势（日线），深色舞台上一条亮线 + 下面一片渐变（小Lin说日元那条图的做法）
// 线跟着话画出来；mark 钉在某一天；level 从最后一个点往回拉一条虚线，碰到"上一次这么低"的那天（= 一年多来最低）；
// focus 镜头推到一段（10 月），这一段变红，旁边立一个大数
// =====================================================================================
K.scene('line',{
 says:'一样东西的价格这一年怎么走的：涨到哪、跌回哪、最近这一段跌了多少',
 use:'有真实的日线数据（金价、油价、汇率、股价）；话里说的是"走势"本身（反而跌、跌回一年前、一个月跌了 7%）',
 avoid:'只有几个年份的数（用 chart / bars）；没有出处的数据',
 need:['data'],
 help:{data:"{points:[['2025-09-02',3592.2],…]} 或者 assets/data/xx.json 的内容（film.js 里先 fetch）",title:"左上角眉题：'黄金价格 · 美元/盎司'",en:"眉题下的英文小字：'GOLD · USD / OZ'",
  color:"线的颜色（默认 gold）",from:"从哪天开始画（'2025-09-01'）",draw:"{at, until}：线从左画到右的时间（默认这一镜开头 1.6 秒）",
  marks:"[{at, date:'2026-01-29'|'max'|'last', text:'历史最高', value:'$5,318'}]：钉在某一天的小牌",
  level:"{at, text:'一年多来最低'}：从最后一个点往回拉一条虚线，停在上一次这么低的那天",
  focus:"{at, from:'2026-10-01', value:'-6.9%', brow:'10月 · 金价'}：镜头推到这一段，线变红，旁边立大数",intro:"开场先贴近线的起点、边画边拉远看整年（默认）；'none' 不要",unit:"y 轴单位前缀（默认 '$'）",source:'数据出处（只写进 brief，不上屏）'},
 minDur:2,
 beats:p=>A(p.marks).length+(p.level?1:0)+(p.focus?1:0),
 make(p,c){
  const pts=(p.data.points??p.data).filter(q=>!p.from||q[0]>=p.from),N=pts.length,vs=pts.map(q=>q[1]);
  const lo=Math.min(...vs),hi=Math.max(...vs),pad=(hi-lo)*.12,y0=lo-pad,y1=hi+pad*.6;
  const X0=250,X1=1690,Y0=210,Y1=800,X=i=>X0+(X1-X0)*i/(N-1),Y=v=>Y1-(Y1-Y0)*(v-y0)/(y1-y0);
  const color=col(p.color??'gold'),lc=p.color?color:'#f3d27a';
  const T=c.at,dA=T(p.draw?.at)??c.t0+.05,dB=T(p.draw?.until)??dA+1.6;
  const idx=d=>d==='max'?vs.indexOf(hi):d==='last'||d==null?N-1:Math.max(0,pts.findIndex(q=>q[0]>=d));
  const marks=A(p.marks).map(m=>({...m,i:idx(m.date),t:T(m.at)??dB}));
  const lv=p.level?{...p.level,t:T(p.level.at)??dB+.2}:null;
  if(lv){const v=vs[N-1];let j=N-2;while(j>0&&vs[j]>v)j--;lv.j=j;}
  const fo=p.focus?{...p.focus,t:T(p.focus.at),i0:idx(p.focus.from),i1:idx(p.focus.to)}:null;
  // 机位：先看整年 → focus 推到那一段（框住那一段 + 右边的大数）
  // 开场：先贴近线的起点，线往右画的时候拉远看整年（拉远 = "整体是这样"）；p.intro:'none' 不要这一下
  const keys=p.intro==='none'?[{t:c.t0,cam:{x:960,y:520,s:1}}]:[{t:c.t0,cam:{x:X0+420,y:Y(vs[0])-40,s:1.32}},{t:dA+.35,cam:{x:960,y:520,s:1},d:Math.max(.9,(dB-dA)*.75)}];
  if(fo){const xs=[X(fo.i0),X(fo.i1)],ys=vs.slice(fo.i0,fo.i1+1).map(Y);keys.push({t:fo.t,cam:fit([xs[0]-700,Math.min(...ys)-90,xs[1]+150,Y(vs[N-1])+330],{pad:30,max:2.1}),d:1});}
  const cam=camSeq(keys,.018);
  const grid=(()=>{let h='';const step=Math.pow(10,Math.floor(Math.log10((y1-y0)/4))),st=[1,2,5].map(k=>k*step).find(s=>(y1-y0)/s<=6)??step*10;
   for(let v=Math.ceil(y0/st)*st;v<y1;v+=st)h+=`<line x1="${X0}" x2="${X1+30}" y1="${f1(Y(v))}" y2="${f1(Y(v))}" stroke="#ffffff14" stroke-dasharray="4 8"/><text x="${X1+46}" y="${f1(Y(v)+8)}" fill="#ffffff55" font-family="Num,'Bebas Neue'" font-size="34">${p.unit??'$'}${v.toLocaleString('en-US')}</text>`;
   let lastM='';pts.forEach((q,i)=>{const m=q[0].slice(0,7);if(m!==lastM){lastM=m;const mm=+m.slice(5);if(mm%3===1||i===0)h+=`<text x="${f1(X(i))}" y="${Y1+46}" fill="#ffffff66" font-family="Mi,MiSans" font-size="30" text-anchor="middle">${mm===1?m.slice(0,4)+'.':''}${mm}月</text><line x1="${f1(X(i))}" x2="${f1(X(i))}" y1="${Y1}" y2="${Y1+12}" stroke="#ffffff33"/>`;}});
   return h;})();
  const pathTo=(i0,i1,k)=>{let d='';const n=Math.floor(k);for(let i=i0;i<=Math.min(i1,n);i++)d+=(i===i0?'M':'L')+f1(X(i))+' '+f1(Y(vs[i]))+' ';
   if(k<i1&&n>=i0&&n+1<=i1){const fr=k-n;d+='L'+f1(lerp(X(n),X(n+1),fr))+' '+f1(lerp(Y(vs[n]),Y(vs[n+1]),fr));}return d;};
  return t=>{
   const cc=cam(t),cp=cam(t-1/30),k=(N-1)*E(C((t-dA)/(dB-dA)));
   const head=[lerp(X(Math.floor(k)),X(Math.min(N-1,Math.floor(k)+1)),k%1),lerp(Y(vs[Math.floor(k)]),Y(vs[Math.min(N-1,Math.floor(k)+1)]),k%1)];
   const fk=fo?E(C((t-fo.t-.25)/.5)):0;
   const line=pathTo(0,N-1,k),area=k>0?line+` L${f1(head[0])} ${Y1} L${X0} ${Y1} Z`:'';
   let svg=`<svg class="k-full" width="1920" height="1080" style="overflow:visible"><defs><linearGradient id="lg_a" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${lc}" stop-opacity=".5"/><stop offset="1" stop-color="${lc}" stop-opacity="0"/></linearGradient></defs>${grid}`;
   svg+=`<path d="${area}" fill="url(#lg_a)"/><path d="${line}" fill="none" stroke="${lc}" stroke-width="6" stroke-linejoin="round" style="filter:drop-shadow(0 0 8px ${alpha(lc,.6)})"/>`;
   if(fo&&fk>0)svg+=`<path d="${pathTo(fo.i0,fo.i1,fo.i1)}" fill="none" stroke="#ff5a5f" stroke-width="6.5" stroke-linejoin="round" style="opacity:${f3(fk)};filter:drop-shadow(0 0 10px #ff5a5f99)"/>`;
   if(k<N-1.01)svg+=`<circle cx="${f1(head[0])}" cy="${f1(head[1])}" r="8" fill="#fff" style="filter:drop-shadow(0 0 10px ${lc})"/>`;
   else{const pu=.5+.5*Math.sin((t-dB)*6);svg+=`<circle cx="${f1(X(N-1))}" cy="${f1(Y(vs[N-1]))}" r="${f1(9+pu*4)}" fill="${fo&&fk>0?'#ff5a5f':lc}" stroke="#fff" stroke-width="3"/>`;}
   if(lv&&t>=lv.t){const e=E(C((t-lv.t)/.6)),xa=X(N-1),xb=lerp(xa,X(lv.j),e),yy=Y(vs[N-1]);
    svg+=`<line x1="${f1(xa)}" x2="${f1(xb)}" y1="${f1(yy)}" y2="${f1(yy)}" stroke="#fff" stroke-width="2.5" stroke-dasharray="10 9" opacity=".8"/>`;
    if(e>.95)svg+=`<circle cx="${f1(X(lv.j))}" cy="${f1(yy)}" r="7" fill="#fff" opacity="${f3(C((t-lv.t-.6)/.2))}"/>`;}
   svg+='</svg>';
   let tags='';
   for(const m of marks){if(t<m.t)continue;const q=appear(t,m.t),x=X(m.i),y=Y(vs[m.i]),up=m.below?1:-1;
    tags+=`<div class="k-tag" style="left:${f1(x+34)}px;top:${f1(y-34)}px;font-size:58px;${K.fx({o:q.o*(1-fk),dy:q.dy},'translate(0,0)')}">${m.text?`<small>${m.text}</small>`:''}${m.value?K.unitHTML(K.num(m.value)):''}</div><div style="position:absolute;left:${f1(x-9)}px;top:${f1(y-9)}px;width:18px;height:18px;border-radius:50%;background:#fff;box-shadow:0 0 12px ${lc};opacity:${f3(q.o*(1-fk))}"></div>`;}
   if(lv&&t>=lv.t+.5&&lv.text){const q=appear(t,lv.t+.5);tags+=`<div class="k-label" style="left:${f1((X(N-1)+X(lv.j))/2)}px;top:${f1(Y(vs[N-1])+64)}px;font-size:54px;${K.fx({o:q.o*(1-fk),dy:q.dy})}">${lv.text}</div>`;}
   if(fo&&fk>0){const bx=X(fo.i0)-40,by=Y(vs[N-1])+200;
    tags+=bignum({x:bx,y:by,value:fo.value,size:190,anchor:'r',color:'red'},{o:fk,dy:(1-fk)*16});
    if(fo.brow)tags+=brow({x:bx,y:by-170,zh:fo.brow,en:fo.en,anchor:'r',size:40},{o:fk});}
   const ttl=p.title?brow({x:X0,y:120,zh:p.title,en:p.en,anchor:'l'},{o:C((t-c.t0)/.3)*(1-fk*.7)}):'';
   return c.bg(t,cc,cp)+L(cc,cp,1,svg+tags+ttl,{mbMax:8,zbMax:1.5});
  };
 }
});

// =====================================================================================
// chain：一条因果链，几张卡一字排开，念到哪张亮哪张（前面的退一步），箭头跟着画出来
// 镜头基本不动（只慢推），适合放进 host:'window' 的板子里：一句话里连着说三四环，镜头追着跑会糊
// =====================================================================================
K.scene('chain',{
 says:'一件事怎么一环扣一环推到下一件：打仗 → 油价 → 通胀 → 利率',
 use:'一句话里连着说三四个"所以"；每一环有一个画面或一个数',
 avoid:'环和环之间不是因果（并列用 stats / discs）；超过 4 环',
 need:['items'],
 help:{items:"[{at, title:'油价', img|value:'$104', sub:'10月30日', color}]：一环一张卡，at 念到它的时候亮起",arrow:'箭头上的字（可选，每段一样）',x0:'卡片从哪儿排起（默认 60；同一镜加了左下圆窗时写 400，给左下圆窗让位）',x1:'排到哪儿（默认 1860）',gap:'卡片间距（默认 4 张 80）'},
 minDur:1.2,
 beats:p=>A(p.items).length,
 make(p,c){
  const its=A(p.items).map((q,i)=>({...q,t:c.at(q.at)??c.t0+.2+i*.5})),n=its.length,H=n>=4?560:520,G=p.gap??(n>=4?80:110);
  // 卡片排在 [x0, x1] 里（默认整屏 60–1860）；有左下圆窗时写 x0:400 给它让位，卡片按区间宽度变窄
  const L0=p.x0??60,L1=p.x1??1860,W=Math.min(n>=4?390:470,(L1-L0-(n-1)*G)/n);
  const tot=n*W+(n-1)*G,x0=(L0+L1)/2-tot/2+W/2,y=500;
  return t=>{
   const cc={x:960,y:520,s:1+.012*(t-c.t0)},cp={...cc,s:1+.012*(t-1/30-c.t0)};
   let cur=-1;its.forEach((q,i)=>{if(t>=q.t)cur=i;});
   let h='';
   its.forEach((q,i)=>{if(t<q.t)return;const a=appear(t,q.t,.25,18),x=x0+i*(W+G),on=i===cur,dim=on?1:.72;
    const cl=col(q.color??'steel');
    const media=q.img?`<img src="${q.img}" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover">`:'';
    const v=q.value?`<div class="ch-v" style="top:${q.img?'30%':'26%'}">${K.unitHTML(K.num(q.value))}</div>`:'';
    h+=`<div class="ch-card${q.img?' img':''}" style="left:${f1(x-W/2)}px;top:${f1(y-H/2)}px;width:${W}px;height:${f1(H)}px;--c:${cl};${K.fx({o:a.o,dy:a.dy,br:dim,sc:on?1.04:1},'translate(0,0)')}">${media}${v}<div class="ch-t"${q.k==='x'?' style="text-decoration:line-through;opacity:.6"':q.k==='p'?' style="display:inline-block;padding:.05em .5em;border-radius:.6em;background:var(--c);color:#0b0e13"':''}>${q.title}</div>${q.sub?`<div class="ch-s">${q.sub}</div>`:''}</div>`;
    if(i>0){const k=E(C((t-q.t+.15)/.3)),ax=x-W/2-G+14,aw=(G-28)*k;
     h+=`<svg style="position:absolute;left:${f1(ax)}px;top:${f1(y-22)}px;overflow:visible" width="${G}" height="44"><path d="M0 22 H${f1(Math.max(0,aw-14))}" stroke="#f3d27a" stroke-width="6" stroke-linecap="round"/>${k>.9?`<path d="M${f1(aw-22)} 8 L${f1(aw)} 22 L${f1(aw-22)} 36" fill="none" stroke="#f3d27a" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>`:''}</svg>`;}
   });
   return c.bg(t,cc,cp)+L(cc,cp,1,h);
  };
 }
});
// =====================================================================================
// docpage：文件逐字原文页（比屏幕宽的纸）：镜头先看标题，再推到高亮条文，荧光笔逐行刷过
// =====================================================================================
K.scene('docpage',{
 says:'政策/文件的逐字原文排满一张比屏幕宽的纸：镜头先看标题，再推到高亮的那一句，荧光笔逐行刷过',
 use:'PDF/纸质/政策条文的逐字原文（长文、多段落）；新闻网页截图用 article',
 avoid:'改写过的转述（必须逐字）；只有一句话（用 quote 或 article）',
 need:['paras'],
 help:{paras:"[['title','国务院关于……的办法'],['meta','2024 年 9 月 · 第二条'],['gap',''],['p','第二条 ……[[0|由十五年逐步提高至二十年]]……']]：[[n|文字]] 标要高亮的片段，n 对应 marks 的下标；跨行自动按行刷",
  marks:"[{at:'@b10:十五', kind:'hl'|'box'|'under', color}]：每个片段刷过的时刻和画法（默认 hl 黄）",
  zoom:"镜头开始推向高亮的时刻（默认第一个 mark 前 0.45 秒）",size:'正文字号（默认 64）',w:'纸宽（默认 2300，比屏幕宽、两边裁切）'},
 defaults:{tone:'navy'},minDur:2.2,
 beats:p=>arr(p.marks).length,
 check(p,c){const all=arr(p.paras).map(q=>q[1]).join('');arr(p.marks).forEach((m,i)=>{if(!all.includes(`[[${i}|`))throw Error(`${c.tag}：marks[${i}] 没有对应的 [[${i}|…]] 片段`);});},
 make(p,c){
  const PW=p.w??2300,X0=960-PW/2,Y0=60,size=p.size??64,pad=110,iw=PW-2*pad;
  const marks=arr(p.marks).map((m,i)=>({...m,i,t:c.at(m.at)??c.t0+1+i*.6}));
  let y=pad+40;const lines=[];
  const put=(text,fs,fam,lh,weight,color)=>{
   const toks=[];let rest=text;
   while(rest.length){const m=rest.match(/\[\[(\d+)\|([^\]]*)\]\]/);
    if(!m){for(const ch of rest)toks.push({ch});break;}
    for(const ch of rest.slice(0,m.index))toks.push({ch});
    for(const ch of m[2])toks.push({ch,mi:+m[1]});
    rest=rest.slice(m.index+m[0].length);}
   let line=[],lw=0;
   const flush=()=>{if(!line.length)return;let html='',x=pad,run=null;const boxes=[];
    for(const t of line){const w=K.textW(t.ch,`${weight} ${fs}px ${fam}`);
     if(t.mi!=null){if(!run||run.i!==t.mi){run={i:t.mi,x,w};boxes.push(run);}else run.w+=w;
      html+=`<span data-i="${t.mi}">${t.ch}</span>`;}
     else{run=null;html+=t.ch;}
     x+=w;}
    lines.push({y,html,boxes,fs,fam,lh,weight,color});y+=lh;line=[];lw=0;};
   for(const t of toks){const w=K.textW(t.ch,`${weight} ${fs}px ${fam}`);if(lw+w>iw)flush();line.push(t);lw+=w;}
   flush();};
  for(const [kind,text] of arr(p.paras)){
   if(kind==='title'){put(text,Math.round(size*1.15),FAM.han,Math.round(size*1.5),700,'#17191d');y+=30;}
   else if(kind==='meta'){put(text,Math.round(size*.62),FAM.ui,Math.round(size*.9),500,'#8a8e96');y+=26;}
   else if(kind==='gap'){y+=Math.round(size*.8);}
   else{put(text,size,FAM.ui,Math.round(size*1.62),500,'#3b3e45');y+=26;}
  }
  const PH=y+pad;
  const mbox=marks.map(m=>{const bs=[];for(const ln of lines)for(const b of ln.boxes)if(b.i===m.i)bs.push([b.x,ln.y,b.x+b.w,ln.y+ln.lh]);return bs.length?K.unionBox(bs):null;});
  const zb=mbox.find(Boolean);
  const tz=c.at(p.zoom)??(marks[0]?marks[0].t-.45:c.t0+1);
  const sA=Math.min(.92,1780/PW),camA={x:960,y:Y0+430/sA,s:sA};
  const keys=[{t:c.t0,cam:{...camA,s:sA*.96}},{t:c.t0,cam:camA,d:.9}];
  if(zb)keys.push({t:tz,cam:{x:X0+(zb[0]+zb[2])/2,y:Y0+(zb[1]+zb[3])/2,s:Math.max(1.15,Math.min(1.7,1250/(zb[2]-zb[0]+320)))},d:1});
  const cam=camSeq(keys,.02);
  return t=>{
   const cc=cam(t),cp=cam(t-1/30);
   let inner='';
   for(const ln of lines){
    let html=ln.html;
    for(const m of marks){if(m.kind==='box')continue;const mk=C((t-m.t)/.5);if(mk<=0)continue;
     html=html.replace(new RegExp(`<span data-i="${m.i}">([\\s\\S]*?)</span>`,'g'),(s,ch)=>`<span style="position:relative">${ch}<u style="position:absolute;left:0;right:0;bottom:8%;height:${m.kind==='under'?'5px':'76%'};background:${m.color??'#ffd84a'};mix-blend-mode:multiply;transform:scaleX(${f3(mk)});transform-origin:0 50%"></u></span>`);}
    inner+=`<div style="position:absolute;left:0;top:${f1(ln.y)}px;width:${PW}px;font:${ln.weight} ${ln.fs}px/${ln.lh}px ${ln.fam};color:${ln.color};white-space:nowrap">${html}</div>`;}
   for(const [i,m] of marks.entries()){if(m.kind!=='box'||!mbox[i])continue;const b=mbox[i],q=C((t-m.t)/.35);if(q<=0)continue;
    inner+=`<div style="position:absolute;left:${f1(b[0]-10)}px;top:${f1(b[1]-6)}px;width:${f1(b[2]-b[0]+20)}px;height:${f1(b[3]-b[1]+12)}px;border:4px solid ${m.color??'#c63038'};border-radius:6px;opacity:${f3(q)};transform:scale(${f3(lerp(1.06,1,E(q)))})"></div>`;}
   const pg=`<div class="k-page" style="left:${X0}px;top:${Y0}px;width:${PW}px;height:${f1(PH)}px">${inner}</div>`;
   const zk=zb?IO((t-tz)/1):0;
   const vig=`<div class="k-full" style="z-index:40;background:radial-gradient(ellipse 70% 66% at 50% 47%,transparent ${f1(lerp(44,32,zk))}%,rgba(4,7,12,${f3(lerp(.62,.78,zk))}) 100%)"></div>`;
   return c.bg(t,cc,cp,{tone:p.tone})+L(cc,cp,1,pg,{mb:false})+vig;
  };
 }
});

// =====================================================================================
// tree：树状拆解（一个根岔成几支、支再岔成叶；支上带 +/−；念到谁镜头找谁）
// =====================================================================================
K.scene('tree',{
 says:'树状拆解：一个根岔成几支、支再岔成叶，每支带 +/− 号；念到哪个节点镜头推过去、其余压暗',
 use:'利润 = 收入 − 成本、成本再拆三项；把一个总数一层层拆开',
 avoid:'线性算式（用 equation）；有先后的流程（用 flow）',
 need:['root'],
 help:{root:"{id:'p', l:'利润', t:'@b05:利润', c:[{id:'r', l:'收入', op:'+', t:'@b05:收入', c:[{l:'咖啡', t}, {l:'甜点', t}]}, {id:'c', l:'成本', op:'−', t, c:[…]}]}：最多三层",
  focus:"[['@b05:收入','r'], ['@b06:成本','c']]：念到的节点 id 亮起、镜头推过去",
  bw:'节点宽（默认 320）',bh:'节点高（默认 150）'},
 defaults:{tone:'navy'},minDur:2,
 beats:p=>arr(p.focus).length,
 make(p,c){
  const bw=p.bw??320,bh=p.bh??150,lv=300,gx=bw+70;
  const root={...p.root,id:p.root.id??'root',x:960,y:240};
  const kids=root.c??[],nodes=[root],edges=[],pos={[root.id]:[960,240]};
  const span=Math.max(kids.length,kids.reduce((a,k)=>a+Math.max(1,(k.c??[]).length),0))*gx;
  let lx=960-span/2;
  kids.forEach((k,i)=>{
   const lf=k.c??[],w=Math.max(1,lf.length)*gx,cx=lx+w/2;lx+=w;
   const kid={...k,id:k.id??'k'+i,x:cx,y:240+lv};nodes.push(kid);pos[kid.id]=[cx,240+lv];
   edges.push({a:[960,240+bh/2],b:[cx,240+lv-bh/2],op:k.op,t:k.t});
   (lf.length?lf:[null]).forEach((q,j)=>{if(!q)return;const x=cx-w/2+gx/2+j*gx;
    const leaf={...q,id:q.id??`l${i}_${j}`,x,y:240+2*lv};nodes.push(leaf);pos[leaf.id]=[x,240+2*lv];
    edges.push({a:[cx,240+lv+bh/2],b:[x,240+2*lv-bh/2],t:q.t});});
  });
  const foc=arr(p.focus).map(f=>({t:c.at(f[0]),id:f[1]})).sort((a,b)=>a.t-b.t);
  const keys=[{t:c.t0,cam:fit([960-span/2,140,960+span/2,240+2*lv+bh/2],{max:1.05,pad:60})}];
  for(const f of foc)if(pos[f.id])keys.push({t:f.t,cam:fit([pos[f.id][0]-bw/2,pos[f.id][1]-bh/2,pos[f.id][0]+bw/2,pos[f.id][1]+bh/2],{max:1.5,pad:140}),d:.8});
  const cam=camSeq(keys,.02);
  return t=>{
   const cc=cam(t),cp=cam(t-1/30),cur=[...foc].reverse().find(f=>t>=f.t);
   const es=edges.map(e=>{const ta=c.at(e.t)??c.t0+.4,k=E((t-ta)/.5);return {a:e.a,b:e.b,curve:0,color:'gold',style:'solid',w:4,k,arrow:false,text:e.op,ts:44};}).filter(e=>e.k>0);
   let h=K.edges(es);
   for(const n of nodes){const a=appear(t,c.at(n.t)??c.t0+.2,.25,14);if(a.o<=0)continue;
    const on=!cur||cur.id===n.id;
    h+=K.card({x:n.x,y:n.y,w:bw,h:bh,color:n.color??(n.id===root.id?'gold':'steel'),title:n.l,size:52,gray:!on},{...a,br:on?1:.55});}
   return c.bg(t,cc,cp,{tone:p.tone})+L(cc,cp,1,h);
  };
 }
});

// =====================================================================================
// calc：计算器（本项目的白图表卡语言）：字段逐个填入，结果从 0 滚出——"现场算一笔账"
// =====================================================================================
K.scene('calc',{
 says:'白底计算器：左边字段念到一个填一个，右边结果从 0 滚出来——"现场算一笔账"',
 use:'屏幕上算账：单价×天数=一年花费；总额÷人数=人均',
 avoid:'只摆算式不算（用 equation）；只有一个数（用 number）',
 need:['fields','res'],
 help:{fields:"[{l:'每杯价格', v:'30', u:'元', at:'@b09:三十'}]：左列字段，念到才填进框",
  res:"[{l:'一年花费', f:'30×365', v:10950, u:'元', at:'@b09:一万', total:true}]：右边结果，从 0 滚到 v；total:true 用大号金字",
  title:'卡标题',sub:'标题下一行小字'},
 defaults:{tone:'navy'},minDur:2,flat:true,
 beats:p=>arr(p.fields).length+arr(p.res).length,
 make(p,c){
  const F=arr(p.fields).map((q,i)=>({...q,t:c.at(q.at)??c.t0+.3+i*.5})),R=arr(p.res).map((q,i)=>({...q,t:c.at(q.at)??c.t0+1+i*.6}));
  const cw=1340,ch=760,cx=960-cw/2,cy=96,lw=430;
  const cam=camSeq([{t:c.t0,cam:{x:960,y:520,s:.94}},{t:c.t0,cam:{x:960,y:500,s:1},d:.8}],.02);
  return t=>{
   const cc=cam(t),cp=cam(t-1/30),su=c.enter==='flat'?E((t-c.t0-.3)/.55):1;
   let rows='';
   F.forEach((q,i)=>{const a=appear(t,q.t,.25,10),y=220+i*120;
    rows+=`<div style="position:absolute;left:70px;top:${y}px;width:${lw-110}px;font:500 40px ${FAM.ui};color:#4a4d55;opacity:${f3(a.o)};transform:translateY(${f1(a.dy)}px)">${q.l}</div>
     <div style="position:absolute;left:${lw}px;top:${y-16}px;width:230px;height:76px;border:2px solid #c9ccd4;border-radius:10px;background:#fff;opacity:${f3(a.o)};transform:translateY(${f1(a.dy)}px);font:600 44px ${FAM.num};color:#23252b;display:flex;align-items:center;justify-content:flex-end;padding:0 18px;box-sizing:border-box">${q.v}<span style="font:500 26px ${FAM.ui};color:#8a8e96;margin-left:8px">${q.u??''}</span></div>`;});
   let res='';
   R.forEach((q,i)=>{if(t<q.t-.05)return;const k=E((t-q.t)/.9),y=230+i*200,pv=K.num(q.v);
    res+=`<div style="position:absolute;left:${lw+320}px;top:${y-52}px;font:500 36px ${FAM.ui};color:#4a4d55">${q.l}</div>
     <div style="position:absolute;left:${lw+320}px;top:${y-4}px;font:500 30px ${FAM.en};color:#8a8e96">${q.f??''}</div>
     <div class="k-num" style="position:absolute;left:${lw+320}px;top:${y+40}px;font-size:${q.total?150:110}px;filter:none;justify-content:flex-start">${K.numHTML(pv,{n:lerp(0,pv.n,k),fixed:true})}</div>`;});
  const card=`<div class="k-chart" style="left:${cx}px;top:${cy}px;width:${cw}px;height:${ch}px;transform-origin:50% 100%;transform:translateY(${f1((1-su)*420)}px) perspective(2400px) rotateX(${f1((1-su)*26)}deg) rotateY(-2deg);opacity:${f3(C(su*2.2))}">${p.title?`<div class="ct">${p.title}</div>`:''}${p.sub?`<div class="cs">${p.sub}</div>`:''}<div style="position:absolute;left:${lw+270}px;top:150px;bottom:90px;width:2px;background:#e3e5ea"></div>${rows}${res}</div>`;
   return c.bg(t,cc,cp,{tone:p.tone})+L(cc,cp,1,card);
  };
 }
});

// =====================================================================================
// stack：钞票堆（钱一张一张叠起来；顶上一张透视躺平；叠完旁边立大数）
// =====================================================================================
K.scene('stack',{
 says:'钞票堆：钱一张一张叠起来（叠了十二张才够付一年房租），顶上一张透视躺平，叠完旁边立大数',
 use:'把一笔钱叠成看得见的一堆；"赚回来的钱一张一张叠"',
 avoid:'比两堆大小（用 bars）；占比（用 share / grid）',
 need:['n'],
 help:{n:'几张',value:'叠完旁边立的大数（\'$12万\'）',brow:'大数上面的眉题',unit:'堆下面一行小字（\'一张 = 一个月房租\'）',sd:'叠一张几秒（默认 .18）',nw:'钞票宽（默认 460）'},
 defaults:{tone:'navy'},minDur:1.5,
 beats:()=>1,
 make(p,c){
  const n=p.n,nw=p.nw??460,gap=13,sd=p.sd??.18,x=960-(p.value?220:0),base=760;
  const ta=c.t0+.2,done=ta+n*sd;
  const keys=[{t:c.t0,cam:{x,y:560,s:.96}},{t:c.t0,cam:{x,y:540,s:1},d:.8}];
  if(p.value)keys.push({t:done+.2,cam:{x:x+180,y:520,s:1.02},d:.7});
  const cam=camSeq(keys,.02);
  return t=>{
   const cc=cam(t),cp=cam(t-1/30);
   let h=`<div style="position:absolute;left:${f1(x-nw/2-160)}px;top:${base+40}px;width:${nw+320}px;height:260px;background:radial-gradient(ellipse 50% 60% at 50% 0%,rgba(150,176,226,.14),transparent 70%)"></div>`;
   // 钞票样式照源项目 els.tsx Stack / bg.tsx Banknote：玫瑰红渐变票身 + 双边框票面，不改样式
   for(let i=0;i<n;i++){const q=C((t-ta-i*sd)/.22);if(q<=0)continue;
    const j=((i*37)%9)-4,y=base-i*gap+(1-E(q))*70;
    h+=`<div style="position:absolute;left:${f1(x-nw/2+j)}px;top:${f1(y)}px;width:${nw}px;height:${gap+3}px;border-radius:3px;background:${i%2?'linear-gradient(180deg,#e98e9c,#c45f76)':'linear-gradient(180deg,#f09aa7,#cc6880)'};border:1.5px solid #9c3f58;box-shadow:0 3px 4px rgba(0,0,0,.25);opacity:${f3(C(q*3))}"></div>`;}
   const topI=Math.min(n-1,Math.floor((t-ta)/sd));
   if(t>ta&&topI>=0){const y=base-topI*gap,nh=nw*.54;
    h+=`<svg width="${nw}" height="${f1(nh)}" viewBox="0 0 120 65" style="position:absolute;left:${f1(x-nw/2)}px;top:${f1(y-nh+2)}px;transform:perspective(600px) rotateX(58deg);transform-origin:50% 100%;opacity:${f3(C((t-ta-topI*sd)/.22))}"><rect x="1.5" y="1.5" width="117" height="62" rx="4" fill="#e98e9c" stroke="#a9455f" stroke-width="2.5"/><rect x="7" y="7" width="106" height="51" rx="2" fill="none" stroke="#fff4f4" stroke-opacity=".75" stroke-width="1.6"/><circle cx="60" cy="32.5" r="15" fill="#fff2f2" stroke="#a9455f" stroke-width="1.6"/><text x="60" y="40" text-anchor="middle" font-size="21" font-weight="900" fill="#c24a66" font-family="Arial">¥</text><circle cx="24" cy="32.5" r="6" fill="none" stroke="#fff4f4" stroke-width="1.6"/><circle cx="96" cy="32.5" r="6" fill="none" stroke="#fff4f4" stroke-width="1.6"/></svg>`;}
   if(p.unit)h+=K.label({x,y:base+90,text:p.unit,size:36},{o:C((t-done)/.3)});
   if(p.value&&t>=done+.2){const a=appear(t,done+.2,.3,16);
    h+=K.bignum({x:x+nw/2+180,y:470,value:p.value,size:170,anchor:'l'},{o:a.o,dy:a.dy});
    if(p.brow)h+=K.brow({x:x+nw/2+180,y:330,zh:p.brow,anchor:'l'},{o:a.o});}
   return c.bg(t,cc,cp,{tone:p.tone})+L(cc,cp,1,h);
  };
 }
});

// =====================================================================================
// grid：百格图（n 个格，念到的部分逐个变色、其余灰掉；旁边立百分比）
// =====================================================================================
K.scene('grid',{
 says:'百格图：n 个小格排成网格，念到的那部分逐个变色（100 个里 37 个有漏洞）、其余灰掉，旁边立百分比',
 use:'把占比演成"数得出来"：100 个里 37 个、10 个里 6 个；一格是一个可数的东西',
 avoid:'只要百分比数（用 share）；连续的量（用 bars）',
 need:['n','hi'],
 help:{n:'总格数（默认 100）',per:'每行几个（默认 10）',hi:'变色几个',hiAt:'开始变色的时刻（逐个错开）',img:'每格的小图标（透明 PNG，可省；默认圆角方块）',alt:'变色格换的图（可省）',color:'变色颜色（默认 red）',label:'网格下一行小字',value:'旁边立的大数（\'37%\'）',brow:'大数上面的眉题',iw:'格子边长（默认 92）'},
 defaults:{tone:'navy',color:'red'},minDur:1.8,
 beats:()=>1,
 make(p,c){
  const n=p.n??100,per=p.per??10,hi=p.hi,iw=p.iw??92,gx=iw*1.12,gy=iw*1.12;
  const rows=Math.ceil(n/per),W=(per-1)*gx+iw,H=(rows-1)*gy+iw;
  const X0=960-W/2-(p.value?180:0),Y0=540-H/2;
  const hiT=c.at(p.hiAt)??c.t0+1,fill=c.t0+.15;
  const order=[...Array(n).keys()];let s=7;for(let i=n-1;i>0;i--){s=(s*9301+49297)%233280;const j=Math.floor(s/233280*(i+1));[order[i],order[j]]=[order[j],order[i]];}
  const rank=[];order.forEach((idx,r)=>rank[idx]=r);
  const cam=camSeq([{t:c.t0,cam:{x:960,y:540,s:.95}},{t:c.t0,cam:{x:960,y:540,s:1},d:.8}],.02);
  const cl=col(p.color);
  return t=>{
   const cc=cam(t),cp=cam(t-1/30);let h='';
   for(let i=0;i<n;i++){const r=Math.floor(i/per),c2=i%per,x=X0+c2*gx,y=Y0+r*gy;
    const q=C((t-fill-(i/n)*.9)/.3);if(q<=0)continue;
    const isHi=rank[i]<hi,hq=isHi?C((t-hiT-(rank[i]/Math.max(1,hi))*.9)/.25):0;
    const rest=!isHi?C((t-hiT-.2)/.6):0;
    const base=`position:absolute;left:${f1(x)}px;top:${f1(y)}px;width:${iw}px;height:${iw}px;`;
    if(p.img){h+=`<img src="${p.img}" style="${base}object-fit:contain;opacity:${f3(q*(1-hq)*(1-.62*rest))};filter:${rest>0?`grayscale(${f3(rest)})`:''}">`;
     if(hq>0)h+=`<img src="${p.alt??p.img}" style="${base}object-fit:contain;opacity:${f3(hq)};filter:drop-shadow(0 0 9px ${alpha(cl,.8)})">`;}
    else h+=`<div style="${base}border-radius:14px;background:${hq>0?cl:'rgba(255,255,255,.16)'};box-shadow:${hq>0?`0 0 14px ${alpha(cl,.55)}`:'inset 0 0 0 1.5px rgba(255,255,255,.22)'};opacity:${f3(q*(1-.62*rest*(1-hq)))};transform:scale(${f3(lerp(.6,1,E(q))*(hq>0?lerp(1.25,1,E(hq)):1))})"></div>`;}
   if(p.label)h+=K.label({x:X0+W/2,y:Y0+H+70,text:p.label,size:38},{o:C((t-fill-1)/.3)});
   if(p.value&&t>=hiT){const a=appear(t,hiT+.4,.3,16);
    h+=K.bignum({x:X0+W+150,y:500,value:p.value,size:190,anchor:'l',color:p.color},{o:a.o,dy:a.dy});
    if(p.brow)h+=K.brow({x:X0+W+150,y:350,zh:p.brow,anchor:'l'},{o:a.o});}
   return c.bg(t,cc,cp,{tone:p.tone})+L(cc,cp,1,h);
  };
 }
});

// =====================================================================================
// bubble：观众想法气泡（虚构昵称+概括想法；要辟的那条亮起来打叉，其余退后）
// =====================================================================================
K.scene('bubble',{
 says:'观众想法气泡：几个虚构网友的概括想法（"大家都以为……"），要辟的那条亮起来打叉、其余退后',
 use:'先摆误区再辟：下一镜接 article/quote 给真证据；想法要概括、虚构昵称，不搬真实用户原话',
 avoid:'真人原话（用 quote）；只有一条想法（口播直接说）',
 need:['items'],
 help:{items:"[{who:'网友甲', text:'买黄金保值', at:'@b02:大家都'}, …]：2–4 条气泡",pick:"{i:1, at:'@b03:但是'}：要辟的那条亮起来打叉、镜头推过去，其余压暗",color:'气泡颜色（默认 steel）'},
 defaults:{tone:'navy'},minDur:1.5,
 beats:p=>arr(p.items).length+(p.pick?1:0),
 check(p,c){const n=arr(p.items).length;if(n<2||n>4)c.warn(`bubble 放 2–4 条气泡，现在 ${n} 条`);if(p.pick&&!arr(p.items)[p.pick.i])throw Error(`${c.tag}：pick.i 超出 items`);},
 make(p,c){
  const I=arr(p.items).map((q,i)=>({...q,i,t:c.at(q.at)??c.t0+.3+i*.5})),n=I.length;
  const pk=p.pick?{...p.pick,t:c.at(p.pick.at)}:null;
  const W=560,H=250,gx=640;
  const pos=n<=2?[[960-gx/2,430],[960+gx/2,560]]:n===3?[[960-gx,400],[960,560],[960+gx,400]]:[[960-gx*.9,380],[960+gx*.9,380],[960-gx*.9,640],[960+gx*.9,640]];
  const keys=[{t:c.t0,cam:{x:960,y:520,s:.95}},{t:c.t0,cam:{x:960,y:520,s:1},d:.8}];
  if(pk)keys.push({t:pk.t,cam:{x:pos[pk.i][0],y:pos[pk.i][1],s:1.12},d:.8});
  const cam=camSeq(keys,.02);
  return t=>{
   const cc=cam(t),cp=cam(t-1/30);let h='';
   I.forEach((q,i)=>{const a=appear(t,q.t,.3,16);if(a.o<=0)return;
    const [x,y]=pos[i],on=pk&&pk.i===i,dim=pk&&!on?C((t-pk.t)/.5):0;
    const cl=col(q.color??p.color??'steel');
    h+=`<div style="position:absolute;left:${f1(x-W/2)}px;top:${f1(y-H/2)}px;width:${W}px;height:${H}px;${K.fx({o:a.o,dy:a.dy,br:lerp(1,.5,dim),sat:lerp(1,.5,dim)},'translate(0,0)')}">
      <div style="position:absolute;inset:0;border-radius:44px;background:linear-gradient(160deg,${mixc(cl,'#ffffff',.14)},${mixc(cl,'#000000',.34)});box-shadow:0 0 0 2px rgba(255,255,255,.16),0 24px 50px rgba(0,0,0,.55)"></div>
      <div style="position:absolute;left:70px;bottom:-26px;width:52px;height:52px;border-radius:50%;background:${mixc(cl,'#000000',.3)}"></div>
      <div style="position:absolute;left:44px;bottom:-52px;width:26px;height:26px;border-radius:50%;background:${mixc(cl,'#000000',.36)}"></div>
      <div style="position:absolute;left:44px;top:30px;font:500 28px ${FAM.ui};color:rgba(255,255,255,.66);letter-spacing:.1em">${q.who}</div>
      <div style="position:absolute;left:44px;right:44px;top:82px;font:600 44px ${FAM.han};color:#f4efdc;letter-spacing:.06em;line-height:1.3">${q.text}</div></div>`;
    if(on){const q2=C((t-pk.t)/.3);h+=K.mark({x:x+W/2-40,y:y-H/2+40,kind:'no',s:56},{o:q2,sc:lerp(.85,1,E(q2))});}
   });
   return c.bg(t,cc,cp,{tone:p.tone})+L(cc,cp,1,h);
  };
 }
});

const css=`.ch-card{position:absolute;border-radius:16px;overflow:hidden;background:linear-gradient(160deg,color-mix(in srgb,var(--c) 70%,#fff 8%),color-mix(in srgb,var(--c) 55%,#000 45%));box-shadow:0 0 0 2px rgba(255,255,255,.18),0 30px 70px rgba(0,0,0,.7)}
.ch-card.img::after{content:'';position:absolute;inset:0;background:linear-gradient(180deg,transparent 45%,rgba(0,0,0,.78))}
.ch-card .ch-t{position:absolute;left:0;right:0;bottom:22px;z-index:2;text-align:center;font:64px Shu,'Alimama ShuHeiTi',sans-serif;letter-spacing:8px;color:#fff;text-shadow:0 3px 12px #000a}
.ch-card .ch-v{position:absolute;left:0;right:0;top:20%;text-align:center;font:150px Num,'Bebas Neue',sans-serif;line-height:1;background:linear-gradient(180deg,#fffef2,#fff3b5 60%,#efdc7a);-webkit-background-clip:text;background-clip:text;color:transparent;filter:drop-shadow(0 4px 10px #0008)}
.ch-card .ch-v .c{font-size:.45em;vertical-align:.9em}.ch-card .ch-v .u{font:.32em Shu,sans-serif}
.ch-card .ch-s{position:absolute;left:0;right:0;top:12px;text-align:center;font:24px Mi,sans-serif;letter-spacing:3px;color:#ffffffa0}`;
const st=document.createElement('style');st.textContent=css;document.head.appendChild(st);
})();
