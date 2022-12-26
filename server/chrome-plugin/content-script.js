// 监听 background 传来的数据 可对页面dom操作
chrome.runtime.onMessage.addListener((data, sender, sendResponse) => {
    console.log("receive from background: ", data);
    if (data.type === "copy") {
        copy(data.data.text, data.data.mimeType)
    } else if (data.type === "notice") {
        toast(data.data.message)
    } else if (data.type === "base64") {
        sendResponse(drawBase64Image(getImg(data.data.srcUrl)));
    }
});

function copy(str, mimeType) {
    document.oncopy = function (event) {
        event.clipboardData.setData(mimeType, str);
        event.preventDefault();
    };
    document.execCommand("copy", false, str);
}

function toast(msg, duration) {
    duration = isNaN(duration) ? 2000 : duration;
    let m = document.createElement('div');
    m.innerHTML = msg;
    m.style.cssText = "width: 40%;min-width: 150px;opacity: 0.7;height: 30px;color: rgb(255, 255, 255);line-height: 30px;text-align: center;border-radius: 5px;position: fixed;top: 5%;left: 30%;z-index: 999999;background: rgb(0, 0, 0);font-size: 12px;";
    document.body.appendChild(m);
    setTimeout(function () {
        var d = 0.5;
        m.style.webkitTransition = '-webkit-transform ' + d + 's ease-in, opacity ' + d + 's ease-in';
        m.style.opacity = '0';
        setTimeout(function () {
            document.body.removeChild(m)
        }, d * 1000);
    }, duration);
}


function getImg(url) {
    return Array.from(document.getElementsByTagName("img")).filter(el => el.src.includes(url))[0];
}

function drawBase64Image(img) {
    console.log("drawBase64Image", img)
    let canvas = document.createElement('canvas');
    canvas.width = img.width;
    canvas.height = img.height;
    let ctx = canvas.getContext('2d');
    ctx.drawImage(img, 0, 0, img.width, img.height);
    let dataURL;
    try {
        dataURL = canvas.toDataURL('image/');
        console.log("dataURL", dataURL)
    } catch (e) {
        console.info(e);
    }
    return dataURL;
}


//监听整个页面的 paste 事件, chrome只能监听文本
document.addEventListener('paste', function (e) {
    let clipboardData = window.clipboardData || e.clipboardData;
    if (!clipboardData) return;
    let type = clipboardData.items[0] && clipboardData.items[0].type;
    if (type && type.match(/image/)) {
        let blob = clipboardData.items[0].getAsFile();
        let file = new FileReader();
        file.addEventListener('loadend', function (e) {
            console.log("paste data", e.target.result)
            chrome.runtime.sendMessage(e.target.result);
        });
        file.readAsDataURL(blob);
    }
})

const image_url_reg = /https?:\/\/.*\.(png|jpg|jpeg)\b.*/ig
//监听整个页面的 copy 事件,只能监听文本,图片链接
document.addEventListener('copy', function (e) {
    chrome.storage.sync.get({"copy_reco": false}, function (config) {
        if (config.copy_reco) {
            let clipboardData = window.clipboardData || e.clipboardData;
            if (!clipboardData) return;
            let text = window.getSelection().toString();
            if (text) {
                console.info("copy text", text)
                if (text.startsWith("data:image") || image_url_reg.test(text)) {
                    chrome.runtime.sendMessage(text);
                }
            }
        }
    })
})
