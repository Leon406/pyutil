// 监听 background 传来的数据 可对页面dom操作
chrome.runtime.onMessage.addListener((data, sender, sendResponse) => {
    console.log("data", data);
    sendResponse(drawBase64Image(getImg(data.srcUrl)))
});

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


//监听整个页面的 paste 事件
document.addEventListener('paste', function (e) {
    let clipboardData = e.clipboardData || window.clipboardData;
    if (!clipboardData) return;
    let type = clipboardData.items[0] && clipboardData.items[0].type;
    if (type && type.match(/image/)) {
        let blob = clipboardData.items[0].getAsFile();
        let file = new FileReader();
        file.addEventListener('loadend', function (e) {
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
            let clipboardData = e.clipboardData || window.clipboardData;
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
