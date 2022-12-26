function save_server_config() {
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

function sendMessage(data) {
    chrome.tabs.query({currentWindow: true, active: true}, function (tabs) {
        chrome.tabs.sendMessage(tabs[0].id, data, function () {
            console.log(arguments, chrome.runtime.lastError);
        });
    });
}
function save_rule() {
    let ele = document.getElementById("rule");
    let hint = "保存规则成功!";
    chrome.storage.sync.set({"rule": ele.value});

    sendMessage({"type": "rule", data: ele.value});
    // Update status to let user know options were saved.
    let status = document.getElementById("status");
    status.innerHTML = hint;
    setTimeout(function () {
        status.innerHTML = "";
    }, 750);
}
function restore_options() {
    document.getElementById("btn").addEventListener('click', save_server_config);
    let ele = document.getElementById("ocrServerUrl");
    chrome.storage.sync.get({"ocr_server": ""}, function (config) {
        let server = config.ocr_server
        if (!server) {
            return;
        }
        ele.value = server
    })

    let ele_rule = document.getElementById("rule");
    chrome.storage.sync.get({"rule": ""}, function (config) {
        ele_rule.value = config.rule
    })
    document.getElementById("btn_rule").addEventListener('click', save_rule);


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
