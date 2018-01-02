# -*- coding:utf-8 -*-
# Create your views here.
import csv
import xlrd
import math
from datetime import datetime
from io import BytesIO
from xlwt import *
from django.utils.six import moves
from django.shortcuts import render, HttpResponse
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger,InvalidPage
from django.db.utils import IntegrityError, ProgrammingError
from django.forms import widgets
from polls.AccountForms import *
from django import forms
from django.http import HttpResponseRedirect,StreamingHttpResponse
from .models import *
from django.core.urlresolvers import reverse
import json
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import modelform_factory


# 每页项目数
try:
    page_item_total = PageItemTotal.objects.get(id=1)
    print(page_item_total.page_item_total)
except PageItemTotal.DoesNotExist:
    page_item_total = PageItemTotal.objects.create(id=1)
    print(page_item_total.page_item_total)
except ProgrammingError:
    pass
else:
    pass


# 教师录入截止日期
try:
    input_date = Deadline.objects.get(id=1)
except Deadline.DoesNotExist:
    input_date = Deadline.objects.create(id=1)
    print("记录不存在")
except ProgrammingError:
    pass
else:
    pass


# 系负责人审核日期
try:
    examination_date = Deadline.objects.get(id=2)
except Deadline.DoesNotExist:
    examination_date = Deadline.objects.create(id=2)
    print("记录不存在")
except ProgrammingError:
    pass
else:
    pass

try:
    year = Year.objects.get(id=1)
except Year.DoesNotExist:
    year = Year.objects.create(id=1)
    print("记录不存在")
except ProgrammingError:
    pass
else:
    pass

try:
    coefficent = WorkloadCoefficent.objects.get(id=1)
except WorkloadCoefficent.DoesNotExist:
    coefficent = WorkloadCoefficent.objects.create(id=1)
    print("记录不存在")
except ProgrammingError:
    pass
else:
    pass


def workload_sum(user):
    workload = WorkloadInfomation.objects.get(teacher=user)
    W1 = workload.theroy
    W2 = workload.experiment
    W3 = workload.intermship
    W_teaching = float(W1) + float(W2) + float(W3)
    workload.teaching_workload = W_teaching
    W4 = workload.achievement
    W5 = workload.object
    W6 = workload.competition
    W7 = workload.paper
    W_searching = W4 + W5 + W6 + W7
    workload.searching_workload = W_searching
    workload.total = W_searching + W_teaching
    workload.save()


# 单类工作量计算函数
# 理论课
def theory_course_count(theory_course_list, profile):
    W1 = 0
    if theory_course_list:
        print("查询")
    else:
        print("查询失败")
    for course in theory_course_list:
        T = course.hours
        class_schedul = ClassSchedule.objects.filter(
            course_id=course.Course_card, teacher_id=profile, year=year.year
        )
        if class_schedul:
            record_workload = 0
            total_student=0
            for clas in class_schedul:
                total_student += clas.class_id.total
            if total_student <= 60:
                k = 1
            else:
                k = 1 + 0.6*math.log(total_student/60)

            # if total_student <= 40:
            #     k = coefficent.L_L_less_four_zero
            # elif total_student <=85:
            #     k = coefficent.L_L_less_eight_five
            # elif total_student <= 125:
            #     k = coefficent.L_L_less_two_zero_zero
            # elif total_student <= 200:
            #     k = coefficent.L_L_less_two_zero_zero
            # elif total_student > 200:
            #     k = coefficent.L_L_more_two_zero_zero
            # else :
            #     k = 0
            record_workload = 6 + T*k
            W1 += record_workload
            W1 = round(W1, 2)
            class_schedul.update(workload=record_workload)
        else:
            return 0
    try:
        check = WorkloadInfomation.objects.get(teacher=profile.user)
        print("理论课")
        check.theroy = W1
        check.save()
        print(check.theroy)
    except WorkloadInfomation.DoesNotExist:
        print("工作量记录未创建")
        check = WorkloadInfomation.objects.create(teacher=profile.user)
        if check:
            check.save()
            check.theroy = W1
            check.save()
            print(check.theroy)
    workload_sum(profile.user)
    return W1


# 实验课
def experimental_course_count(experimental_course_list, profile):
    W1 = 0
    if experimental_course_list:
        print("查询")
    else:
        print("查询失败")
    for course in experimental_course_list:
        record_workload = 0
        X = course.hours
        class_schedul = ClassSchedule.objects.filter(course_id=course.Course_card, teacher_id=profile)
        if class_schedul:
            R = 0
            for clas in class_schedul:
                R += clas.class_id.total
        else:
            return 0
        if course.course_property == 2:
            L = coefficent.SY_Z_Y
        elif course.course_property == 3:
            L = coefficent.SY_S_J
        elif course.course_property == 4:
            L = coefficent.SY_K_F
        else:
            L = 0
        record_workload = X*L*R
        W1 += record_workload
        class_schedul.update(workload=record_workload)
    W1 = float(W1)
    try:
        check = WorkloadInfomation.objects.get(teacher=profile.user)
        print("实验课")
        check.experiment = W1
        check.save()
        print(check.experiment)
    except WorkloadInfomation.DoesNotExist:
        print("achievement does not exist")
        check = WorkloadInfomation.objects.create(teacher=profile.user)
        if check:
            check.save()
            check.experiment = W1
            check.save()
            print(check.experiment)
    workload_sum(profile.user)
    return W1


# 实习实训
def internship_count(internship_list, profile):
    W = 0
    if internship_list:
        print("查询")
    else:
        print("查询失败")
    for internship in internship_list:
        record_workload = 0
        # 教师数
        profile_list = Profile.objects.filter(from_teacher__course_id=internship).distinct()
        M = profile_list.count()
        M = 1.0*M
        Z = internship.hours
        # for teacher in teacher_list:
        W = 0
        class_schedul = ClassSchedule.objects.filter(course_id=internship, teacher_id=profile)
        if class_schedul:
            R = 0
            for clas in class_schedul:
                R += clas.class_id.total
        else:
            return 0
        if internship.course_property == 5:
            S = coefficent.SX_S_Q_R_S
            # return S
        elif internship.course_property == 6:
            S = float(coefficent.SX_W_D_R_S)
        elif internship.course_property == 7:
            S = float(coefficent.SX_W_D_S_C)
        else:
            S = 0
        record_workload = Z*R*float(S)/M
        W += record_workload
        class_schedul.update(workload=record_workload)
    try:
        check = WorkloadInfomation.objects.get(teacher=profile.user)
        print("实习")
        check.intermship = float(W)
        check.save()
        print(check.intermship)
    except WorkloadInfomation.DoesNotExist:
        print("achievement does not exist")
        check = WorkloadInfomation.objects.create(teacher=profile.user)
        if check:
            check.save()
            check.intermship = float(W)
            check.save()
            print(check.intermship)
    workload_sum(profile.user)
    return 1


# 教研工作量
# 本科教学项目
def teaching_object_count(teach_obj_list,user):
    # if teach_obj_list:
    W = 0
    if teach_obj_list:
        print("查询")
    else:
        print("查询失败")
    for teach_obj in teach_obj_list:
        K = 0
        if teach_obj.type ==1:
            if teach_obj.level == 1:
                K = coefficent.ZX_GJJ
            elif teach_obj.level == 2:
                K = coefficent.ZX_SBJ
            elif teach_obj.level == 3:
                K = coefficent.ZX_XJ
            else:
                K = 0
        elif teach_obj.type == 2:
            if teach_obj.level == 1:
                K = coefficent.KC_GJJ
            elif teach_obj.level == 2:
                K = coefficent.KC_SBJ
            elif teach_obj.level == 3:
                K = coefficent.KC_XJ
            else:
                K = 0
        elif teach_obj.type == 3:
            if teach_obj.level == 1:
                K = coefficent.GCSJ
            else:
                K = 0
        elif teach_obj.type == 4:
            if teach_obj.level == 1:
                K = coefficent.MS_GJJ
            elif teach_obj.level == 2:
                K = coefficent.MS_SBJ
            elif teach_obj.level == 3:
                K = coefficent.MS_XJ
            else:
                K = 0
        elif teach_obj.type == 5:
            if teach_obj.level == 1:
                K = coefficent.DC_GJJ
            elif teach_obj.level == 2:
                K = coefficent.DC_SBJ
            elif teach_obj.level == 3:
                K = coefficent.DC_XJ
            else:
                K = 0
        else:
            K = 0
        teach_obj.workload = K
        teach_obj.save()
        W += K
    try:
        check = WorkloadInfomation.objects.get(teacher=user)
        print("教学项目")
        check.object = W
        check.save()
        print(check.object)
    except WorkloadInfomation.DoesNotExist:
        print("achievement does not exist")
        check = WorkloadInfomation.objects.create(teacher=user)
        if check:
            check.save()
            check.object = W
            check.save()
            print(check.object)
    workload_sum(user)
    return W


# 教学成果项目
def teaching_achievement_count(teach_ach_list, user):
    # if teach_ach_list:
    W = 0
    if teach_ach_list:
        print("查询")
    else:
        print("查询失败")
    for teach_ach in teach_ach_list:
        K = 0
        if teach_ach.type ==1:
            if teach_ach.level == 1:
                K = coefficent.JYLW_HX
            elif teach_ach.level == 2:
                K = coefficent.JYLW_YB
            else:
                K = 0
        elif teach_ach.type == 2:
            if teach_ach.level1 == 1:
                K = coefficent.JGXM_GJJ
            elif teach_ach.level1 == 2:
                K = coefficent.JGXM_SBJ
            elif teach_ach.level1 == 3:
                K = coefficent.JGXM_XJ
            else:
                K = 0
        elif teach_ach.type == 3:
            if teach_ach.level1 == 1:
                if teach_ach.level2 == 1:
                    K = coefficent.JXCG_GT
                elif teach_ach.level2 == 2:
                    K = coefficent.JXCG_GY
                elif teach_ach.level2 == 3:
                    K = coefficent.JXCG_GE
                else:
                    K = 0
            elif teach_ach.level1 == 2:
                if teach_ach.level2 == 1:
                    K = coefficent.JXCG_ST
                elif teach_ach.level2 == 2:
                    K = coefficent.JXCG_SY
                elif teach_ach.level2 == 3:
                    K = coefficent.JXCG_SE
                else:
                    K = 0
            elif teach_ach.level1 == 3:
                if teach_ach.level2 == 1:
                    K = coefficent.JXCG_XT
                elif teach_ach.level2 == 2:
                    K = coefficent.JXCG_XY
                elif teach_ach.level2 == 3:
                    K = coefficent.JXCG_XE
                else:
                    K = 0
        elif teach_ach.type == 4:
            if 1 <= teach_ach.level3 <= 4:
                K = coefficent.JC_TS
            elif teach_ach.level3 == 5:
                K = coefficent.JC_YB
            else:
                K = 0
        else:
            K = 0
        teach_ach.workload = K
        teach_ach.save()
        W += K
    try:
        check = WorkloadInfomation.objects.get(teacher=user)
        print("教学成果")
        check.achievement = W
        check.save()
        print(check.achievement)
    except WorkloadInfomation.DoesNotExist:
        print("achievement does not exist")
        check = WorkloadInfomation.objects.create(teacher=user)
        if check:
            check.save()
            check.achievement = W
            check.save()
            print(check.achievement)
    workload_sum(user)
    return W


# 指导竞赛
def competition_guide_count(competition_guide_list, user):
    # if competition_guide_list:
    W = 0
    if competition_guide_list:
        print("查询")
    else:
        print("查询失败")
    for coompetition_guide in competition_guide_list:
        K = 0
        if coompetition_guide.type ==1:
            if coompetition_guide.level == 1:
                K = coefficent.QGXK_TD
            elif coompetition_guide.level == 2:
                K = coefficent.QGXK_YD
            elif coompetition_guide.level == 3:
                K = coefficent.QGXK_ED
            else:
                K = 0
        elif coompetition_guide.type == 2:
            if coompetition_guide.level == 1:
                K = coefficent.SBJS_TD
            elif coompetition_guide.level == 2:
                K = coefficent.SBJS_YD
            elif coompetition_guide.level == 3:
                K = coefficent.SBJS_ED
            else:
                K = 0
        else:
            K = 0
        coompetition_guide.workload = K
        coompetition_guide.save()
        W += K
    try:
        check = WorkloadInfomation.objects.get(teacher=user)
        print("竞赛指导")
        check.competition = W
        check.save()
        print(check.competition)
    except WorkloadInfomation.DoesNotExist:
        print("achievement does not exist")
        check = WorkloadInfomation.objects.create(teacher=user)
        if check:
            check.save()
            check.competition = W
            check.save()
            print(check.competition)
    workload_sum(user)
    return W


# 论文指导
def paper_guide_count(paper_guide_list, user):
    W = 0
    if paper_guide_list:
        print("查询")
    else:
        print("查询失败")
    for paper_guide in paper_guide_list:
        K = 0
        if paper_guide.level == 1:
            K = coefficent.SCI
        elif paper_guide.level == 2:
            K = coefficent.HX
        elif paper_guide.level == 3:
            K = coefficent.YB
        else:
            K = 6
        paper_guide.workload = K
        paper_guide.save()
        W += K
    try:
        check = WorkloadInfomation.objects.get(teacher=user)
        print("论文指导e")
        check.paper = W
        check.save()
        print(check.paper)
    except WorkloadInfomation.DoesNotExist:
        print("achievement does not exist")
        check = WorkloadInfomation.objects.create(teacher=user)
        if check:
            check.save()
            check.paper = W
            check.save()
            print(check.paper)
    workload_sum(user)
    return W


# 三种身份各自的工作量页面
@login_required
def workload_count(request):
    confirm_data = request.GET.get("confirm_data")
    user = request.user
    authority = user.profile.authority
    if authority == 1 or confirm_data == "alert":
        if confirm_data == "alert":
            alert_teacher_id = request.GET.get("alert_teacher_id")
            try:
                user = User.objects.get(id=alert_teacher_id)
            except User.DoesNotExist:
                return HttpResponse(0)
        workload = WorkloadInfomation.objects.get(teacher=user)
        theory_course_list = ClassSchedule.objects.filter(
            teacher_id=user.profile,
            course_id__course_property=1,
        ).values_list('course_id__course_name', 'workload').distinct()
        theory_course_list_count = theory_course_list.count()
        print(theory_course_list_count)
        # a = (5, 7)
        # print(a)
        if theory_course_list_count == 0:
            theory_course_list_count = 1
        internship_course_list = ClassSchedule.objects.filter(
            teacher_id=user.profile,
            course_id__course_property__range=(5, 7),
        ).values_list('course_id__course_name', 'workload').distinct()
        internship_course_list_count = internship_course_list.count()
        print(internship_course_list_count)
        if internship_course_list_count == 0:
            internship_course_list_count = 1
        experimental_course_list = ClassSchedule.objects.filter(
            teacher_id=user.profile,
            course_id__course_property__range=(2, 4),
        ).values_list('course_id__course_name', 'workload').distinct()
        experimental_course_list_count = experimental_course_list.count()
        print(experimental_course_list_count)
        if experimental_course_list_count == 0:
            experimental_course_list_count = 1
        teaching_workload_count = \
            theory_course_list_count + experimental_course_list_count + internship_course_list_count
        teaching_achievement_list = TeachAchievement.objects.filter(teacher_id=user)
        teaching_achievement_list_count = teaching_achievement_list.count()
        if teaching_achievement_list_count == 0:
            teaching_achievement_list_count = 1
        teaching_object_list = TeachObject.objects.filter(teacher_id=user)
        teaching_object_list_count = teaching_object_list.count()
        if teaching_object_list_count == 0:
            teaching_object_list_count = 1
        guid_competition_list = Competition.objects.filter(teacher_id=user)
        guid_competition_list_count = guid_competition_list.count()
        if guid_competition_list_count == 0:
            guid_competition_list_count = 1
        guid_paper_list = GuidePaper.objects.filter(teacher_id=user)
        guid_paper_list_count = guid_paper_list.count()
        if guid_paper_list_count == 0:
            guid_paper_list_count = 1
        searching_workload_count = \
            teaching_achievement_list_count + \
            teaching_object_list_count + guid_competition_list_count + guid_paper_list_count



        # print(type(theory_course_list))
        # for course in theory_course_list:
        #     print(type(course))
        #     print(len(course))
        #     for i in course:
        #         print(i)
            # print(course.course_id.course_name)
        content = {
            'workload': workload,
            'erro_message': "error",
            'theory_course_list': theory_course_list,
            'experimental_course_list': experimental_course_list,
            'internship_course_list': internship_course_list,
            'teaching_achievement_list': teaching_achievement_list,
            'teaching_object_list': teaching_object_list,
            'guid_competition_list': guid_competition_list,
            'guid_paper_list': guid_paper_list,
            'theory_course_list_count': theory_course_list_count,
            'internship_course_list_count': internship_course_list_count,
            'experimental_course_list_count': experimental_course_list_count,
            'teaching_workload_count': teaching_workload_count,
            'teaching_achievement_list_count': teaching_achievement_list_count,
            'teaching_object_list_count': teaching_object_list_count,
            'guid_competition_list_count': guid_competition_list_count,
            'guid_paper_list_count': guid_paper_list_count,
            'searching_workload_count': searching_workload_count,
        }
        if confirm_data == "alert":
            return render(
                request, 'twss/Academic_officer/workload_total/alert_teacher_workload_info.html', content
            )
        return render(request, "twss/teacher/teacher_workload_count.html", content)
    else:
        if authority == 2:
            workload_list = WorkloadInfomation.objects.filter(teacher__profile__authority=1).order_by("teacher")
        elif authority == 3:
            departartment = user.profile.department
            workload_list = WorkloadInfomation.objects.filter(
                teacher__profile__department=departartment, teacher__profile__authority=1
            ).order_by("teacher")
        else:
            return HttpResponse("you don't have the authority")
        paginator = Paginator(workload_list, 2)
        page = request.POST.get("page")
        try:
            workload_list = paginator.page(page)
        except (EmptyPage, InvalidPage, PageNotAnInteger):
            workload_list = paginator.page(1)
        content = {
            'workload_list': workload_list,
            'erro_message': "error",
        }
        return render(request, "twss/Academic_officer/workload_total/workload_total.html", content)


