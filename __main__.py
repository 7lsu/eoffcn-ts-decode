import re
import os
import sys
import json
import glob
import requests as req
import execjs
import threading
import queue
import time


class myThread (threading.Thread):
    def __init__(self, threadID, q):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.q = q

    def run(self):
        print("开启线程： " + self.threadID)
        process_data(self.q)


def process_data(q):
    while not exitFlag:
        queueLock.acquire()
        if not workQueue.empty():
            data = q.get()
            queueLock.release()
            download_and_decode(data['path'], data['mda'])
        else:
            queueLock.release()
        time.sleep(0.1)


def getmidstring(html, start_str, end):
    start = html.find(start_str)
    if start >= 0:
        start += len(start_str)
        end = html.find(end, start)
        if end >= 0:
            return html[start:end].strip()


def mkdir(path):
    import os
    path = path.strip()
    path = path.rstrip("\\")
    isExists = os.path.exists(path)
    if not isExists:
        os.makedirs(path)
        return True
    else:
        return False


def files(curr_dir='.', ext='*.exe'):
    for i in glob.glob(os.path.join(curr_dir, ext)):
        yield i


def remove_files(rootdir, ext, show=False):
    for i in files(rootdir, ext):
        if show:
            print(i)
        os.remove(i)


def download_and_decode(path, mda):
    path = path.replace('>', '')
    path = path.replace('  ', '_')
    mkdir('.' + path)
    print(path)
    if os.path.exists('.' + path + '/output.mp4') == False:
        if mda != '':
            video_url = 'https://gcik47gyt746q6nqdze.exp.bcevod.com/' + mda + '/' + mda + '.m3u8'
            # video_url = 'https://gcik47gyt746q6nqdze.exp.bcevod.com/' + mda + '/src/src-' + mda + '.mp4'
            print(video_url)
            r = req.get(video_url)
            if r.status_code == 200:
                url = 'https://drm.media.baidubce.com/v1/encryptedVideoKey?videoKeyId=' + mda + '&playerId=pid-1-5-1'
                j4 = req.get(url, headers=headers).json()
                vi = getmidstring(r.text, 'IV=', ',K')
                key = j4.get('encryptedVideoKey', None)
                data = '#EXTM3U\n#EXT-X-VERSION:3\n#EXT-X-TARGETDURATION:37\n'
                if key != None:
                    js = execjs.compile(open('main.js', 'r', encoding='utf8').read())
                    key = js.call('decrypt', key)
                    f = open('.' + path + '/k.key', 'w')
                    f.write(key)
                    f.close()
                    data += '#EXT-X-KEY:METHOD=AES-128,URI="' + (sys.path[0]).replace('\\', '/') + path + '/k.key",IV=' + vi + '\n'
                for m in re.findall('.\d{1,3}.ts', r.text, re.S):
                    r = req.get(video_url + m)
                    with open('.' + path + '/' + mda + '.m3u8' + m, 'wb') as c:
                        print(mda + '.m3u8' + m)
                        c.write(r.content)
                    data += '#EXTINF:0,\n' + (sys.path[0]).replace('\\', '/') + path + '/' + mda + '.m3u8' + m + '\n'
                data += '#EXT-X-ENDLIST'
                f = open('.' + path + '/index.m3u8', 'w')
                f.write(data)
                f.close()
                p = 'ffmpeg -allowed_extensions ALL -protocol_whitelist "file,http,crypto,tcp" -i ' + \
                    (sys.path[0]).replace('\\', '/') + path + '/index.m3u8 -c copy ' + (sys.path[0]).replace('\\', '/') + path + '/output.mp4'
                # queueLock.acquire()
                os.system(p)
                # queueLock.release()
                remove_files('.' + path, '*.ts')
                remove_files('.' + path, '*.key')
                remove_files('.' + path, '*.m3u8')


queueLock = threading.Lock()
exitFlag = 0
workQueue = queue.Queue(10)

for i in range(10):
    thread = myThread(str(i), workQueue)
    thread.start()

headers = {
    'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_1_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.1 Mobile/15E148 Safari/604.1',
    'cookie': ''
}

r = req.get('http://xue.eoffcn.com/api/new/goods/list', headers=headers)

j = r.json()

if j['code'] != 0:
    headers['cookie'] = str(input('需要更新cookie:'))

for i in j['data']:
    print(i['name'])
    order_num = i['system_order_num']
    j1 = req.get('http://xue.eoffcn.com/api/new/course/list?system_order=' + order_num, headers=headers).json()
    # print(j1)
    for i1 in j1['data']:
        for i2 in i1['list']:
            cid = i2['coding']
            j2 = req.get('http://xue.eoffcn.com/api/package/list?system_order=' + order_num + '&coding=' + cid, headers=headers).json()
            for i3 in j2['data']:
                pid = str(i3['id'])
                j3 = req.get('http://xue.eoffcn.com/api/course/production/catagory/' + pid + '?packageid=' + pid, headers=headers).json()
                for i4 in j3['data']['outline_info']:
                    for i5 in i4['child']:
                        if i5.get('child', None) != None:
                            for i6 in i5['child']:
                                if i6.get('child', None) != None:
                                    for i7 in i6['child']:
                                        print('[*7]' + str(i7))
                                        mda = i7.get('data_path', None)
                                        if mda != None:
                                            path = '/' + i['name'] + '/' + i1['name'] + '/' + i2['name'] + '/' + i3['name'] + '/' + i4['name'] + '/' + i5['name'] + '/' + i6['name'] + '/' + i7['name']
                                            #download_and_decode(path, mda)
                                            workQueue.put({'path': path, 'mda': mda})
                                else:
                                    print('[*6]' + str(i6))
                                    mda = i6.get('data_path', None)
                                    if mda != None:
                                        path = '/' + i['name'] + '/' + i1['name'] + '/' + i2['name'] + '/' + i3['name'] + '/' + i4['name'] + '/' + i5['name'] + '/' + i6['name']
                                        #download_and_decode(path, mda)
                                        workQueue.put({'path': path, 'mda': mda})
                        else:
                            print('[*5]' + str(i5))
                            mda = i5.get('data_path', None)
                            if mda != None:
                                path = '/' + i['name'] + '/' + i1['name'] + '/' + i2['name'] + '/' + i3['name'] + '/' + i4['name'] + '/' + i5['name']
                                #download_and_decode(path, mda)
                                workQueue.put({'path': path, 'mda': mda})

# http://xue.eoffcn.com/api/new/goods/list
# http://xue.eoffcn.com/api/new/course/list?system_order={system_order}
# http://xue.eoffcn.com/api/package/list?system_order={system_order}&coding={coding}
# http://xue.eoffcn.com/api/course/production/catagory/{packageid}?packageid={packageid}
# http://xue.eoffcn.com/api/course/production/lesson/info?lesson_id={lesson_id}&package_id={packageid}
