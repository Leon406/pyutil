// 部署后配置服务器地址
const ocrServer = "";

chrome.contextMenus.create({
		title: '识别验证码',
		id: 'search',
		type: 'normal',
		contexts: ['image'],
	});

// 点击弹出菜单
chrome.contextMenus.onClicked.addListener(function(item, tab) {
	chrome.tabs.sendMessage(tab.id, item, function(base64) {
		handleBase64(base64);
		console.log(arguments, chrome.runtime.lastError);
	});
});


function handleBase64(base64) {
	console.log("handleBase64",base64)
	if(!base64) {
		notification("图片转base64错误,请确认图片是否有跨域限制", '失败')
	    return;
	}
	return fetch(ocrServer +"/ocr", {
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
		iconUrl: 'icon48.png',
	})
}