# 刷新
@csrf_exempt
@login_required
def index_workload_count_select(request):
    user = request.user
    if user.profile.authority == 2:
        items_list = WorkloadInfomation.objects.all().order_by("teacher")
    elif user.profile.authority == 3:
        items_list = WorkloadInfomation.objects.filter(teacher__profile__department=user.profile.department).order_by("teacher")
    else:
        return HttpResponse("You Don't Have The Authority")
    # 排序的实现
    type_order = request.POST.get("type_order")
    if type_order == "name_up_arrow":
        items_list = items_list.order_by("teacher__first_name")
    elif type_order == "name_down_arrow":
        items_list = items_list.order_by("-teacher__first_name")
    elif type_order == "card_up_arrow":
        items_list = items_list.order_by("teacher__profile__stuff_card")
    elif type_order == "card_down_arrow":
        items_list = items_list.order_by("-teacher__profile__stuff_card")
    elif type_order == "department_up_arrow":
        items_list = items_list.order_by("teacher__profile__department")
    elif type_order == "department_down_arrow":
        items_list = items_list.order_by("-teacher__profile__department")
    elif type_order == "teaching_up_arrow":
        items_list = items_list.order_by("teaching_workload")
    elif type_order == "teaching_down_arrow":
        items_list = items_list.order_by("-teaching_workload")
    elif type_order == "searching_up_arrow":
        items_list = items_list.order_by("searching_workload")
    elif type_order == "searching_down_arrow":
        items_list = items_list.order_by("-searching_workload")
    elif type_order == "total_up_arrow":
        items_list = items_list.order_by("total")
    elif type_order == "total_down_arrow":
        items_list = items_list.order_by("-total")
    else:
        pass
    # # 分页
    paginator = Paginator(items_list, 2)
    page = request.POST.get("page")
    try:
        items_list = paginator.page(page)
    except (EmptyPage, InvalidPage, PageNotAnInteger):
        items_list = paginator.page(1)
        # return HttpResponse("error")
    content = {
        'workload_list': items_list,
        'type_order': type_order,
        'erro_message': "记录已审核完毕",

    }
    return render(request, "twss/Academic_officer/workload_total/workload_total_select.html", content)


# 搜索
@csrf_exempt
@login_required
def index_workload_count_search(request):
    search_type = request.POST['search_type']
    search_text = request.POST['search_text']
    print(search_type,search_text)
    user = request.user
    authority = user.profile.authority
    if authority == 3:
        department = user.profile.department
        if search_type == "name":
            items_list = WorkloadInfomation.objects.filter(
                teacher__first_name=search_text, teacher__profile__department=department
            ).order_by("teacher__first_name")
        elif search_type == "card":
            items_list = WorkloadInfomation.objects.filter(
                teacher__profile__stuff_card=search_text, teacher__profile__department=department
            ).order_by("teacher__profile__stuff_card")
        else:
            return HttpResponse("search type error")
    elif authority == 2:
        if search_type == "name":
            items_list = WorkloadInfomation.objects.filter(
                teacher__first_name=search_text
            ).order_by("teacher__first_name")
        elif search_type == "card":
            items_list = WorkloadInfomation.objects.filter(
                teacher__profile__stuff_card=search_text
            ).order_by("teacher__profile__stuff_card")
        else:
            return HttpResponse("search type error")
    else:
        return HttpResponse("you don't have the authority")
    paginator = Paginator(items_list, 2)
    page = request.POST.get("page")
    try:
        items_list = paginator.page(page)
    except (EmptyPage, InvalidPage, PageNotAnInteger):
        items_list = paginator.page(1)

    content = {
        'workload_list': items_list,
        # 'department_id': department_search,
        'erro_message': "No teacher found in the database!",
    }
    return render(request, "twss/Academic_officer/workload_total/workload_total_select.html", content)


# 权限检验
def teacher_authority_check(user):
    if user.profile.authority == 1:
        return True
    else:
        return False


def academic_officer_authority_check(user):
    if user.profile.authority == 2:
        return True
    else:
        return False


def SJ_department_header_authority_check(user):
    if user.profile.authority == 3 and user.profile.department == 1:
        return True
    else:
        return False


def SX_department_header_authority_check(user):
    if user.profile.authority == 3 and user.profile.department == 2:
        return True
    else:
        return False


def SG_department_header_authority_check(user):
    if user.profile.authority == 3 and user.profile.department == 3:
        return True
    else:
        return False


def index_login(request):
    if request.method == "POST":
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data.get("username")
            password = login_form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                if user.profile.authority == 1:
                    # 教师
                    return HttpResponse(1)
                    # return HttpResponseRedirect(reverse("polls:index_teacher"))
                elif user.profile.authority == 2:
                    # 教务员
                    return HttpResponse(2)
                    # return HttpResponseRedirect(reverse("polls:index_academic_officer"))
                elif user.profile.authority == 3:
                    # 各系负责人
                    if user.profile.department == 1:
                        return HttpResponse(31)
                        # return HttpResponseRedirect(reverse("polls:index_D_H_biotechnology"))
                    if user.profile.department == 2:
                        return HttpResponse(32)
                        # return HttpResponseRedirect(reverse("polls:index_D_H_bioinfomation"))
                    if user.profile.department == 3:
                        return HttpResponse(33)
                        # return HttpResponseRedirect(reverse("polls:index_D_H_bioobject"))
                    else:
                        content = {
                            "login_form": login_form,
                        }
                        return render(request, 'twss/login/login_form_select.html', content)
        else:
            content = {
                "login_form": login_form,
            }
            return render(request, 'twss/login/login_form_select.html', content)
    else:
        login_form = LoginForm()
        content = {
            "login_form": login_form,
        }
        return render(request, 'twss/login/index.html', content)


@login_required
def index_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse("polls:index_login"))


@login_required
@user_passes_test(teacher_authority_check)
def index_teacher(request):
    user = request.user
    name = user.first_name
    content = {
        'login_user':name,
    }
    return render(request, "twss/teacher/teacher.html",content)


@csrf_exempt
@login_required
def index_teacher_user_info(request):
    user = request.user
    if request.method == "POST":
        user_info_form = UserInfoEditForm(request.POST, instance=user.profile)
        if user_info_form.is_valid():
            user_info_form.save()
            return HttpResponse(1)
        else:
            content = {
                'user_info_form': user_info_form,
                'user': user,
            }
            return render(request, "twss/teacher/user_info_form.html", content)
    else:
        user_info_form = UserInfoEditForm(instance=user.profile)
        content = {
            'user_info_form': user_info_form,
            'user': user,
        }
        return render(request, "twss/teacher/user_info_form.html", content)


# @login_required
# def index_alert_record_info(request, record_id):           # 记录信息弹窗
#     record = TeachAchievement.objects.get(id=record_id)
#     content={
#         'record': record,
#     }
#     return render(request, "twss/Academic_officer/alert_teacher_info.html", content)

# @login_required
# def index_alert_teacher_workload_info(request, teacher_id):           # 工作量信息弹窗
#     teacher = User.objects.get(id=teacher_id)
#     content={
#         'teacher': teacher,
#     }
#     return render(request, "twss/Academic_officer/alert_teacher_info.html", content)

@login_required
def index_alert_class_info(request, class_id):       # 课程信息弹窗
    clas = Class.objects.get(class_card=class_id)
    content = {
        'class': clas,
    }
    return render(
        request,
        "twss/Academic_officer/basic_infomation/class_schedul/alert_class_info.html",
        content
    )


@login_required
def index_alert_course_info(request, course_id):       # 课程信息弹窗
    course = Course.objects.get(Course_card=course_id)
    content = {
        'course': course,
    }
    return render(
        request,
        "twss/Academic_officer/basic_infomation/class_schedul/alert_course_info.html",
        content
    )


@login_required
def index_alert_teacher_info(request, teacher_id):           # 教师信息弹窗
    teacher = User.objects.get(id=teacher_id)
    content={
        'teacher': teacher,
    }
    return render(request, "twss/Academic_officer/alert_teacher_info.html", content)


@login_required
def index_A_O_teaching_achievement_reject_reason(request):
    reason=request.GET.get("reason")
    reject_id=int(request.GET.get("reject"))
    record=TeachAchievement.objects.get(id=reject_id)
    record.rejectReason=reason
    record.save()
    return HttpResponse(reason)


@login_required
def index_alert_TA_reject_reason(request, items_id):           # 拒绝原因
    item = TeachAchievement.objects.get(id=items_id)
    content={
        'item': item,
    }
    return render(request, "twss/Academic_officer/alert_reject_info.html", content)


@login_required
def index_A_O_teaching_object_reject_reason(request):
    reason = request.GET.get("reason")
    reject_id = int(request.GET.get("reject"))
    record = TeachObject.objects.get(id=reject_id)
    record.rejectReason = reason
    record.save()
    return HttpResponse(reason)


@login_required
def index_alert_OB_reject_reason(request, items_id):           # 拒绝原因
    item = TeachObject.objects.get(id=items_id)
    content={
        'item': item,
    }
    return render(request, "twss/Academic_officer/alert_reject_info.html", content)


@login_required
def index_A_O_competition_guide_reject_reason(request):
    reason=request.GET.get("reason")
    reject_id=int(request.GET.get("reject"))
    record=Competition.objects.get(id=reject_id)
    record.rejectReason=reason
    record.save()
    return HttpResponse(reason)


@login_required
def index_alert_CM_reject_reason(request, items_id):           # 拒绝原因
    item = Competition.objects.get(id=items_id)
    content={
        'item': item,
    }
    return render(request, "twss/Academic_officer/alert_reject_info.html", content)


@login_required
def index_alert_class_reject_reason(request, items_id):           # 拒绝原因
    item = ClassSchedule.objects.get(id=items_id)
    content={
        'item': item,
    }
    return render(request, "twss/Academic_officer/alert_reject_info.html", content)


@login_required
def index_A_O_papaer_guide_reject_reason(request):
    reason=request.GET.get("reason")
    reject_id=int(request.GET.get("reject"))
    record=GuidePaper.objects.get(id=reject_id)
    record.rejectReason=reason
    record.save()
    return HttpResponse(reason)


@login_required
def index_alert_PA_reject_reason(request, items_id):           # 拒绝原因
    item = GuidePaper.objects.get(id=items_id)
    content={
        'item': item,
    }
    return render(request, "twss/Academic_officer/alert_reject_info.html", content)


# 教学
@login_required
@user_passes_test(teacher_authority_check)
def index_teacher_class_theory(request, type):
    profile = request.user.profile
    type = int(type)
    if type == 1:
        class_theory_list = ClassSchedule.objects.filter(teacher_id=profile, year=year.year, course_id__course_property=type).order_by("state")
    elif type == 2:
        class_theory_list = ClassSchedule.objects.filter(
            teacher_id=profile, year=year.year, course_id__course_property__range=(2, 4)).order_by("state")
    elif type == 3:
        class_theory_list = ClassSchedule.objects.filter(teacher_id=profile, year=year.year, course_id__course_property__range=(5,7)).order_by("state")
    else:
        return HttpResponse("error")

    content = {
        'class_schedule_list':class_theory_list,
        "type": type,
    }
    return render(request, "twss/teacher/index_teacher_class_schedule/index_teacher_class_schedule_form.html", content)


@csrf_exempt
@login_required
@user_passes_test(teacher_authority_check)
def index_teacher_new_class_schedule(request):
    if request.method == "POST":
        # 课程工作量计算
        index_new_class_schedule_form = TeacherClassSchedulModelForm(request.POST)
        if index_new_class_schedule_form.is_valid():
            term = index_new_class_schedule_form.cleaned_data.get("term")
            clas = index_new_class_schedule_form.cleaned_data.get("class_id")
            place = index_new_class_schedule_form.cleaned_data.get("place")
            course = index_new_class_schedule_form.cleaned_data.get("course_id")
            profile = request.user.profile
            try:
                add_record = ClassSchedule.objects.create(
                    year=year.year,
                    term=term,
                    class_id=clas,
                    course_id=course,
                    teacher_id=profile,
                    place=place,
                    state=0,
                )
                print("OK")
            except IntegrityError:
                return HttpResponse(2)
# 计算工作量
            if course.course_property == 1:
                course_list = Course.objects.filter(from_course__teacher_id=profile, course_property=1).distinct()
                workload = theory_course_count(course_list, profile)
            elif 1 < course.course_property < 5:
                course_list = Course.objects.filter(from_course__teacher_id=profile,
                                                    course_property__range=(1, 4)).distinct()
                workload = experimental_course_count(course_list, profile)
            elif course.course_property > 4:
                profile_list = Profile.objects.filter(from_teacher__course_id=course).distinct()
                for teacher_profile in profile_list:
                    course_list = Course.objects.filter(from_course__teacher_id=teacher_profile,
                                                        course_property__gt=4).distinct()
                    workload = internship_count(course_list, teacher_profile)
            else:
                return HttpResponse("未知课程类型错误")
            return HttpResponse(1)
        else:
            tp = request.POST.get("type")
            content = {
                'index_new_class_schedule_form': index_new_class_schedule_form,
                'type': tp,
            }
            return render(
                request,
                "twss/teacher/index_teacher_class_schedule/index_teacher_class_schedul_add.html",
                content
            )
    else:
        tp = request.GET.get("type")
        index_new_class_schedule_form=TeacherClassSchedulModelForm()
        content = {
            'index_new_class_schedule_form': index_new_class_schedule_form,
            'type': tp,
        }
        return render(
            request,
            "twss/teacher/index_teacher_class_schedule/index_teacher_class_schedul_add.html",
            content
        )


@csrf_exempt
@login_required
@user_passes_test(teacher_authority_check)
def index_teacher_edit_class_schedule(request, class_schedule_id):
    try:
        edit_record = ClassSchedule.objects.get(id=class_schedule_id)
    except ClassSchedule.DoesNotExist:
        print("未找到该记录")
        return HttpResponse(2)
    if request.method == "POST":
        # 课程工作量计算
        index_new_class_schedule_form = TeacherClassSchedulModelForm(request.POST,instance=edit_record)
        if index_new_class_schedule_form.is_valid():
            index_new_class_schedule_form.save()
            edit_record.state = 0
            edit_record.save()
            course = index_new_class_schedule_form.cleaned_data.get("course_id")
            profile = request.user.profile
                # 计算工作量
            if course.course_property == 1:
                course_list = Course.objects.filter(from_course__teacher_id=profile, course_property=1).distinct()
                workload = theory_course_count(course_list, profile)
            elif 1 < course.course_property < 5:
                course_list = Course.objects.filter(from_course__teacher_id=profile,
                                                    course_property__range=(1, 4)).distinct()
                workload = experimental_course_count(course_list, profile)
            elif course.course_property > 4:
                profile_list = Profile.objects.filter(from_teacher__course_id=course).distinct()
                for teacher_profile in profile_list:
                    course_list = Course.objects.filter(from_course__teacher_id=teacher_profile,
                                                        course_property__gt=4).distinct()
                    workload = internship_count(course_list, teacher_profile)
            else:
                return HttpResponse("未知课程类型错误")
            return HttpResponse(1)
        else:
            tp = request.POST.get("type")
            content = {
                'index_new_class_schedule_form': index_new_class_schedule_form,
                'edit': 1,
                'class_schedule_id': class_schedule_id,
                'type': tp,
            }
            return render(
                request,
                "twss/teacher/index_teacher_class_schedule/index_teacher_class_schedul_add.html",
                content
            )
    else:
        tp = request.GET.get("type")
        index_new_class_schedule_form = TeacherClassSchedulModelForm(instance=edit_record)
        content = {
            'index_new_class_schedule_form': index_new_class_schedule_form,
            'edit': 1,
            'class_schedule_id': class_schedule_id,
            'type': tp,
        }
        return render(
            request,
            "twss/teacher/index_teacher_class_schedule/index_teacher_class_schedul_add.html",
            content
        )


@login_required
@user_passes_test(teacher_authority_check)
def index_teacher_delete_class_schedule(request, record_id):
    try:
        delete_record = ClassSchedule.objects.get(id=record_id)
    except ClassSchedule.DoesNotExist:
        return HttpResponse(2)
    delete_record.delete()
    return HttpResponse(1)


@csrf_exempt
@login_required
@user_passes_test(teacher_authority_check)
def index_teacher_class_select(request, tp):
    profile = request.user.profile
    tp = int(tp)
    if tp == 1:
        class_theory_list = ClassSchedule.objects.filter(teacher_id=profile, year=year.year,
                                                         course_id__course_property=1).order_by("state")
    elif tp == 2:
        class_theory_list = ClassSchedule.objects.filter(teacher_id=profile, year=year.year,
                                                         course_id__course_property__range=(2, 4)).order_by("state")
    elif tp == 3:
        class_theory_list = ClassSchedule.objects.filter(teacher_id=profile, year=year.year,
                                                         course_id__course_property__range=(5, 7)).order_by("state")
    else:
        return HttpResponse("error")

    content = {
        'class_schedule_list': class_theory_list,
        "type": tp,
    }
    return render(
        request,
        "twss/teacher/index_teacher_class_schedule/index_teacher_class_schedule_form_select.html", content
    )


@login_required
def index_teacher_class_reject_reason(request):
    reject = request.GET.get("reject")
    reason = request.GET.get("reason")
    record_reject = ClassSchedule.objects.get(id=reject)
    if record_reject:
        record_reject.rejectReason=reason
        record_reject.save()
        return HttpResponse(reason)
    else:
        return HttpResponse("未找到该记录")


@login_required
def index_teacher_class_pass(request, type):
    chk_value = request.GET.getlist('test')
    query = ClassSchedule.objects.filter(id__in=chk_value)
    for record in query:
        if record.state == 1:
            record.state = 2
            record.save()
    return HttpResponse(1)


# 教学成果
@login_required
@user_passes_test(teacher_authority_check)
@csrf_exempt
def index_teacher_teaching_achievement(request):
    teaching_achievement_list = TeachAchievement.objects.filter(teacher_id__id=request.user.id, year=year.year).order_by("id")
    content = {
        'teaching_achievement_list':teaching_achievement_list,
    }
    return render(request, "twss/teacher/index_teacher_achievement/index_teacher_teaching_achiecement.html", content)


@login_required
@user_passes_test(teacher_authority_check)
@csrf_exempt
def index_teacher_teaching_achievement_select(request):
    if request.POST.get("type"):
        type = request.POST.get("type")
        teaching_achievement_list = TeachAchievement.objects.filter(teacher_id__id=request.user.id, type=type, year=year.year).order_by("id")
        content = {
            'teaching_achievement_list': teaching_achievement_list,
            'type': type,
        }
        return render(request, "twss/teacher/index_teacher_achievement/index_teacher_achievement_select.html", content)
    else:
        teaching_achievement_list = TeachAchievement.objects.filter(teacher_id__id=request.user.id, year=year.year).order_by("id")
        content = {
            'teaching_achievement_list': teaching_achievement_list,
        }
        return render(request, "twss/teacher/index_teacher_achievement/index_teacher_achievement_select.html", content)


