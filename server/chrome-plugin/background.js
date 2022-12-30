// 部署后配置默认服务器地址,也可手动设置 修改 "http://127.0.0.1:5000"为默认服务器地址
const default_server = "http://127.0.0.1:5000"

chrome.contextMenus.create({
    title: '识别验证码',
    id: 'recognize_verify_code',
    type: 'normal',
    contexts: ['image']
});

// 兼容MV3
chrome.contextMenus.onClicked.addListener(function (item, tab) {
    if (item.srcUrl.startsWith("data:image/")) {
        console.log("background: 识别data:image/ 大小", item.srcUrl.length)
        handleBase64(item.srcUrl.replaceAll("\n", "").replaceAll("%0D%0A", ""));
    } else {
        if (new URL(item.pageUrl).host === new URL(item.srcUrl).host) {
            console.log("background: 同源url ", item.srcUrl)
            chrome.tabs.sendMessage(tab.id, {"type": "base64", data: item}, function (base64) {
                handleBase64(base64, item.srcUrl);
                console.log(arguments, chrome.runtime.lastError);
            });
        } else {
            console.log("background: 跨域url ", item.srcUrl)
            handleBase64(undefined, item.srcUrl);
        }

    }
});


//background.js添加监听，并把结果反馈给浏览器页面console显示。
chrome.runtime.onMessage.addListener(function (request) {
    console.log(request);
    if (request.startsWith("data:image/")) {
        handleBase64(request);
    } else if (request.startsWith("http")) {
        handleBase64(undefined, request);
    }
});

// 在后台请求没有跨域问题
function handleBase64(base64, url) {
    console.log("handleBase64", base64, url)
    chrome.storage.sync.get({"ocr_server": default_server}, function (config) {
        let ocrServer = config["ocr_server"] || default_server
        if (!ocrServer.includes("http")) {
            toast("错误: 服务设置错误")
            return;
        }

        !base64 && console.log("图片转base64错误,请确认图片是否有跨域限制");

        fetch(ocrServer + "/ocr", {
            "headers": {
                "accept": "application/json, text/javascript, */*; q=0.01",
                "accept-language": "zh-CN,zh;q=0.9",
                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                "x-requested-with": "XMLHttpRequest"
            },
            "body": base64 ? ("base64=" + encodeURIComponent(base64.replace(/.*,/, ""))) : ("url=" + url),
            "method": "POST"
        })
            .then(response => response.json())
            .then(res => {
                console.log(res)
                if (res.status) {
                    copy(res.result, 'text/plain')
                    toast(`验证码: ${res.result} ,如未复制到粘贴板请手动填写`, '成功')
                } else {
                    toast("解析错误: " + res.msg)
                }
            })
            .catch(error => {
                toast('请求失败: ' + error.toString() + "\n请确认设置的服务是否有效!",)
            })
    })
}

function copy(text, mimeType) {
    chrome.tabs.query({currentWindow: true, active: true}, function (tabs) {
        chrome.tabs.sendMessage(tabs[0].id, {
            "type": "copy", data: {text, mimeType}
        }, function () {
            console.log(arguments, chrome.runtime.lastError);
        });
    });
}

function toast(message) {
    chrome.tabs.query({currentWindow: true, active: true}, function (tabs) {
        chrome.tabs.sendMessage(tabs[0].id, {
            "type": "notice", data: {message}
        }, function () {
            console.log(arguments, chrome.runtime.lastError);
        });
    });
}


