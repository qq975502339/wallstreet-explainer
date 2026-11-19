#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修缺陷7：事实账本对账（纪律变检查）。
  python scripts/facts_check.py <片子目录> [--facts facts.md]

查两件事：
 1 账本结构：每条 F/D/P 是否有必填字段（链接/两个日期/级别/用在…），缺哪条哪字段报出来；
 2 上屏对账：film.js 里 value:'…' 的每个上屏数字，是否能在账本里找到（归一化后子串匹配）；
   找不到 = 上屏数字没进账本（或账本写法不一致），报出来人工核。
"未验证"区条目只提醒不上屏。退出码 1 = 有缺字段或对不上的数字。
"""
import json, re, sys
from pathlib import Path

a = sys.argv[1:]
if not a:
    print(__doc__); sys.exit(1)
film = Path(a[0])
facts_p = Path(a[a.index('--facts') + 1]) if '--facts' in a else film / 'facts.md'
if not facts_p.exists():
    sys.exit(f'没有账本：{facts_p}（从 references/facts_template.md 复制建起）')
text = facts_p.read_text('utf-8')
norm = lambda s: re.sub(r'[\s,，]', '', str(s))
ntext = norm(text)

REQ = {'F': ['上屏写法', '来源', '链接', '发布日期', '查阅日期', '级别', '用在'],
       'D': ['原文', '来源', '发布日期', '查阅日期', '用在'],
       'P': ['文件', '作者', '许可', '页面', '用在']}
problems = []
entries = re.split(r'^## ', text, flags=re.M)[1:]
for e in entries:
    head = e.splitlines()[0].strip()
    m = re.match(r'([FDP])\d+', head)
    if not m:
        continue
    kind = m.group(1)
    for field in REQ[kind]:
        # 字段可能带括注（"原文（逐字）："）、可能与其他字段同一行（"发布日期：…；查阅日期：…"）
        if not re.search(rf'{field}(（[^）]*）)?[：:]\s*[^\s；;<>]+', e):
            problems.append(f'{head} 缺字段「{field}」')
unver = re.search(r'## 未验证[^\n]*\n(.*)$', text, flags=re.S)
if unver:
    n = len([l for l in unver.group(1).splitlines() if l.strip().startswith('-')])
    print(f'提醒：未验证区 {n} 条——确认都没上屏')

film_js = (film / 'film.js').read_text('utf-8')
values = re.findall(r"value:\s*'([^']+)'", film_js) + re.findall(r'"value":\s*"([^"]+)"', film_js)
missing = []
for v in values:
    if not any(norm(v) == norm(m.group(1)) for e in entries if re.match(r"F\d+", e.splitlines()[0]) for m in re.finditer(r"上屏写法[：:]\s*([^\n]+)", e)):
        missing.append(v)
for v in missing:
    problems.append(f'上屏数字「{v}」在账本里找不到（补记录或统一写法）')

if not entries or not any(re.match(r'[FDP]\d+', e.splitlines()[0]) for e in entries):
    problems.append('账本没有有效条目')
if not values:
    problems.append('未检查到 value 字符串；无法确认上屏数字，需人工核对')
print('覆盖范围：仅 film.js 的 value 字符串；series/parts/rows/算式及动态数值须人工核对')
if problems:
    print(f'facts_check：{len(problems)} 个问题')
    for p in problems:
        print(' -', p)
    sys.exit(1)
n_entries = len([e for e in entries if re.match(r'[FDP]\d+', e.splitlines()[0])])
print(f'facts_check：账本 {n_entries} 条结构齐全；{len(values)} 个 value 字符串对账通过（其他字段须人工核对）')