@login_required
@user_passes_test(teacher_authority_check)
@csrf_exempt
def index_teacher_new_jiao_gai_xiang_mu(request):
    # 判断截止日期
    now = datetime.now().date()
    if now < input_date.start_time or now > input_date.end_time:
        return HttpResponse(1)
    # 截止日期内则可正常输出
    j_y_l_w = "教研论文"
    j_g_x_m = "教改项目"
    j_x_c_g = "教学成果"
    j_c = "教材"
    user=request.user
    if request.method == "POST":
        type = request.POST["type"]
        if type == j_y_l_w:
            tp = 1
            new_teaching_achievement = user.teachachievement_set.create(type=tp, year=year.year)
            index_new_teaching_achievement_form = JiaoYanLunWenModelForm(
                request.POST, request.FILES, instance=new_teaching_achievement)
        elif type == j_g_x_m:
            tp = 2
            new_teaching_achievement = user.teachachievement_set.create(type=tp, year=year.year)
            index_new_teaching_achievement_form = JiaoGaiXiangMuModelForm(
                request.POST, request.FILES, instance=new_teaching_achievement)
        elif type == j_x_c_g:
            tp = 3
            new_teaching_achievement = user.teachachievement_set.create(type=tp, year=year.year)
            index_new_teaching_achievement_form = JiaoXueChengGuoModelForm(
                request.POST, request.FILES, instance=new_teaching_achievement)
        elif type == j_c:
            tp = 4
            new_teaching_achievement = user.teachachievement_set.create(type=tp, year=year.year)
            index_new_teaching_achievement_form = JiaoCaiModelForm(
                request.POST, request.FILES, instance=new_teaching_achievement)
        else:
            return HttpResponse("error")
        if index_new_teaching_achievement_form.is_valid():
            index_new_teaching_achievement_form.save()
            # 工作量计算
            teach_ach_list = TeachAchievement.objects.filter(teacher_id=user.id, state__gte=2, year=year.year)
            workload = teaching_achievement_count(teach_ach_list, user)
            return HttpResponse(tp)
        else:
            # 返回错误信息
            content = {
                "index_new_teaching_achievement_form": index_new_teaching_achievement_form,
                "type": type,
            }
            return render(request, "twss/teacher/index_teacher_achievement/index_teacher_achievement_add.html",
                          content)
    elif request.GET.get('type'):
        type = int(request.GET.get('type'))
        if type == 1:
            index_new_teaching_achievement_form = JiaoYanLunWenModelForm()
            Type = j_y_l_w
        elif type == 2:
            index_new_teaching_achievement_form = JiaoGaiXiangMuModelForm()
            Type = j_g_x_m
        elif type==3:
            index_new_teaching_achievement_form = JiaoXueChengGuoModelForm()
            Type = j_x_c_g
        elif type==4:
            index_new_teaching_achievement_form = JiaoCaiModelForm()
            Type = j_c
        else:
            return HttpResponse("error")
        content = {
            "index_new_teaching_achievement_form": index_new_teaching_achievement_form,
            "type": Type,
        }
        return render(request, "twss/teacher/index_teacher_achievement/index_teacher_achievement_add.html", content)
    else:
        return HttpResponse("error")


# 审核时不能删除
@login_required
@user_passes_test(teacher_authority_check)
@csrf_exempt
def index_teacher_teaching_achievement_delete(request,achievement_id):
    user = request.user
    delete_record = TeachAchievement.objects.get(id=achievement_id)
    # if delete_record:
    if delete_record.state != 3 and delete_record.state != 4:
        type = delete_record.type
        delete_record.delete()
        # 工作量计算
        teach_ach_list = TeachAchievement.objects.filter(teacher_id=user.id, state__gte=2, year=year.year)
        teaching_achievement_count(teach_ach_list, user)
        return HttpResponse(type)
    else:
        return HttpResponse("该记录正在审核，无法删除！")


@login_required
@user_passes_test(teacher_authority_check)
@csrf_exempt
def index_teacher_teaching_achievement_edit(request,achievement_id):
    user = request.user
    edit_record = TeachAchievement.objects.get(id=achievement_id)
    if edit_record.state == 3 or edit_record.state == 4:
        return HttpResponse(0)
    type = edit_record.type
    j_y_l_w = "教研论文"
    j_g_x_m = "教改项目"
    j_x_c_g = "教学成果"
    j_c = "教材"
    if type == 1:
        type = j_y_l_w
    elif type == 2:
        type = j_g_x_m
    elif type == 3:
        type = j_x_c_g
    elif type == 4:
        type = j_c
    else:
        return HttpResponse("参数错误!")
    if request.method == "POST":
        file = request.FILES.get('file')
        if file:
            print(file.name)
            print()
        else:
            print(2)
        if edit_record.state != 3 and edit_record.state != 4:
            if edit_record.type == 1:
                updata_record_form = JiaoYanLunWenModelForm(request.POST, request.FILES, instance=edit_record)
                # new_form = modelform_factory(TeachAchievement,fields=["achievement","level"])
            elif edit_record.type == 2:
                updata_record_form = JiaoGaiXiangMuModelForm(request.POST, request.FILES, instance=edit_record)
                # new_form = modelform_factory(TeachAchievement,fields=["achievement","level1"])
            elif edit_record.type == 3:
                updata_record_form = JiaoXueChengGuoModelForm(request.POST, request.FILES, instance=edit_record)
                # new_form = modelform_factory(TeachAchievement,fields=["achievement","level1","level2"])
            elif edit_record.type == 4:
                updata_record_form = JiaoCaiModelForm(request.POST, request.FILES, instance=edit_record)
                # new_form = modelform_factory(TeachAchievement,fields=["achievement","level3"])
            else:
                return HttpResponse("type is error")
            edit_record.state = 2
            if updata_record_form.is_valid():
                updata_record_form.save()
                teach_ach_list = TeachAchievement.objects.filter(teacher_id=user.id, state__gte=2, year=year.year)
                # 工作量计算
                teaching_achievement_count(teach_ach_list, user)
                return HttpResponse(edit_record.type)
            else:
                # new_form_veiw = new_form(instance=edit_record)
                content = {
                    "index_new_teaching_achievement_form": updata_record_form,
                    "type": type,
                    "achievement_id": achievement_id,
                }
                return render(request, "twss/teacher/index_teacher_achievement/index_teacher_achievement_edit.html",
                              content)

                # return HttpResponse("error")
        else:
            return HttpResponse("正在审核无法修改")
    else:
        if type == j_y_l_w:
            # new_form = modelform_factory(TeachAchievement,fields=("achievement","level"))
            new_form_veiw = JiaoYanLunWenModelForm(instance=edit_record)
            content = {
                "index_new_teaching_achievement_form": new_form_veiw,
                "type": type,
                "achievement_id": achievement_id,
            }
            return render(request, "twss/teacher/index_teacher_achievement/index_teacher_achievement_edit.html", content)
        elif type == j_g_x_m:
            # new_form = modelform_factory(TeachAchievement, fields=("achievement", "level1"))
            new_form_veiw = JiaoGaiXiangMuModelForm(instance=edit_record)
            content = {
                "index_new_teaching_achievement_form": new_form_veiw,
                "type": type,
                "achievement_id": achievement_id,
            }
            return render(request, "twss/teacher/index_teacher_achievement/index_teacher_achievement_edit.html", content)
        elif type == j_x_c_g:
            new_form_veiw = JiaoXueChengGuoModelForm(instance=edit_record)
            content = {
                "index_new_teaching_achievement_form": new_form_veiw,
                "type": type,
                "achievement_id": achievement_id,
            }
            return render(request, "twss/teacher/index_teacher_achievement/index_teacher_achievement_edit.html", content)
        elif type == j_c:
            new_form_veiw = JiaoCaiModelForm(instance=edit_record)
            content = {
                "index_new_teaching_achievement_form": new_form_veiw,
                "type": type,
                "achievement_id": achievement_id,
            }
            return render(request, "twss/teacher/index_teacher_achievement/index_teacher_achievement_edit.html",
                          content)
        else:
            return HttpResponse("error")


# 教学项目
@login_required
@user_passes_test(teacher_authority_check)
@csrf_exempt
def index_teacher_teaching_object(request):
    teaching_object_list = TeachObject.objects.filter(teacher_id__id=request.user.id, year=year.year).order_by("id")
    content = {
        'teaching_object_list':teaching_object_list,
    }
    return render(request, "twss/teacher/index_teacher_teaching_object/index_teacher_teaching_object.html", content)


@login_required
@user_passes_test(teacher_authority_check)
@csrf_exempt
def index_teacher_teaching_object_select(request):
    if request.POST.get("type"):
        type = request.POST.get("type")
        teaching_object_list = TeachObject.objects.filter(
            teacher_id__id=request.user.id, type=type, year=year.year).order_by("id")
        content = {
            'teaching_object_list': teaching_object_list,
            'type': type
        }
    else:
        teaching_object_list = TeachObject.objects.filter(teacher_id__id=request.user.id, year=year.year).order_by("id")
        content = {
            'teaching_object_list': teaching_object_list,
        }
    return render(request, "twss/teacher/index_teacher_teaching_object/index_teacher_teaching_object_select.html", content)


@login_required
@user_passes_test(teacher_authority_check)
@csrf_exempt
def index_teacher_new_teaching_object(request):
    now = datetime.now().date()
    if now < input_date.start_time or now > input_date.end_time:
        return HttpResponse(1)
    z_t_s_l = "专业、团队及实验中心"
    k_c_l = "课程类"
    g_c_s_j_l = "工程实践"
    j_x_m_s = "教学名师"
    d_c_x_c_y = "大学生创新创业训练"
    user=request.user
    if request.method == "POST":
        typ = request.POST["type"]
        if typ==z_t_s_l:
            tp = 1
        elif typ==k_c_l:
            tp = 2
        elif typ==g_c_s_j_l:
            tp = 3
        elif typ==j_x_m_s:
            tp = 4
        elif typ==d_c_x_c_y:
            tp = 5
        else:
            return HttpResponse("wrong")
        index_new_teaching_object_form = TeachingObjectModelForm(request.POST, request.FILES)
        if index_new_teaching_object_form.is_valid():
            new_teach_object = user.teachobject_set.create(type=tp, year=year.year)
            index_new_teaching_object_form = TeachingObjectModelForm(request.POST, request.FILES,
                                                                     instance=new_teach_object)
            index_new_teaching_object_form.save()
            # 计算工作量
            teach_obj_list = TeachObject.objects.filter(teacher_id=user.id, state__gte=2, year=year.year)
            teaching_object_count(teach_obj_list,user)
            return HttpResponse(tp)
        else:
            # 返回错误信息
            content = {
                "index_new_teaching_object_form": index_new_teaching_object_form,
                "type": typ,
            }
            return render(request, "twss/teacher/index_teacher_teaching_object/index_teacher_teaching_object_add.html",
                          content)

            # print(index_new_teaching_object_form.errors)
            # return HttpResponse("failed")
    elif request.GET.get('type'):
        typ = int(request.GET.get('type'))
        if typ==1:
            Type = z_t_s_l
        elif typ==2:
            Type = k_c_l
        elif typ==3:
            Type = g_c_s_j_l
        elif typ==4:
            Type = j_x_m_s
        elif typ==5:
            Type = d_c_x_c_y
        else:
            return HttpResponse("none")
        index_new_teaching_object_form = TeachingObjectModelForm()
        content = {
            "index_new_teaching_object_form": index_new_teaching_object_form,
            "type": Type,
        }
        return render(request, "twss/teacher/index_teacher_teaching_object/index_teacher_teaching_object_add.html", content)
    else:
        return HttpResponse("error")


@login_required
@user_passes_test(teacher_authority_check)
@csrf_exempt
def index_teacher_teaching_object_delete(request,object_id):
    delete_record = TeachObject.objects.get(id=object_id)
    user = request.user
    if delete_record:
        type = delete_record.type
        delete_record.delete()

        # 计算工作量
        teach_obj_list = TeachObject.objects.filter(teacher_id=user.id, state__gte=2, year=year.year)
        workload = teaching_object_count(teach_obj_list, user)
        return HttpResponse(type)
    else:
        return HttpResponse("you need work harder")


@login_required
@user_passes_test(teacher_authority_check)
@csrf_exempt
def index_teacher_teaching_object_edit(request,object_id):
    edit_record = TeachObject.objects.get(id=object_id)
    user = request.user
    typ = edit_record.type
    z_t_s_l = "专业、团队及实验中心"
    k_c_l = "课程类"
    g_c_s_j_l = "工程实践"
    j_x_m_s = "教学名师"
    d_c_x_c_y = "大学生创新创业训练"
    if typ == 1:
        typ = z_t_s_l
    elif typ == 2:
        typ = k_c_l
    elif typ == 3:
        typ = g_c_s_j_l
    elif typ == 4:
        typ = j_x_m_s
    elif typ == 5:
        typ = d_c_x_c_y
    else:
        return HttpResponse("error")
    if request.method == "POST":
        edit_record.state = 2
        index_new_teaching_object_form = TeachingObjectModelForm(request.POST, request.FILES, instance=edit_record)
        if index_new_teaching_object_form.is_valid():
            index_new_teaching_object_form.save()
            # 计算工作量
            teach_obj_list = TeachObject.objects.filter(teacher_id=user.id, state__gte=2, year=year.year)
            teaching_object_count(teach_obj_list, user)
            return HttpResponse(edit_record.type)
        else:
            content = {
                "index_new_teaching_object_form": index_new_teaching_object_form,
                "type": typ,
                "object_id": object_id,
            }
            return render(request, "twss/teacher/index_teacher_teaching_object/index_teacher_teaching_object_edit.html",
                          content)
    else:
        new_form_veiw = TeachingObjectModelForm(instance=edit_record)
        content = {
            "index_new_teaching_object_form": new_form_veiw,
            "type": typ,
            "object_id": object_id,
        }
        return render(request, "twss/teacher/index_teacher_teaching_object/index_teacher_teaching_object_edit.html", content)


####竞赛指导
@login_required
@user_passes_test(teacher_authority_check)
@csrf_exempt
def index_teacher_competition_guide(request):
    competition_object_list = Competition.objects.filter(teacher_id__id=request.user.id, year=year.year).order_by("id")

    # paginator = Paginator(competition_object_list, 2)
    # page = request.POST.get("page")
    # try:
    #     competition_object_list = paginator.page(page)
    # except (EmptyPage, InvalidPage, PageNotAnInteger):
    #     competition_object_list = paginator.page(1)

    content = {
        'competition_object_list':competition_object_list,
    }
    return render(request, "twss/teacher/index_teacher_competition_guide/index_teacher_competition_guide.html", content)


@login_required
@user_passes_test(teacher_authority_check)
@csrf_exempt
def index_teacher_competition_guide_select(request):
    if request.POST.get("type"):
        type = request.POST.get("type")
        competition_guide_list = Competition.objects.filter(teacher_id__id=request.user.id, type=type, year=year.year).order_by("id")
        content = {
            'competition_guide_list': competition_guide_list,
            'type':type,
        }

    else:
        competition_guide_list = Competition.objects.filter(teacher_id__id=request.user.id, year=year.year).order_by("id")
        content = {
            'competition_guide_list':competition_guide_list,
        }
    return render(request, "twss/teacher/index_teacher_competition_guide/index_teacher_competition_guide_select.html", content)


@csrf_exempt
@login_required
@user_passes_test(teacher_authority_check)
def index_teacher_competition_guide_add(request):
    now = datetime.now().date()
    if now < input_date.start_time or now > input_date.end_time:
        return HttpResponse(1)
    qgj = "全国性大学生学科竞赛"
    sbj = "省部级大学生竞赛"
    user = request.user

    if request.method == "POST":
        typ = request.POST["type"]
        if typ == qgj:
            tp = 1
        elif typ == sbj:
            tp = 2
        else:
            return HttpResponse("wrong")
        new_competition_form = CompetitionGuideModelForm(request.POST, request.FILES)
        if new_competition_form.is_valid():
            new_competition = user.competition_set.create(type=tp, year=year.year)
            new_competition_form = CompetitionGuideModelForm(request.POST, request.FILES, instance=new_competition)
            new_competition_form.save()

            # 计算工作量
            competition_list = Competition.objects.filter(teacher_id=user.id, state__gte=2, year=year.year)
            competition_guide_count(competition_list, user)
            return HttpResponse(tp)
        else:
            content = {
                "index_teacher_competition_form": new_competition_form,
                "type": typ,
            }
            return render(request,
                          "twss/teacher/index_teacher_competition_guide/index_teacher_competition_guide_add.html",
                          content)
    elif request.GET.get('type'):
        typ = int(request.GET.get('type'))
        if typ == 1:
            typ = qgj
        elif typ == 2:
            typ = sbj
        else:
            return HttpResponse("none")
        index_teacher_competition_form = CompetitionGuideModelForm()
        content = {
            "index_teacher_competition_form": index_teacher_competition_form,
            "type": typ,
        }
        return render(request, "twss/teacher/index_teacher_competition_guide/index_teacher_competition_guide_add.html", content)
    else:
        return HttpResponse("error")


@csrf_exempt
@login_required
@user_passes_test(teacher_authority_check)
def index_teacher_competition_guide_delete(request,competition_id):
    delete_record = Competition.objects.get(id=competition_id)
    user = request.user
    if delete_record:
        type = delete_record.type
        delete_record.delete()
        # 计算工作量
        competition_list = Competition.objects.filter(teacher_id=user.id, state__gte=2, year=year.year)
        workload = competition_guide_count(competition_list, user)
        return HttpResponse(type)
    else:
        return HttpResponse("you need work harder")


@csrf_exempt
@login_required
@user_passes_test(teacher_authority_check)
def index_teacher_competition_guide_edit(request,competition_id):
    edit_record = Competition.objects.get(id=competition_id)
    user = request.user
    QGXXKJS = "全国性大学生学科竞赛"
    SBJJS = "省部级大学生竞赛"
    type = edit_record.type
    if type == 1:
        type = QGXXKJS
    elif type == 2:
        type = SBJJS
    else:
        return HttpResponse("error")
    if request.method == "POST":
        # competion_edited = modelform_factory(Competition, fields=("competition", "level"))
        edit_record.state = 2
        index_new_competition_form = CompetitionGuideModelForm(request.POST, request.FILES, instance=edit_record)
        if index_new_competition_form.is_valid():
            index_new_competition_form.save()

            # 计算工作量
            competition_list = Competition.objects.filter(teacher_id=user.id, state__gte=2, year=year.year)
            workload = competition_guide_count(competition_list, user)
            return HttpResponse(edit_record.type)
        else:
            content = {
                "new_competition_form_veiw": index_new_competition_form,
                "type": type,
                "competition_id": competition_id,
            }
            return render(request,
                          "twss/teacher/index_teacher_competition_guide/index_teacher_competition_guide_edit.html",
                          content)

            # return HttpResponse("failed")
    else:
        new_form_veiw = CompetitionGuideModelForm(instance=edit_record)
        content = {
            "new_competition_form_veiw": new_form_veiw,
            "type": type,
            "competition_id": competition_id,
        }
        return render(request, "twss/teacher/index_teacher_competition_guide/index_teacher_competition_guide_edit.html", content)


####论文指导
@csrf_exempt
@login_required
@user_passes_test(teacher_authority_check)
def index_teacher_paper_guide(request):
    paper_guide_list = GuidePaper.objects.filter(teacher_id__id=request.user.id, year=year.year).order_by("id")
    # paginator = Paginator(paper_guide_list, 2)
    # page = request.POST.get("page")
    # try:
    #     paper_guide_list = paginator.page(page)
    # except (EmptyPage, InvalidPage, PageNotAnInteger):
    #     paper_guide_list = paginator.page(1)
    content = {
        'paper_guide_list':paper_guide_list,
    }
    return render(request, "twss/teacher/index_teacher_paper_guide/index_teacher_paper_guide.html", content)


@login_required
@user_passes_test(teacher_authority_check)
@csrf_exempt
def index_teacher_paper_guide_select(request):
    paper_guide_list = GuidePaper.objects.filter(teacher_id__id=request.user.id, year=year.year).order_by("id")
    # paginator = Paginator(paper_guide_list, 2)
    # page = request.POST.get("page")
    # try:
    #     paper_guide_list = paginator.page(page)
    # except (EmptyPage, InvalidPage, PageNotAnInteger):
    #     paper_guide_list = paginator.page(1)
    content = {
        'paper_guide_list':paper_guide_list,
    }
    return render(request, "twss/teacher/index_teacher_paper_guide/index_teacher_paper_guide_select.html", content)


