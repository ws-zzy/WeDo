var nickname_legal = false;
$("#nickname-input").blur(function(){
	var nick = $(this).val();

	if(nick.length == 0){
		alert("昵称不能为空");
		nickname_legal = false;
	}

	if(nick.length > 16){
    	alert("昵称长度不能超过16位");
    	nickname_legal = false;
 	}
 	nickname_legal = true;
})
$("#nickname-ok").click(function(){
	var nickname = $("#nickname-input").val();
		
	if(nickname_legal){
        $.ajax({
        	type : "POST",
        	url:"/usr/info/name",
        	data:
        	{
        		name:nickname
        	},
        	contentType:"application/json",
        	dataType:"json",
        	success:function(data){
        		if(data == 200){
        			//todo:显示修改成功
        		}
        		else{
        			//todo:显示修改失败
        		}
        	},
        	error:function(XML,test){
        		alert(test);
        	}
        });
	}
	else{
		//todo:增加错误提示
	}
})

var mail_legal = false;
$("#mail-input").blur(function(){
	var mail = $(this).val();
	var test_mail = /^[A-Za-z\d]+([-_.][A-Za-z\d]+)*@([A-Za-z\d]+[-.])+[A-Za-z\d]{2,4}$/;
	if(mail.length == 0){
		alert("邮箱不能为空");
		mail_legal = false;
	}

	if(!test_mail.test(mail)){
    	alert("非法的邮箱格式");
    	mail_legal = false;
 	}
 	mail_legal = true;
})

$("#mail-ok").click(function(){
	var mail = $("#mail-input").val();

	if(mail_legal){
        $.ajax({
        	type : "POST",
        	url:"/usr/info/mail",
        	data:
        	{
        		mail:mail
        	},
        	contentType:"application/json",
        	dataType:"json",
        	success:function(data){
        		if(data == 200){
        			//todo:显示修改成功
        		}
        		else{
        			//todo:显示修改失败
        		}
        	}
        });
	}
	else{
		//todo:增加错误提示
	}
})
///////////////////////////////////////////////////////////////
var password_legal = false;
var password_con_legal = false;
$("#password-input").blur(function(){
	var password = $(this).val();
	if(password.length == 0){
		alert("密码不能为空");
		password_legal = false;
		return;
	}

	if(password.length > 16 || password.length < 8){
    	alert("密码长度必须在8到16之间");
    	password_legal = false;
    	return;
 	}
 	mail_legal = true;
})
$("#password-con-input").blur(function(){
	var password = $("#password-input").val();
	var password_con = $("#password-con-input").val();
	
	if(password_con !== password){
		alert("两次输入密码不一致");
		password_con_legal = false;
		return;
	}
    password_con_legal = true;

})
$("#password-ok").click(function(){
	var password = $("#password-input").val();

	if(password_legal&&password_con_legal){
        $.ajax({
        	type : "POST",
        	url:"/usr/info/mail",
        	data:
        	{
        		password:password
        	},
        	contentType:"application/json",
        	dataType:"json",
        	success:function(data){
        		if(data == 200){
        			//todo:显示修改成功
        		}
        		else{
        			//todo:显示修改失败
        		}
        	}
        });
	}
	else{
		//todo:增加错误提示
	}
})
var a = '{\
    "status": 1,\
    "total": 7,\
    "project": [{\
        "photo_url": "www.werwe.com",\
        "project_name": "江苏苏州1",\
        "project_intro": "中国"\
    },\
    {\
        "photo_url": "www.werwe.com",\
        "project_name": "江苏苏州2",\
        "project_intro": "中国"\
    },\
    {\
        "photo_url": "www.werwe.com",\
        "project_name": "江苏苏州3",\
        "project_intro": "中国"\
    },\
    {\
        "photo_url": "www.werwe.com",\
        "project_name": "江苏苏州4",\
        "project_intro": "中国"\
    },\
    {\
        "photo_url": "www.werwe.com",\
        "project_name": "江苏苏州5",\
        "project_intro": "中国"\
    },\
    {\
        "photo_url": "www.werwe.com",\
        "project_name": "江苏苏州6",\
        "project_intro": "中国"\
    },\
    {\
        "photo_url": "www.werwe.com",\
        "project_name": "江苏苏州7",\
        "project_intro": "中国"\
    }\
    ]\
}';

a = JSON.parse(a);
num_per_page=2;
//JSON.stringify(a);
var status = a.status;
console.log(status);
var total = a.total;
console.log(total);
var left = total%num_per_page;
console.log(left);
var pages = (total-left)/num_per_page;
console.log(pages);
var project = a.project;
//console.log(project);
if(left > 0){
	pages += 1;
}
document.getElementById("my-collection-pages").innerHTML = "";
document.getElementById("my-collection-pages").innerHTML += '<li><a href="#" aria-label="Previous">&laquo;</a></li>';
var string = "";
for(var i=1;i<=pages;i++){
	string = string + '<li><a class="current" href="#" id="collection-page-';
	string = string + i.toString();
	string = string + '" onclick="click_page_collection(';
	string = string + i.toString();
	string = string + ')">';
	string = string + i.toString();
	string = string + '</a></li>';
}
document.getElementById("my-collection-pages").innerHTML += string;
document.getElementById("my-collection-pages").innerHTML += '<li><a href="#" aria-label="Next">&raquo;</a></li>';

function click_page_collection(page_num){
	page_start = (page_num-1) * num_per_page + 1;
	if(page_num < pages){
		page_end = page_num * num_per_page;
	}
	else{
		page_end = total;
	}
	document.getElementById("my-collection-show").innerHTML = "";
	string = "";
	for(var i=page_start;i<=page_end;i++){
		string = string +  
		 '<div class="media border p-3 mb-5" style="height:100px"> \
                <img src="./assets/img/bulb.jpg" alt="创意图片" class="mr-3 mt-3 rounded-circle big-icon"> \
                <div class="media-body"> \
                  <h3>';
        string = string + project[i-1].project_name;
        string = string + '</h3> <p>';
        string = string + project[i-1].project_intro;
        string = string + '</p> </div> </div>';
	}
	document.getElementById("my-collection-show").innerHTML += string;
}