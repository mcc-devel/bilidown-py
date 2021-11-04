from os import system
from bs4 import BeautifulSoup
import requests
import multitasking
import re
chunk_size = 1024*1024*2

headers = {
    'accept':'*/*',
    'accept-encoding':'identity;q=1, *;q=0',
    'accept-language':'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    #'referer':'link',
    'sec-ch-ua':'''" Not A;Brand";v="99", "Chromium";v="96", "Microsoft Edge";v="96"''',
    'sec-ch-us-mobile':'?0',
    'sec-ch-ua-platform':'''"macOS"''',
    'sec-fatch-dist':'video',
    'sec-fetch-mode':'no-cors',
    'sec-fatch-site':'same-origin',
    'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.1047.0 Safari/537.36 Edg/96.0.1047.0'
}

#driver = WebDriver()
session = requests.session()

@multitasking.task
def bchunk(lnk, chunk):
    global headers
    headers['Content-Range'] = 'bytes=%s-%s'%(chunk[0], chunk[1])
    resp = session.get(lnk, headers = headers).content
    finalArr[chunk[2]] = resp

def getchunk(lnk):
    sz = requests.head(lnk, headers = headers).headers.get('Content-Length')
    print(sz)
    cnt = 0
    if sz is not None:
        sz = int(sz)
        chunks = []
        for start in range(0, sz, chunk_size):
            if start+chunk_size-1 >= sz:
                chunks.append((start, '', cnt))
            else:
                chunks.append((start, start+chunk_size-1, cnt))
            cnt = cnt + 1
        print('num %s'%(cnt))
        return chunks
    else:
        print('Wrong no multi')
        exit(255)

def chunkd(lnk, name):
    chunks = getchunk(lnk)
    global finalArr
    global finalVid
    finalArr = []
    finalVid = bytes()
    for i in range(len(chunks)):
        finalArr.append(bytes())
    system('''rm -rf %s'''%(name))
    for chunk in chunks:
        bchunk(lnk, chunk)
    multitasking.wait_for_tasks()
    for elem in finalArr:
        finalVid = finalVid + elem
    with open(name, 'wb') as f:
        f.write(finalVid)

def down(lnk:str, preferrnm):
    global headers
    lnk = lnk.replace('www.bilibili.com', 'www.ibilibili.com')
    reres = re.match("https?://www.ibilibili.com/video/(av|AV|bv|BV)([0-9]|[a-z]|[A-Z])*", lnk)
    lnk = reres.group()
    res = requests.get(lnk).text
    bs = BeautifulSoup(res, features = 'html.parser')
    name = preferrnm + '.mp4'
    lst = bs.find_all('input')
    aid = lst[0]['value']
    cid = lst[1]['value']
    final = requests.get('https://api.bilibili.com/x/player/playurl?avid=%s&cid=%s&qn=1&type=&otype=json&platform=html5&high_quality=1'%(aid, cid)).json()['data']['durl'][0]['url'].replace(r'\u0026', '&')
    headers['referer'] = final
    chunkd(final, name)

down('https://www.bilibili.com/video/BV1ys411W7rd?afasdgabesdfasDgfaszxvj', '1')