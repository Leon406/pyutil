function save_options() {
  var ele = document.getElementById("ocrServerUrl");
  var hint = "保存成功!";
  if(ele.value.includes("http")) {
	  localStorage["ocr_server"] = ele.value;
  }else {
	  localStorage["ocr_server"]= "";
	  hint = "服务地址错误!!!";
  }
 
  // Update status to let user know options were saved.
  var status = document.getElementById("status");
  status.innerHTML = hint;
  setTimeout(function() {
    status.innerHTML = "";
  }, 750);
}
// Restores select box state to saved value from localStorage.
function restore_options() {
  document.getElementById("btn").addEventListener('click',save_options);
  var server = localStorage["ocr_server"];
  if (!server) {
    return;
  }
  var ele = document.getElementById("ocrServerUrl");
  ele.value = server
}

window.addEventListener('load',  restore_options)

 //监听整个页面的 paste 事件
document.addEventListener('paste',function(e){
	let clipboardData = e.clipboardData || window.clipboardData;
	var type = clipboardData.items[0].type;
	if(!clipboardData) return ;
	
	if (type.match(/image/)) {
		var blob = clipboardData.items[0].getAsFile();
		var file = new FileReader();
		file.addEventListener('loadend', function(e){
			chrome.runtime.sendMessage(e.target.result);
		});
		file.readAsDataURL(blob);
	}
})
