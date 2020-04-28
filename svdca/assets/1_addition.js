function showCrawlDetail(){
    let path = sessionStorage.getItem('sessionStore')
    let url = JSON.parse(path)
    let lastId=-2
    let mk = document.getElementById('crawlShow')
    let btn = document.getElementById('crawlBtn')
    let analyseBtn = document.getElementById('analyseBtn')
    btn.disabled = true
    mk.innerHTML=''
    analyseBtn.style.visibility = 'hidden'
    function getData(url){
         fetch(url, {
                method: 'get'
            }).then(res => {
                res.json().then((data) => {
                    handleData(data, mk)
                    if(!data.end){
                        setTimeout(()=>{
                            getData(url)
                        }, 100)
                    } else {
                        btn.disabled = false
                        analyseBtn.style.visibility = 'visible'
                    }

                    return;
                })
            }).catch(e => {
                 console.log(e)
            });
    }
    function handleData(data, mk){
        if((lastId==-2)|| (data.id>lastId)){
            console.log(data)
            lastId = data.id
            let dfElem = document.createDocumentFragment()
            dfElem.appendChild(getStrong(data.status))

            let arr = data.result.filter(item=>item).map(item=>item.replace(/\n/g,' '))
            console.log(arr)
            if(arr.length >0){
                detail = document.createElement('div')
                detail.innerHTML = arr.reduce((acc,cur)=>{
                    return acc+cur+'<br/>'
                }, '')
                dfElem.appendChild(detail)
            }

            if(data.cur > 0){
                dfElem.appendChild(getStrong(`本次爬取${data.cur}个视频`))
            }

            mk.appendChild(dfElem)
        } else if(data.id==-1){
            console.log(data)
            mk.appendChild(getStrong(data.status))
        }
        mk.scrollTop = mk.scrollHeight;
    }
    function getStrong(text){
        let strong = document.createElement('strong')
        strong.innerHTML = text+'<br/>'
        return strong
    }
    getData(url)
}

function showSimilarDetail(task_id) {
    console.log('taskid', task_id)
    let url = `/similar_status/${task_id}`
    function getData(){
        fetch(url, {
                method: 'get'
            }).then(res => {
                res.json().then((data) => {
                    console.log(data)
                    if(!data.end){
                        setTimeout(()=>{
                            getData()
                        }, 100)
                    } else {

                    }
                })
            }).catch(e => {
                 console.log(e)
            });
    }
    getData()
}

function addSimilarEvent(name='similarPanel_content'){
    console.log('添加监听器o', name)

    setTimeout(()=>{
        let el = document.getElementById(name)
        console.log('元素', el)
        el.onclick=function(e){
            console.log('监听', e)
            let target_el = e.path[1]
            console.log(target_el)
            let name = target_el.dataset.nickname
            let input_el = document.getElementById('analyseInput')
            let btn_el = document.getElementById('startAnalyse')
            input_el.value = name
            input_el.setAttribute('value', name)
            btn_el.click()
       }
    }, 1000)

}

window.addEventListener('load', function(){
    let path = sessionStorage.getItem('sessionStore')
    if(path){
        setTimeout(()=>{

            let url = JSON.parse(path)
            fetch(url, {
                        method: 'get'
                    }).then(res => {
                        res.json().then((data) => {
                            let showPanel = document.getElementById('showPanel')
                            let info_crawl = document.getElementById('info_crawl')
                            console.log('请求有效', data)
                            showPanel.style.display = ''
                            info_crawl.style.display = 'none'
                            let crawlingP = document.getElementById('crawlingP')
                            let analyseBtn = document.getElementById('analyseBtn')
                            params = getAllUrlParams(location.href)
                            crawlingP.innerText = '上次爬取任务～'+data.nickname
                            analyseBtn.setAttribute('href', '/analysing?uid='+params.uid)
                            showCrawlDetail()
                        })
                    }).catch(e => {
                         console.log('请求无效',e)
                    });
        }, 1000)
    }

})

function getAllUrlParams(url) {
    // 用JS拿到URL，如果函数接收了URL，那就用函数的参数。如果没传参，就使用当前页面的URL
    var queryString = url ? url.split('?')[1] : window.location.search.slice(1);
    // 用来存储我们所有的参数
    var obj = {};
    // 如果没有传参，返回一个空对象
    if (!queryString) {
        return obj;
    }
    // stuff after # is not part of query string, so get rid of it
    queryString = queryString.split('#')[0];
    // 将参数分成数组
    var arr = queryString.split('&');
    for (var i = 0; i < arr.length; i++) {
        // 分离成key:value的形式
        var a = arr[i].split('=');
        // 将undefined标记为true
        var paramName = a[0];
        var paramValue = typeof (a[1]) === 'undefined' ? true : a[1];
        // 如果调用对象时要求大小写区分，可删除这两行代码
        paramName = paramName.toLowerCase();
        if (typeof paramValue === 'string') paramValue = paramValue.toLowerCase();
        // 如果paramName以方括号结束, e.g. colors[] or colors[2]
        if (paramName.match(/\[(\d+)?\]$/)) {
            // 如果paramName不存在，则创建key
            var key = paramName.replace(/\[(\d+)?\]/, '');
            if (!obj[key]) obj[key] = [];
            // 如果是索引数组 e.g. colors[2]
            if (paramName.match(/\[\d+\]$/)) {
                // 获取索引值并在对应的位置添加值
                var index = /\[(\d+)\]/.exec(paramName)[1];
                obj[key][index] = paramValue;
            } else {
                // 如果是其它的类型，也放到数组中
                obj[key].push(paramValue);
            }
        } else {
            // 处理字符串类型
            if (!obj[paramName]) {
                // 如果如果paramName不存在，则创建对象的属性
                obj[paramName] = paramValue;
            } else if (obj[paramName] && typeof obj[paramName] === 'string') {
                // 如果属性存在，并且是个字符串，那么就转换为数组
                obj[paramName] = [obj[paramName]];
                obj[paramName].push(paramValue);
            } else {
                // 如果是其它的类型，还是往数组里丢
                obj[paramName].push(paramValue);
            }
        }
    }
    return obj;
}