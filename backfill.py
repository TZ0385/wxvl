#!/usr/bin/env python3
"""一次性补档脚本 v2: 从 chainreactors picker 的 daily dump 直接复制文章。

数据源:
  2025-08, 2025-09          -> 本地 /mnt/d/Learn/picker-chainreactors (master)
  2025-10-26~31, 11, 12 月  -> /root/picker-dump (上游 archive 分支导出)
  2026-06                   -> /root/picker-dump

URL 映射: 优先 daily.json ({feed: {title: url}}), 其次 daily.md 的 [title](url) 行;
映射不上的用 dump:// 合成键。标题按项目关键词规则过滤, 与 run.py 语义一致。
"""
import os
import re
import json
import shutil

WXVL = '/mnt/d/Tools/Vuln-db/wxvl'
DATA_FILE = os.path.join(WXVL, 'data.json')
DOC = os.path.join(WXVL, 'doc')

SOURCES = [
    ('2025-08', '/mnt/d/Learn/picker-chainreactors/archive/2025/08'),
    ('2025-09', '/mnt/d/Learn/picker-chainreactors/archive/2025/09'),
    ('2025-10', '/root/picker-dump/archive/2025/10'),
    ('2025-11', '/root/picker-dump/archive/2025/11'),
    ('2025-12', '/root/picker-dump/archive/2025/12'),
    ('2026-06', '/root/picker-dump/archive/2026/06'),
]

KEYWORDS = re.compile(
    r'(?:复现|漏洞|CVE-\d+|CNVD-\d+|CNNVD-\d+|XVE-\d+|QVD-\d+|POC|EXP|0day|1day|nday|RCE|代码执行|命令执行)',
    re.I)
MD_LINK = re.compile(r'- \[ \] \[(?P<title>[^\]]+)\]\((?P<url>https?://[^)]+)\)')
ILLEGAL = re.compile(r'[\/\\\:\*\?\"\<\>\|]')


def load_day_map(day_dir):
    """返回 (title->url, exact_filename->url) 两个映射"""
    title2url, file2url = {}, {}

    jf = os.path.join(day_dir, 'daily.json')
    if os.path.exists(jf):
        try:
            feeds = json.load(open(jf, encoding='utf-8'))
            for feed, arts in feeds.items():
                if isinstance(arts, dict):
                    for title, url in arts.items():
                        if isinstance(url, str) and url.startswith('http'):
                            title2url[title] = url
                            file2url['%s_%s.md' % (feed, title)] = url
                elif isinstance(arts, list):
                    for a in arts:
                        t, u = a.get('title'), a.get('url')
                        if t and u:
                            title2url[t] = u
                            file2url['%s_%s.md' % (feed, t)] = u
        except Exception as e:
            print('  daily.json 解析失败:', e)

    mf = os.path.join(day_dir, 'daily.md')
    if os.path.exists(mf):
        for m in MD_LINK.finditer(open(mf, encoding='utf-8').read()):
            title2url.setdefault(m.group('title'), m.group('url'))

    return title2url, file2url


def safe_dest(month_dir, name):
    name = ILLEGAL.sub('', name).strip() or 'untitled'
    dest = os.path.join(month_dir, name + '.md')
    i = 2
    while os.path.exists(dest):
        dest = os.path.join(month_dir, '%s (%d).md' % (name, i))
        i += 1
    return dest


def main():
    data = json.load(open(DATA_FILE, encoding='utf-8'))
    base = len(data)
    stats = {}

    for month, src in SOURCES:
        if not os.path.isdir(src):
            print('!! 缺少源目录:', src)
            continue
        month_dir = os.path.join(DOC, month)
        os.makedirs(month_dir, exist_ok=True)
        s = stats.setdefault(month, {'copied': 0, 'skip_dup': 0, 'no_keyword': 0, 'unmapped': 0})

        for day in sorted(os.listdir(src)):
            day_dir = os.path.join(src, day)
            daily = os.path.join(day_dir, 'daily')
            if not os.path.isdir(daily):
                continue
            date = '%s-%s' % (month, day)
            title2url, file2url = load_day_map(day_dir)

            for fn in sorted(os.listdir(daily)):
                if not fn.endswith('.md'):
                    continue
                raw_title = fn[:-3]
                url = file2url.get(fn)
                if url is None and '_' in raw_title:
                    url = title2url.get(raw_title.split('_', 1)[1])
                if url is None:
                    url = title2url.get(raw_title)
                # 展示标题: 去掉 feed 前缀
                title = raw_title.split('_', 1)[1] if (url and '_' in raw_title) else raw_title

                if not KEYWORDS.search(title) and not KEYWORDS.search(raw_title):
                    s['no_keyword'] += 1
                    continue
                key = url if url else 'dump://%s/%s' % (date, fn)
                if key in data:
                    s['skip_dup'] += 1
                    continue
                try:
                    shutil.copy2(os.path.join(daily, fn), safe_dest(month_dir, title))
                    data[key] = title
                    s['copied'] += 1
                    if url is None:
                        s['unmapped'] += 1
                except Exception as e:
                    print('  复制失败 %s: %s' % (fn[:50], e))

        print('%s: 新增 %d (无URL映射 %d), 已存在跳过 %d, 非漏洞类跳过 %d'
              % (month, s['copied'], s['unmapped'], s['skip_dup'], s['no_keyword']))

    tmp = DATA_FILE + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    os.replace(tmp, DATA_FILE)
    print('data.json: %d -> %d (+%d)' % (base, len(data), len(data) - base))


if __name__ == '__main__':
    main()
