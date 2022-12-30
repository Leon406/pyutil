let delay = 200
let last_time = 0
const INTERVAL = 2000
let DEBUG = false

// 监听 background 传来的数据 可对页面dom操作
chrome.runtime.onMessage.addListener((data, sender, sendResponse) => {
    DEBUG && console.log("receive from background: ", data);

    switch (data.type) {
        case "copy":
            copy(data.data.text, data.data.mimeType)
            break;
        case "debug":
            DEBUG = data.data
            break;
        case "notice":
            toast(data.data.message)
            break;
        case "base64":
            let img = getImg(data.data.srcUrl) || getImgFromIFrame(data.data.srcUrl);
            // 限制验证码图片高度, 防止滥用
            if (img.height > 200) {
                toast("你确定这是验证码?")
            } else {
                sendResponse(drawBase64Image(img));
            }
            break;
        case "rule":
            parse_config(data.data)
            break;
        case "free_edit":
            free_edit()
            break;
        case "copy_cookie":
            copy_cookie()
            break;
        case "remove_restrict":
            remove_restrict()
            break;
        default:
            console.log("error type")
    }
});


chrome.storage.sync.get({"rule": ""}, config => {
    parse_config(config.rule)
})

function img_click(event) {
    let now = Date.now();
    if (now - last_time < INTERVAL) {
        toast("请勿频繁点击", 1500)
        return
    }
    last_time = now;
    DEBUG && console.log("img click", event.path[0], delay)
    // 等待页面刷新后再转base64,否者会白屏
    setTimeout(() => {
        chrome.runtime.sendMessage(drawBase64Image(event.path[0]));
    }, delay)

}

function copy(str, mimeType) {
    let config = fill_config[location.host];
    // 无内容适当调整延迟
    if (!str) {
        delay = Math.min(delay * 1.2, 2000)
    }
    if (config) {
        let ele = find_element(config.selector, config.index)
        if (ele) {
            ele.value = str
            // vue 双向绑定更新数据
            ele.dispatchEvent(new Event("input"))
        }
    } else {
        auto_detect_and_fill(str)
    }
    document.oncopy = function (event) {
        event.clipboardData.setData(mimeType, str);
        event.preventDefault();
    };
    document.execCommand("copy", false, str);
}

function auto_detect_and_fill(code) {
    let verification_code_ele = Array.from(document.getElementsByTagName("input")).filter(el =>
            el.type !== 'hidden' && (
                find_attribute(el, "data-msg-required")
                || find_attribute(el)
                || find_attribute(el, "tip")
                || find_attribute(el, "id", "verify")
                || find_attribute(el, "id", "validate")
                || find_attribute(el, "alt", "kaptcha")
            )
    )[0];
    if (verification_code_ele) {
        verification_code_ele.value = code
        // vue 双向绑定更新数据
        verification_code_ele.dispatchEvent(new Event("input"))
        window.setTimeout(() => {
            verification_code_ele.focus()
        }, 200);
    }
}


// 获取placeholder="验证码" ,  alt="kaptcha"
function find_attribute(element, attr = "placeholder", val = "验证码", eq = false) {
    let elementKeys = element.attributes;
    if (elementKeys == null) {
        return false;
    }
    for (let i = 0; i < elementKeys.length; i++) {
        let key = elementKeys[i].name.toLowerCase();
        if (typeof val === "string") {
            if (key === attr && (eq ? elementKeys[attr].value === val : elementKeys[attr].value.includes(val))) {
                return true;
            }
        } else {
            if (key === attr && (eq ? val.test(elementKeys[attr].value) : val.exec(elementKeys[attr].value))) {
                return true;
            }
            val.exec()
        }
    }
    return false;
}


let exist_toast

function toast(msg, duration) {
    if (exist_toast) {
        document.body.removeChild(exist_toast)
    }
    duration = isNaN(duration) ? 2000 : duration;
    let m = document.createElement('div');
    exist_toast = m
    m.innerHTML = msg;
    m.style.cssText = "width: 40%;min-width: 150px;opacity: 0.7;height: 30px;color: rgb(255, 255, 255);line-height: 30px;text-align: center;border-radius: 5px;position: fixed;top: 5%;left: 30%;z-index: 999999;background: rgb(0, 0, 0);font-size: 12px;";
    document.body.appendChild(m);
    setTimeout(() => {
        var d = 0.5;
        m.style.webkitTransition = '-webkit-transform ' + d + 's ease-in, opacity ' + d + 's ease-in';
        m.style.opacity = '0';
        setTimeout(() => {
            try {
                document.body.removeChild(m)
            } catch (e) {
                DEBUG && console.error("remove ", e)
            }

            exist_toast = null
        }, d * 1000);
    }, duration);
}


function getImgFromIFrame(url) {
    let elements = Array.from(document.querySelectorAll("iframe"))
        .map(el => getImg(url, el.contentDocument))
        .filter(el => el);
    return elements && elements[0];
}

