window.load = $(function(){
  $(".choose").click(function(){
      if(!$(this).hasClass("c_active")){
          $(this).addClass("c_active");
          $(".menu").slideDown();
        }
      else{
        $(this).removeClass("c_active");
        $(".menu").slideUp();
      }
  });
  $(".switchon").click(function(){
    $(this).addClass("s_active");
    $(".switchoff").removeClass("s_active");
    $(".s_check").removeAttr("disabled");
  });
  $(".switchoff").click(function(){
    $(this).addClass("s_active");
    $(".switchon").removeClass("s_active");
    $(".s_check").attr("disabled",true);
  });
  $(".cancel").click(function(){
    $(".menu").slideUp();
    $(".choose").removeClass("c_active");
  });
  $(".verify").click(function(){
    $(".menu").slideUp();
    $(".choose").removeClass("c_active");
    var update = {};
    if($("#c_school").val() != "" && $("#c_school").val() != undefined){
      var schoolid;
      var schools = JSON.parse(localStorage.getItem("schools"));
      for(var i=0;i<schools.length;i++){
        if(schools[i].name = $("#c_school").val()){
          schoolid = schools[i].id + 1;
        }
      }
      if(schoolid != ""){
        $.extend({},update,{"school":schoolid});
      }else{
        alert("请选择正确的学校");
        return;
      }
    }
    if($("#c_degree").val() != "" && $("#c_degree").val() != undefined){
      var degree,degree0 = $("#c_degree").val();
      if(degree0 == "未知"){
        degree = 0;
      }else if(degree0 == "本科生"){
        degree = 1;
      }else if(degree0 == "研究生"){
        degree = 2;
      }else if(degree0 == "博士"){
        degree = 3;
      }else{
        alert("请选择正确的学历");
        return;
      }
      $.extend({},update,{"degree":degree});
    }
    //没有写专业、认证
    if($("#c_tall_min").val() != "" && $("#c_tall_min").val() != undefined){
      var tall_min = $("#c_tall_min").val();
      $.extend({},update,{"height_min":tall_min});
    }
    if($("#c_tall_max").val() != "" && $("#c_tall_max").val() != undefined){
      var tall_max = $("#c_tall_max").val();
      if(tall_max <= $("#c_tall_min").val()){
        $.extend({},update,{"height_max":tall_max});
      }else{
        alert("请输入正确的身高");
        return;
      }
    }
    if($("#c_hometown").val() != "" && $("#c_hometown").val() != undefined){
      var cityid,provinceid,hometown0 = $("#c_hometown").val();
      var provinces = JSON.parse(localStorage.getItem(provinces));
      for(var i=0;i<provinces.length;i++){
        for(var j=0;j<provinces[i].cities.length;j++){
          if(provinces[i].cities[i] == hometown0){
            provinceid = i+1;
            cityid = j+1;
          }
        }
      }
      if(cityid != ""){
        $.extend({},update,{"hometown_province":provinceid});
        $.extend({},update,{"hometown_city":cityid});
      }else{
        alert("请输入正确的城市");
        return;
      }
    }
    if($("#c_work_city").val() != "" && $("#c_work_city").val() != undefined){
      var cityid,provinceid,city = $("#c_work_city").val();
      var provinces = JSON.parse(localStorage.getItem(provinces));
      for(var i=0;i<provinces.length;i++){
        for(var j=0;j<provinces[i].cities.length;j++){
          if(provinces[i].cities[i] == hometown0){
            provinceid = i+1;
            cityid = j+1;
          }
        }
      }
      if(cityid != ""){
        $.extend({},update,{"work_province":provinceid});
        $.extend({},update,{"work_city":cityid});
      }else{
        alert("请输入正确的城市");
        return;
      }
    }
    if($("#c_age_min").val() != "" && $("#c_age_min").val() != undefined){
      var tall_min = $("#c_age_min").val();
      $.extend({},update,{"age_min":tall_min});
    }
    if($("#c_age_max").val() != "" && $("#c_age_max").val() != undefined){
      var tall_max = $("#c_age_max").val();
      if(tall_max <= $("#c_age_min").val()){
        $.extend({},update,{"height_max":tall_max});
      }else{
        alert("请输入正确的身高");
        return;
      }
    }
    if($("#c_horoscope").val() != "" && $("#c_horoscope").val() != undefined){
      var horoscopeid,horos0 = $("#c_horoscope").val();
      var horoscopes = JSON.parse(localStorage.getItem("horoscopes"));
      for(var i=0;i<horoscopes.length;i++){
        if(horoscopes[i].name == horos0){
          horoscopeid = i+1;
        }
      }
      if(horoscopeid != ""){
        $.extend({},update,{"horoscope":horoscopeid});
      }else{
        alert("请输入正确的星座");
        return;
      }
    }
    if(update == []){
      return;
    }else{
      $.post("/api/wall/edit_filter",update,function(data){
        var uid0 = [];
        for(var i=0;i<data.length;i++){
          var uid1 = {"uid":data[i].uid};
          uid0.push(uid1);
        }
        load_filter_onlines();
      });
    }
  });
  var alert_h = $(".navbar").height();
  var alert_t = (alert_h - $(".choose").height())/2;
  $(".choose").css("margin-top",alert_t);
  $(".alert").css("top",alert_h);
  $(".menu").css("top",alert_h);
  var line_h = $(".wall_pic").height();
  $(".wall_pic img").css("margin-top",(line_h-40)/2);
  var main_nav_w = $(".main_nav").width();
  $(".main_nav").css("width",main_nav_w+20);
  $(".col1").click(function(){
    $(".col2,.col3").css("background","#ccc");
    $(this).css("background","#fff");
    $(".near,.weak-hot").hide();
    $(".choose_sex").fadeIn();
    $("#c_sex_woman").click(function(){
      $(".male").hide();
      $("#c_sex_").text("♂");
      $(".female").show();
      $(this).parent().fadeOut();
    });
    $("#c_sex_man").click(function(){
      $(".female").hide();
      $("#c_sex_").text("♀");
      $(".male").show();
      $(this).parent().fadeOut();
    });
  });
  $(".user_").click(function(){
    $(this).next().slideToggle();
  });
  $(".col2").click(function(){
    $(".col1,.col3").css("background","#ccc");
    $(this).css("background","#fff");
    $(".now,.weak-hot").hide();
    $(".near").show();
    $(".choose_sex").hide();
  });
  $(".col3").click(function(){
    $(".col2,.col1").css("background","#ccc");
    $(this).css("background","#fff");
    $(".now,.near").hide();
    $(".weak-hot").show();
    $(".choose_sex").hide();
  });
  var c_left = parseInt($(".headicon").css("margin-left")) + 33;
  $(".circle").css("left",c_left);
  $("[name='my-checkbox']").bootstrapSwitch();
  $(".headicon").click(function(){
    $(".UserInfor_").fadeIn();
  });
  $(".U_off").click(function(){
    $(".UserInfor_").fadeOut();
  });
  $(".U_logout").click(function(){
    $(".UserInfor_").fadeOut();
    $.post("/api/user/logout",function(data){
      window.location = "/index";
    });
  });
  if(!$(".U_circle2").is(":hidden") || !$(".U_circle3").is(":hidden") || !$(".U_circle3").is(":hidden")){
    $(".U_circle").show();
    $(".circle").show();
  }
});

