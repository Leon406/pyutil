function save_options() {
    let ele = document.getElementById("ocrServerUrl");
    let hint = "保存成功!";
    if (ele.value.includes("http")) {
        chrome.storage.sync.set({"ocr_server": ele.value});
    } else {
        chrome.storage.sync.set({"ocr_server": ""});
        hint = "服务地址错误!!!";
    }
    // Update status to let user know options were saved.
    let status = document.getElementById("status");
    status.innerHTML = hint;
    setTimeout(function () {
        status.innerHTML = "";
    }, 750);
}

function restore_options() {
    document.getElementById("btn").addEventListener('click', save_options);
    let ele = document.getElementById("ocrServerUrl");
    chrome.storage.sync.get({"ocr_server": ""}, function (config) {
        let server = config.ocr_server
        if (!server) {
            return;
        }
        ele.value = server
    })

    let checkbox = document.getElementById("copy_uri_reco");
    chrome.storage.sync.get({"copy_reco": false}, function (config) {
        checkbox.checked = config.copy_reco
        checkbox.addEventListener('change', function (state) {
            chrome.storage.sync.set({"copy_reco": checkbox.checked})
        })
    })
}

window.addEventListener('load', restore_options)

//监听整个页面的 paste 事件
document.addEventListener('paste', function (e) {
    let clipboardData = e.clipboardData || window.clipboardData;
    let type = clipboardData.items[0].type;
    if (!clipboardData) return;

    if (type.match(/image/)) {
        let blob = clipboardData.items[0].getAsFile();
        let file = new FileReader();
        file.addEventListener('loadend', function (e) {
            chrome.runtime.sendMessage(e.target.result);
        });
        file.readAsDataURL(blob);
    }
})
