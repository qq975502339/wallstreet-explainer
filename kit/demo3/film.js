// demo3：接入版式对照（源项目能力换成本项目视觉语言）。演示数据 + 占位图，看版式不看内容。
window.ready=(async()=>{
const F=await FB.init({counts:['assets/clips/counts.json'],cuts:[],fonts:KIT.FONTS});
const K=await KIT.use(F);
const PH='assets/kit/ph/';

await K.film([
 {scene:'chart', until:'@d02', says:'两条线的口子越拉越大（多序列）',
  series:[{v:[100,120,150,190,240,300],label:'收入',color:'green'},{v:[60,85,120,170,240,330],label:'成本',color:'red'}],
  x:['2020','2021','2022','2023','2024','2025'], title:'收入与成本（演示）', unit:'亿',
  draw:{at:'@d01:收入', until:'@d01:口子'}, mark:[{at:'@d01:口子', i:5, text:'成本反超'}]},

 {scene:'share', until:'@d03', says:'实心饼 + 右边图例：一杯钱去哪了',
  pie:true, legend:true, title:'一杯咖啡的成本（演示）',
  parts:[{label:'房租',value:30},{label:'人工',value:30},{label:'豆子',value:10,color:'green'},{label:'其他和利润',value:30}],
  focus:[{at:'@d02:豆子', i:2}]},

 {scene:'timeline', until:'@d04', says:'卡片上下交替的时间轴',
  alt:true, gap:520,
  nodes:[{year:'1652',title:'第一家咖啡馆',at:'@d03:一六五二'},{year:'1908',title:'发明滤纸',at:'@d03:一九零八'},
         {year:'1971',title:'星巴克成立',at:'@d03:一九七一'},{year:'2017',title:'瑞幸成立',at:'@d03:二零一七'}]},

 {scene:'flow', until:'@d05', says:'流程 + 绕回起点的回环箭头',
  nodes:[{id:'a',title:'种植',at:'@d04:种植'},{id:'b',title:'采摘',at:'@d04:种植+0.4'},{id:'c',title:'烘焙',at:'@d04:种植+0.8'},
         {id:'d',title:'运输',at:'@d04:种植+1.2'},{id:'e',title:'萃取',at:'@d04:萃取'}],
  links:[{from:'a',to:'b'},{from:'b',to:'c'},{from:'c',to:'d'},{from:'d',to:'e'}],
  loop:{label:'下一批豆子', at:'@d04:下一批'}},

 {scene:'tree', until:'@d06', says:'利润一层层岔开拆成收入和成本',
  root:{id:'p',l:'利润',t:'@d05:利润',c:[
    {id:'r',l:'收入',op:'+',t:'@d05:收入',c:[{l:'咖啡',t:'@d05:咖啡'},{l:'甜点',t:'@d05:甜点'}]},
    {id:'c',l:'成本',op:'−',t:'@d05:成本',c:[{l:'原料',t:'@d05:原料'},{l:'房租',t:'@d05:房租'},{l:'人工',t:'@d05:人工'}]}]},
  focus:[['@d05:收入','r'],['@d05:成本','c']]},

 {scene:'map', until:'@d07', says:'矢量国界 + 按国家填色 + 航线',
  style:'countries',
  countries:[{id:'BRA',at:'@d06:巴西',color:'gold',label:'巴西'},{id:'VNM',at:'@d06:越南',color:'teal',label:'越南'}],
  nodes:[{id:'us',lon:-98,lat:39,label:'美国',at:'@d06:美国'},{id:'eu',lon:9,lat:53,label:'欧洲',at:'@d06:欧洲'},{id:'jp',lon:139,lat:36,label:'日本',at:'@d06:日本'}],
  links:[{from:'_cBRA',to:'us',text:'咖啡'},{from:'_cBRA',to:'eu'},{from:'_cVNM',to:'jp'}],
  steps:[{at:'@d06:日本+0.2', focus:'all', d:.4}]},

 {scene:'compare', until:'@d08', says:'表头下立大数 + 要点（vs6 的写法）',
  left:{title:'精品咖啡馆',color:'gold',value:'40',sub:'一杯拿铁（演示）',pts:[{s:'一天卖 200 杯',at:'@d07:两百杯'},{s:'单品豆、手冲',at:'@d07:两百杯+0.4'}]},
  right:{title:'连锁咖啡店',color:'steel',value:'15',sub:'一杯拿铁（演示）',pts:[{s:'一天卖 1000 杯',at:'@d07:一千杯'},{s:'机器出品',at:'@d07:一千杯+0.4'}]},
  rows:[{label:'一天销量',left:'200 杯',right:'1000 杯',win:'right',at:'@d07:一千杯'}]},

 {scene:'network', until:'@d09', says:'持股 / 供豆 / 管理费 / 授权的关系网',
  layout:'hub',
  nodes:[{id:'brand',title:'咖啡品牌',color:'gold',w:400,h:180,type:'card'},
         {id:'inv',name:'投资方',color:'steel',at:'@d08:投资方'},{id:'sup',name:'供应商',color:'green',at:'@d08:供应商'},{id:'fr',name:'加盟店',color:'brick',at:'@d08:加盟店'}],
  links:[{from:'inv',to:'brand',text:'持股 51%'},{from:'sup',to:'brand',text:'供豆'},{from:'fr',to:'brand',text:'管理费'},{from:'brand',to:'fr',text:'授权'}],
  steps:[{at:'@d08:投资方',focus:'inv'},{at:'@d08:供应商',flow:'sup>brand'},{at:'@d08:加盟店',focus:'fr'},{at:'@d08:授权',flow:'brand>fr'},{at:'@d08:加盟店+0.3',focus:'all',d:.5}]},

 {scene:'article', until:'@d10', says:'刷黄之后盖章 + 手绘圈注（判决那一下）',
  mock:{source:'报道',date:'2026-09-18',title:'OpenAI 预计 2030 年前累计烧掉约 2780 亿美元',
    body:['（示例排版：截不到原文时，用核实过的文字排一页通用样式。）','报道称，算力投入会继续增加，收入暂时追不上支出。'],mark:'2780 亿美元'},
  zoom:'@d09:两千七百八十',
  stamp:{text:'已核实',color:'green',at:'@d09:核实'},
  scribble:{at:'@d09:核实+0.4',kind:'circle',color:'red'}},

 {scene:'docpage', until:'@d11', says:'政策条文逐字上纸，镜头推过去逐行刷黄',
  paras:[['title','国务院关于渐进式延迟法定退休年龄的办法'],['meta','2024 年 9 月 · 第二条'],['gap',''],
    ['p','第二条 从2030年1月1日起，将职工按月领取基本养老金最低缴费年限[[0|由十五年逐步提高至二十年]]，每年提高六个月。']],
  marks:[{at:'@d10:十五年',kind:'hl'}], zoom:'@d10:十五年-0.45'},

 {scene:'calc', until:'@d12', says:'字段逐个填入，结果滚出来（现场算账）',
  title:'咖啡开销计算器（演示）', sub:'每天一杯',
  fields:[{l:'每杯价格',v:'30',u:'元',at:'@d11:三十'},{l:'一年天数',v:'365',u:'天',at:'@d11:三百六十五'}],
  res:[{l:'一年花费',f:'30×365',v:10950,u:'元',at:'@d11:一万零九百五十',total:true}]},

 {scene:'stack', until:'@d13', says:'钱一张一张叠成堆，叠完立大数',
  n:12, value:'$12万', brow:'叠了十二张', unit:'一张 = 一个月房租（演示）'},

 {scene:'grid', until:'@d14', says:'100 格里 37 格逐个变红，其余灰掉',
  n:100, hi:37, hiAt:'@d13:三十七', value:'37%', brow:'有漏洞的 skill', label:'100 个 skill 包（演示）'},

 {scene:'bubble', until:'@d15', says:'摆误区：要辟的那条亮起来打叉',
  items:[{who:'网友甲',text:'买黄金保值',at:'@d14:大家都'},{who:'网友乙',text:'乱世才买黄金',at:'@d14:大家都+0.5'},{who:'网友丙',text:'黄金不会跌',at:'@d14:大家都+1'}],
  pick:{i:2,at:'@d14:但是'}},

 {scene:'desk', until:'@d16', says:'桌面上圈注 + 盖章（每张截图各自带）',
  items:[{img:PH+'news_a.jpg',at:'@d15:两篇',hl:[[120,140,700,90]],scribble:{at:'@d15:圈'}},
         {img:PH+'news_b.jpg',at:'@d15:两篇+0.4',hl:[[120,140,700,90]],stamp:{text:'谣言',at:'@d15:谣言'}}],
  read:{i:0,at:'@d15:圈'}},

 {scene:'line', until:'@d17', says:'示意：一条日线边画边拉远，回踩处亮标记',
  data:{points:[['2025-01-02',100],['2025-02-02',118],['2025-03-02',112],['2025-04-02',140],['2025-05-02',165],['2025-06-02',150],['2025-07-02',190],['2025-08-02',220],['2025-09-02',210],['2025-10-02',260],['2025-11-02',300]]},
  title:'示意走势（演示数据）', en:'DEMO LINE',
  draw:{at:'@d16:这条', until:'@d16:新高'},
  marks:[{at:'@d16:回踩', date:'2025-06-02', text:'回踩'}]},

 {scene:'chain', says:'示意：因果链四张竖卡，念到哪张亮哪张',
  items:[{at:'@d17:打仗', title:'打仗', img:PH+'city.jpg'},
         {at:'@d17:油价', title:'油价', img:PH+'chip.jpg'},
         {at:'@d17:通胀', title:'通胀', img:PH+'crowd.jpg'},
         {at:'@d17:利率', title:'利率', img:PH+'news_a.jpg'}]},
]);
return K.go();
})();
