/**
 * Created by hasee on 2017/12/13.
 */
$(document).ready(function () {
    $("#columns-form").animate({top:'100px'});
    $(".cancel_new_index_teacher").click(function () {
        $("#columns-form").animate({top:'-400px'},function () {
            $("#form_load").html(" ");
        });
    });
});