function getImg(url, doc = document) {
    let elements = Array.from(doc.getElementsByTagName("img")).filter(el => el.src.includes(url));
    return elements && elements[0];
}

function drawBase64Image(img) {
    DEBUG && console.log("drawBase64Image", img)
    if (img) {
        if (!Array.from(very_code_nodes).includes(img)) {
            DEBUG && console.log("add nodes", img)
            very_code_nodes.push(img)
            img.addEventListener('click', img_click);
        }
    }
    let canvas = document.createElement('canvas');
    canvas.width = img.width;
    canvas.height = img.height;
    let ctx = canvas.getContext('2d');
    ctx.drawImage(img, 0, 0, img.width, img.height);
    let dataURL;
    try {
        dataURL = canvas.toDataURL('image/webp');
    } catch (e) {
        console.info("drawBase64Image to webp", e);
        // 不支持webp时,转jpeg
        try {
            dataURL = canvas.toDataURL('image/jpeg');
        } catch (e2) {
            console.info("drawBase64Image to jpeg", e2);
        }
    }
    return dataURL;
}


//监听整个页面的 paste 事件, chrome只能监听文本
document.addEventListener('paste', e => {
    let clipboardData = window.clipboardData || e.clipboardData;
    if (!clipboardData) return;
    let type = clipboardData.items[0] && clipboardData.items[0].type;
    if (type && type.match(/image/)) {
        let blob = clipboardData.items[0].getAsFile();
        let file = new FileReader();
        file.addEventListener('loadend', e => {
            DEBUG && console.log("paste data", e.target.result)
            chrome.runtime.sendMessage(e.target.result);
        });
        file.readAsDataURL(blob);
    }
})

const image_url_reg = /https?:\/\/.*\.(png|jpg|jpeg)\b.*/ig
//监听整个页面的 copy 事件,只能监听文本,图片链接
document.addEventListener('copy', e => {
    chrome.storage.sync.get({"copy_reco": false}, config => {
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

function find_element(selector, index) {
    return document.querySelectorAll(selector)[index];
}

let fill_config = {}

// "domain,selector[,index]"
function parse_config(config) {
    DEBUG && console.log("解析规则:", config)
    fill_config = {}
    let items = config.split(";")
    DEBUG && console.log("解析规则 items:", items)
    for (let i = 0; i < items.length; i++) {
        let info = items[i].split(",");
        DEBUG && console.log("解析规则 info:", items[i], info)
        if (info.length >= 2) {
            let selector = info[1]
            let index = info.length === 3 ? info[2] : 0
            fill_config[info[0]] = {selector, index}
        } else {
            DEBUG && console.log("配置错误:", items[i])
        }
    }
    DEBUG && console.log("解析结束:", fill_config)
}

function free_edit() {
    "true" === document.body.getAttribute("contenteditable") ? (
            document.body.setAttribute("contenteditable", !1), alert("网页不能编辑啦！"))
        : (document.body.setAttribute("contenteditable", !0), alert("网页可以编辑啦！"))
}

function remove_restrict() {
    let t = function (t) {
        t.stopPropagation(),
        t.stopImmediatePropagation && t.stopImmediatePropagation()
    };
    ["copy", "cut", "contextmenu", "selectstart", "mousedown", "mouseup", "keydown", "keypress", "keyup"]
        .forEach(function (e) {
            document.documentElement.addEventListener(e, t, {capture: !0})
        }), alert("解除限制成功啦！")
}

function copy_cookie() {
    let oInput = document.createElement('input');
    oInput.value = document.cookie;
    document.body.appendChild(oInput);
    oInput.select();
    document.execCommand("Copy");
    oInput.className = 'oInput';
    oInput.style.display = 'none';
    alert('复制成功');
}

const very_code_nodes = []

window.onload = function () {
    chrome.storage.sync.get({"debug": false}, config => {
        DEBUG = config.debug
        console.log("debug", DEBUG)
    })
    let verifycode_ele = Array.from(document.getElementsByTagName("img")).filter(el =>
        find_attribute(el, "alt", "图片刷新") ||
        find_attribute(el, "src", /Validate|captcha|login-code-img/gi) ||
        find_attribute(el, "class", /login-code/gi)
    )
    DEBUG && console.log("_______loaded_____ find", verifycode_ele)
    very_code_nodes.push(verifycode_ele)
    verifycode_ele.forEach(el => {
            very_code_nodes.push(el)
            el.addEventListener('click', img_click)
            DEBUG && console.log("_______add click_____", el)
            let start = Date.now()
            if (el.src.startsWith("http")) {
                fetch(el.src)
                    .then(() => {
                        delay = Math.min(Math.max((Date.now() - start) * 1.2, delay), 2000)
                        DEBUG && console.log("_______重设图片刷新延迟____", delay)
                    })
                    .catch(error => {
                        toast("请求验证码图片失败: ", error)
                    })
            }
        }
    )
}
