$(".share .spread").click(function(){
  $(this).addClass("s_active");
  $(this).hide();
  var length = $(".share ul li").length;
  var max;
  for(var i=0;i<length;i++){
    if(!$(".share ul li").eq(i).is(":hidden")){
      max = i;
    }
  }
  $(".share ul li").slice(max-1,max+4).fadeIn();
});
$(".share .next").click(function(){
  var length = $(".share ul li").length;
  var max;
  for(var i=0;i<length;i++){
    if(!$(".share ul li").eq(i).is(":hidden")){
      max = i;
    }
  }
  if(!$(".share .spread").is(":hidden") && max != length-1){
    $(".share ul li").hide();
    $(".share ul li").slice(max+1,max+4).fadeIn();
  }
  else if($(".share .spread").is(":hidden") && max != length-1){
    $(".share ul li").hide();
    $(".share ul li").slice(max+1,max+7).fadeIn();
  }
});
$(".share .last").click(function(){
  var length = $(".share ul li").length;
  var min;
  for(var i=length-1;i>=0;i--){
    if(!$(".share ul li").eq(i).is(":hidden")){
      min = i;
    }
  }
  if(min != 0){
    if(!$(".share .spread").is(":hidden")){
      $(".share ul li").hide();
      $(".share ul li").slice(min-3,min).fadeIn();
    }
    else if($(".share .spread").is(":hidden") && min < 6){
      $(".share ul li").hide();
      $(".share ul li").slice(0,min).fadeIn();
    }
    else{
      $(".share ul li").hide();
      $(".share ul li").slice(min-6,min).fadeIn();
    }
  }
});
$(".share .first").click(function(){
  if(!$(".share .spread").is(":hidden")){
    $(".share ul li").hide();
    $(".share ul li:lt(3)").fadeIn();
  }
  else{
    $(".share ul li").hide();
    $(".share ul li:lt(6)").fadeIn();
  }
});
$(".share .end").click(function(){
  var length = $(".share ul li").length;
  if(!$(".share .spread").is(":hidden")){
    $(".share ul li").hide();
    $(".share ul li").slice(length-3,length).fadeIn();
  }
  else{
    $(".share ul li").hide();
    $(".share ul li").slice(length-6,length).fadeIn();
  }
});
