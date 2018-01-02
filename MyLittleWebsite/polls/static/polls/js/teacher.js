
$(document).ready(function () {
    $("#user_info_user_info").click(function () {
        $("#div_user_info").load("/polls/index/teacher/user_info");
    });

    $("#workload_input_theory_class").click(function () {
        $("#div_user_info").load("/polls/index/teacher/theory_class/1/");
    });
    $("#workload_input_experiment").click(function () {
        $("#div_user_info").load("/polls/index/teacher/theory_class/2/");
    });
    $("#workload_input_internship").click(function () {
        $("#div_user_info").load("/polls/index/teacher/theory_class/3/");
    });
    $("#workload_input_teaching_achievement").click(function () {
        $("#div_user_info").load("/polls/index/teacher/teaching_achievement");
    });
    $("#workload_input_teaching_project").click(function () {
        $("#div_user_info").load("/polls/index/teacher/teaching_object");
    });
    $("#workload_input_competition_guide").click(function () {
        $("#div_user_info").load("/polls/index/teacher/competition_guide");
    });
    $("#workload_input_paper_guide").click(function () {
        $("#div_user_info").load("/polls/index/teacher/paper_guide");
    });
    $("#user_info_change_password").click(function () {
        $("#div_user_info").load("/polls/index/change_password");
    });
    $("#workload_count_title").click(function () {
        $("#div_user_info").load("/polls/index/teacher/workload_count",function (data) {

        });
    });
});
