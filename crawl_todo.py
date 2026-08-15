#!/usr/bin/env python3
"""按 /tmp/backfill_todo.json 抓取: python3 crawl_todo.py short|long|sample"""
import os, re, json, time, shutil, tempfile, subprocess, sys

WXVL = '/mnt/d/Tools/Vuln-db/wxvl'
EXE = os.path.join(WXVL, 'bin/wechatmp2markdown-v1.1.11_linux_amd64')
ILLEGAL = re.compile(r'[\/\\\:\*\?\"\<\>\|]')
MODE = sys.argv[1] if len(sys.argv) > 1 else 'short'

todo = json.load(open('/tmp/backfill_todo.json'))
if MODE == 'sample':
    items = sorted(todo['long'].items())
    step = max(1, len(items) // 20)
    items = items[::step][:20]
    items = [(u, d) for u, d in items if u not in json.load(open(os.path.join(WXVL, 'data.json')))]
else:
    data = json.load(open(os.path.join(WXVL, 'data.json')))
    items = [(u, d) for u, d in sorted(todo[MODE].items()) if u not in data]

print(f'[{MODE}] 本次处理 {len(items)} 条')
ok = dead = 0
t0 = time.time()
for i, (url, date) in enumerate(items, 1):
    with tempfile.TemporaryDirectory() as tmp:
        try:
            subprocess.run([EXE, url, tmp, '--image=url'], capture_output=True, timeout=90)
        except subprocess.TimeoutExpired:
            pass
        got = None
        for root, _, files in os.walk(tmp):
            for fn in files:
                if fn.endswith('.md') and fn != '.md':
                    got = (fn[:-3], os.path.join(root, fn))
        if got is None:
            dead += 1
        else:
            data = json.load(open(os.path.join(WXVL, 'data.json')))
            if url in data:
                continue
            month_dir = os.path.join(WXVL, 'doc', date[:7])
            os.makedirs(month_dir, exist_ok=True)
            title = ILLEGAL.sub('', got[0]).strip() or 'untitled'
            dest = os.path.join(month_dir, title + '.md')
            n = 2
            while os.path.exists(dest):
                dest = os.path.join(month_dir, '%s (%d).md' % (title, n)); n += 1
            shutil.copy2(got[1], dest)
            data[url] = got[0]
            with open(os.path.join(WXVL, 'data.json') + '.tmp', 'w', encoding='utf8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            os.replace(os.path.join(WXVL, 'data.json') + '.tmp', os.path.join(WXVL, 'data.json'))
            ok += 1
            print('OK', date, got[0][:40])
    if MODE != 'sample':
        # 触发微信风控后需低速; SLOW=1 时 4s/条
        time.sleep(4.0 if os.environ.get('SLOW') else 0.8)
print(f'[{MODE}] 完成: 成功 {ok} / 失败(死链或拦截) {dead}, 耗时 {(time.time()-t0)/60:.1f} 分钟')