@login_required
@user_passes_test(teacher_authority_check)
@csrf_exempt
def index_teacher_paper_guide_add(request):
    now = datetime.now().date()
    if now < input_date.start_time or now > input_date.end_time:
        return HttpResponse(1)

    user=request.user
    if request.method == "POST":
        new_paper_form = PaperGuideModelForm(request.POST, request.FILES)
        if new_paper_form.is_valid():
            new_paper = GuidePaper.objects.create(teacher_id=user, state=2, year=year.year)
            new_paper.save()
            new_paper_form = PaperGuideModelForm(request.POST, request.FILES, instance=new_paper)
            new_paper_form.save()
            # 计算工作量
            paper_list = GuidePaper.objects.filter(teacher_id=user.id, year=year.year)
            paper_guide_count(paper_list, user)
            return HttpResponse(1)
        else:
            content = {
                "index_teacher_paper_guid_form": new_paper_form,
            }
            return render(request, "twss/teacher/index_teacher_paper_guide/index_teacher_paper_guide_add.html", content)
    else:
        index_teacher_paper_guid_form = PaperGuideModelForm()
        content = {
            "index_teacher_paper_guid_form": index_teacher_paper_guid_form,
        }
        return render(request, "twss/teacher/index_teacher_paper_guide/index_teacher_paper_guide_add.html", content)


@login_required
@user_passes_test(teacher_authority_check)
def index_teacher_paper_guide_delete(request,paper_id):
    delete_record = GuidePaper.objects.get(id=paper_id)
    user = request.user
    if delete_record:
        delete_record.delete()

        paper_list = GuidePaper.objects.filter(teacher_id=user.id, year=year.year)
        # print("OK")
        workload = paper_guide_count(paper_list,user)
        return HttpResponse("good")
    else:
        return HttpResponse("you need work harder")


@login_required
@user_passes_test(teacher_authority_check)
@csrf_exempt
def index_teacher_paper_guide_edit(request,paper_id):
    edit_record = GuidePaper.objects.get(id=paper_id)
    user = request.user
    if request.method == "POST":
        edit_record.state = 2
        index_new_paper_form = PaperGuideModelForm(request.POST, request.FILES, instance=edit_record)
        if index_new_paper_form.is_valid():
            index_new_paper_form.save()
            paper_list = GuidePaper.objects.filter(teacher_id=user.id, state__gte=2, year=year.year)

            workload = paper_guide_count(paper_list,user)
            return HttpResponse(1)
        else:
            content = {
                "new_paper_form_view": index_new_paper_form,
                "paper_id": paper_id,
            }
            return render(request, "twss/teacher/index_teacher_paper_guide/index_teacher_paper_guide_edit.html",
                          content)

            # return HttpResponse("failed")
    else:
        new_form_veiw = PaperGuideModelForm(instance=edit_record)
        content = {
            "new_paper_form_view": new_form_veiw,
            "paper_id": paper_id,
        }
        return render(request, "twss/teacher/index_teacher_paper_guide/index_teacher_paper_guide_edit.html", content)


# 教务员
# 教学成果
# 教务员
# 日期设定
@csrf_exempt
@login_required
@user_passes_test(academic_officer_authority_check)
def index_A_O_input_time_set(request, number):
    num = int(number)
    if num == 1:
        item_date = input_date
        item_date.name = "教师录入起止时间"
        item_date.save()
    elif int(num) == 2:
        item_date = examination_date
        item_date.name = "主任审核起止时间"
        item_date.save()
    else:
        return HttpResponse("参数错误")
    if request.method == "POST":
        new_form = ExaminationDateModelForm(request.POST)
        if new_form.is_valid():
            print(new_form.is_valid())
            print(new_form.errors)
            print(new_form.cleaned_data)
            new_form_save = ExaminationDateModelForm(request.POST, request.FILES, instance=item_date)
            new_form_save.save()
            return HttpResponse(1)
        else:
            content = {
                "item_date": item_date,
                "new_form": new_form,
            }
            return render(request, "twss/Academic_officer/date_set/alert_date_set.html", content)
        pass
    else:
        new_form = InputDateModelForm()
        content = {
            "item_date": item_date,
            "new_form": new_form,
        }
        return render(request, "twss/Academic_officer/date_set/alert_date_set.html", content)


@login_required
@user_passes_test(academic_officer_authority_check)
def index_A_O_set_year(request):
    set_year = request.GET.get("year")
    typ = request.GET.get("type")
    if typ and int(typ) == 1:
        return HttpResponse(year.year)
    else:
        pass
    try:
        year.year = int(set_year)
        year.save()
    except Exception:
        return HttpResponse(0)
    ret = "%s,%d" %(set_year, year.year)
    print(ret)
    return HttpResponse(1)


# 每页项目数设定
@login_required
@user_passes_test(academic_officer_authority_check)
def index_A_O_set_page_item_total(request):
    number = request.GET.get("year")
    typ = request.GET.get("type")
    if typ and int(typ) == 1:
        return HttpResponse(page_item_total.page_item_total)
    else:
        pass
    try:
        page_item_total.page_item_total = int(number)
        page_item_total.save()
    except Exception:
        return HttpResponse(0)
    ret = "%s,%d" % (number, year.year)
    print(ret)
    return HttpResponse(1)


@login_required
@user_passes_test(academic_officer_authority_check)
def index_academic_officer(request):
    user = request.user
    name = user.first_name
    content = {
        'login_user': name,
    }
    return render(request, "twss/Academic_officer/academic_officer.html",content)


@login_required
@csrf_exempt
def index_A_O_SJ_teaching_achievement_select(request, department_id):
    user = request.user
    if user.profile.authority==2:
        teachachievement = [0, 1, 2, 3, 4]
    elif user.profile.authority==3:
        teachachievement = [0, 2, 3]
    else:
        return HttpResponse("You Don't Have The Authority")
    items_list = TeachAchievement.objects.filter(
        year=year.year, state__in=teachachievement,teacher_id__profile__department=department_id).order_by("state")
    # 排序的实现
    type_order = request.POST.get("type_order")
    if type_order == "teacher_up_arrow":
        items_list = items_list.order_by("teacher_id__first_name")
    if type_order == "teacher_down_arrow":
        items_list = items_list.order_by("-teacher_id__first_name")
    if type_order == "id_up_arrow":
        items_list = items_list.order_by("teacher_id__profile__stuff_card")
    if type_order == "id_down_arrow":
        items_list = items_list.order_by("-teacher_id__profile__stuff_card")
    if type_order == "achievement_up_arrow":
        items_list = items_list.order_by("achievement")
    if type_order == "achievement_down_arrow":
        items_list = items_list.order_by("-achievement")
    if type_order == "type_up_arrow":
        items_list = items_list.order_by("type")
    if type_order == "type_down_arrow":
        items_list = items_list.order_by("-type")
    if type_order == "state_up_arrow":
        items_list = items_list.order_by("state")
    if type_order == "state_down_arrow":
        items_list = items_list.order_by("-state")
    else:
        pass
    # # 分页
    paginator = Paginator(items_list, page_item_total.page_item_total)
    page = request.POST.get("page")
    try:
        items_list = paginator.page(page)
    except (EmptyPage, InvalidPage, PageNotAnInteger):
        items_list = paginator.page(1)
    if items_list is not None:
        content = {
            'items_list':items_list,
            'department_id': department_id,
            'type_order':type_order,
        }
        return render(request, "twss/Academic_officer/jiao_xue_cheng_guo/jiao_xue_cheng_guo_select.html", content)
    else:
        content = {
            'erro_message': "记录已审核完毕",
            'department_id': department_id,
        }
        return render(request, "twss/Academic_officer/jiao_xue_cheng_guo/jiao_xue_cheng_guo.html", content)


@login_required
@csrf_exempt
def index_A_O_SJ_teaching_achievement_search(request):
    search_type = request.POST['search_type']
    search_text = request.POST['search_text']
    department_search = request.POST.get("department_search")
    if search_type == "teacher_name":
        items_list = TeachAchievement.objects.filter(
            year=year.year, teacher_id__first_name=search_text, teacher_id__profile__department=department_search
        ).order_by("state")
    elif search_type == "teacher_card":
        items_list = TeachAchievement.objects.filter(
            year=year.year, teacher_id__profile__stuff_card=search_text, teacher_id__profile__department=department_search
        ).order_by("state")
    elif search_type == "achievement":
        items_list = TeachAchievement.objects.filter(
            year=year.year, achievement=search_text, teacher_id__profile__department=department_search
        ).order_by("state")
    else:
        return HttpResponse("search type error")
    paginator = Paginator(items_list, page_item_total.page_item_total)
    page = request.POST.get("page")
    try:
        items_list = paginator.page(page)
    except (EmptyPage, InvalidPage, PageNotAnInteger):
        items_list = paginator.page(1)

    content = {
        'items_list': items_list,
        'department_id': department_search,
        'erro_message': "No Class found in the database!",
    }
    return render(request, "twss/Academic_officer/jiao_xue_cheng_guo/jiao_xue_cheng_guo_select.html", content)


@login_required
@csrf_exempt
def index_A_O_SJ_teaching_achievement(request, department_id):
    user = request.user
    if user.profile.authority == 2:
        teachachievement = [0, 1, 2, 3, 4]
    elif user.profile.authority==3:
        teachachievement = [0, 2, 3]
    else:
        return HttpResponse("You Don't Have The Authority")
    items_list = TeachAchievement.objects.filter(
        year=year.year, state__in=teachachievement, teacher_id__profile__department=department_id
    ).order_by("state")
    paginator = Paginator(items_list, page_item_total.page_item_total)
    page = request.POST.get("page")
    try:
        items_list = paginator.page(page)
    except (EmptyPage, InvalidPage, PageNotAnInteger):
        items_list = paginator.page(1)
    if items_list:
        content = {
            'items_list':items_list,
            'department_id': department_id,
        }
        return render(request, "twss/Academic_officer/jiao_xue_cheng_guo/jiao_xue_cheng_guo.html", content)
    else:
        content = {
            'erro_message': "记录已审核完毕",
            'department_id': department_id,
        }
        return render(request, "twss/Academic_officer/jiao_xue_cheng_guo/jiao_xue_cheng_guo.html", content)


@login_required
def index_A_O_SJ_teaching_achievement_pass(request,department_id):
    chk_value = request.GET.getlist('test')
    query = TeachAchievement.objects.filter(id__in=chk_value)
    user = request.user
    if user.profile.authority == 2:
        # 教务员
        state_number = 4
        query = query.filter(state__in=[1, 3, 4])
    elif user.profile.authority == 3:
        # 系负责人
        if examination_date:
            now = datetime.now().date()
            if now < examination_date.start_time or now > examination_date.end_time:
                return HttpResponse(1)

        state_number = 3
    else:
        return HttpResponse("You Don't Have The Authority")
    query.update(state=state_number)
    return HttpResponse(0)


@csrf_exempt
@login_required
def index_A_O_SJ_teaching_achievement_reject(request, department_id):
    user = request.user
    if request.method == "GET":
        chk_valure = request.GET.get("test")
    else:
        chk_valure = request.POST.get("test")
        type = request.POST.get("type")
    try:
        query = TeachAchievement.objects.get(id=chk_valure)
    except TeachAchievement.DoesNotExist:
        return HttpResponse(2)
    if user.profile.authority == 2:
        # 教务员
        state_number = 1
        if query.state in [0, 2]:
            return HttpResponse(3)
    elif user.profile.authority == 3:
        # 系负责人
        # 判断截止日期
        if examination_date:
            now = datetime.now().date()
            if now < examination_date.start_time or now > examination_date.end_time:
                return HttpResponse(1)
        state_number = 0
    else:
        return HttpResponse("You Don't Have The Authority")

    if request.method == "POST":
        reject_reason = RejectReasonForm(request.POST)
        if reject_reason.is_valid():
            query.rejectReason = reject_reason.cleaned_data.get("reject_reason")
            query.state = state_number
            query.save()
            return HttpResponse(0)
        else:
            content = {
                'type': type,
                'reject_reason_form': reject_reason,
                'query': query,
                'department_id': department_id,
            }
            return render(request, "twss/Academic_officer/alert_reject_info.html", content)
    else:
        reject_reason = RejectReasonForm()
        content = {
            'reject_reason_form': reject_reason,
            'query': query,
            'department_id': department_id,
            'type': '1',
        }
        return render(request, "twss/Academic_officer/alert_reject_info.html", content)
        # pass


# 竞赛指导
@login_required
@csrf_exempt
def index_A_O_SJ_competition_guide_search(request):
    search_type = request.POST['search_type']
    search_text = request.POST['search_text']
    department_search = request.POST.get("department_search")
    if search_type == "teacher_name":
        items_list = Competition.objects.filter(
            year=year.year, teacher_id__first_name=search_text, teacher_id__profile__department=department_search
        ).order_by("state")
    elif search_type == "teacher_card":
        items_list = Competition.objects.filter(
            year=year.year, teacher_id__profile__stuff_card=search_text, teacher_id__profile__department=department_search
        ).order_by("state")
    elif search_type == "competition":
        items_list = Competition.objects.filter(
            year=year.year, competition=search_text, teacher_id__profile__department=department_search
        ).order_by("state")
    else:
        return HttpResponse("search type error")
    paginator = Paginator(items_list, 2)
    page = request.POST.get("page")
    try:
        items_list = paginator.page(page)
    except (EmptyPage, InvalidPage, PageNotAnInteger):
        items_list = paginator.page(1)

    content = {
        'items_list': items_list,
        'department_id': department_search,
        'erro_message': "No Class found in the database!",
    }
    return render(request, "twss/Academic_officer/jing_sai_zhi_dao/jing_sai_zhi_dao_select.html", content)


@login_required
@csrf_exempt
def index_A_O_SJ_competition_guide_select(request, department_id):
    user = request.user
    if user.profile.authority==2:
        teachachievement = [0, 1, 2, 3, 4]
    elif user.profile.authority==3:
        teachachievement = [0, 2, 3]
    else:
        return HttpResponse("You Don't Have The Authority")
    items_list = Competition.objects.filter(
        year=year.year, state__in=teachachievement, teacher_id__profile__department=department_id
    ).order_by("state")
    # 排序的实现
    type_order = request.POST.get("type_order")
    if type_order == "teacher_up_arrow":
        items_list = items_list.order_by("teacher_id__first_name")
    if type_order == "teacher_down_arrow":
        items_list = items_list.order_by("-teacher_id__first_name")
    if type_order == "id_up_arrow":
        items_list = items_list.order_by("teacher_id__profile__stuff_card")
    if type_order == "id_down_arrow":
        items_list = items_list.order_by("-teacher_id__profile__stuff_card")
    if type_order == "achievement_up_arrow":
        items_list = items_list.order_by("competition")
    if type_order == "achievement_down_arrow":
        items_list = items_list.order_by("-competition")
    if type_order == "type_up_arrow":
        items_list = items_list.order_by("type")
    if type_order == "type_down_arrow":
        items_list = items_list.order_by("-type")
    if type_order == "state_up_arrow":
        items_list = items_list.order_by("state")
    if type_order == "state_down_arrow":
        items_list = items_list.order_by("-state")
    else:
        pass
    # # 分页
    paginator = Paginator(items_list, page_item_total.page_item_total)
    page = request.POST.get("page")
    try:
        items_list = paginator.page(page)
    except (EmptyPage, InvalidPage, PageNotAnInteger):
        items_list = paginator.page(1)
        # return HttpResponse("error")
    if items_list is not None:
        content = {
            'items_list':items_list,
            'department_id': department_id,
            'type_order':type_order,
        }
        return render(request, "twss/Academic_officer/jing_sai_zhi_dao/jing_sai_zhi_dao_select.html", content)
    else:
        content = {
            'erro_message': "记录已审核完毕",
            'department_id': department_id,
        }
        return render(request, "twss/Academic_officer/jing_sai_zhi_dao/jing_sai_zhi_dao_select.html", content)


@login_required
@csrf_exempt
def index_A_O_SJ_competition_guide(request,department_id):
    user = request.user
    if user.profile.authority == 2:
        teachachievement = [0, 1, 2, 3, 4]
    elif user.profile.authority == 3:
        teachachievement = [0, 2, 3]
    else:
        return HttpResponse("You Don't Have The Authority")
    items_list = Competition.objects.filter(
        year=year.year, state__in=teachachievement, teacher_id__profile__department=department_id
    ).order_by("state")
    paginator = Paginator(items_list, page_item_total.page_item_total)
    page = request.POST.get("page")
    type = request.POST.get("type")
    try:
        items_list = paginator.page(page)
    except (EmptyPage, InvalidPage, PageNotAnInteger):
        items_list = paginator.page(1)
    if items_list:
        content = {
            'items_list':items_list,
            'department_id': department_id,
        }
        if type:
            return render(request, "twss/Academic_officer/jing_sai_zhi_dao/jing_sai_zhi_dao_select.html", content)
        else:
            return render(request, "twss/Academic_officer/jing_sai_zhi_dao/jing_sai_zhi_dao.html", content)
    else:
        content = {
            'erro_message': "记录已审核完毕",
            'department_id': department_id,
        }
        return render(request, "twss/Academic_officer/jing_sai_zhi_dao/jing_sai_zhi_dao.html", content)


@login_required
@csrf_exempt
def index_A_O_SJ_competition_guide_pass(request,department_id):
    chk_value = request.GET.getlist('test')
    query = Competition.objects.filter(id__in=chk_value)
    user = request.user
    if user.profile.authority == 2:
        # 教务员
        state_number = 4
        query = query.filter(state__in=[1, 3, 4])
    elif user.profile.authority == 3:
        # 系负责人
        # 判断截止日期
        if examination_date:
            now = datetime.now().date()
            if now < examination_date.start_time or now > examination_date.end_time:
                return HttpResponse(1)
        state_number = 3
    else:
        return HttpResponse("You Don't Have The Authority")
    query.update(state=state_number)
    return HttpResponse(0)


@login_required
@csrf_exempt
def index_A_O_SJ_competition_guide_reject(request,department_id):
    user = request.user
    if request.method == "GET":
        chk_valure = request.GET.get("test")
    else:
        chk_valure = request.POST.get("test")
        type = request.POST.get("type")
    try:
        query = Competition.objects.get(id=chk_valure)
    except Competition.DoesNotExist:
        return HttpResponse(2)
    if user.profile.authority == 2:
        # 教务员
        state_number = 1
        if query.state in [0, 2]:
            return HttpResponse(3)
    elif user.profile.authority == 3:
        # 系负责人
        # 判断截止日期
        if examination_date:
            now = datetime.now().date()
            if now < examination_date.start_time or now > examination_date.end_time:
                return HttpResponse(1)
        state_number = 0
    else:
        return HttpResponse("You Don't Have The Authority")

    if request.method == "POST":
        reject_reason = RejectReasonForm(request.POST)
        if reject_reason.is_valid():
            query.rejectReason = reject_reason.cleaned_data.get("reject_reason")
            query.state = state_number
            query.save()
            return HttpResponse(0)
        else:
            content = {
                'type': type,
                'reject_reason_form': reject_reason,
                'query': query,
                'department_id': department_id,
            }
            return render(request, "twss/Academic_officer/alert_reject_info.html", content)
    else:
        reject_reason = RejectReasonForm()
        content = {
            'reject_reason_form': reject_reason,
            'query': query,
            'department_id': department_id,
            'type': '3',
        }
        return render(request, "twss/Academic_officer/alert_reject_info.html", content)