window.load = $(function(){
  $("#c_school").click(function(){
    $(".SchoolName").show();
    $(".SchoolName").show().find("li").bind("click" ,function(){
      $("#c_school").val($(this).text());
      $(".SchoolName").hide();
    });
  });
  $("#c_subject").click(function(){
    $(".SubjectName").show();
    $(".SubjectName").show().find("li").bind("click" ,function(){
      $("#c_subject").val($(this).text());
      $(".SubjectName").hide();
    });
    myApp.controller('Filter_Subject',function($scope,$http){
      $http.post("").success(function(data){

      });
    });
  });
  $("#c_degree").click(function(){
    $(".GradeName").show();
    $(".GradeName").show().find("li").bind("click" ,function(){
      $("#c_degree").val($(this).text());
      $(".GradeName").hide();
    });
  });
  $("#c_permission").click(function(){
    $(".PermissionName").show();
    $(".PermissionName").show().find("li").bind("click" ,function(){
      $("#c_permission").val($(this).text());
      $(".PermissionName").hide();
    });
  });
  $("#c_hometown").click(function(){
    $(".HometownName").show();
    $(".HometownName").show().find("li").bind("click" ,function(){
      $("#c_hometown").val($(this).text());
      $(".HometownName").hide();
    });
  });
  $("#c_work_city").click(function(){
    $(".WorkplaceName").show();
    $(".WorkplaceName").show().find("li").bind("click" ,function(){
      $("#c_work_city").val($(this).text());
      $(".WorkplaceName").hide();
    });
  });
  $("#c_horoscope").click(function(){
    $(".HoroscopeName").show();
    $(".HoroscopeName").show().find("li").bind("click" ,function(){
      $("#c_horoscope").val($(this).text());
      $(".HoroscopeName").hide();
    });
  });
});
