import requests
from hyper import HTTPConnection, tls

headers={
        ":authority": "api.amemv.com",
        "cookie": "install_id=104243110108, ttreq=1$0982c95be39210c4cedda04ccd70095de17c7de9, d_ticket=91c7682f2d9cc9bd821075f286b97c9ecb138, odin_tt=a7056720e8585b5dcc7c9bf3aed08349078974999caa4844ca9881e7225ddde80516c82854a8f5095d66d36308d5858a, sid_guard=846d26a0aed08ec2496c90e73a227d66%7C1582358865%7C5184000%7CWed%2C+22-Apr-2020+08%3A07%3A45+GMT, uid_tt=c3d97367d0d47449cbf301f7e5e0a8e9, sid_tt=846d26a0aed08ec2496c90e73a227d66, sessionid=846d26a0aed08ec2496c90e73a227d66",
        "accept-encoding": "gzip",
        "x-ss-req-ticket": "1582358887070",
        "x-tt-token": "00846d26a0aed08ec2496c90e73a227d663fc8db9044e03eff2b8d105d0a250f6b05505d72588779153e7b025fec6b029c41",
        "sdk-version": "1",
        "x-ss-tc": "0",
        "user-agent": "com.ss.android.ugc.aweme/400 (Linux; U; Android 8.0.0; zh_CN; EVA-AL10; Build/HUAWEIEVA-AL10; Cronet/58.0.2991.0)",
        "x-khronos": "1582358887",
        "x-gorgon": "0192cb7ea5883f4b2021f11674d12a3162e6870a7a457100d2",
        "x-pods": ""
    }

# url="/aweme/v1/user/?user_id=71912868448&retry_type=no_retry&mcc_mnc=46003&iid=104243110108&device_id=61908178454&ac=wifi&channel=wandoujia_aweme&aid=1128&app_name=aweme&version_code=400&version_name=4.0.0&device_platform=android&ssmix=a&device_type=EVA-AL10&device_brand=HUAWEI&language=zh&os_api=26&os_version=8.0.0&uuid=861533036745840&openudid=0f772e0fa9d36257&manifest_version_code=400&resolution=1080*1792&dpi=480&update_version_code=4002&_rticket=1582295017514&ts=1582295016&js_sdk_version=1.6.4&as=a1354ea4083e8e67cf0677&cp=eeede6568bf84f7fe1Wo_w&mas=0175542def29312fc1860a1de9f3ed4088ecec6c0c66c6ec6ca61c"
# response = requests.get(url, headers=headers).text
# url="/aweme/v2/comment/list/?aweme_id=6786492441756257536&cursor=0&count=20&ts=1582295195&js_sdk_version=1.6.4&app_type=normal&manifest_version_code=400&_rticket=1582295195798&ac=wifi&device_id=61908178454&iid=104243110108&mcc_mnc=46003&os_version=8.0.0&channel=wandoujia_aweme&version_code=400&device_type=EVA-AL10&language=zh&uuid=861533036745840&resolution=1080*1792&openudid=0f772e0fa9d36257&update_version_code=4002&app_name=aweme&version_name=4.0.0&os_api=26&device_brand=HUAWEI&ssmix=a&device_platform=android&dpi=480&aid=1128&as=a175de84ebd93e585f0266&cp=eb9feb59b8fb458be1KmSq&mas=01a125260b232b9e3bb3af6c498847a5106c6c4c0c66ac1caca6cc"
# url="/aweme/v1/general/search/single/?keyword=%E5%A4%A7%E7%8B%BC%E7%8B%97%E9%83%91%E5%BB%BA%E9%B9%8F%E5%A4%AB%E5%A6%87&offset=0&count=10&is_pull_refresh=0&hot_search=0&latitude=24.352902&longitude=118.033784&ts=1582334159&js_sdk_version=1.6.4&app_type=normal&manifest_version_code=400&_rticket=1582334160365&ac=wifi&device_id=61908178454&iid=104243110108&mcc_mnc=46003&os_version=8.0.0&channel=wandoujia_aweme&version_code=400&device_type=EVA-AL10&language=zh&uuid=861533036745840&resolution=1080*1792&openudid=0f772e0fa9d36257&update_version_code=4002&app_name=aweme&version_name=4.0.0&os_api=26&device_brand=HUAWEI&ssmix=a&device_platform=android&dpi=480&aid=1128&as=a19518258fdc0e00d00266&cp=8bcced51fd005701e1KmSq&mas=011645234873c6a138cb1ee205243d7f386c6c4c0c0c260c0ca60c"
url="/aweme/v1/general/search/single/?keyword=%E5%A4%A7%E7%8B%BC%E7%8B%97%E9%83%91%E5%BB%BA%E9%B9%8F%E5%A4%AB%E5%A6%87&offset=0&count=10&is_pull_refresh=0&hot_search=0&latitude=24.352849&longitude=118.033782&ts=1582358886&js_sdk_version=1.6.4&app_type=normal&manifest_version_code=400&_rticket=1582358887072&ac=wifi&device_id=61908178454&iid=104243110108&mcc_mnc=46003&os_version=8.0.0&channel=wandoujia_aweme&version_code=400&device_type=EVA-AL10&language=zh&uuid=861533036745840&resolution=1080*1792&openudid=0f772e0fa9d36257&update_version_code=4002&app_name=aweme&version_name=4.0.0&os_api=26&device_brand=HUAWEI&ssmix=a&device_platform=android&dpi=480&aid=1128&as=a115ee7596b6deb1800655&cp=ee66ea5a6309571de1[mIq&mas=0139aecceef69eb8f522479b562ffa1773acac6c0c0c1c8c46a626"

c = HTTPConnection('api.amemv.com:443')
c.request('GET', url, headers=headers)

response = c.get_response()
print(response.read())