#教学项目
@login_required
@csrf_exempt
def index_A_O_SJ_teaching_object_search(request):
    search_type = request.POST['search_type']
    search_text = request.POST['search_text']
    department_search = request.POST.get("department_search")
    if search_type == "teacher_name":
        items_list = TeachObject.objects.filter(
            year=year.year, teacher_id__first_name=search_text, teacher_id__profile__department=department_search
        ).order_by("state")
    elif search_type == "teacher_card":
        items_list = TeachObject.objects.filter(
            year=year.year, teacher_id__profile__stuff_card=search_text, teacher_id__profile__department=department_search
        ).order_by("state")
    elif search_type == "object":
        items_list = TeachObject.objects.filter(
            year=year.year, object=search_text, teacher_id__profile__department=department_search
        ).order_by("state")
    else:
        return HttpResponse("search type error")
    paginator = Paginator(items_list, 2)
    page = request.POST.get("page")
    try:
        items_list = paginator.page(page)
    except (EmptyPage, InvalidPage, PageNotAnInteger):
        items_list = paginator.page(1)

    content = {
        'items_list': items_list,
        'department_id': department_search,
        'erro_message': "No object found in the database!",
    }
    return render(request, "twss/Academic_officer/jiao_xue_xiang_mu/jiao_xue_xiang_mu_select.html", content)


@login_required
@csrf_exempt
def index_A_O_SJ_teaching_object_select(request,department_id):
    user = request.user
    if user.profile.authority==2:
        teachachievement = [0, 1, 2, 3, 4]
    elif user.profile.authority==3:
        teachachievement = [0, 2, 3]
    else:
        return HttpResponse("You Don't Have The Authority")
    items_list = TeachObject.objects.filter(
        year=year.year, state__in=teachachievement, teacher_id__profile__department=department_id
    ).order_by("state")
    # 排序的实现
    type_order = request.POST.get("type_order")
    if type_order == "teacher_up_arrow":
        items_list = items_list.order_by("teacher_id__first_name")
    if type_order == "teacher_down_arrow":
        items_list = items_list.order_by("-teacher_id__first_name")
    if type_order == "id_up_arrow":
        items_list = items_list.order_by("teacher_id__profile__stuff_card")
    if type_order == "id_down_arrow":
        items_list = items_list.order_by("-teacher_id__profile__stuff_card")
    if type_order == "achievement_up_arrow":
        items_list = items_list.order_by("object")
    if type_order == "achievement_down_arrow":
        items_list = items_list.order_by("-object")
    if type_order == "type_up_arrow":
        items_list = items_list.order_by("type")
    if type_order == "type_down_arrow":
        items_list = items_list.order_by("-type")
    if type_order == "state_up_arrow":
        items_list = items_list.order_by("state")
    if type_order == "state_down_arrow":
        items_list = items_list.order_by("-state")
    else:
        pass
    # # 分页
    paginator = Paginator(items_list, page_item_total.page_item_total)
    page = request.POST.get("page")
    try:
        items_list = paginator.page(page)
    except (EmptyPage, InvalidPage, PageNotAnInteger):
        items_list = paginator.page(1)
    if items_list is not None:
        if type_order:
            content = {
                'items_list': items_list,
                'department_id': department_id,
                'type_order': type_order,
            }
        else:
            content = {
                'items_list':items_list,
                'department_id': department_id,
            }
        return render(request, "twss/Academic_officer/jiao_xue_xiang_mu/jiao_xue_xiang_mu_select.html", content)
    else:
        content = {
            'erro_message': "记录已审核完毕",
            'department_id': department_id,
        }
        return render(request, "twss/Academic_officer/jiao_xue_xiang_mu/jiao_xue_xiang_mu_select.html", content)


@login_required
@csrf_exempt
def index_A_O_SJ_teaching_object(request,department_id):
    user = request.user
    if user.profile.authority == 2:
        query_number = [0, 1, 2, 3, 4]
    elif user.profile.authority == 3:
        query_number = [0, 2, 3]
    else:
        return HttpResponse("You Don't Have The Authority")
    items_list = TeachObject.objects.filter(
        year=year.year, state__in=query_number, teacher_id__profile__department=department_id
    ).order_by("state")
    paginator = Paginator(items_list, page_item_total.page_item_total)
    page = request.POST.get("page")
    type = request.POST.get("type")
    try:
        items_list = paginator.page(page)
    except (EmptyPage, InvalidPage, PageNotAnInteger):
        items_list = paginator.page(1)

    if items_list:
        content = {
            'items_list':items_list,
            'department_id': department_id,
        }
        if type:
            return render(request, "twss/Academic_officer/jiao_xue_xiang_mu/jiao_xue_xiang_mu_select.html", content)
        else:
            return render(request, "twss/Academic_officer/jiao_xue_xiang_mu/jiao_xue_xiang_mu.html", content)

    else:
        content = {
            'erro_message': "记录已审核完毕",
            'department_id': department_id,
        }
        return render(request, "twss/Academic_officer/jiao_xue_xiang_mu/jiao_xue_xiang_mu.html", content)


@login_required
def index_A_O_SJ_teaching_object_pass(request,department_id):
    chk_value = request.GET.getlist('test')
    query = TeachObject.objects.filter(id__in=chk_value)
    user = request.user
    if user.profile.authority == 2:
        # 教务员
        state_number = 4
        query.filter(state__in=[1, 3, 4])
    elif user.profile.authority == 3:
        # 系负责人
        # 判断截止日期
        if examination_date:
            now = datetime.now().date()
            if now < examination_date.start_time or now > examination_date.end_time:
                return HttpResponse(1)
        state_number = 3
    else:
        return HttpResponse("You Don't Have The Authority")
    query.update(state=state_number)
    return HttpResponse(0)


@login_required
def index_A_O_SJ_teaching_object_reject(request,department_id):
    user = request.user
    if request.method == "GET":
        chk_valure = request.GET.get("test")
    else:
        chk_valure = request.POST.get("test")
        type = request.POST.get("type")
    try:
        query = TeachObject.objects.get(id=chk_valure)
    except TeachObject.DoesNotExist:
        return HttpResponse(2)

    if user.profile.authority == 2:
        # 教务员
        state_number = 1
        if query.state in [0, 2]:
            return HttpResponse(3)
    elif user.profile.authority == 3:
        # 系负责人
        # 判断截止日期
        if examination_date:
            now = datetime.now().date()
            if now < examination_date.start_time or now > examination_date.end_time:
                return HttpResponse(1)
        state_number = 0
    else:
        return HttpResponse("You Don't Have The Authority")

    if request.method == "POST":
        reject_reason = RejectReasonForm(request.POST)
        if reject_reason.is_valid():
            query.rejectReason = reject_reason.cleaned_data.get("reject_reason")
            query.state = state_number
            query.save()
            return HttpResponse(0)
        else:
            content = {
                'type': type,
                'reject_reason_form': reject_reason,
                'query': query,
                'department_id': department_id,
            }
            return render(request, "twss/Academic_officer/alert_reject_info.html", content)
    else:
        reject_reason = RejectReasonForm()
        content = {
            'reject_reason_form': reject_reason,
            'query': query,
            'department_id': department_id,
            'type': '2',
        }
        return render(request, "twss/Academic_officer/alert_reject_info.html", content)


# 论文指导
@login_required
@csrf_exempt
def index_A_O_SJ_paper_guide_select(request,department_id):
    user = request.user
    if user.profile.authority==2:
        teachachievement = [0, 1, 2, 3, 4]
    elif user.profile.authority==3:
        teachachievement = [0, 2, 3]
    else:
        return HttpResponse("You Don't Have The Authority")
    items_list = GuidePaper.objects.filter(
        year=year.year, state__in=teachachievement, teacher_id__profile__department=department_id
    ).order_by("state")
    # 排序的实现
    type_order = request.POST.get("type_order")
    if type_order == "teacher_up_arrow":
        items_list = items_list.order_by("teacher_id__first_name")
    if type_order == "teacher_down_arrow":
        items_list = items_list.order_by("-teacher_id__first_name")
    if type_order == "id_up_arrow":
        items_list = items_list.order_by("teacher_id__profile__stuff_card")
    if type_order == "id_down_arrow":
        items_list = items_list.order_by("-teacher_id__profile__stuff_card")
    if type_order == "achievement_up_arrow":
        items_list = items_list.order_by("Paper")
    if type_order == "achievement_down_arrow":
        items_list = items_list.order_by("-Paper")
    if type_order == "type_up_arrow":
        items_list = items_list.order_by("type")
    if type_order == "type_down_arrow":
        items_list = items_list.order_by("-type")
    if type_order == "state_up_arrow":
        items_list = items_list.order_by("state")
    if type_order == "state_down_arrow":
        items_list = items_list.order_by("-state")
    else:
        pass
    # # 分页
    paginator = Paginator(items_list, page_item_total.page_item_total)
    page = request.POST.get("page")
    try:
        items_list = paginator.page(page)
    except (EmptyPage, InvalidPage, PageNotAnInteger):
        items_list = paginator.page(1)
    if items_list is not None:
        if type_order:
            content = {
                'items_list': items_list,
                'department_id': department_id,
                'type_order': type_order,
            }
        else:
            content = {
                'items_list':items_list,
                'department_id': department_id,
            }
        return render(request, "twss/Academic_officer/lun_wen_zhi_dao/lun_wen_zhi_dao_select.html", content)
    else:
        content = {
            'erro_message': "记录已审核完毕",
            'department_id': department_id,
        }
        return render(request, "twss/Academic_officer/lun_wen_zhi_dao/lun_wen_zhi_dao_select.html", content)


@login_required
@csrf_exempt
def index_A_O_SJ_paper_guide_search(request):
    search_type = request.POST['search_type']
    search_text = request.POST['search_text']
    department_search = request.POST.get("department_search")
    if search_type == "teacher_name":
        items_list = GuidePaper.objects.filter(
            year=year.year, teacher_id__first_name=search_text, teacher_id__profile__department=department_search
        ).order_by("state")
    elif search_type == "teacher_card":
        items_list = GuidePaper.objects.filter(
            year=year.year, teacher_id__profile__stuff_card=search_text, teacher_id__profile__department=department_search
        ).order_by("state")
    elif search_type == "paper":
        items_list = GuidePaper.objects.filter(
            year=year.year, Paper=search_text, teacher_id__profile__department=department_search
        ).order_by("state")
    else:
        return HttpResponse("search type error")
    paginator = Paginator(items_list, page_item_total.page_item_total)
    page = request.POST.get("page")
    try:
        items_list = paginator.page(page)
    except (EmptyPage, InvalidPage, PageNotAnInteger):
        items_list = paginator.page(1)

    content = {
        'items_list': items_list,
        'department_id': department_search,
        'erro_message': "No Class found in the database!",
    }
    return render(request, "twss/Academic_officer/lun_wen_zhi_dao/lun_wen_zhi_dao_select.html", content)


@login_required
@csrf_exempt
def index_A_O_SJ_paper_guide(request,department_id):
    user = request.user
    if user.profile.authority == 2:
        query_number = [0, 1, 2, 3, 4]
    elif user.profile.authority == 3:
        query_number = [0, 2, 3]
    else:
        return HttpResponse("You Don't Have The Authority")
    items_list = GuidePaper.objects.filter(
        year=year.year, state__in=query_number, teacher_id__profile__department=department_id
    ).order_by("state")
    paginator = Paginator(items_list, 2)
    page = request.POST.get("page")
    type = request.POST.get("type")
    try:
        items_list = paginator.page(page)
    except (EmptyPage, InvalidPage, PageNotAnInteger):
        items_list = paginator.page(1)

    if items_list:
        content = {
            'items_list':items_list,
            'department_id': department_id,
        }
        if type:
            return render(request, "twss/Academic_officer/lun_wen_zhi_dao/lun_wen_zhi_dao_select.html", content)
        else:
            return render(request, "twss/Academic_officer/lun_wen_zhi_dao/lun_wen_zhi_dao.html", content)

    else:
        content = {
            'erro_message': "记录已审核完毕",
            'department_id': department_id,
        }
        return render(request, "twss/Academic_officer/lun_wen_zhi_dao/lun_wen_zhi_dao.html", content)


@login_required
def index_A_O_SJ_paper_guide_pass(request,department_id):
    chk_value = request.GET.getlist('test')
    query = GuidePaper.objects.filter(id__in=chk_value)
    user = request.user
    if user.profile.authority == 2:
        # 教务员
        state_number = 4
        query = query.filter(state__in=[1, 3, 4])
    elif user.profile.authority == 3:
        # 系负责人
        # 判断截止日期
        if examination_date:
            now = datetime.now().date()
            if now < examination_date.start_time or now > examination_date.end_time:
                return HttpResponse(1)
        state_number = 3
    else:
        return HttpResponse("You Don't Have The Authority")
    query.update(state=state_number)
    return HttpResponse(0)


@login_required
def index_A_O_SJ_paper_guide_reject(request,department_id):
    user = request.user
    if request.method == "GET":
        chk_valure = request.GET.get("test")
    else:
        chk_valure = request.POST.get("test")
        type = request.POST.get("type")
    try:
        query = GuidePaper.objects.get(id=chk_valure)
    except GuidePaper.DoesNotExist:
        return HttpResponse(2)

    if user.profile.authority == 2:
        # 教务员
        state_number = 1
        if query.state in [0, 2]:
            return HttpResponse(3)

    elif user.profile.authority == 3:
        # 系负责人
        # 判断截止日期
        if examination_date:
            now = datetime.now().date()
            if now < examination_date.start_time or now > examination_date.end_time:
                return HttpResponse(1)
        state_number = 0
    else:
        return HttpResponse("You Don't Have The Authority")

    if request.method == "POST":
        reject_reason = RejectReasonForm(request.POST)
        if reject_reason.is_valid():
            query.rejectReason = reject_reason.cleaned_data.get("reject_reason")
            query.state = state_number
            query.save()
            return HttpResponse(0)
        else:
            content = {
                'type': type,
                'reject_reason_form': reject_reason,
                'query': query,
                'department_id': department_id,
            }
            return render(request, "twss/Academic_officer/alert_reject_info.html", content)
    else:
        reject_reason = RejectReasonForm()
        content = {
            'reject_reason_form': reject_reason,
            'query': query,
            'department_id': department_id,
            'type': '4',
        }
        return render(request, "twss/Academic_officer/alert_reject_info.html", content)


#系负责人
@login_required
@user_passes_test(SX_department_header_authority_check)
def index_D_H_bioinfomation(request):
    user = request.user
    name = user.first_name
    content = {
        'login_user': name,
    }
    return render(request,"twss/department_header/bioinfomation_header/bioinfomation_header.html",content)


@login_required
@user_passes_test(SG_department_header_authority_check)
def index_D_H_bioobject(request):
    user = request.user
    name = user.first_name
    content = {
        'login_user': name,
    }
    return render(request,"twss/department_header/bioobject_header/bioobject_header.html",content)


@login_required
@user_passes_test(SJ_department_header_authority_check)
def index_D_H_biotechnology(request):
    user = request.user
    name = user.first_name
    content = {
        'login_user': name,
    }
    return render(request,"twss/department_header/biotechnology_header/biotechnology_header.html",content)


# 师资管理
@login_required
@csrf_exempt
def management_of_teacher_resource(request,department_id):
    authority = request.user.profile.authority
    if authority == 2:
        teacher_list = User.objects.filter(is_active=True).order_by("profile__stuff_card")
    elif authority == 3:
        teacher_list = User.objects.filter(profile__department=department_id, is_active=True, profile__authority=1).order_by("id")
    else:
        return HttpResponse(0)
    paginator = Paginator(teacher_list, page_item_total.page_item_total)
    page = request.POST.get("page")
    try:
        teacher_list = paginator.page(page)
    except (EmptyPage, InvalidPage, PageNotAnInteger):
        teacher_list = paginator.page(1)

    content = {
        'teacher_list':teacher_list,
        'erro_message': "No teacher in your department found!",
        'department': department_id,
    }
    return render(request, "twss/department_header/management_of_teacher_resource/management_of_teacher_resource.html", content)


@login_required
@csrf_exempt
def management_of_teacher_resource_search(request, department_id):
    search_type = request.POST['search_type']
    search_text = request.POST['search_text']
    if search_type == "stuff_card":
        if search_text:
            try:
                search_text = int(search_text)
                if department_id == '4':
                    teacher_list = User.objects.filter(profile__stuff_card__contains=search_text,
                                                       is_active=True).order_by("id")
                else:
                    teacher_list = User.objects.filter(profile__stuff_card__contains=search_text,
                                                       profile__department=department_id, is_active=True).order_by("id")
            except Exception:
                return HttpResponse(1)
        else:
            return HttpResponse(1)
    else:
        if search_text and isinstance(search_text, str):
            pass
        else:
            return HttpResponse(1)
        if department_id == '4':
            teacher_list = User.objects.filter(first_name__contains=search_text,
                                               is_active=True).order_by("id")
        else:
            teacher_list = User.objects.filter(first_name__contains=search_text, profile__department=department_id, is_active=True).order_by("id")
    paginator = Paginator(teacher_list, page_item_total.page_item_total)
    page = request.POST.get("page")
    try:
        teacher_list = paginator.page(page)
    except (EmptyPage, InvalidPage, PageNotAnInteger):
        teacher_list = paginator.page(1)

    content = {
        'teacher_list': teacher_list,
        'erro_message': "No teacher in your department found!",
        'department': department_id,
    }
    return render(request,
                  "twss/department_header/management_of_teacher_resource/management_of_teacher_resource_select.html",content)


@login_required
@csrf_exempt
def management_of_teacher_resource_select(request):
    user = request.user
    department_id = user.profile.department
    department = request.POST.get("department")
    if department == '4':
        items_list = User.objects.filter(is_active=True).order_by("id")
    else:
        items_list = User.objects.filter(profile__department=department_id, is_active=True).order_by("id")
    type_order = request.POST.get("type_order")
    if type_order == "card_up_arrow":
        items_list = items_list.order_by("profile__stuff_card")
    if type_order == "card_down_arrow":
        items_list = items_list.order_by("-profile__stuff_card")
    if type_order == "name_up_arrow":
        items_list = items_list.order_by("first_name")
    if type_order == "name_down_arrow":
        items_list = items_list.order_by("-first_name")
    if type_order == "title_up_arrow":
        items_list = items_list.order_by("profile__title")
    if type_order == "title_down_arrow":
        items_list = items_list.order_by("-profile__title")
    if type_order == "authority_up_arrow":
        items_list = items_list.order_by("profile__authority")
    if type_order == "authority_down_arrow":
        items_list = items_list.order_by("-profile__authority")
    if type_order == "department_up_arrow":
        items_list = items_list.order_by("profile__department")
    if type_order == "department_down_arrow":
        items_list = items_list.order_by("-profile__department")
    else:
        pass
    paginator = Paginator(items_list, page_item_total.page_item_total)
    page = request.POST.get("page")
    try:
        items_list = paginator.page(page)
    except (EmptyPage, InvalidPage, PageNotAnInteger):
        items_list = paginator.page(1)

    content = {
        'type_order':type_order,
        'teacher_list':items_list,
        'department':department,
        'erro_message': "No teacher in your department found!",
    }
    return render(request,
                  "twss/department_header/management_of_teacher_resource/management_of_teacher_resource_select.html",content)


