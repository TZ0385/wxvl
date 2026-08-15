import os
import re
import sys
import json
import xml.etree.ElementTree as ET
import platform
import tempfile
import requests
import shutil
import subprocess
import datetime
from urllib.parse import urlparse, parse_qsl, urlencode


def canon_url(u):
    '''规范化微信文章URL: 短链保留token; 长链只留 __biz/mid/idx/sn,
    去掉 chksm/scene 等跟踪参数和 #fragment —— 同一篇文章的多种写法归一,
    否则不同源(裸参数版/带跟踪参数版)会被当成两篇导致重复入库'''
    try:
        p = urlparse(u)
        if p.path.startswith('/s/') and len(p.path) > 3:
            return 'https://mp.weixin.qq.com' + p.path
        q = [(k, v) for k, v in parse_qsl(p.query) if k in ('__biz', 'mid', 'idx', 'sn')]
        if not q:
            return u
        return 'https://mp.weixin.qq.com/s?' + urlencode(q)
    except Exception:
        return u


def write_json(path, data, encoding="utf8"):
    """写入json"""
    with open(path, "w", encoding=encoding) as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def read_json(path, default_data={}, encoding="utf8"):
    """读取json, 解析失败时保留原文件并报错退出, 避免误清空历史记录"""
    if not os.path.exists(path):
        return default_data
    try:
        return json.loads(open(path, "r", encoding=encoding).read())
    except Exception as e:
        print("data.json 解析失败, 已停止以免覆盖历史记录: {}".format(e))
        sys.exit(1)

def get_executable_path():
    '''获取可执行文件路径'''
    system = platform.system()
    if system == 'Windows':
        executable_path = './bin/wechatmp2markdown-v1.1.11_win64.exe'
    else:
        executable_path = './bin/wechatmp2markdown-v1.1.11_linux_amd64'
    # 添加执行权限
    os.chmod(executable_path, 0o755)
    # 返回可执行文件的完整路径
    return executable_path

def get_md_path(executable_path,url):
    '''获取md文件路径'''
    # finally 保证临时目录被清理, 子进程 120s 超时防止卡死整个 workflow
    temp_directory = tempfile.mkdtemp()
    command = [executable_path, url, temp_directory, '--image=url']
    try:
        subprocess.check_output(command, timeout=120)
        for root, _, files in os.walk(temp_directory):
            for file in files:
                if file.endswith(".md"):
                    file_path = os.path.join(root, file)
                    yield file_path
    finally:
        shutil.rmtree(temp_directory, ignore_errors=True)

def get_chainreactors_url():
    '''从 chainreactors picker (archive 分支) 当日 dump 的 frontmatter 提取微信文章链接。

    dump 结构: archive/{年}/{月}/{日}/daily/{公众号_标题}.md, frontmatter 带 url 字段。
    目录滞后一天生成(次日约 12:02 CST 提交), 故取昨天+今天两个目录。
    只收 /s/ 短链: s?__biz= 长链自 2025-07 起对机房IP(含 GitHub runners)启用
    wappoc 验证码, 家用IP实测约85%可爬但 CI 必失败, 为防烧坏 runner IP 直接过滤。
    先按文件名(含标题)做关键词过滤, 只下载命中文件的 frontmatter, 减少请求量。
    '''
    keyword = re.compile(r'(?:复现|漏洞|CVE-\d+|CNVD-\d+|CNNVD-\d+|XVE-\d+|QVD-\d+|POC|EXP|0day|1day|nday|RCE|代码执行|命令执行)', re.I)
    api_headers = {'Accept': 'application/vnd.github+json'}
    token = os.environ.get('GH_TOKEN')
    if token:
        api_headers['Authorization'] = 'token ' + token
    urls = []
    today = datetime.date.today()
    for delta in (1, 0):
        d = today - datetime.timedelta(days=delta)
        api = 'https://api.github.com/repos/chainreactors/picker/contents/archive/{}/{:02d}/{:02d}/daily?ref=archive'.format(d.year, d.month, d.day)
        try:
            resp = requests.get(api, headers=api_headers, timeout=30)
            if resp.status_code != 200:
                continue
            for item in resp.json():
                name = item.get('name', '')
                if not name.endswith('.md') or not keyword.search(name):
                    continue
                # Range 只取文件头, frontmatter (含 url 行) 在前 2KB 内
                raw = requests.get(item['download_url'], timeout=30,
                                   headers={'Range': 'bytes=0-2047'})
                m = re.search(r'^url:\s*(https://mp\.weixin\.qq\.com/s/\S+)', raw.text, re.M)
                if m:
                    urls.append(m.group(1).rstrip(').,，'))
        except Exception as e:
            print("chainreactors 源({})获取失败: {}".format(d, e))
    return urls

