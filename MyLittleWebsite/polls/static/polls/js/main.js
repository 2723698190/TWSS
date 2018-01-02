/**
 * Created by hasee on 2017/8/25.
 */
$(document).ready(function () {
    $(document).keyup(function (event) {
               if(event.keyCode==13){
               }
            });
    $(".unit_title_level").hide();
    $(".unit_title_level3").hide();
    $(".unit_title_level1").click(function () {
        $(this).parents().siblings().children("div.unit_title_level").hide("fast");
        $(this).next().toggle("fast");

    });
    $(".unit_title_level2").mouseover(function () {
        $(this).stop().animate({paddingLeft:'50px'});
    });
    $(".unit_title_level2").mouseout(function () {
        $(this).stop().animate({paddingLeft:"10px"})
    });
    $(".unit_title_level2").click(function () {
        $(this).parents().siblings().children("div.unit_title_level3").hide("fast");
        $(this).next().toggle("fast");
    });
    $(".unit_detail").mouseover(function(){
        $(this).stop().animate({paddingRight:'50px'});
        $(this).find(".topLine,.bottomLine").stop().animate({"width":"100%"});
        $(this).find(".rightLine,.leftLine").stop().animate({"height":"100%"});
    });
    $(".unit_detail").mouseout(function(){
    $(this).stop().animate({paddingRight:'0px'});
    $(this).find(".topLine,.bottomLine").stop().animate({"width":"0px"});
    $(this).find(".rightLine,.leftLine").stop().animate({"height":"0px"});
    });





    $("#changing_password").click(function () {
        $("#div_user_info").load("/polls/index/change_password");
    });
    $("#user_index_info").click(function () {
        $("#div_user_info").load("/polls/index/teacher/user_info");
    });
});