class ChangepwdForm(forms.Form):
    oldpassword = forms.CharField(
        required=True,
        label=u"原密码",
        error_messages={'required': u'请输入原密码'},
        widget=forms.PasswordInput(
            attrs={
                'placeholder':u"原密码",
            }
        ),
    )
    newpassword1 = forms.CharField(
        required=True,
        label=u"新密码",
        error_messages={'required': u'请输入新密码'},
        widget=forms.PasswordInput(
            attrs={
                'placeholder': u"新密码",
            }
        ),
    )
    newpassword2 = forms.CharField(
        required=True,
        label=u"确认密码",
        error_messages={'required': u'请再次输入新密码'},
        widget=forms.PasswordInput(
            attrs={
                'placeholder':u"确认密码",
            }
        ),
    )


@login_required
@csrf_exempt
def index_change_password(request):
    if request.method == "POST":
        username = request.user.username
        oldpassword = request.POST.get('old_password')
        user = authenticate(username=username, password=oldpassword)
        if user is not None and user.is_active:
            newpassword1 = request.POST.get('new_password1')
            newpassword2 = request.POST.get('new_password2')
            if newpassword1==newpassword2:
                user.set_password(newpassword1)
                user.save()
                return HttpResponse("OK")
            else:
                return HttpResponse("两次密码不一致")
        else:
            return HttpResponse("原密码错误")
    else:
        form = ChangepwdForm()
        content={
            'form':form,
        }
        return render(request,"twss/teacher/change_password.html",content)


@login_required
@csrf_exempt
def index_regisiter(request, type):
    request_user = request.user
    department = request_user.profile.department
    if request.method == "POST":
        register_form = RegisterForm(request.POST)
        profile_form = ProfileModelForm(request.POST)
        if register_form.is_valid() and profile_form.is_valid():
            user_data = register_form.cleaned_data
            user_name = user_data.get('username')
            password = user_data.get('password_1')
            first_name = user_data.get('first_name')
            added_user = User.objects.create_user(username=user_name, email=None, password=password)
            added_user.first_name = first_name
            added_user.save()
            user_profile = Profile.objects.create(user=added_user, stuff_card=profile_form.cleaned_data.get('stuff_card'))
            profile = ProfileModelForm(request.POST, instance=user_profile)
            profile.save()
            return HttpResponse(2)
        else:
            content = {
                'profile_form': profile_form,
                'register_form': register_form,
                'type': type,
                'department': department,
            }
            return render(request, 'twss/login/register_form.html', content)
        pass
    else:
        profile_form=ProfileModelForm()
        register_form = RegisterForm()
        content ={
            'profile_form': profile_form,
            'register_form': register_form,
            'type': type,
            'department': department,
        }
        return render(request, 'twss/login/register_form.html', content)


@login_required
@csrf_exempt
def MOTRS_teacher_info_edit(request, teacher_id):
    edit_teacher = User.objects.get(id=teacher_id, is_active=True)
    department = request.GET.get("department")
    if request.method == "POST":
        password_reset = request.POST.get("password_reset")
        if password_reset:
            password_reset = int(password_reset)
        profile_form = ProfileEditModelForm(request.POST, instance=edit_teacher.profile)
        user_name_form = UserNameForm(request.POST, instance=edit_teacher)
        if profile_form.is_valid() and user_name_form.is_valid():
            profile_form.save()
            user_name_form.save()
            if password_reset == 1:
                edit_teacher.set_password(edit_teacher.profile.stuff_card)
                edit_teacher.save()
            return HttpResponse(1)
        else:
            type_order = request.POST.get("type_order")
            page = request.POST.get("page")
            content = {
                'edit_teacher': edit_teacher,
                "new_form_veiw": profile_form,
                "user_name_form": user_name_form,
                "teacher_id": teacher_id,
                "department": department,
                "type_order": type_order,
                "page": page,
            }
            return render(
                request,
                "twss/department_header/management_of_teacher_resource/management_of_teacher_resource_edit.html",
                content
            )
    else:
        type_order = request.GET.get("type_order")
        page = request.GET.get("page")
        profile_form = ProfileEditModelForm(instance=edit_teacher.profile)
        user_name_form = UserNameForm(instance=edit_teacher)
        content = {
            'edit_teacher': edit_teacher,
            "new_form_veiw": profile_form,
            "user_name_form": user_name_form,
            "teacher_id": teacher_id,
            "department": department,
            "type_order": type_order,
            "page": page,
        }
        return render(request, "twss/department_header/management_of_teacher_resource/management_of_teacher_resource_edit.html", content)


def MOTRS_teacher_info_delete(request, teacher_id):
        delete_record = User.objects.get(id=teacher_id, is_active=True)
        if delete_record:
            if delete_record.is_staff:
                return HttpResponse("该用户为管理员，无法删除！")
            else:
                if delete_record.profile.authority == 2:
                    return HttpResponse("该用户为教务员，无法删除！")
                else:
                    delete_record.delete()
                    return HttpResponse("已删除")
        else:
            return HttpResponse("未找到记录")


@login_required
@user_passes_test(academic_officer_authority_check)
@csrf_exempt
def index_AO_class_info(request):
    class_info_list = Class.objects.all().order_by("class_card")
    paginator = Paginator(class_info_list, page_item_total.page_item_total)
    page = request.POST.get("page")
    try:
        class_info_list = paginator.page(page)
    except (EmptyPage, InvalidPage, PageNotAnInteger):
        class_info_list = paginator.page(1)
    content = {
        'class_info_list':class_info_list,
        'erro_message':"未找到班级！"
    }
    return render(request, "twss/Academic_officer/basic_infomation/class_info/class_info.html", content)


@login_required
@user_passes_test(academic_officer_authority_check)
@csrf_exempt
def index_AO_class_info_select(request):
    class_info_list = Class.objects.all().order_by("class_card")
    type_order = request.POST.get("type_order")
    if type_order == "name_up_arrow":
        class_info_list = class_info_list.order_by("class_name")
    elif type_order == "name_down_arrow":
        class_info_list = class_info_list.order_by("-class_name")
    elif type_order == "major_up_arrow":
        class_info_list = class_info_list.order_by("class_major")
    elif type_order == "major_down_arrow":
        class_info_list = class_info_list.order_by("-class_major")
    elif type_order == "grade_up_arrow":
        class_info_list = class_info_list.order_by("grade")
    elif type_order == "grade_down_arrow":
        class_info_list = class_info_list.order_by("-grade")
    elif type_order == "total_up_arrow":
        class_info_list = class_info_list.order_by("total")
    elif type_order == "total_down_arrow":
        class_info_list = class_info_list.order_by("-total")
    elif type_order == "card_up_arrow":
        class_info_list = class_info_list.order_by("class_card")
    elif type_order == "card_down_arrow":
        class_info_list = class_info_list.order_by("-class_card")
    paginator = Paginator(class_info_list, page_item_total.page_item_total)
    page = request.POST.get("page")

    try:
        class_info_list = paginator.page(page)
    except (EmptyPage, InvalidPage, PageNotAnInteger):
        class_info_list = paginator.page(1)
    if type_order:
        content = {
            'class_info_list': class_info_list,
            'type_order':type_order,
            'erro_message':"未找到班级!",
        }
    else:
        content = {
            'class_info_list': class_info_list,
            'erro_message':"未找到班级",
        }
    return render(request, "twss/Academic_officer/basic_infomation/class_info/class_info_select.html", content)


@login_required
@user_passes_test(academic_officer_authority_check)
@csrf_exempt
def index_AO_class_info_add(request):
    if request.method == "POST":
        index_new_class_form = ClassModelForm(request.POST)
        if index_new_class_form.is_valid():
            index_new_class_form.save()
            return HttpResponse(1)
        else:
            content = {
                "index_new_class_form": index_new_class_form,
            }
            return render(request, "twss/Academic_officer/basic_infomation/class_info/class_info_add.html", content)

    else:
        index_new_class_form = ClassModelForm()
        content = {
            "index_new_class_form": index_new_class_form,
        }
        return render(request, "twss/Academic_officer/basic_infomation/class_info/class_info_add.html", content)


@login_required
@user_passes_test(academic_officer_authority_check)
@csrf_exempt
def index_AO_class_info_delete(request,class_id):
    delete_record = Class.objects.get(class_card=class_id)
    if delete_record:
        delete_record.delete()
        return HttpResponse("good")
    else:
        return HttpResponse("you need work harder")


@login_required
@user_passes_test(academic_officer_authority_check)
@csrf_exempt
def index_AO_class_info_edit(request,class_id):
    class_edit = Class.objects.get(class_card=class_id)
    if request.method == "POST":
        index_new_class_form = ClassModelForm(request.POST, instance=class_edit)
        if index_new_class_form.is_valid():
            index_new_class_form.save()
            return HttpResponse(1)
        else:
            type_order = request.POST.get("type_order")
            page = request.POST.get("page")
            content = {
                "index_new_class_form": index_new_class_form,
                "class_id": class_id,
                "type_order": type_order,
                "page": page,
            }
            return render(request, "twss/Academic_officer/basic_infomation/class_info/class_info_edit.html", content)
            # return HttpResponse("error:you can't edit the class")
    else:
        type_order = request.GET.get("type_order")
        page = request.GET.get("page")
        index_new_class_form = ClassModelForm(instance=class_edit)
        content = {
            "index_new_class_form": index_new_class_form,
            "class_id": class_id,
            "type_order": type_order,
            "page": page,
        }
        return render(request, "twss/Academic_officer/basic_infomation/class_info/class_info_edit.html", content)


@login_required
@user_passes_test(academic_officer_authority_check)
@csrf_exempt
def index_AO_class_info_search(request):
    search_type = request.POST['search_type']
    search_text = request.POST['search_text']
    if search_type == "class_name":
        if search_text and isinstance(search_text, str):
            class_info_list = Class.objects.filter(class_name__contains=search_text).order_by("class_card")
        else:
            return HttpResponse(1)
    elif search_type == "class_card":
        if search_text:
            try:
                search_text = int(search_text)
                class_info_list = Class.objects.filter(class_card__contains=search_text).order_by("class_card")
            except Exception:
                return HttpResponse(1)
        else:
            return HttpResponse(1)
    else:
        return HttpResponse("search type error")
    paginator = Paginator(class_info_list, page_item_total.page_item_total)
    page = request.POST.get("page")
    try:
        class_info_list = paginator.page(page)
    except (EmptyPage, InvalidPage, PageNotAnInteger):
        class_info_list = paginator.page(1)

    content = {
        'class_info_list': class_info_list,
        'erro_message': "No Class found in the database!",
    }
    return render(request, "twss/Academic_officer/basic_infomation/class_info/class_info_select.html",content)


# 课程信息

@login_required
@user_passes_test(academic_officer_authority_check)
@csrf_exempt
def index_AO_course_info(request):
    course_info_list = Course.objects.all().order_by("Course_card")
    paginator = Paginator(course_info_list, page_item_total.page_item_total)
    page = request.POST.get("page")
    try:
        course_info_list = paginator.page(page)
    except (EmptyPage, InvalidPage, PageNotAnInteger):
        course_info_list = paginator.page(1)

    content = {
        'course_info_list':course_info_list,
        'erro_message': "未找到课程！"

    }
    return render(request, "twss/Academic_officer/basic_infomation/course_info/course_info.html", content)


@login_required
@user_passes_test(academic_officer_authority_check)
@csrf_exempt
def index_AO_course_info_select(request):
    course_info_list = Course.objects.all().order_by("Course_card")
    type_order = request.POST.get("type_order")
    if type_order == "name_up_arrow":
        course_info_list = course_info_list.order_by("course_name")
    if type_order == "name_down_arrow":
        course_info_list = course_info_list.order_by("-course_name")
    if type_order == "card_up_arrow":
        course_info_list = course_info_list.order_by("Course_card")
    if type_order == "card_down_arrow":
        course_info_list = course_info_list.order_by("-Course_card")
    if type_order == "type_up_arrow":
        course_info_list = course_info_list.order_by("course_property")
    if type_order == "type_down_arrow":
        course_info_list = course_info_list.order_by("-course_property")
    if type_order == "hour_up_arrow":
        course_info_list = course_info_list.order_by("hours")
    if type_order == "hour_down_arrow":
        course_info_list = course_info_list.order_by("-hours")
    if type_order == "score_up_arrow":
        course_info_list = course_info_list.order_by("credit")
    if type_order == "score_down_arrow":
        course_info_list = course_info_list.order_by("-credit")
    paginator = Paginator(course_info_list, page_item_total.page_item_total)
    page = request.POST.get("page")
    try:
        course_info_list = paginator.page(page)
    except (EmptyPage, InvalidPage, PageNotAnInteger):
        course_info_list = paginator.page(1)

    if type_order:
        content = {
            'course_info_list': course_info_list,
            'type_order':type_order,
            'erro_message': "未找到课程！",
        }
    else:
        content = {
            'course_info_list': course_info_list,
        }
    return render(request, "twss/Academic_officer/basic_infomation/course_info/course_info_select.html", content)


@login_required
@user_passes_test(academic_officer_authority_check)
@csrf_exempt
def index_AO_course_info_add(request):
    if request.method == "POST":
        index_new_ourse_form = CourseModelForm(request.POST)
        if index_new_ourse_form.is_valid():
            index_new_ourse_form.save()
            return HttpResponse(1)
        else:
            content = {
                "index_new_course_form": index_new_ourse_form,
            }
            return render(request, "twss/Academic_officer/basic_infomation/course_info/course_info_add.html", content)
    else:
        index_new_ourse_form = CourseModelForm()
        content = {
            "index_new_course_form": index_new_ourse_form,
        }
        return render(request, "twss/Academic_officer/basic_infomation/course_info/course_info_add.html", content)


def index_AO_course_info_delete(request,course_id):
    delete_record = Course.objects.get(Course_card=course_id)
    if delete_record:
        delete_record.delete()
        return HttpResponse("good")
    else:
        return HttpResponse("you can't delete this course")


@login_required
@user_passes_test(academic_officer_authority_check)
@csrf_exempt
def index_AO_course_info_edit(request, course_id):
    course_edit = Course.objects.get(Course_card=course_id)
    if request.method == "POST":
        index_new_course_form = CourseModelForm(request.POST, instance=course_edit)
        if index_new_course_form.is_valid():
            index_new_course_form.save()
            return HttpResponse(1)
        else:
            type_order = request.POST.get("type_order")
            page = request.POST.get("page")
            content = {
                "index_new_course_form": index_new_course_form,
                "course_id": course_id,
                "type_order": type_order,
                "page": page,
            }
            return render(
                request, "twss/Academic_officer/basic_infomation/course_info/course_info_edit.html", content
            )
    else:
        type_order = request.GET.get("type_order")
        page = request.GET.get("page")
        # print(str(page))
        index_new_course_form = CourseModelForm(instance=course_edit)
        content = {
            "index_new_course_form": index_new_course_form,
            "course_id":course_id,
            "type_order":type_order,
            "page": page,
        }
        return render(request, "twss/Academic_officer/basic_infomation/course_info/course_info_edit.html", content)


@login_required
@user_passes_test(academic_officer_authority_check)
@csrf_exempt
def index_AO_course_info_search(request):
    search_type = request.POST['search_type']
    search_text = request.POST['search_text']
    if search_type == "course_name":
        if search_text and isinstance(search_text, str):
            course_info_list = Course.objects.filter(course_name__contains=search_text).order_by("Course_card")
        else:
            return HttpResponse(1)
    elif search_type == "course_card":
        if search_text:
            try:
                search_text = int(search_text)
                course_info_list = Course.objects.filter(Course_card__contains=search_text).order_by("Course_card")
            except Exception:
                return HttpResponse(1)
        else:
            return HttpResponse(1)
    else:
        content = {
            'erro_message': "No Course in your department found!",
        }
        return render(request, "twss/Academic_officer/basic_infomation/course_info/course_info_select.html",
                      content)
    paginator = Paginator(course_info_list, page_item_total.page_item_total)
    page = request.POST.get("page")
    try:
        course_info_list = paginator.page(page)
    except (EmptyPage, InvalidPage, PageNotAnInteger):
        course_info_list = paginator.page(1)

    content = {
        'course_info_list': course_info_list,
        'erro_message': "No Course in your department found!",
    }
    return render(request, "twss/Academic_officer/basic_infomation/course_info/course_info_select.html",content)


@login_required
@user_passes_test(academic_officer_authority_check)
@csrf_exempt
def index_AO_class_schedul(request):
    class_schedul_list = ClassSchedule.objects.filter(year=year.year).order_by("state")
    paginator = Paginator(class_schedul_list, page_item_total.page_item_total)
    page = request.POST.get("page")
    try:
        class_schedul_list = paginator.page(page)
    except (EmptyPage, InvalidPage, PageNotAnInteger):
        class_schedul_list = paginator.page(1)
    content = {
        'class_schedul_list':class_schedul_list,
        'error_message':"未找到课表!"
    }
    return render(request, "twss/Academic_officer/basic_infomation/class_schedul/class_schedul.html", content)


# 搜索函数
def index_AO_class_schedul_search_function(search_type,search_text):
    if search_type == "year":
        if search_text:
            try:
                search_text = int(search_text)
                class_schedul_list = ClassSchedule.objects.filter(year=search_text).order_by("id")
            except Exception:
                return 0
        else:
            return 0
    elif search_type == "term":
        if search_text and isinstance(search_text, str):
            if search_text == "春期":
                search_text = 1
            elif search_text == "秋期":
                search_text = 2
            else:
                return 0
            class_schedul_list = ClassSchedule.objects.filter(term=search_text, year=year.year).order_by("id")
        else:
            return 0
    elif search_type == "teacher":
        if search_text and isinstance(search_text, str):
            class_schedul_list = ClassSchedule.objects.filter(teacher_id__first_name=search_text, year=year.year).order_by("id")
        else:
            return 0
    elif search_type == "class":
        if search_text and isinstance(search_text, str):
            class_schedul_list = ClassSchedule.objects.filter(class_id__class_name=search_text, year=year.year).order_by("id")
        else:
            return 0
    else:
        return 0
    return class_schedul_list


@login_required
@user_passes_test(academic_officer_authority_check)
@csrf_exempt
def index_AO_class_schedul_search(request):
    search_type = request.POST['search_type']
    search_text = request.POST['search_text']
    class_schedul_list = index_AO_class_schedul_search_function(search_type, search_text)
    if class_schedul_list == 0:
        return HttpResponse(1)
    paginator = Paginator(class_schedul_list, page_item_total.page_item_total)
    page = request.POST.get("page")
    try:
        class_schedul_list = paginator.page(page)
    except (EmptyPage, InvalidPage, PageNotAnInteger):
        class_schedul_list = paginator.page(1)
    content = {
        'class_schedul_list': class_schedul_list,
        'erro_message': "未找到记录",
    }
    return render(request, "twss/Academic_officer/basic_infomation/class_schedul/class_schedul_select.html",content)


