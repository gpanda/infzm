/**
 * infzm.com JavaScript Library
 * com.infzm
 * 
 * @version 1.1
 * @author tvrcgo 
 * @since 09.07.06
 * 
 */
(function(){
document.domain = "infzm.com";
if(typeof Assemble=='undefined'){
	return false;
}

// ===================== com.infzm ============================

Assemble.plugin({
	
	ajax: function(url_, data_, options_){
		var temp;
		var options = (typeof options_ != 'undefined') ? options_ : {};

		if (typeof jQuery == 'undefined'){
			Assemble.debug('infzm.js[25]: jQuery not found');
			return false;
		}

		jQuery.ajax({
			url:url_, 
			dataType: options.dataType ? options.dataType : 'json',
			type: options.method ? options.method : "POST",
			data: data_, 
			cache: options.cache ? options.cache : false, 
			async: options.async ? options.async : false,
			success:function(data){
				(typeof options_ == 'function') ? options_(data) : '';
				(typeof options.success=='function') ? options.success(data) : '';//complete
				temp = data;
			}, 
			error:function(){
				(typeof options.error=='function') ? options.error() : '';//error
				temp = 404;
			}
		});
		
		return temp;
		
	}

});


Assemble.plugin("Assemble.ajax", {
	
	jsonp: function(url_, data_, callback_){
		
		if (typeof jQuery == 'undefined'){
			Assemble.debug('infzm.js[58]: jQuery not found');
			return false;
		}

		if(url_.indexOf('?')==-1) url_+= "?callback=?";

		jQuery.getJSON(url_, data_, function(data){
			if(typeof callback_ == 'function')
				callback_(data);
		});
	}

});

// ===================== com.infzm.link ==============================

Assemble.construct({name:'com.infzm.link', obj:{

	diggUp: function(link_id){

		if(link_id!=""){
			var url = '/link/userDiggLink/raw';
			var data = 'link_id=' + parseInt(link_id) + '&digg_type=1';

			return Assemble.ajax(url, data);
		}
		else{
			return 0;
		}
	},

	diggDown: function(link_id){
		var core = Assemble.mod['com.infzm'];

		if(link_id!=""){
			var url = '/link/userDiggLink/raw';
			var data = 'link_id=' + parseInt(link_id) + '&digg_type=0';
			return Assemble.ajax(url, data);
		}
		else{
			return 0;
		}
	},

	remove: function(){},

	favorite: {

		check: function(id){
			var url = "/link/checkCollection/raw/"+id;
		},

		add: function(args){

			var url = "/link/saveCollection/raw";
			var data = {"digg_type":args.digg_type||0, "link_id":args.link_id||-1, "link_tags":args.link_tags||"", "link_type":args.link_type||1};

			return Assemble.ajax(url, data);
		},

		remove: function(){
			var url = "/my/delcollection/raw/";
		}

	},

	comment: {
		
		post: function(args){

			var url = "/link/submitcomment/raw";
			var data = "link_id="+args.link_id+"&comment_content="+args.comment_content+"&source="+args.source;

			return Assemble.ajax(url, data);
		},

		remove: function(){
			
		},

		diggUp: function(link_id, comment_id){

			var url = '/link/userDiggComment/raw';
			var data = 'link_id='+link_id+'&comment_id='+comment_id+'&digg_type=1';

			return Assemble.ajax(url, data);
		},

		diggDown: function(link_id, comment_id){

			var url = '/link/userDiggComment/raw';
			var data = 'link_id='+link_id+'&comment_id='+comment_id+'&digg_type=0';

			return Assemble.ajax(url, data);
		}

	}
	
}});

// 顶文章
diggContent = function(link_id){
	var link = Assemble.mod['com.infzm.link'];

	var result = link.diggUp(link_id);
	
	if (result.login==0) {
		//Assemble.dispatch('diggContent-noLogin');
		_TEMPOBJECT = link_id;
		_AFTERlOGIN = "autoDiggContentComment()";
		Assemble.mod['com.infzm.passport'].localLogin();
		return false;
	}

	if (result.res==1) {
		Assemble.dispatch('diggContent-yes', result);
	} else {
		Assemble.dispatch('diggContent-no', result);
	}
};


//登录成功后继续之前的顶文章操作
autoDiggContentComment = function (){
	diggContent(_TEMPOBJECT);
};


// 顶踩评论
diggComment = function(link_id, comment_id, digg_type){

	var link = Assemble.mod['com.infzm.link'];
	
	if(digg_type==1){
		var result = link.comment.diggUp(link_id, comment_id);
	}
	else if(digg_type==0){
		var result = link.comment.diggDown(link_id, comment_id);
	}
	else{
		return false;
	}

	if (result.login==0) {
		Assemble.dispatch('diggComment-noLogin');
		return false;
	}
			
	if (result.res==1) {
		if (digg_type==1){
			Assemble.dispatch('diggComment-yes-up', result);
		}
		else{
			Assemble.dispatch('diggComment-yes-down', result);
		}
	} else {
		Assemble.dispatch('diggComment-no', result);
	}

};

// 提交评论

// @ 网摘ID，评论内容，来源
submitComment = function(link_id, comment_content, isToWeibo){

	var link = Assemble.mod['com.infzm.link'];
	
	if(link_id==null||link_id==''){
		return false;
	}

	if(comment_content==''){
		Assemble.dispatch('submitComment-empty');
		return false;
	}
//	var source = {callback:window.location,commnet:comment}
//	var data = Assemble.post("/content/connectToSina",source);
//	if(data.status){
//		cookie("=>"")
//			redirect(aurl);                                                                                                                                                                      
//		} else{
//			
//			}
		

	var result = link.comment.post({link_id:link_id, comment_content:comment_content, isToWeibo:isToWeibo, source:arguments[2]||0});

	if(result.res==1){
		Assemble.dispatch('submitComment-yes', result);
	}
	else{
		Assemble.dispatch('submitComment-no', result);
	}
};


// 收藏
favorite = function(link_id, link_tags){

	var link = Assemble.mod['com.infzm.link'];

	if(link_id>0&&link_tags!=""){
		var result = link.favorite.add({'link_id':link_id, 'link_tags':link_tags});
		//Assemble.ui.msgbox(result.msg);
		Assemble.dispatch('favorite', result);
	}

};

// ========================= com.infzm.passport ===================================

Assemble.construct({name:'com.infzm.passport', obj:{

	login : function(args){
		var url = "/passport/login/raw";
		args.refer = args.refer ? args.refer : "http://www.infzm.com";

		if( args && args.loginname!="" && args.password!="" ){
			return Assemble.ajax(url, args);
		}
		else{
			return -1;
		}
	},
	
	_createAuthWindow : function(platform){
		var url = "http://rest.infzm.com/doauth?platform=" + platform;
		if (arguments.length==2){
			var from = arguments[1];
			if (from)
			url =  url + "&from=" + from ;	
		}
		//var oauth_login_window = window.open(url, "oauth_login_window", "width=700,height=600,toolbar=no,menubar=no,resizable=no,status=no");
		var oauth_login_window = window.open(url, "oauth_login_window", "width=700,height=600,toolbar=yes,menubar=yes,resizable=yes,status=yes");
    oauth_login_window.focus();
	},
	
	localLogin:function(args){
		url = 'http://' + window.location.host + '/passport/loginPanel' ;
		var ajaxFace = new LightFace.Request({
				 	width:'680px',
				 	height:'412px',
					url: url,
					buttons: [
						{ title: '关闭', event: function() { this.close(); } }
					],
					request: { 
						evalResponse:true,
						evalScripts :true,
						method: 'get'
					},
					onSuccess:function(){
						// console.debug( this); 
					}
					 
					//title: '登录iNFZM'
				});
				 
		ajaxFace.open();	
		Assemble.construct({name:'com.infzm.passport.loginModel', obj:ajaxFace});
	},
	
	needUserMail:function(args){
		url = 'http://' + window.location.host + '/passport/needUserMail';
		var ajaxFace = new LightFace.Request({
				 	width:'680px',
				 	height:'300px',
					url: url,
					buttons: [
						{ title: '关闭', event: function() { 
						//if in usercenter reffer to index
							if(window.location.href.substr(7,8) == 'passport'){
								window.location = "http://www.infzm.com";
							}
							this.close(); 
							}
						}
					],
					request: { 
						evalResponse:true,
						evalScripts :true,
						method: 'get'
					},
					onSuccess:function(){// console.debug( this); 
						}
					 
					//title: '登录iNFZM'
				});
				 
		ajaxFace.open();	
		Assemble.construct({name:'com.infzm.passport.loginModel', obj:ajaxFace});
	},
	
	snsLogin:function(args){
		args.from = args.from ? args.from : 'page';
		this._createAuthWindow(args.platform, args.from);	
	},
	
	snsBind:function(args){
		args.from = args.from ? args.from : 'page';
		this._createAuthWindow(args.platform, args.from);
	},
	
	logout : function(){
		var url = "/passport/logout/raw";
		return Assemble.ajax(url, null);
	},
	
	finishAuth:function(args){
		// the model window has open .if the user has bound ,then close it
		var loginModel = Assemble.mod['com.infzm.passport.loginModel'];
		if (loginModel){
			if (parseInt(args.isLogin)==1){
				loginModel.close();
				loadLoginform();//here need to fix;
			} else {
				 
				toBind(args);
			}
		 	//Assemble.mod['com.infzm.passport.']
		} else {
			if (parseInt(args.isLogin)==1){		
				loadLoginform();
			}
		}
	},
	
	
	
	isLogin : function(){
		var url = '/passport/islogin';
		try {
			var res = Assemble.ajax(url, null, 'json');
			return res.status;
		}
		catch(e){
			Assemble.debug(e);
			return false;
		}
	},
	
	loginform: function(){
		var url = "/passport/loginform/raw";
		return Assemble.ajax(url, "style=top");
	},

	getUserInfo : function(){
		
	},

	sync : {
	
		isbind: function(_platform){
			return Assemble.ajax("/sync/isbind","platform="+_platform);
		},
	
		bind: function(_platform, _options){
			return Assemble.ajax("/sync/bind", "platform="+_platform+"&uid="+_options.uid+"&pwd="+_options.pwd);
		},
	
		unbind: function(_platform){
			return Assemble.ajax("/sync/unbind", "platform="+_platform);
		}
	
	}
}});

// 登录
login = function(args){
	
	var uid = args.loginname||"";
	var pwd = args.password||"";

	if(uid==""||pwd=="")
		return false;

	var passport = Assemble.mod["com.infzm.passport"];
	var res = passport.login({"loginname":args.loginname, "password":args.password, "remember":args.remember});
	Assemble.dispatch('login', null);
	loadLoginform();
};

// 注销
logout = function(){
	var passport = Assemble.mod["com.infzm.passport"];
	passport.logout();
	Assemble.dispatch('logout', null);
	loadLoginform();
};

// 载入登录区
loadLoginform = function(){
	var passport = Assemble.mod["com.infzm.passport"];
	var loginform = passport.loginform();
	Assemble.dispatch('loadLoginform', loginform);
	
	if (typeof jQuery!='undefined'){
		jQuery("#userPanel").html(loginform);
	}
	else{
		Assemble.debug('infzm.js -> loadLoginform():jQuery not found');
	}
	if(typeof _AFTERlOGIN != "undefined" && _AFTERlOGIN!=null){
		if(Assemble.mod['com.infzm.passport'].isLogin()){
			eval(_AFTERlOGIN);
		}
	}
	if(typeof getNotice == "function"){
		getNotice();
	}
};

})();

