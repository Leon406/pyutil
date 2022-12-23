// 监听 background 传来的数据 可对页面dom操作
chrome.runtime.onMessage.addListener((data, sender, sendResponse) => {
  console.log("data",data);
  sendResponse(drawBase64Image(getImg(data.srcUrl)))
});

function getImg(url) {
	return Array.from(document.getElementsByTagName("img")).filter(el=>el.src.includes(url))[0];
}
function drawBase64Image (img){
	console.log("drawBase64Image",img)
    var canvas = document.createElement('canvas');
    canvas.width = img.width;
    canvas.height = img.height;
    var ctx = canvas.getContext('2d');
    ctx.drawImage(img, 0, 0, img.width, img.height);
	var dataURL;
	try{
	   dataURL = canvas.toDataURL('image/');
	   console.log("dataURL",dataURL)
	}catch(e) {
	   console.error(e);
	}
    return dataURL;
}


 //监听整个页面的 paste 事件
document.addEventListener('paste',function(e){
	let clipboardData = e.clipboardData || window.clipboardData;
	if(!clipboardData) return ;
	var type = clipboardData.items[0]&&clipboardData.items[0].type;
	if (type && type.match(/image/)) {
		var blob = clipboardData.items[0].getAsFile();
		var file = new FileReader();
		file.addEventListener('loadend', function(e){
			chrome.runtime.sendMessage(e.target.result);
		});
		file.readAsDataURL(blob);
	}
})

//监听整个页面的 copy 事件,只能监听文本,不能监听图片
/*
document.addEventListener('copy',function(e){
	let clipboardData = e.clipboardData || window.clipboardData;
	if(!clipboardData) return ;
	console.info("copy",clipboardData)
	var type = clipboardData.items[0]&&clipboardData.items[0].type;
	let text = window.getSelection().toString();
    if (text) {
		console.info("copy text",text)
	}
	console.info("type",type)
	if (type&&type.match(/image/)) {
		var blob = clipboardData.items[0].getAsFile();
		var file = new FileReader();
		file.addEventListener('loadend', function(e){
			chrome.runtime.sendMessage(e.target.result);
		});
		file.readAsDataURL(blob);
	}
})
*/
