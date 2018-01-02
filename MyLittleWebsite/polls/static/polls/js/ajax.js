/**
 * Created by hasee on 2017/8/23.
 */
// $(document).ready(function () {
//     $("button").click(function () {
//         $("#div1").load(
//             "/test/test.html",function (responseTxt,statusTxt,xhr) {
//                 if(statusTxt=="success")
//                     alert("外部内容加载成功");
//                 if(statusTxt=="error")
//                     alert("error:"+xhr.status+":"+xhr.statusText);
//
//
//
//             }
//         );
//
//     });
// });


$(document).ready(function(){
  $("button").click(function(){
    $("#div1").load("/polls/index/teacher/user_info/",function(responseTxt,statusTxt,xhr){
      if(statusTxt=="success")
        alert("外部内容加载成功！");
      if(statusTxt=="error")
        alert("Error: "+xhr.status+": "+xhr.statusText);
    });
  });
});
