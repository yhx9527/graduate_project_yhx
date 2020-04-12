import pandas as pd
import json
import os
import sys

def getCityGeo():
    target = os.path.join(sys.path[0], 'geojson-map-china/geometryProvince')
    filelist = os.listdir(target)
    result = []
    print('文件列表数量', len(filelist))
    for file in filelist:
        print('正在处理文件', file)
        with open(os.path.join(target,file), 'r') as f:
            data = f.read()
            obj = json.loads(data)
            for feature in obj.get('features'):
                print(feature['properties'])
                name = feature['properties']['name']
                cp = feature['properties'].get('cp', obj.get('cp'))
                area = dict(city=name,
                            lon=cp[0],
                            lat=cp[1])
                result.append(area)

    df = pd.DataFrame(result)
    print('生成df',df)
    print('正在存储csv...')
    df.to_csv(os.path.join(sys.path[0], 'city_geo.csv'))
    print('存储完成')


if __name__ == '__main__':
    getCityGeo()


