function sign_in(){
	var data = $("form").serializeArray();
	var xmlhttp = new XMLHttpRequest();
	xmlhttp.open("POST","../../www/controller/LoginController.php",true);
	xmlhttp.setRequestHeader('content-type', 'application/x-www-form-urlencoded');
    xmlhttp.onreadystatechange=function(){
      if (xmlhttp.readyState===4){
      	if(xmlhttp.getResponseHeader('content-type')==='application/json'){
      		var result = JSON.parse(xmlhttp.responseText);
	  	  if(result.status===400){
            alert('登录失败');
            // TODO:登陆失败的操作。
	      }
	      else{
	      	alert("登录成功");
	      	// TODO：登陆成功后的操作。
	      }
        }
        else{
        	console.log(xmlhttp.responseText);
        }
      }
    }
	xmlhttp.send('loginInfo=' + JSON.stringify(data));
}