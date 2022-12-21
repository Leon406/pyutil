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

