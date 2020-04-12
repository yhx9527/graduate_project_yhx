function showCrawlDetail(){
    path = sessionStorage.getItem('sessionStore')
    url = JSON.parse(path)
    lastId=-2
    mk = document.getElementById('crawlShow')
    btn = document.getElementById('crawlBtn')
    analyseBtn = document.getElementById('analyseBtn')
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
            dfElem = document.createDocumentFragment()
            dfElem.appendChild(getStrong(data.status))

            arr = data.result.filter(item=>item).map(item=>item.replace(/\n/g,' '))
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
        strong = document.createElement('strong')
        strong.innerHTML = text+'<br/>'
        return strong
    }
    getData(url)
}

function showSimilarDetail(task_id) {
    console.log('taskid', task_id)
    url = `/similar_status/${task_id}`
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