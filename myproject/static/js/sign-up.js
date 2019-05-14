var read_clicked;
window.onload=function(){
    read_clicked = false;
};
function read_con(){
	read_clicked = !read_clicked;
}
function sign_up(){
	if(!sign_up_check()){
		return;
	}

	url = "../../www/controller/RegisterController.php";//修改url

	var data = $("#form-sign-up").serializeArray();
	console.log(data);
	var xmlhttp = new XMLHttpRequest();
	xmlhttp.open("POST",url,true);
	xmlhttp.setRequestHeader('content-type', 'application/x-www-form-urlencoded');

    xmlhttp.onreadystatechange=function(){
      if (xmlhttp.readyState===4){
      	if(xmlhttp.getResponseHeader('content-type')==='application/json'){
	      var result = JSON.parse(xmlhttp.responseText);	
	  	  if(result.status===400){
            alert('注册失败');
	      }
	      else{
	      	alert("注册成功");
	      }
        }
        else{
        	console.log(xmlhttp.responseText);
        }
      }
    };
	xmlhttp.send("RegInfo="+JSON.stringify(data));
	console.log("happy");
	console.log("RegInfo="+JSON.stringify(data));
}
function sign_up_check(){
	var tmp = document.getElementById("username-sign-up").value;
	//alert(tmp);
	var p = /^[0-9a-zA-Z]+$/; 
	if(!p.test(tmp)){
		alert("用户名只能包含数字和字母");
		return false;
	}
	if(tmp.length > 16 || tmp.length < 8){
		alert("用户名长度必须在8至16位之间");
		return false;
	}
	
	tmp = document.getElementById("password-sign-up").value;
	if(!p.test(tmp)){
		alert("密码只能包含数字和字母");
		return false;
	}
	if(tmp.length > 16 || tmp.length < 8){
		alert("密码长度必须在8至16位之间");
		return false;
	}
	var tmp2 = document.getElementById("password-con-sign-up").value;
	if(tmp!==tmp2){
		alert("两次输入密码不一致");
		return false;
	}
	if(read_clicked === false){
		alert("请确认服务协议");
		return false;
	}
	return true;
}