def get_BruceFeIix_url():
    '''获取今日url'''
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    base_url = 'https://raw.githubusercontent.com/BruceFeIix/picker/refs/heads/master/archive/daily/{}/{}.md'.format(current_date[:4], current_date)
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'priority': 'u=0, i',
        'referer': 'https://github.com/BruceFeIix/picker',
        'sec-ch-ua': '"Chromium";v="130", "Microsoft Edge";v="130", "Not?A_Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0',
    }
    try:
        response = requests.get(
            base_url,
            headers=headers,
            timeout=30,
        )
        # 注意: 字符类必须覆盖 URL 全部合法字符 (/ ? = & 等), 否则链接被截断
        urls = re.findall('(?:复现|漏洞|CVE-\d+|CNVD-\d+|CNNVD-\d+|XVE-\d+|QVD-\d+|POC|EXP|0day|1day|nday|RCE|代码执行|命令执行).*?(https://mp.weixin.qq.com/[A-Za-z0-9\-._~:/?#@!$&*+,;=%]+)',response.text,re.I)
        urls = [url.rstrip(')') for url in urls]
        return urls
    except Exception as e:
        print("BruceFeIix 源获取失败: {}".format(e))
        return []


def get_doonsec_url():
    '''从 Doonsec RSS 获取今日URL，使用 XML 解析'''
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'priority': 'u=0, i',
        'sec-ch-ua': '"Chromium";v="130", "Microsoft Edge";v="130", "Not?A_Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0',
    }

    try:
        response = requests.get('https://wechat.doonsec.com/rss.xml', headers=headers, timeout=30)
        response.encoding = response.apparent_encoding

        # XML 解析
        root = ET.fromstring(response.text)
        urls = []
        for item in root.findall('./channel/item'):
            title = item.findtext('title') or ''
            link = item.findtext('link') or ''
            if re.search(r'(复现|漏洞|CVE-\d+|CNVD-\d+|CNNVD-\d+|XVE-\d+|QVD-\d+|POC|EXP|0day|1day|nday|RCE|代码执行|命令执行)', title, re.I) and link.startswith('https://mp.weixin.qq.com/'):
                urls.append(link.rstrip(')'))

        return urls
    except Exception as e:
        print("Error parsing Doonsec RSS:", e)
        return []


    
def rep_filename(result_path):
    '''
    替换不能用于文件名的字符; 同名冲突时追加序号避免覆盖已有文章
    '''
    for root, _, files in os.walk(result_path):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                new_file = re.sub(r'[\/\\\:\*\?\"\<\>\|]', '', file)
                if new_file == file:
                    continue
                dest = os.path.join(root, new_file)
                i = 2
                while os.path.exists(dest):
                    stem, ext = os.path.splitext(new_file)
                    dest = os.path.join(root, '{} ({}).{}'.format(stem, i, ext))
                    i += 1
                shutil.move(file_path, dest)
                
def main():
    '''主函数'''
    data_file = 'data.json'
    data = {}
    executable_path = get_executable_path()
    base_result_path = 'doc'
    # 创建基于当前年月的子目录 (格式: YYYY-MM)
    current_month = datetime.datetime.now().strftime("%Y-%m")
    result_path = os.path.join(base_result_path, current_month)
    os.makedirs(result_path, exist_ok=True)
    # 读取历史记录
    data = read_json(data_file, default_data=data)
    urls = []
    if len(sys.argv) == 2 and sys.argv[1] == 'today':
        print("正在获取URL...")
        chainreactors_urls = get_chainreactors_url()
        print(f"chainreactors: {len(chainreactors_urls)} 个URL")

        brucefelix_urls = get_BruceFeIix_url()
        print(f"BruceFeIix: {len(brucefelix_urls)} 个URL")

        doonsec_urls = get_doonsec_url()
        print(f"Doonsec: {len(doonsec_urls)} 个URL")

        urls = list(set(chainreactors_urls + brucefelix_urls + doonsec_urls))
        print(f"总共去重后: {len(urls)} 个URL")
        # 三个源同时归零说明数据源已失效, 退出非零让 workflow 失败并通知,
        # 防止再次出现断档空转无人察觉 (2025-08~12 的教训)
        if not urls:
            sys.exit(1)
    # 规范化去重: 同一篇文章在不同源里可能带不同跟踪参数, 按规范化键判重
    known = {canon_url(u) for u in data}
    for url in urls:
        if url in data or canon_url(url) in known:
            continue
        try:
            for file_path in get_md_path(executable_path, url):
                name = os.path.splitext(os.path.basename(file_path))[0]
                if name == '.md':
                    continue
                shutil.copy2(file_path,result_path)
                data[url] = name
                known.add(canon_url(url))
                write_json(data_file,data)
                print(name,end='、')
        except Exception as e:
            print(f"\n处理URL失败 {url}: {e}")
            continue
    rep_filename(result_path)
    
if __name__ == '__main__':
    main()
