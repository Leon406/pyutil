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
    setTimeout(() => {
        status.innerHTML = "";
    }, 750);
}

function sendMessage(data) {
    chrome.tabs.query({currentWindow: true, active: true}, (tabs) => {
        chrome.tabs.sendMessage(tabs[0].id, data, () => {
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
    setTimeout(() => {
        status.innerHTML = "";
    }, 750);
}

function restore_options() {
    document.getElementById("btn").addEventListener('click', save_server_config);
    let ele = document.getElementById("ocrServerUrl");
    chrome.storage.sync.get({"ocr_server": ""}, config => {
        let server = config.ocr_server
        if (!server) {
            return;
        }
        ele.value = server
    })

    let ele_rule = document.getElementById("rule");
    chrome.storage.sync.get({"rule": ""}, config => {
        ele_rule.value = config.rule
    })
    document.getElementById("btn_rule").addEventListener('click', save_rule);

    document.getElementById("btn_cookie").addEventListener('click', () => {
        sendMessage({"type": "copy_cookie"});
    });
    document.getElementById("btn_remove_restrict").addEventListener('click', () => {
        sendMessage({"type": "remove_restrict"});
    });
    document.getElementById("btn_free_edit").addEventListener('click', () => {
        sendMessage({"type": "free_edit"});
    });


    let checkbox = document.getElementById("copy_uri_reco");
    chrome.storage.sync.get({"copy_reco": false}, config => {
        checkbox.checked = config.copy_reco
        checkbox.addEventListener('change', (state) => {
            chrome.storage.sync.set({"copy_reco": checkbox.checked})
        })
    })

    let checkbox_debug = document.getElementById("debug");
    chrome.storage.sync.get({"debug": false}, config => {
        checkbox_debug.checked = config.debug
        checkbox_debug.addEventListener('change', () => {
            chrome.storage.sync.set({"debug": checkbox_debug.checked})
            sendMessage({"type": "debug", data: checkbox_debug.checked});
        })
    })
}

window.addEventListener('load', restore_options)

//监听整个页面的 paste 事件
document.addEventListener('paste', e => {
    let clipboardData = e.clipboardData || window.clipboardData;
    let type = clipboardData.items[0].type;
    if (!clipboardData) return;

    if (type.match(/image/)) {
        let blob = clipboardData.items[0].getAsFile();
        let file = new FileReader();
        file.addEventListener('loadend', e => {
            chrome.runtime.sendMessage(e.target.result);
        });
        file.readAsDataURL(blob);
    }
})