@login_required
@user_passes_test(academic_officer_authority_check)
@csrf_exempt
def index_AO_class_schedul_select(request):
    class_schedul_list = ClassSchedule.objects.filter(year=year.year).order_by("state")
    search_type = request.POST.get('search_type')
    search_text = request.POST.get('search_text')
    if search_text:
        class_schedul_list = index_AO_class_schedul_search_function(search_type,search_text)
    type_order = request.POST.get("type_order")
    if type_order == "year_up_arrow":
        class_schedul_list = class_schedul_list.order_by("year")
    if type_order == "year_down_arrow":
        class_schedul_list = class_schedul_list.order_by("-year")
    if type_order == "term_up_arrow":
        class_schedul_list = class_schedul_list.order_by("term")
    if type_order == "term_down_arrow":
        class_schedul_list = class_schedul_list.order_by("-term")
    if type_order == "place_up_arrow":
        class_schedul_list = class_schedul_list.order_by("place")
    if type_order == "place_down_arrow":
        class_schedul_list = class_schedul_list.order_by("-place")
    if type_order == "teacher_up_arrow":
        class_schedul_list = class_schedul_list.order_by("teacher_id__first_name")
    if type_order == "teacher_down_arrow":
        class_schedul_list = class_schedul_list.order_by("-teacher_id__first_name")
    if type_order == "class_up_arrow":
        class_schedul_list = class_schedul_list.order_by("class_id__class_name")
    if type_order == "class_down_arrow":
        class_schedul_list = class_schedul_list.order_by("-class_id__class_name")
    if type_order == "course_up_arrow":
        class_schedul_list = class_schedul_list.order_by("course_id__course_name")
    if type_order == "course_down_arrow":
        class_schedul_list = class_schedul_list.order_by("-course_id__course_name")
    paginator = Paginator(class_schedul_list, page_item_total.page_item_total)
    page = request.POST.get("page")
    try:
        class_schedul_list = paginator.page(page)
    except (EmptyPage, InvalidPage, PageNotAnInteger):
        class_schedul_list = paginator.page(1)

    if type_order:
        content = {
            'class_schedul_list': class_schedul_list,
            'type_order':type_order,
            'error_message':"未找到课表记录!"
        }
    else:
        content = {
            'class_schedul_list': class_schedul_list,
            'error_message': "未找到课表记录!"
        }
    return render(request, "twss/Academic_officer/basic_infomation/class_schedul/class_schedul_select.html", content)


@login_required
def index_AO_teacher_list(request):
    name = request.GET.get("value")
    teacher_list = User.objects.filter(first_name__icontains=name, is_active=True)
    rejson = []
    for teacher in teacher_list:
        rejson.append(teacher.first_name)
    return HttpResponse(json.dumps(rejson),content_type="application/json")


@csrf_exempt
@login_required
def index_AO_class_list(request):
    grade = request.POST.get("grade")
    grade = int(grade)
    iterm_list = Class.objects.filter(grade=grade)
    content={
        "iterm_list": iterm_list
    }
    return render(request, "twss/Academic_officer/basic_infomation/class_schedul/class_list.html", content)


@login_required
def index_AO_course_list(request):
    name = request.GET.get("value")
    iterm_list = Course.objects.filter(course_name__contains=name)
    rejson = []
    for item in iterm_list:
        # rejson.append(str(item.Course_card)+item.course_name)
        rejson.append(item.course_name)
    return HttpResponse(json.dumps(rejson),content_type="application/json")


@login_required
@user_passes_test(academic_officer_authority_check)
@csrf_exempt
def index_AO_class_schedul_add(request):
    if request.method == "POST":
        term = request.POST.get("term")
        profile = request.POST.get("teacher")
        course = request.POST.get("course")
        place = request.POST.get("place")
        class_id = request.POST.getlist("class_id_id")
        # 有不足如果传来的数据错误就有麻烦
        if class_id:
            pass
        else:
            return HttpResponse("未选择班级或该班级不存在")

        try:
            check_teacher = Profile.objects.get(user__first_name__exact=profile)
        except Profile.DoesNotExist:
            return HttpResponse("未输入教师或该教师不存在")
        try:
            check_course = Course.objects.get(course_name__exact=course)
        except Course.DoesNotExist:
            return HttpResponse("未输入课程或该课程不存在")
        for id in class_id:
            try:
                clas = Class.objects.get(class_card=id)
            except Class.DoesNotExist:
                return HttpResponse("未选择班级或该班级不存在")
            class_schedul = ClassSchedule.objects.create(
                year=year.year, term=term, place=place, class_id=clas, teacher_id=check_teacher,
                course_id=check_course
            )
            class_schedul.save()
        # 课程工作量计算
        profile = check_teacher
        if check_course.course_property == 1:
            course_list = Course.objects.filter(from_course__teacher_id=profile, course_property=1).distinct()
            workload = theory_course_count(course_list, profile)
        elif 1 < check_course.course_property < 5:
            course_list = Course.objects.filter(from_course__teacher_id=profile, course_property__range=(1, 4)).distinct()
            workload = experimental_course_count(course_list, profile)
        elif check_course.course_property > 4:
            teacher_list = Profile.objects.filter(from_teacher__course_id=check_course).distinct()
            for profile in teacher_list:
                course_list = Course.objects.filter(from_course__teacher_id=profile,
                                                    course_property__gt=4).distinct()
                workload = internship_count(course_list, profile)
        else:
            return HttpResponse("未知课程类型错误")
        return HttpResponse(1)
    else:
        grade = Class.objects.values_list("grade").distinct()
        content = {
            "grade": grade,
        }
        return render(request, "twss/Academic_officer/basic_infomation/class_schedul/class_schedul_add.html", content)


# 此处也应有工作量审计
@login_required
def index_AO_class_schedul_delete(request, class_schedul_id):
    delete_record = ClassSchedule.objects.get(id=class_schedul_id)
    if delete_record:
        check_course = delete_record.course_id
        profile_list = Profile.objects.filter(from_teacher__course_id=check_course).distinct()
        if profile_list:
            pass
        else:
            return HttpResponse("未知课程类型错误")
        delete_record.delete()

        # 课程工作量计算
        teacher_profile = delete_record.teacher_id
        if check_course.course_property == 1:
            course_list = Course.objects.filter(from_course__teacher_id=teacher_profile, course_property=1).distinct()
            workload = theory_course_count(course_list, teacher_profile)
        elif 1 < check_course.course_property < 5:
            course_list = Course.objects.filter(from_course__teacher_id=teacher_profile, course_property__range=(1, 4)).distinct()
            workload = experimental_course_count(course_list, teacher_profile)
        elif check_course.course_property > 4:
            for teacher_profile in profile_list:
                course_list = Course.objects.filter(from_course__teacher_id=teacher_profile,
                                                    course_property__gt=4).distinct()
                if course_list is None:
                    print("空")
                else:
                    print("有")
                workload = internship_count(course_list, teacher_profile)
            return HttpResponse("OK")
        else:
            return HttpResponse("未知课程类型错误")
        return HttpResponse("good")
    else:
        return HttpResponse("you can't delete this course")


# 此处应有工作量审计
@login_required
@csrf_exempt
def index_AO_class_schedul_edit(request, class_schedul_id):
    class_schedul_edit = ClassSchedule.objects.get(id=class_schedul_id)
    grade = Class.objects.values_list("grade").distinct()
    if request.method == "POST":
        index_new_class_schedule_form = ClassScheduleEditModelForm(request.POST, instance=class_schedul_edit)
        if index_new_class_schedule_form.is_valid():
            index_new_class_schedule_form.save()
            class_schedul_edit.state = 1
            if request.user.profile.authority == 1:
                class_schedul_edit.state = 0
            else:
                class_schedul_edit.state = 1
            class_schedul_edit.save()

            # 工作量计算
            # 课程工作量计算
            profile = class_schedul_edit.teacher_id
            check_course = class_schedul_edit.course_id
            # teacher_list = User.objects.filter(profile__from_teacher__course_id=check_course).distinct()
            profile_list = Profile.objects.filter(from_teacher__course_id=check_course).distinct()
            if check_course.course_property == 1:
                course_list = Course.objects.filter(from_course__teacher_id=profile, course_property=1).distinct()
                workload = theory_course_count(course_list, profile)
            elif 1 < check_course.course_property < 5:
                course_list = Course.objects.filter(from_course__teacher_id=profile,
                                                    course_property__range=(1, 4)).distinct()
                workload = experimental_course_count(course_list, profile)
            elif check_course.course_property > 4:
                for profile in profile_list:
                    course_list = Course.objects.filter(from_course__teacher_id=profile,
                                                        course_property__gt=4).distinct()
                    if course_list is None:
                        print("空")
                    else:
                        print("有")
                    workload = internship_count(course_list, profile)

            return HttpResponse(1)
        else:
            type_order = request.POST.get("type_order")
            page = request.POST.get("page")
            content = {
                "index_new_class_schedule_form": index_new_class_schedule_form,
                "class_schedul_id": class_schedul_id,
                "class_schedul_edit": class_schedul_edit,
                "type_order": type_order,
                "page": page,
                "grade": grade
            }
            return render(request, "twss/Academic_officer/basic_infomation/class_schedul/class_schedul_edit.html",
                          content)
    else:
        type_order = request.GET.get("type_order")
        page = request.GET.get("page")
        # index_new_class_schedule = modelform_factory(
        #     ClassSchedule, fields=(
        #         "term", "teacher_id", "course_id", "place"
        #     )
        # )
        index_new_class_schedule_form = ClassScheduleEditModelForm(instance=class_schedul_edit)
        content = {
            "index_new_class_schedule_form": index_new_class_schedule_form,
            "class_schedul_id":class_schedul_id,
            "class_schedul_edit":class_schedul_edit,
            "type_order": type_order,
            "page": page,
            "grade": grade
        }
        return render(request, "twss/Academic_officer/basic_infomation/class_schedul/class_schedul_edit.html", content)


@login_required
@csrf_exempt
@user_passes_test(academic_officer_authority_check)
def index_AO_class_schedul_pass(request):
    chk_value_list = request.GET.getlist('test')
    for value in chk_value_list:
        value = int(value)
        try:
            record = ClassSchedule.objects.get(id=value)
            if record.state == 0:
                record.state = 2
                record.save()
        except ClassSchedule.DoesNotExist:
            pass
    return HttpResponse(1)


@login_required
@csrf_exempt
@user_passes_test(academic_officer_authority_check)
def index_AO_class_schedul_reject(request):
    if request.method == "POST":
        try:
            chk_value = request.POST.get("test")
            record = ClassSchedule.objects.get(id=chk_value)
        except Exception:
            return HttpResponse(4)
        reject_reason = RejectReasonForm(request.POST)
        if record.state != 1:
            if reject_reason.is_valid():
                record.state = 3
                record.save()
                return HttpResponse(0)
            else:
                content = {
                    'reject_reason_form': reject_reason,
                    'query': record,
                    'type': '5',
                }
                return render(request, "twss/Academic_officer/alert_reject_info.html", content)
        else:
            return HttpResponse(3)
    else:
        try:
            chk_value = request.GET.get("test")
            record = ClassSchedule.objects.get(id=chk_value)
        except Exception:
            return HttpResponse(4)
        reject_reason = RejectReasonForm()
        content = {
            'reject_reason_form': reject_reason,
            'query': record,
            'type': '5',
        }
        return render(request, "twss/Academic_officer/alert_reject_info.html", content)


@login_required
@csrf_exempt
def index_AO_workload_coefficent(request):
    edited_record = WorkloadCoefficent.objects.get(id=1)
    if request.method == "POST":
        new_item_form = CoefficientModelForm(request.POST, instance=edited_record)
        if new_item_form.is_valid():
            new_item_form.save()
            return HttpResponse(1)
        else:
            content = {
                'new_item_form': new_item_form,
            }
            return render(request,
                          "twss/Academic_officer/basic_infomation/workload_coefficent/workload_coefficent.html",
                          content)

    else:
        new_item_form = CoefficientModelForm(instance=edited_record)
        content = {
            'new_item_form': new_item_form,
        }
        return render(request,"twss/Academic_officer/basic_infomation/workload_coefficent/workload_coefficent.html",content)


# 生成excel
class Echo(object):
    def write(self,value):
        return value


# def some_streaming_csv_view(request):
#     rows = (["Row {}".format(idx)] for idx in moves.range(65536))
#     pseudo_buffer = Echo()
#     writer = csv.writer(pseudo_buffer)
#     response = StreamingHttpResponse((writer.writerow(row) for row in rows), content_type="text/csv")
#     response['Content-Dispossition'] = 'attachment; filename = "somfilename.csv"'
#     return response


def some_streaming_csv_view(request):
    rows = (["Row {}".format(idx)] for idx in moves.range(65536))
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    response = StreamingHttpResponse((writer.writerow(row) for row in rows), content_type="text/csv")
    response['Content-Dispossition'] = 'attachment; filename = "somfilename.csv"'
    return response


#################***分割线******
#导出界面
def excel_chose_view(request):
    return render(request,'twss/Academic_officer/workload_total/workload_download_chose_alert.html')


# 导出工作量信息
def some_excel_ret_view(request, download_type):
    download_type = int(download_type)
    if download_type == 0:
        # 全部
        record_list = WorkloadInfomation.objects.all().order_by(
            "teacher__profile__department", "total", "teacher__first_name"
        )
    elif download_type == 1:
        # 生技
        record_list = WorkloadInfomation.objects.filter(teacher__profile__department=1).order_by(
            "teacher__profile__department", "total", "teacher__first_name"
        )
    elif download_type == 2:
        # 生信
        record_list = WorkloadInfomation.objects.filter(teacher__profile__department=2).order_by(
            "teacher__profile__department", "total", "teacher__first_name"
        )
    elif download_type == 3:
        # 生工
        record_list = WorkloadInfomation.objects.filter(teacher__profile__department=3).order_by(
            "teacher__profile__department", "total", "teacher__first_name"
        )
    else:
        return HttpResponse("OK")

    response = HttpResponse(content_type='application/vnd.ms-excel')
    response[
        'Content-Disposition'] = 'attachment: filename="45455.xls"'
    ws = Workbook(encoding='utf-8')
    w = ws.add_sheet(u'工作量总览')
    w.write(0, 0, "姓名")
    w.write(0, 1, "工号")
    w.write(0, 2, "系部")
    w.write(0, 3, "教学")
    w.write(0, 4, "教研")
    w.write(0, 5, "汇总")
    excel_row = 1
    if record_list:
        for record in record_list:
            name = record.teacher.first_name
            card = record.teacher.profile.stuff_card
            dept = record.teacher.profile.get_department_display()
            teach = record.teaching_workload
            search = record.searching_workload
            total = record.total
            w.write(excel_row,0,name)
            w.write(excel_row, 1, card)
            w.write(excel_row, 2, dept)
            w.write(excel_row, 3, teach)
            w.write(excel_row, 4, search)
            w.write(excel_row, 5, total)
            excel_row += 1
    output = BytesIO()
    ws.save(output)
    output.seek(0)
    response.write(output.getvalue())
    return response


# def send_email(request):
#     send_mail('Subject here', 'Here is the message.', 'zzuslzy@163.com', ['2723698190@qq.com',], fail_silently=False)
    # send_mail('subject', 'message', 'zzuslzy@163.com', ['2723698190@qq.com'], fail_silently=False)
    # send_mail('subject here', 'Here is the message', 'zzuslzy@163.com', ['2723698190@qq.com'], fail_silently=False)


# 导出教师信息
def excel_teacher_ret_view(request):
    record_list = User.objects.filter(profile__authority=1).order_by(
        "profile__department", "profile__stuff_card"
    )
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response[
        'Content-Disposition'] = 'attachment: filename="45455.xls"'
    ws = Workbook(encoding='utf-8')
    w = ws.add_sheet(u'师资队伍总览')
    w.write(0, 0, "教职工号")
    w.write(0, 1, "姓名")
    w.write(0, 2, "性别")
    w.write(0, 3, "部门")
    w.write(0, 4, "职称")
    w.write(0, 5, "权限")
    w.write(0, 6, "电话")
    excel_row = 1
    for record in record_list:
        name = record.first_name
        card = record.profile.stuff_card
        dept = record.profile.get_department_display()
        sex = record.profile.get_sex_display()
        title = record.profile.get_title_display()
        authority = record.profile.get_authority_display()
        phone = record.profile.phone
        w.write(excel_row, 0, card)
        w.write(excel_row, 1, name)
        w.write(excel_row, 2, sex)
        w.write(excel_row, 3, dept)
        w.write(excel_row, 4, title)
        w.write(excel_row, 5, authority)
        w.write(excel_row, 6, phone)
        excel_row += 1
    output = BytesIO()
    ws.save(output)
    output.seek(0)
    response.write(output.getvalue())
    return response


# 导出班级信息
def excel_class_ret_view(request):
    record_list = Class.objects.all().order_by(
        "grade", "class_major", "class_name"
    )
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response[
        'Content-Disposition'] = 'attachment: filename="45455.xls"'
    ws = Workbook(encoding='utf-8')
    w = ws.add_sheet(u'班级总览')
    w.write(0, 0, "编号")
    w.write(0, 1, "年级")
    w.write(0, 2, "班名")
    w.write(0, 3, "专业")
    w.write(0, 4, "人数")
    excel_row = 1
    for record in record_list:
        card = record.class_card
        grade = record.grade
        name = record.class_name
        major = record.get_class_major_display()
        total = record.total
        w.write(excel_row, 0, card)
        w.write(excel_row, 1, grade)
        w.write(excel_row, 2, name)
        w.write(excel_row, 3, major)
        w.write(excel_row, 4, total)
        excel_row += 1
    output = BytesIO()
    ws.save(output)
    output.seek(0)
    response.write(output.getvalue())
    return response


# def send_email(request):
#     send_mail('Subject here', 'Here is the message.', 'zzuslzy@163.com', ['2723698190@qq.com',], fail_silently=False)
    # send_mail('subject', 'message', 'zzuslzy@163.com', ['2723698190@qq.com'], fail_silently=False)
    # send_mail('subject here', 'Here is the message', 'zzuslzy@163.com', ['2723698190@qq.com'], fail_silently=False)


# 导出课程信息
def excel_course_ret_view(request):
    record_list = Course.objects.all().order_by(
        "course_property", "Course_card"
    )
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response[
        'Content-Disposition'] = 'attachment: filename="45455.xls"'
    # 课程编号、课程名、课程类别、学时、学分
    ws = Workbook(encoding='utf-8')
    w = ws.add_sheet(u'工作量总览')
    w.write(0, 0, "课程编号")
    w.write(0, 1, "课程名")
    w.write(0, 2, "课程类别")
    w.write(0, 3, "学时")
    w.write(0, 4, "学分")
    excel_row = 1
    for record in record_list:
        card = record.Course_card
        name = record.course_name
        type = record.get_course_property_display()
        hour = record.hours
        credit = record.credit
        w.write(excel_row, 0, card)
        w.write(excel_row, 1, name)
        w.write(excel_row, 2, type)
        w.write(excel_row, 3, hour)
        w.write(excel_row, 4, credit)
        excel_row += 1
    output = BytesIO()
    ws.save(output)
    output.seek(0)
    response.write(output.getvalue())
    return response


