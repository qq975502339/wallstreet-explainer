#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""事实账本对账与口播防错检查（纪律变检查）。
  python scripts/facts_check.py <片子目录> [--facts facts.md] [--script script.json] [--check-links] [--strict-script] [--long]

查四件事：
 1 账本结构：每条 F/D/P/C 是否有必填字段（链接/两个日期/级别/用在…），缺哪条哪字段报出来；
 2 链接与日期形态：链接须为完整 https://（禁裸域名与占位链接）；日期须为 YYYY-MM-DD（年报发布日期可 YYYY/YYYY-MM），禁"上周/今年"等相对时间；加 --check-links 可联网 HEAD 探测死链（404/410 判失败，401/403/405/429 标反爬不误报）；
 3 上屏对账（有 film.js 时）：film.js 里 value:'…' 的每个上屏数字，是否能在账本里找到（归一化后匹配）；
 4 口播 AI 腔与长片反方/开页提醒：同目录有 script.json 时扫描 AI 腔套话（默认提醒，--strict-script 升级为失败）；中长片（--long 或 brief.md 标中长）提醒是否含 C 类反方证据与「原页核对」留痕。
"未验证"区条目只提醒不上屏。退出码 1 = 有缺字段、链接/日期违规、死链或对不上的数字。
"""
import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

REQ = {
    'F': ['上屏写法', '来源', '链接', '发布日期', '查阅日期', '级别', '用在'],
    'D': ['原文', '来源', '发布日期', '查阅日期', '用在'],
    'P': ['文件', '作者', '许可', '页面', '用在'],
    'C': ['结论', '来源', '链接', '发布日期', '查阅日期', '级别', '用在'],
}

SUSPECT_URL_MARKERS = (
    'example.com', 'example.org', 'example.net', 'localhost', '127.0.0.1',
    'placeholder', 'does-not-exist', '/xxx', 'tbd', 'todo', '待补充', '<链接>', '<填>',
)

RELATIVE_DATE_RE = re.compile(r'(上周|上月|昨天|前天|今天|最近|近期|今年|去年|本月|刚刚|日前|此前)')
FULL_DATE_RE = re.compile(r'^\d{4}-\d{2}-\d{2}$')
PUB_DATE_RE = re.compile(r'^\d{4}(?:-\d{2}(?:-\d{2})?)?$')

CLICHE_PATTERNS = (
    r'值得注意的是',
    r'总而言之',
    r'综上所述',
    r'众所周知',
    r'毋庸置疑',
    r'不难发现',
    r'在当今',
    r'随着[^。！？\n]{0,12}的不断发展',
    r'赋能',
    r'全方位',
    r'一站式',
    r'打造闭环',
)


def norm(s):
    return re.sub(r'[\s,，]', '', str(s))


def extract_field_values(entry, field):
    pat = rf'{field}(?:（[^）]*）|/[^\s：:]+)?[：:]\s*([^\n；;]+)'
    return [m.group(1).strip() for m in re.finditer(pat, entry)]


def validate_url(url):
    u = url.strip().strip('<>')
    low = u.lower()
    if not low.startswith('https://'):
        return f'链接须为完整 https://（当前：{u}）'
    for marker in SUSPECT_URL_MARKERS:
        if marker in low:
            return f'链接包含占位特征「{marker}」（当前：{u}）'
    if re.search(r'\s', u):
        return f'链接包含空白字符（当前：{u}）'
    return None


def validate_date(val, field):
    v = val.strip()
    if RELATIVE_DATE_RE.search(v):
        return f'{field}不可写相对时间（当前：{v}），须用 YYYY-MM-DD'
    pattern = FULL_DATE_RE if field == '查阅日期' else PUB_DATE_RE
    if not pattern.match(v):
        fmt = 'YYYY-MM-DD' if field == '查阅日期' else 'YYYY-MM-DD（或年报 YYYY / YYYY-MM）'
        return f'{field}格式不对（当前：{v}），应为 {fmt}'
    return None


def probe_url(url, timeout=8):
    headers = {'User-Agent': 'wallstreet-explainer-facts-check/1.0'}
    for method in ('HEAD', 'GET'):
        req = urllib.request.Request(url, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                code = getattr(resp, 'status', 200) or 200
                if 200 <= code < 400:
                    return 'ok', code
                return 'error', code
        except urllib.error.HTTPError as e:
            if e.code == 405 and method == 'HEAD':
                continue
            if e.code in (404, 410):
                return 'dead', e.code
            if e.code in (401, 403, 405, 429):
                return 'blocked', e.code
            return 'error', e.code
        except Exception as e:
            return 'error', str(e)
    return 'blocked', 405


def check_script_cliches(script_path):
    hits = []
    if not script_path or not script_path.exists():
        return hits
    try:
        data = json.loads(script_path.read_text('utf-8'))
    except Exception as e:
        return [('script.json', f'JSON 解析失败：{e}')]
    for line in data.get('lines', []):
        lid = line.get('id', '?')
        txt = str(line.get('text', ''))
        for pat in CLICHE_PATTERNS:
            m = re.search(pat, txt)
            if m:
                hits.append((lid, m.group(0)))
    return hits


def detect_long_form(film_dir, explicit_long=False):
    if explicit_long:
        return True
    brief_p = film_dir / 'brief.md'
    if brief_p.exists():
        txt = brief_p.read_text('utf-8', errors='ignore')
        if re.search(r'目标档位[：:]\s*[^\n]*(中长|长片|深度|5[–-]10)', txt):
            return True
    return False


def check_facts(film_dir, facts_path=None, script_path=None, check_links=False, strict_script=False, is_long=False):
    film = Path(film_dir)
    facts_p = Path(facts_path) if facts_path else film / 'facts.md'
    if not facts_p.exists():
        return 1, [f'没有账本：{facts_p}（从 references/facts_template.md 复制建起）'], [], []

    text = facts_p.read_text('utf-8')
    problems = []
    warnings = []
    notes = []

    entries = re.split(r'^## ', text, flags=re.M)[1:]
    valid_entries = []
    urls_to_probe = []
    has_counter = False
    has_spot_check = False

    for e in entries:
        head = e.splitlines()[0].strip()
        m = re.match(r'([FDPC])\d+', head)
        if not m:
            continue
        kind = m.group(1)
        valid_entries.append((kind, head, e))
        if kind == 'C':
            has_counter = True
        if re.search(r'原页核对[：:]\s*[^\s<>]+', e):
            has_spot_check = True

        for field in REQ[kind]:
            # 字段可能带括注（"原文（逐字）："）或斜杠（"结论/反例："）、可能与其他字段同一行
            if not re.search(rf'{field}(?:（[^）]*）|/[^\s：:]+)?[：:]\s*[^\s；;<>]+', e):
                problems.append(f'{head} 缺字段「{field}」')

        for ufield in ('链接', '页面'):
            for raw_url in extract_field_values(e, ufield):
                # 忽略字段内括号说明（如 "https://...（示例）"）
                u_clean = re.split(r'[（(]', raw_url)[0].strip()
                err = validate_url(u_clean)
                if err:
                    problems.append(f'{head} {ufield}无效：{err}')
                else:
                    urls_to_probe.append((head, u_clean))

        for dfield in ('发布日期', '查阅日期'):
            for raw_d in extract_field_values(e, dfield):
                d_clean = re.split(r'[（(]', raw_d)[0].strip()
                err = validate_date(d_clean, dfield)
                if err:
                    problems.append(f'{head} {err}')

    unver = re.search(r'## 未验证[^\n]*\n(.*)$', text, flags=re.S)
    if unver:
        n = len([l for l in unver.group(1).splitlines() if l.strip().startswith('-')])
        notes.append(f'提醒：未验证区 {n} 条——确认都没上屏')

    if not valid_entries:
        problems.append('账本没有有效条目')

    if check_links and urls_to_probe:
        seen_urls = {}
        for head, u in urls_to_probe:
            if u not in seen_urls:
                seen_urls[u] = probe_url(u)
            status, detail = seen_urls[u]
            if status == 'dead':
                problems.append(f'{head} 死链（HTTP {detail}）：{u}')
            elif status == 'blocked':
                warnings.append(f'{head} 链接返回 HTTP {detail}（疑似反爬，需人工开页核对）：{u}')
            elif status == 'error':
                warnings.append(f'{head} 链接探测异常（{detail}）：{u}')

    film_js_p = film / 'film.js'
    values = []
    if film_js_p.exists():
        film_js = film_js_p.read_text('utf-8')
        values = re.findall(r"value:\s*'([^']+)'", film_js) + re.findall(r'"value":\s*"([^"]+)"', film_js)
        missing = []
        for v in values:
            if not any(
                norm(v) == norm(mm.group(1))
                for kind, _, e in valid_entries
                if kind == 'F'
                for mm in re.finditer(r'上屏写法[：:]\s*([^\n]+)', e)
            ):
                missing.append(v)
        for v in missing:
            problems.append(f'上屏数字「{v}」在账本里找不到（补记录或统一写法）')
        if not values:
            problems.append('未检查到 value 字符串；无法确认上屏数字，需人工核对')
        notes.append('覆盖范围：仅 film.js 的 value 字符串；series/parts/rows/算式及动态数值须人工核对')
    else:
        notes.append('提示：尚未找到 film.js，本次仅检查账本结构、链接、日期与口播稿（写完 film.js 后须再跑一次对账）')

    sp = Path(script_path) if script_path else film / 'script.json'
    cliches = check_script_cliches(sp)
    for lid, word in cliches:
        msg = f'口播 {lid} 含 AI 腔套话「{word}」：建议改写成具体动作或直接删掉'
        if strict_script:
            problems.append(msg)
        else:
            warnings.append(msg)

    long_mode = detect_long_form(film, explicit_long=is_long)
    if long_mode:
        if not has_counter:
            warnings.append('中长片账本缺少 C 类反方证据 / 失效边界（如 ## C01）：建议补至少 1 条权威反方或边界条件防确认偏误')
        if not has_spot_check:
            warnings.append('中长片账本未见「原页核对」留痕：建议对 2–3 个承重核心数补记开页核对结果')

    if problems:
        return 1, problems, warnings, notes
    summary = f'facts_check：账本 {len(valid_entries)} 条结构/链接/日期齐全'
    if film_js_p.exists():
        summary += f'；{len(values)} 个 value 字符串对账通过（其他字段须人工核对）'
    notes.append(summary)
    return 0, problems, warnings, notes


def main(argv=None):
    ap = argparse.ArgumentParser(description='事实账本对账与口播防错检查')
    ap.add_argument('film_dir', help='片子目录')
    ap.add_argument('--facts', help='指定 facts.md 路径')
    ap.add_argument('--script', help='指定 script.json 路径')
    ap.add_argument('--check-links', action='store_true', help='联网 HEAD/GET 探测账本链接是否 404/410 死链')
    ap.add_argument('--strict-script', action='store_true', help='口播命中 AI 腔套话时返回退出码 1')
    ap.add_argument('--long', action='store_true', help='按中长片检查反方证据与开页留痕提醒')
    args = ap.parse_args(argv)

    code, problems, warnings, notes = check_facts(
        args.film_dir,
        facts_path=args.facts,
        script_path=args.script,
        check_links=args.check_links,
        strict_script=args.strict_script,
        is_long=args.long,
    )
    for n in notes:
        print(n)
    if warnings:
        print(f'提醒（{len(warnings)} 条）：')
        for w in warnings:
            print(' !', w)
    if problems:
        print(f'facts_check：{len(problems)} 个问题')
        for p in problems:
            print(' -', p)
    sys.exit(code)


if __name__ == '__main__':
    main()
