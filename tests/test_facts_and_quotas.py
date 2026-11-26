import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import facts_check  # noqa: E402


VALID_FACTS = """# 测试选题 事实账本

## F01 核心支出
- 上屏写法：$7250亿
- 来源：公司一季度财报汇总
- 链接：https://www.sec.gov/edgar/searchedgar/companysearch
- 发布日期：2026-04-30；查阅日期：2026-05-01
- 级别：一手
- 原页核对：已开页，第 12 页现金流量表确认支持
- 用在：镜 1（number）

## C01 反方边界
- 结论/反例：云业务经营现金流覆盖了大部分资本开支
- 来源：SEC 10-Q 财报
- 链接：https://www.sec.gov/edgar/browse/
- 发布日期：2026-04-30；查阅日期：2026-05-01
- 级别：一手
- 原页核对：已开页，自由现金流小节确认支持
- 用在：第 4 章边界段
"""

VALID_FILM_JS = """
const shots = [
  { scene: 'number', value: '$7250亿' }
];
"""


class FactsCheckAndQuotasTest(unittest.TestCase):
    def test_valid_facts_and_film_pass(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            (p / 'facts.md').write_text(VALID_FACTS, encoding='utf-8')
            (p / 'film.js').write_text(VALID_FILM_JS, encoding='utf-8')
            code, problems, warnings, _ = facts_check.check_facts(p, is_long=True)
            self.assertEqual(code, 0, problems)
            self.assertEqual(problems, [])
            self.assertEqual(warnings, [])

    def test_station1_without_film_js_passes_gracefully(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            (p / 'facts.md').write_text(VALID_FACTS, encoding='utf-8')
            code, problems, _, notes = facts_check.check_facts(p)
            self.assertEqual(code, 0, problems)
            self.assertTrue(any('尚未找到 film.js' in n for n in notes))

    def test_bare_domain_and_placeholder_url_fail(self):
        bad_facts = VALID_FACTS.replace(
            'https://www.sec.gov/edgar/searchedgar/companysearch',
            'bloomberg.com/news'
        ).replace(
            'https://www.sec.gov/edgar/browse/',
            'https://example.com/placeholder'
        )
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            (p / 'facts.md').write_text(bad_facts, encoding='utf-8')
            (p / 'film.js').write_text(VALID_FILM_JS, encoding='utf-8')
            code, problems, _, _ = facts_check.check_facts(p)
            self.assertEqual(code, 1)
            self.assertTrue(any('完整 https://' in x for x in problems))
            self.assertTrue(any('占位特征' in x for x in problems))

    def test_relative_date_fails(self):
        bad_facts = VALID_FACTS.replace('发布日期：2026-04-30', '发布日期：上周')
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            (p / 'facts.md').write_text(bad_facts, encoding='utf-8')
            (p / 'film.js').write_text(VALID_FILM_JS, encoding='utf-8')
            code, problems, _, _ = facts_check.check_facts(p)
            self.assertEqual(code, 1)
            self.assertTrue(any('相对时间' in x for x in problems))

    def test_script_cliche_warning_and_strict_mode(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            (p / 'facts.md').write_text(VALID_FACTS, encoding='utf-8')
            (p / 'film.js').write_text(VALID_FILM_JS, encoding='utf-8')
            (p / 'script.json').write_text(
                json.dumps({'lines': [{'id': 'b01', 'text': '值得注意的是，这项技术正在全面赋能行业。'}]}, ensure_ascii=False),
                encoding='utf-8',
            )
            code, problems, warnings, _ = facts_check.check_facts(p, strict_script=False)
            self.assertEqual(code, 0)
            self.assertEqual(problems, [])
            self.assertTrue(any('值得注意的是' in w for w in warnings))
            self.assertTrue(any('赋能' in w for w in warnings))

            code2, problems2, _, _ = facts_check.check_facts(p, strict_script=True)
            self.assertEqual(code2, 1)
            self.assertTrue(any('AI 腔套话' in x for x in problems2))

    def test_check_links_dead_vs_blocked_vs_ok(self):
        def fake_probe(url, timeout=8):
            if 'companysearch' in url:
                return 'dead', 404
            return 'blocked', 403

        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            (p / 'facts.md').write_text(VALID_FACTS, encoding='utf-8')
            (p / 'film.js').write_text(VALID_FILM_JS, encoding='utf-8')
            with patch.object(facts_check, 'probe_url', side_effect=fake_probe):
                code, problems, warnings, _ = facts_check.check_facts(p, check_links=True)
            self.assertEqual(code, 1)
            self.assertTrue(any('死链（HTTP 404）' in x for x in problems))
            self.assertTrue(any('疑似反爬' in w for w in warnings))

    def test_long_form_missing_counter_and_spot_check_warns(self):
        short_facts = """# 账本
## F01 测试数据
- 上屏写法：$7250亿
- 来源：SEC 财报
- 链接：https://www.sec.gov/edgar/searchedgar/companysearch
- 发布日期：2026-04-30；查阅日期：2026-05-01
- 级别：一手
- 用在：镜 1
"""
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            (p / 'facts.md').write_text(short_facts, encoding='utf-8')
            (p / 'brief.md').write_text('- 目标档位：中长深度档（5–10 分钟）\n', encoding='utf-8')
            code, _, warnings, _ = facts_check.check_facts(p)
            self.assertEqual(code, 0)
            self.assertTrue(any('反方证据' in w for w in warnings))
            self.assertTrue(any('原页核对' in w for w in warnings))

    def test_kit_js_syntax_and_dynamic_quota_bounds(self):
        r = subprocess.run(['node', '--check', str(ROOT / 'kit/kit.js')], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        js = (ROOT / 'kit/kit.js').read_text(encoding='utf-8')
        self.assertIn('dur>240?Math.ceil((dur-240)/180):0', js)
        probe = (
            "const f=dur=>{const extra=dur>240?Math.ceil((dur-240)/180):0;"
            "return {r:2+extra,w:1+Math.floor(Math.max(0,dur-1)/300),s:3+extra,c:3+extra};};"
            "console.log(JSON.stringify([f(77),f(240),f(300),f(480),f(600)]));"
        )
        r2 = subprocess.run(['node', '-e', probe], capture_output=True, text=True)
        self.assertEqual(r2.returncode, 0, r2.stderr)
        vals = json.loads(r2.stdout)
        # <=4m keeps original strict limits
        self.assertEqual(vals[0], {'r': 2, 'w': 1, 's': 3, 'c': 3})
        self.assertEqual(vals[1], {'r': 2, 'w': 1, 's': 3, 'c': 3})
        # 5m -> +1 on roll/statement/chapter, wine still 1
        self.assertEqual(vals[2], {'r': 3, 'w': 1, 's': 4, 'c': 4})
        # 8m & 10m -> roll 4, wine 2, statement 5, chapter 5
        self.assertEqual(vals[3], {'r': 4, 'w': 2, 's': 5, 'c': 5})
        self.assertEqual(vals[4], {'r': 4, 'w': 2, 's': 5, 'c': 5})


if __name__ == '__main__':
    unittest.main()