# def send_email(request):
#     send_mail('Subject here', 'Here is the message.', 'zzuslzy@163.com', ['2723698190@qq.com',], fail_silently=False)
    # send_mail('subject', 'message', 'zzuslzy@163.com', ['2723698190@qq.com'], fail_silently=False)
    # send_mail('subject here', 'Here is the message', 'zzuslzy@163.com', ['2723698190@qq.com'], fail_silently=False)


# 导出课表信息
def excel_class_schedule_ret_view(request):
    record_list = ClassSchedule.objects.filter(year=year.year).order_by(
        "term", "teacher_id"
    )
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment: filename="45455.xls"'
    # if record_list:
    ws = Workbook(encoding='utf-8')
    w = ws.add_sheet(u'课表总览')
    w.write(0, 0, "年份")
    w.write(0, 1, "学期")
    w.write(0, 2, "课程编号")
    w.write(0, 3, "课程")
    w.write(0, 4, "教师编号")
    w.write(0, 5, "教师")
    w.write(0, 6, "班级编号")
    w.write(0, 7, "班级")
    w.write(0, 8, "地点")
    excel_row = 1
    for record in record_list:
        term = record.get_term_display()
        course = record.course_id.course_name
        course_card = record.course_id.Course_card
        teacher = record.teacher_id.first_name
        teacher_card = record.teacher_id.username
        clas_card = record.class_id.class_card
        clas = record.class_id.class_name
        place = record.place
        w.write(excel_row, 0, year.year)
        w.write(excel_row, 1, term)
        w.write(excel_row, 2, course_card)
        w.write(excel_row, 3, course)
        w.write(excel_row, 4, teacher_card)
        w.write(excel_row, 5, teacher)
        w.write(excel_row, 6, clas_card)
        w.write(excel_row, 7, clas)
        w.write(excel_row, 8, place)
        excel_row += 1
    output = BytesIO()
    ws.save(output)
    output.seek(0)
    response.write(output.getvalue())
    return response

#################***分割线******
# 上传教师信息
@csrf_exempt
def excel_upload_teacher(request):
    man = "男"
    woman = '女'
    SJ = "生物技术"
    SX = "生物信息"
    SG = "生物工程"
    ZJ = "助教"
    JS = '讲师'
    FJSHOU = "副教授"
    JSHOU = "教授"
    AJS = "教师"
    AJWY = "教务员"
    XFZR = '系负责人'
    myfileform = modelform_factory(Myfile, fields="__all__")
    if request.method == "POST":
        file = request.FILES.get("file")
        if file:
            wb = xlrd.open_workbook(
                filename=None, file_contents=file.read())
            if wb:
                table = wb.sheets()[0]
                nrows = table.nrows
                # 若标题栏相同则向下读取，否则提示出错
                if table.cell(0, 0).value == "授课教师工号" and table.cell(0, 1).value == "授课教师":
                    l = list()
                    i = 0
                    n = 0
                    for i in range(1, nrows):
                        n = i + 1
                        l.append(n)
                        card = table.cell(i, 0).value
                        # 数据验证
                        if card:
                            try:
                                card = int(card)
                            except Exception:
                                l.append('第%d行1列: 必须为数字\n' % n)
                                continue
                        else:
                            # l.append('第%d行1列: 不能为空\n' % n)
                            continue

                        name = table.cell(i, 1).value
                        # 数据验证
                        if name and isinstance(name, str):
                            pass
                        else:
                            l.append('第%d行2列：数据格式错误\n' % n)
                            continue

                        # 验重
                        try:
                            repeat = User.objects.get(profile__stuff_card=card)
                            repeat_name = repeat.first_name
                            if repeat_name == name:
                                # l.append('第%d行：该条记录已录入\n' % n)
                                continue
                            else:
                                l.append('第%d行：职工号已存在,且姓名与系统不一致，系统为 %s 教师，该记录为%s\n' % (n, repeat_name, name))
                                continue
                        except User.DoesNotExist:
                            pass
                        # 检验重复
                        try:
                            repeat = User.objects.get(first_name=name)
                            repeat_card = repeat.profile.stuff_card
                            if repeat_card != card:
                                l.append('第%d行：教师已存在，且职工号不一致，系统为%d，该记录为%s\n' % (n, repeat_card, card))
                                continue
                            else:
                                continue
                        except User.DoesNotExist:
                            pass
                        except User.MultipleObjectsReturned:
                            continue
                        # 创建用户
                        try:
                            user = User.objects.create_user(username=card, email=None, password=card)
                        except IntegrityError:
                            l.append('第%d行：用户创建失败\n' % n)
                            continue
                        user.first_name = name
                        user.save()
                        user_profile = Profile.objects.create(user=user,
                                                              stuff_card=card)
                        user_profile.save()
                    if l:
                        return HttpResponse(l)
                    else:
                        return HttpResponse(1)
                else:
                    return HttpResponse("警告！请检查excel表格的标题，确保第一行是：授课教师工号、授课教师")
            else:
                return HttpResponse("文件无法读取，请上传excel文件")
        else:
            return HttpResponse("未检测到文件，请重新上传")
    else:
        mys = myfileform()
        content = {
            'form': mys,
            'type': 4,
            'title': "提示：请检查excel表格的标题，务必确保第一行前两列依次是：授课教师工号、授课教师"
        }
        return render(request, "twss/Academic_officer/basic_infomation/class_info/class_excel_upload.html",
                      content)

# 上传班级信息
@csrf_exempt
def excel_upload_class(request):
    SJ = "生物技术"
    SX = "生物信息"
    SG = "生物工程"
    SWKX = "生物科学类"
    myfileform = modelform_factory(Myfile, fields="__all__")
    if request.method == "POST":
        file = request.FILES.get("file")
        if file:
            try:
                wb = xlrd.open_workbook(
                    filename=None, file_contents=file.read()
                )
            except Exception:
                return HttpResponse("请上传excel")
            if wb:
                table = wb.sheets()[0]
                nrows = table.nrows
                # 若标题栏相同则向下读取，否则提示出错
                # 年级、班名、专业、人数
                if table.cell(0, 0).value == "编号" and table.cell(0, 1).value == "年级" and table.cell(0,
                                                                                                      2).value == "班名" and table.cell(
                    0, 3).value == "专业" and table.cell(0,4).value:
                    # l存储错误信息
                    l = list()
                    for i in range(1, nrows):
                        card = table.cell(i, 0).value
                        n = i + 1
                        if card:
                            try:
                                card = int(card)
                            except Exception:
                                l.append('第%d行1列: 必须为数字\n' % n)
                                continue
                        else:
                            # l.append('第%d行1列: 不能为空\n' % n)
                            continue
                        grade = table.cell(i, 1).value
                        if grade:
                            try:
                                grade = int(grade)
                            except Exception:
                                l.append('第%d行2列: 必须为数字\n' % n)
                                continue
                        else:
                            # l.append('第%d行2列: 不能为空\n' % n)
                            continue

                        name = table.cell(i, 2).value
                        if name and isinstance(name, str):
                            pass
                        else:
                            l.append('第%d行3列数据错误\n' % i)
                            continue
                        major = table.cell(i, 3).value
                        if major and isinstance(major, str):
                            pass
                        else:
                            l.append('第%d行4列数据错误\n' % i)
                            continue
                        if major == SJ:
                            major = 1
                        elif major == SX:
                            major = 2
                        elif major == SG:
                            major = 3
                        elif major == SWKX:
                            major = 4
                        else:
                            l.append('第%d行4列：无法识别的专业\n' % i)
                            continue
                        total = table.cell(i, 4).value
                        if total:
                            try:
                                total = int(total)
                            except Exception:
                                l.append('第%d行5列数据错误\n' % i)
                                continue
                        else:
                            continue
                        ret = '%s,%s,%d,%s' % (grade, name, major, total)
                        print(ret)
                        # 创建班级
                        try:
                            clas = Class.objects.create(
                                class_card=card,
                                grade=grade,
                                class_name=name,
                                class_major=major,
                                total=total,
                            )
                        except IntegrityError:
                            l.append('第%d行:创建出错\n' % i)
                            continue
                    if l:
                        return HttpResponse(l)
                    else:
                        return HttpResponse(1)
                else:
                    return HttpResponse("警告！请检查excel表格的标题，务必确保第一行依次是：编号、年级、班名、专业、人数")
            else:
                return HttpResponse("文件无法读取，请确保上传文件为excel")
        else:
            return HttpResponse("未检测到文件，请重新上传")
    else:
        mys = myfileform()
        content = {
            'form': mys,
            'type': 1,
            'title': "提示：请确保excel第一行依次是：编号、年级、班名、专业、人数"
        }
        return render(request, "twss/Academic_officer/basic_infomation/class_info/class_excel_upload.html",
                      content)


# 上传课程信息
@csrf_exempt
def excel_upload_course(request):
    LWK = "理论课程"
    ZYSY = "专业课实验"
    SJSY = "计算机上机实验"
    KFSY = "开放实验"
    SNRSSX = "市内认识实习"
    WDRSSX = "外地认识,市内生产实习"
    WDSCSX = "外地生产,毕业实习/设计"
    myfileform = modelform_factory(Myfile, fields="__all__")
    if request.method == "POST":
        file = request.FILES.get("file")
        if file:
            try:
                wb = xlrd.open_workbook(
                    filename=None, file_contents=file.read()
                )
            except Exception:
                return HttpResponse("请上传excel")
            if wb:
                table = wb.sheets()[0]
                nrows = table.nrows
                # 若标题栏相同则向下读取，否则提示出错
                # 课程编号、课程名、课程类别、学时、学分

                if table.cell(0, 0).value == "课程名称" and table.cell(0, 1).value == "课程号" and table.cell(0,
                                                                                                      2).value == "学时":
                # if table.cell(0, 0).value == "课程编号" and table.cell(0, 1).value == "课程名" and table.cell(0,
                #                                                                                       2).value == "课程类别" and table.cell(
                #     0, 3).value == "学时" and table.cell(0, 4).value == "学分":
                    l = list()
                    for i in range(1, nrows):
                        n = i + 1
                        # card = int(card) + 200

                        name = table.cell(i, 0).value
                        if name and isinstance(name, str):
                            name = name.strip()
                            pass
                        else:
                            l.append('第%d行1列：数据错误\n' % n)
                            continue

                        # 学时
                        hour = table.cell(i, 2).value
                        if hour:
                            try:
                                hour = int(hour)
                            except Exception:
                                l.append('第%d行3列：数据错误 课时无法识别\n' % n)
                                continue
                        else:
                            l.append('第%d行3列：数据为空\n' % n)
                            continue
                        card = table.cell(i, 1).value
                        if card:
                            try:
                                card = int(card)
                                # 验重
                                try:
                                    repeat = Course.objects.get(Course_card=card)
                                    if repeat:
                                        if repeat.course_name == name and repeat.hours == hour:
                                            continue
                                        else:
                                            l.append(
                                                '第%d行3列：系统记录为:编号%d,课名%s,学时%d.'
                                                '本地记录为:编号%d,课名%s,学时%d\n' % (
                                                    n, repeat.Course_card, repeat.course_name, repeat.hours,
                                                    card, name, hour
                                                )
                                            )
                                            continue
                                except Course.DoesNotExist:
                                    pass
                            except Exception:
                                l.append('第%d行1列数据错误\n' % i)
                                continue
                            pass
                        else:
                            l.append('第%d行2列：数据为空\n' % n)
                            continue
                        # major = table.cell(i, 2).value
                        # if major and isinstance(major, str):
                        #     pass
                        # else:
                        #     l.append('第%d行3列数据错误\n' % i)
                        #     continue
                        # if major == LWK:
                        #     major = 1
                        # elif major == ZYSY:
                        #     major = 2
                        # elif major == SJSY:
                        #     major = 3
                        # elif major == KFSY:
                        #     major = 4
                        # elif major == SNRSSX:
                        #     major = 5
                        # elif major == WDRSSX:
                        #     major = 6
                        # elif major == WDSCSX:
                        #     major = 7
                        # else:
                        #     l.append('第%d行3列无法识别的课程类型\n' % i)
                        #     continue
                        # hour = table.cell(i, 3).value
                        # if isinstance(hour, float):
                        #     pass
                        # else:
                        #     l.append('第%d行4列数据错误\n' % i)
                        #     continue
                        # hour = int(hour)
                        # # credit = int(table.cell(i, 4).value)
                        # ret = '%d,%s,%d,%d' % (card, name, major, hour)
                        # print(ret)
                        # 创建课程
                        try:
                            course = Course.objects.create(Course_card=card)
                        except IntegrityError:
                            l.append('第%d行: 创建失败，未知错误\n' % n)
                            continue
                        course.course_name = name
                        course.hours = hour
                        course.save()
                        SY = '实验'
                        SX = '实习'
                        if SY in course.course_name:
                            course.course_property = 2
                            course.save()
                        elif SX in course.course_name:
                            course.course_property = 7
                            course.save()
                        else:
                            pass
                    if l:
                        return HttpResponse(l)
                    else:
                        return HttpResponse(1)
                    # return HttpResponse("下一步")
                else:
                    return HttpResponse("警告！请检查excel表格的标题，确保第一行依次是：课程名称、课程号、学时")
            else:
                return HttpResponse("文件无法读取，请确保上传文件为excel")
        else:
            return HttpResponse("未检测到文件，请重新上传")
    else:
        mys = myfileform()
        content = {
            'form': mys,
            'type': 2,
            'title': "提示：请检查excel表格的标题，确保第一行依次是：课程编号、课程名、课程类型、学时"
        }
        return render(request, "twss/Academic_officer/basic_infomation/class_info/class_excel_upload.html",
                      content)


#上传课表信息
@csrf_exempt
def excel_upload_class_schedul(request):
    myfileform = modelform_factory(Myfile, fields="__all__")
    if request.method == "POST":
        file = request.FILES.get("file")
        if file:
            try:
                wb = xlrd.open_workbook(
                    filename=None, file_contents=file.read()
                )
            except Exception:
                return HttpResponse("请上传excel")
            if wb:
                table = wb.sheets()[0]
                nrows = table.nrows
                # 若标题栏相同则向下读取，否则提示出错
                # 学期、课程编号、教师编号、班级编号、地点
                if table.cell(0, 0).value == "学期" and table.cell(0, 1).value == "课程名称" \
                        and table.cell(0, 2).value == "课程编号" and table.cell(0, 3).value == "教师姓名" \
                        and table.cell(0, 4).value == "教职工号" and table.cell(0, 5).value == "班级名称":
                    l = list()
                    for i in range(1, nrows):
                        n = i + 1
                        # 学期 0
                        term = table.cell(i, 0).value
                        if term and isinstance(term, str):
                            pass
                        else:
                            l.append('第%d行第2列：数据类型错误' % n)
                            continue
                        if term == "春期":
                            term = 1
                        elif term == "秋期":
                            term = 2
                        else:
                            l.append('第%d行第2列：无法识别的学期' % n)
                            continue

                        # 课程名称 1
                        course_name = table.cell(i, 1).value
                        if course_name and isinstance(course_name, str):
                            course_name = course_name.strip()
                            pass
                        else:
                            l.append('第%d行1列：数据错误\n' % n)
                            continue

                        # 课程编号 1
                        course_card = table.cell(i, 2).value
                        if course_card:
                            try:
                                course_card = int(course_card)
                                course = Course.objects.get(Course_card=course_card)
                                if course.course_name == course_name:
                                    pass
                                else:
                                    l.append('第%d行第3列：课程名与课程编号不匹配' % n)
                                    continue
                            except Exception:
                                l.append('第%d行第3列：数据类型错误或课程不存在' % n)
                                continue
                        else:
                            l.append('第%d行第3列：数据不存在' % n)
                            continue
                        # 教师名 3
                        teacher_name = table.cell(i, 3).value
                        if teacher_name and isinstance(teacher_name, str):
                            teacher_name = teacher_name.strip()
                            pass
                        else:
                            l.append('第%d行4列：数据错误\n' % n)
                            continue

                        # 教师编号 4

                        teacher_card = table.cell(i, 4).value
                        if teacher_card:
                            try:
                                teacher_card = int(teacher_card)
                                teacher = User.objects.get(username=teacher_card)
                                if teacher.first_name == teacher_name:
                                    pass
                                else:
                                    l.append('第%d行第3列：教师名与教师编号不匹配' % n)
                                    continue
                            except Exception:
                                l.append('第%d行第3列：数据类型错误或教师不存在' % n)
                                continue
                        else:
                            l.append('第%d行第3列：数据不存在' % n)
                            continue
                        clas_card = table.cell(i, 6).value
                        # 数据类型检验
                        if isinstance(clas_card, float):
                            pass
                        else:
                            l.append('第%d行第7列数据类型错误' % i)
                            continue
                        # 存在性检验
                        try:
                            clas = Class.objects.get(class_card=clas_card)
                        except Class.DoesNotExist:
                            l.append('第%d行第7列：班级不存在' % i)
                            continue
                        # 创建课表
                        try:
                            schedul = ClassSchedule.objects.create(
                                year=year.year, term=term, class_id=clas, course_id=course, teacher_id=teacher
                            )
                        except Exception:
                            l.append('第%d行: 创建出错' % i)
                        if schedul.course_id:
                            schedul.save()
                            user = teacher
                            if course.course_property == 1:
                                course_list = Course.objects.filter(from_course__teacher_id=user,
                                                                    course_property=1).distinct()
                                workload = theory_course_count(course_list, user)
                            elif 1 < course.course_property < 5:
                                course_list = Course.objects.filter(from_course__teacher_id=user,
                                                                    course_property__range=(1, 4)).distinct()
                                workload = experimental_course_count(course_list, user)
                            elif course.course_property > 4:
                                teacher_list = User.objects.filter(from_teacher__course_id=course).distinct()
                                for teach in teacher_list:
                                    course_list = Course.objects.filter(from_course__teacher_id=teach,
                                                                        course_property__gt=4).distinct()
                                    workload = internship_count(course_list, teach)
                            else:
                                return HttpResponse("未知课程类型错误")
                        else:
                            print("课程创建失败")
                            continue
                    if l:
                        return HttpResponse(l)
                    else:
                        return HttpResponse(1)
                else:
                    return HttpResponse("警告！请检查excel表格的标题，确保第一行依次是：学期、课程编号、教师编号、班级编号、地点")
            else:
                return HttpResponse("文件无法读取，请确保上传文件为excel")
        else:
            return HttpResponse("未检测到文件，请重新上传")
    else:
        mys = myfileform()
        content = {
            'form': mys,
            'type': 3,
            'title': "提示：请检查excel表格的标题，确保第一行依次是：学期、课程编号、教师编号、班级编号、地点"
        }
        return render(request, "twss/Academic_officer/basic_infomation/class_info/class_excel_upload.html",
                      content)


# 数据库备份与恢复
# def databaseBake(request):