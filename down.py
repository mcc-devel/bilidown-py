from os import system
from bs4 import BeautifulSoup
import requests
import multitasking

chunk_size = 1024*512

headers = {
    'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4642.0 Safari/537.36 Edg/96.0.1025.0',
    'Host':'upos-sz-mirrorcos.bilivideo.com',
    'Connection':'keep-alive',
    'Origin':'https://www.bilibili.com',
    'Accept':'*/*',
    'Sec-Fetch-Dest':'empty',
    'Sec-Fetch-Mode':'cors',
    'Accept-Encoding':'identity',
    'Accept-Language':'zh-CH,zh;q=0.9'
}

session = requests.session()

@multitasking.task
def bchunk(lnk, chunk):
    headers['Range'] = 'bytes=%s-%s'%(chunk[0], chunk[1])
    resp = session.get(lnk, headers = headers).content
    finalArr[chunk[2]] = resp

def getchunk(lnk):
    sz = requests.head(lnk, headers = headers).headers.get('Content-Length')
    cnt = 0
    if sz is not None:
        sz = int(sz)
        chunks = []
        for start in range(0, sz, chunk_size):
            chunks.append((start, min(start+chunk_size, sz), cnt))
            cnt = cnt + 1
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

def down(lnk, preferrnm):
    headers['Referer'] = lnk
    lnk = lnk.replace('www.bilibili.com', 'www.ibilibili.com')
    res = requests.get(lnk).text
    bs = BeautifulSoup(res, features = 'html.parser')
    name = preferrnm + '.mp4'
    lst = bs.find_all('input')
    aid = lst[0]['value']
    cid = lst[1]['value']
    final = requests.get('https://api.bilibili.com/x/player/playurl?avid=%s&cid=%s&qn=1&type=&otype=json&platform=html5&high_quality=1'%(aid, cid)).json()['data']['durl'][0]['url'].replace(r'\u0026', '&')
    chunkd(final, name)

down('https://www.bilibili.com/video/BV1x64y167hh?spm_id_from=333.999.0.0', '1')