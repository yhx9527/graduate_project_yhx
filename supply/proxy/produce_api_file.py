import json
from os import path, mkdir
import sys
import re

def response(flow):
    global index
    try:
        domin = re.search(r'\/\/(.*)\?', flow.request.url)
        if not domin:
            domin=flow.request.url
        else:
            domin=domin.group(1)
        temp = domin.lower().split('/')
        api = {
            'name': '#{}'.format('#'.join(temp)),
            'url': flow.request.url,
            'query': dict(flow.request.query),
            'headers': dict(flow.request.headers),
            'content': dict(flow.request.content),
            'text': json.loads(flow.response.text)
        }
        targetDir = path.join(sys.path[0], 'douyin_analyse')

        if not path.isdir(targetDir):
            mkdir(targetDir)
        filename=path.join(targetDir, api['name']+'1.json')
        print(filename)
        with open(filename, "w") as f:
            f.write(json.dumps(api, indent=4, ensure_ascii=False))
            print(api['name']+ "文件载入完成...")
    except Exception as e:
        print(e)