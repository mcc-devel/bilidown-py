from bs4 import BeautifulSoup
import requests

def down(lnk):
    headers = {
        'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4642.0 Safari/537.36 Edg/96.0.1025.0',
        'Host':'upos-sz-mirrorcos.bilivideo.com',
        'Connection':'keep-alive',
        'Origin':'https://www.bilibili.com',
        'Accept':'*/*',
        'Sec-Fetch-Dest':'empty',
        'Sec-Fetch-Mode':'cors',
        'Referer':lnk,
        'Accept-Encoding':'identity',
        'Accept-Language':'zh-CH,zh;q=0.9'
    }
    lnk = lnk.replace('www.bilibili.com', 'www.ibilibili.com')
    res = requests.get(lnk).text
    bs = BeautifulSoup(res, features = 'html.parser')
    name = bs.find('h4').text
    lst = bs.find_all('input')
    aid = lst[0]['value']
    cid = lst[1]['value']
    session = requests.session()
    final = requests.get('https://api.bilibili.com/x/player/playurl?avid=%s&cid=%s&qn=1&type=&otype=json&platform=html5&high_quality=1'%(aid, cid)).json()['data']['durl'][0]['url'].replace(r'\u0026', '&')
    data = session.get(final, headers = headers).content
    with open('%s.mp4'%(name), 'wb') as f:
        f.write(data)

down('https://www.bilibili.com/video/BV1x64y167hh?spm_id_from=333.999.0.0')