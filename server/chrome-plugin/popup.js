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
    let ele = document.getElementById("ocrServerUrl");
    chrome.storage.sync.get({"ocr_server": ""})
        .then(config => {
            let server = config.ocr_server
            if (!server) {
                return;
            }
            ele.value = server
        })

    let ele_rule = document.getElementById("rule");
    chrome.storage.sync.get({"rule": ""})
        .then(config => {
            ele_rule.value = config.rule
        })

    ele_click("btn", save_server_config)
    ele_click("btn_rule", save_rule)
    ele_click("btn_cookie", () => {
        sendMessage({"type": "copy_cookie"});
    });
    ele_click("btn_remove_restrict", () => {
        sendMessage({"type": "remove_restrict"});
    });
    ele_click("btn_free_edit", () => {
        sendMessage({"type": "free_edit"});
    });

    add_check_box_listener("reco_on_load", "reco_on_load")
    add_check_box_listener("debug", "debug", true)
    add_check_box_listener("copy_uri_reco", "copy_reco")
}

function add_check_box_listener(id, prop, is_send = false) {
    prop = prop || id
    let cb = document.getElementById(id);
    let dict = {}
    dict[prop] = false
    chrome.storage.sync.get(dict)
        .then(config => {
            cb.checked = config[prop]
            cb.addEventListener('change', () => {
                console.log("___ listenr", prop, cb.checked);
                dict[prop] = cb.checked
                chrome.storage.sync.set(dict)
                is_send && sendMessage({"type": prop, data: cb.checked});
            })
        })
}

function ele_click(id, callback) {
    document.getElementById(id).addEventListener('click', callback)
}

window.addEventListener('load', restore_options)

//监听整个页面的 paste 事件
document.addEventListener('paste', e => {
    let clipboardData = window.clipboardData || e.clipboardData;
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
