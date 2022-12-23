
chrome.contextMenus.create({
    title: '识别验证码',
    id: 'search',
    type: 'normal',
    contexts: ['image'],
    onclick: function (item, tab) {
        chrome.tabs.sendMessage(tab.id, item, function (base64) {
            handleBase64(base64);
            console.log(arguments, chrome.runtime.lastError);
        });
    }
});


function handleBase64(base64) {
    console.log("handleBase64", base64)
    //todo 部署后配置默认服务器地址,也可手动设置 修改 "http://127.0.0.1:5000"为默认服务器地址
    let ocrServer = localStorage["ocr_server"] ? localStorage["ocr_server"] : "http://127.0.0.1:5000";
    console.log("server", ocrServer)
    if (!ocrServer.includes("http")) {
        notification("服务设置错误", '错误')
        return;
    }
    if (!base64) {
        notification("图片转base64错误,请确认图片是否有跨域限制", '失败')
        return;
    }
    return fetch(ocrServer + "/ocr", {
        "headers": {
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-language": "zh-CN,zh;q=0.9",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "x-requested-with": "XMLHttpRequest"
        },
        "body": "base64=" + encodeURIComponent(base64),
        "method": "POST"
    })

    .then(response => response.json())
    .then(res => {
        console.log(res)
        if (res.status) {
            copy(res.result, 'text/plain')
            notification(`验证码: ${res.result} ,如未复制到粘贴板请手动填写`, '成功')
        } else {
            notification(res.msg, '失败')
        }
    })
    .catch(error => {
        notification(error, '失败')
    })
}

function copy(str, mimeType) {
    document.oncopy = function (event) {
        event.clipboardData.setData(mimeType, str);
        event.preventDefault();
    };
    document.execCommand("copy", false, null);
}

function notification(message, title = '') {
    chrome.notifications.create(null, {
        type: 'basic',
        title,
        message,
        // contextMessage: '',
        iconUrl: 'icon48.png',
    })
}


//background.js添加监听，并把结果反馈给浏览器页面console显示。
chrome.runtime.onMessage.addListener(function(request,sender,callback){
	console.log(request);
    if(request.startsWith("data:image/")) {
		handleBase64(request);
	}
});
