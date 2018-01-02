/**
 * Created by hasee on 2017/12/13.
 */
$(document).ready(function () {
    $("#register").click(function () {
        alert("本系统暂关闭用户注册功能，请联系管理员开启")
    });
    $("#forget_password").click(function () {
        alert("请联系教务员找回密码");
    });
    $("#login").click(function () {
        $.ajax({
            type:"POST",
            data:$("#login_form").serialize(),
            url:"{% url 'polls:index_login' %}",
            datatype:"json",
            success: function(data){
                if(data==="1"){
                    $(location).attr('href', "{% url 'polls:index_teacher' %}");
                }else if (data==='2'){
                    $(location).attr('href', "{% url 'polls:index_academic_officer' %}");
                }else if (data==='31'){
                    $(location).attr('href', "{% url 'polls:index_D_H_biotechnology' %}");
                }else if (data==='32'){
                    $(location).attr('href', "{% url 'polls:index_D_H_bioinfomation' %}");
                }else if (data==='33'){
                    $(location).attr('href', "{% url 'polls:index_D_H_bioobject' %}");
                }else {
                    $("#load_login_form_div").html(data);
                }
            },
            error: function(data) {
                alert(data)
            }
        });
    })
});