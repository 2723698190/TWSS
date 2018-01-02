/**
 * Created by hasee on 2017/12/12.
 */
$(document).ready(function () {
    $("#form").animate({top:'100px'});
    $(".cancel_new_index_teacher").click(function () {
        $("#form").animate({top:'-400px'},function () {
            $("#form_load").html(" ");
        });
    });
});