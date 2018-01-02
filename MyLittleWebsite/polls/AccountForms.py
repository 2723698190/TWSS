# -*- coding:utf-8 -*-
from django import forms
from django.forms import ModelForm
from polls.models import *
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
# from django.db import models
# import re
# from django.core.exceptions import ValidationError


class LoginForm(forms.Form):
    username = forms.CharField(
        required=True,
        min_length=6,
        max_length=16,
        label="用户账号",
        widget=forms.TextInput(
            attrs={
                'placeholder': '账号为6-16个字符'
            }
        ),
        error_messages={
            'required': '账号不能为空',
            'min_length': '账号至少为6个字符',
            'max_length': '账号最多为16个字符',
        }
    )
    password = forms.CharField(
        required=True,
        min_length=6,
        max_length=16,
        label="用户密码",
        widget=forms.PasswordInput(
            attrs={
                'placeholder': '密码为6-16个字符'
            }
        ),
        error_messages={
            'required': '密码不能为空',
            'min_length': '密码至少为6个字符',
            'max_length': '密码最多为16个字符',
        }
    )

    def _exist_of_user(self):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")
        user = authenticate(username=username, password=password)
        if user:
            pass
        else:
            raise ValidationError("账号或密码错误")

# 调用内部函数
    def clean(self):
        self._exist_of_user()


class InputDateModelForm(forms.Form):
    start_time = forms.DateField(
        label="起始时间", required=True, widget=forms.SelectDateWidget(
            months={
                1: '一月', 2: '二月', 3: '三月', 4: '四月',
                5: '五月', 6: '六月', 7: '七月', 8: '八月',
                9: '九月', 10: '十月', 11: '十一月', 12: '十二月'
            }
        ),
        error_messages={'required': u'时间不能为空', 'invalid': u'无效的时间格式'},
    )
    end_time = forms.DateField(
        label="起始时间", required=True, widget=forms.SelectDateWidget(
            months={
                1: '一月', 2: '二月', 3: '三月', 4: '四月',
                5: '五月', 6: '六月', 7: '七月', 8: '八月',
                9: '九月', 10: '十月', 11: '十一月', 12: '十二月'
            }
        ),
        error_messages={'required': u'时间不能为空', 'invalid': u'无效的时间格式'},
    )


class ExaminationDateModelForm(ModelForm):
    class Meta:
        model = Deadline
        fields = ['start_time', 'end_time']
        widgets = {
            "start_time": forms.SelectDateWidget(
                # empty_label=(1, 1, 1),
                months={
                    1: '一月', 2: '二月', 3: '三月', 4: '四月',
                    5: '五月', 6: '六月', 7: '七月', 8: '八月',
                    9: '九月', 10: '十月', 11: '十一月', 12: '十二月'
                }
            ),
            "end_time": forms.SelectDateWidget(
                months={
                    1: '一月', 2: '二月', 3: '三月', 4: '四月',
                    5: '五月', 6: '六月', 7: '七月', 8: '八月',
                    9: '九月', 10: '十月', 11: '十一月', 12: '十二月'
                }
            )
        }
        error_messages = {
            "start_time":{
                'required': u'时间不能为空！',
                'invalid': u'无效的时间格式！'
            },
            "end_time": {
                'required': u'时间不能为空！',
                'invalid': u'无效的时间格式！'
            }
        }


class PaperGuideModelForm(ModelForm):
    class Meta:
        model = GuidePaper
        fields = ['Paper', 'level', 'time', 'file']
        widgets = {
            "time": forms.SelectDateWidget(
                months={
                    1: '一月', 2: '二月', 3: '三月', 4: '四月',
                    5: '五月', 6: '六月', 7: '七月', 8: '八月',
                    9: '九月', 10: '十月', 11: '十一月', 12: '十二月'
                }
            )
        }
        error_messages = {
            "time": {
                'required': u'时间不能为空！',
                'invalid': u'无效的时间格式！'
            },
            "Paper": {
                'required': u'成果不能为空！'
            }
        }


class CompetitionGuideModelForm(ModelForm):
    class Meta:
        model=Competition
        fields = ['competition', 'level', 'time', 'file']
        widgets = {
            "time": forms.SelectDateWidget(
                months={
                    1: '一月', 2: '二月', 3: '三月', 4: '四月',
                    5: '五月', 6: '六月', 7: '七月', 8: '八月',
                    9: '九月', 10: '十月', 11: '十一月', 12: '十二月'
                }
            )
        }
        error_messages = {
            "time": {
                'required': u'时间不能为空！',
                'invalid': u'无效的时间格式！'
            },
            "competition": {
                'required': u'成果不能为空！'
            }
        }


class RegisterForm(forms.Form):
    username = forms.CharField(
        required=True,
        min_length=6,
        max_length=16,
        label="用户账号",
        widget=forms.TextInput(
            attrs={
                'placeholder': '账号为6-16个字符'
            }
        ),
        error_messages={
            'required': '账号不能为空',
            'min_length': '账号至少为6个字符',
            'max_length': '账号最多为16个字符',
        }
    )
    password_1 = forms.CharField(
        required=True,
        min_length=6,
        max_length=16,
        label="用户密码",
        widget=forms.PasswordInput(
            attrs={
                'placeholder': '密码为6-16个字符'
            }
        ),
        error_messages={
            'required': '密码不能为空',
            'min_length': '密码至少为6个字符',
            'max_length': '密码最多为16个字符',
        }
    )
    password_2 = forms.CharField(
        required=True,
        label="重复密码",
        widget=forms.PasswordInput(
            attrs={
                'placeholder': '请重复密码'
            }
        ),
        error_messages={
            'required': '重复密码不能为空',
        }
    )
    first_name = forms.CharField(
        required=True,
        max_length=10,
        label="用户姓名",
        widget=forms.TextInput(),
        error_messages={
            'required': '用户姓名不能为空',
            'max_length': '姓名最大长度为10个字符',
        }
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        users = User.objects.filter(username=username)
        if users:
            raise ValidationError('该账号已存在')
        return username

    def clean_password_2(self):
        password_1 = self.cleaned_data.get('password_1')
        password_2 = self.cleaned_data.get('password_2')
        if password_1 and password_2:
            if password_1 != password_2:
                raise ValidationError('两次密码不匹配！')


class ProfileModelForm(ModelForm):
    class Meta:
        model = Profile
        exclude = ['user']
        error_messages = {
            "sex": {
                'required': u'该项不能为空！',
                'invalid': u'无效的数据格式！'
            },
            "stuff_card": {
                'required': u'该项不能为空！',
                'invalid': u'无效的数据格式！',
                'unique': u'该教职工号已存在！'
            },
            "birth": {
                'required': u'该项不能为空！',
                'invalid': u'无效的数据格式！'
            },
            "school": {
                'required': u'该项不能为空！',
                'invalid': u'无效的数据格式！'
            },
            "major": {
                'required': u'该项不能为空！',
                'invalid': u'无效的数据格式！'
            },
            "title": {
                'required': u'该项不能为空！',
                'invalid': u'无效的数据格式！'
            },
            "authority": {
                'required': u'该项不能为空！',
                'invalid': u'无效的数据格式！'
            },
            "department": {
                'required': u'该项不能为空！',
                'invalid': u'无效的数据格式！'
            },
            "phone": {
                'required': u'该项不能为空！',
                'invalid': u'无效的数据格式！'
            },
        }


class ProfileEditModelForm(ProfileModelForm):
    class Meta(ProfileModelForm.Meta):
        exclude = ['stuff_card']


class UserNameForm(ModelForm):
    class Meta:
        model = User
        fields = ['first_name']
        error_messages = {
            "first_name": {
                'required': u'该项不能为空！',
                'invalid': u'无效的数据格式！'
            },
        }


class UserInfoEditForm(ProfileModelForm):
    class Meta(ProfileModelForm.Meta):
        fields = ['sex', 'birth', 'school', 'major', 'title', 'department', 'phone']


class TeachingObjectModelForm(ModelForm):
    class Meta:
        model = TeachObject
        fields = ['object', 'level', 'time', 'file']
        widgets = {
            "time": forms.SelectDateWidget(
                months={
                    1: '一月', 2: '二月', 3: '三月', 4: '四月',
                    5: '五月', 6: '六月', 7: '七月', 8: '八月',
                    9: '九月', 10: '十月', 11: '十一月', 12: '十二月'
                }
            )
        }
        error_messages = {
            "time": {
                'required': u'时间不能为空！',
                'invalid': u'无效的时间格式！'
            },
            "object": {
                'required': u'成果不能为空！'
            }
        }


class TeachingAchievementModelForm(ModelForm):
    class Meta:
        model=TeachAchievement
        fields = ['achievement', 'level', 'level1', 'level2', 'level3', 'time', 'file']
        widgets = {
            "time": forms.SelectDateWidget(
                months={
                    1: '一月', 2: '二月', 3: '三月', 4: '四月',
                    5: '五月', 6: '六月', 7: '七月', 8: '八月',
                    9: '九月', 10: '十月', 11: '十一月', 12: '十二月'
                }
            ),
        }
        error_messages = {
            "time": {
                'required': u'时间不能为空！',
                'invalid': u'无效的时间格式！'
            },
            "achievement": {
                'required': u'成果不能为空！'
            }
        }


class JiaoCaiModelForm(TeachingAchievementModelForm):
    class Meta(TeachingAchievementModelForm.Meta):
        exclude = ['level', 'level1', 'level2']


class JiaoXueChengGuoModelForm(TeachingAchievementModelForm):
    class Meta(TeachingAchievementModelForm.Meta):
        exclude = ('level', 'level3',)


class JiaoGaiXiangMuModelForm(TeachingAchievementModelForm):
    class Meta(TeachingAchievementModelForm.Meta):
        exclude = ('level', 'level2', 'level3')


class JiaoYanLunWenModelForm(TeachingAchievementModelForm):
    class Meta(TeachingAchievementModelForm.Meta):
        exclude = ('level1', 'level2', 'level3')


class ClassModelForm(ModelForm):
    class Meta:
        model = Class
        fields = '__all__'
        error_messages={
            "class_card": {
                "required": u'班级编号不能为空',
                "invalid": u'请输入正整数'
            },
            "grade": {
                "required": u'年级不能为空',
                "invalid": u'请输入正整数'
            },
            "class_name": {
                "required": u'班名不能为空',
                "invalid": u'请输入汉字',
                "unique": u'班名不能重复',
            },
            "total": {
                "required": u'人数不能为空',
                "invalid": u'请输入正整数'
            }
        }


class CourseModelForm(ModelForm):
    class Meta:
        model = Course
        fields = '__all__'
        error_messages={
            "Course_card": {
                "required": u'课程编号不能为空',
                "invalid": u'请输入正整数'
            },
            "course_name": {
                "required": u'课程名不能为空',
                "invalid": u'请输入汉字'
            },
            "hours": {
                "required": '学时不能为空',
                "invalid": u'请输入正整数'
            },
            "days": {
                "required": u'天数不能为空',
                "invalid": u'请输入正整数'
            }
        }


class ClassScheduleEditModelForm(ModelForm):
    class Meta:
        model = ClassSchedule
        fields = ['term', 'place', 'teacher_id', 'course_id', 'class_id']
        error_messages={
            "term": {
                "required": u'学期不能为空',
                "invalid": u'请选择有效的学期'
            },
            "place": {
                "invalid": u'请输入有效的地点'
            },
            "teacher_id": {
                "required": '授课教师不能为空',
                "invalid": u'请输入正确的教师'
            },
            "course_id": {
                "required": u'课程不能为空',
                "invalid": u'请输入有效的课程'
            },
            "class_id": {
                "required": u'班级不能为空',
                "invalid": u'请输入有效的班级'
            }
        }


class TeacherClassSchedulModelForm(ClassScheduleEditModelForm):
    class Meta(ClassScheduleEditModelForm.Meta):
        exclude = ['teacher_id']


class CoefficientModelForm(ModelForm):
    class Meta:
        model = WorkloadCoefficent
        exclude = [
            'L_L_less_four_zero', 'L_L_less_eight_five', 'L_L_less_one_two_five',
            'L_L_less_two_zero_zero', 'L_L_more_two_zero_zero'
        ]
        error_messages = {
            "SY_Z_Y": {
                "required": u'系数不能为空！',
                "invalid": u'格式不正确！'
            },
            "SY_S_J": {
                "required": u'系数不能为空！',
                "invalid": u'格式不正确！'
            },
            "SY_K_F": {
                "required": u'系数不能为空！',
                "invalid": u'格式不正确！'
            },
            "SX_S_Q_R_S": {
                "required": u'系数不能为空！',
                "invalid": u'格式不正确！'
            },
            "SX_W_D_R_S": {
                "required": u'系数不能为空！',
                "invalid": u'格式不正确！'
            },
            "SX_W_D_S_C": {
                "required": u'系数不能为空！',
                "invalid": u'格式不正确！'
            },
            "JYLW_HX": {
                "required": u'系数不能为空！',
                "invalid": u'格式不正确！'
            },
            "JYLW_YB": {
                "required": u'系数不能为空！',
                "invalid": u'格式不正确！'
            },
            "JGXM_GJJ": {
                "required": u'系数不能为空！',
                "invalid": u'格式不正确！'
            },
            "JGXM_SBJ": {
                "required": u'系数不能为空！',
                "invalid": u'格式不正确！'
            },
            "JGXM_XJ": {
                "required": u'系数不能为空！',
                "invalid": u'格式不正确！'
            },
            "JXCG_GT": {
                "required": u'系数不能为空！',
                "invalid": u'格式不正确！'
            },
            "JXCG_GY": {
                "required": u'系数不能为空！',
                "invalid": u'格式不正确！'
            },
            "JXCG_GE": {
                "required": u'系数不能为空！',
                "invalid": u'格式不正确！'
            },
            "JXCG_ST": {
                "required": u'系数不能为空！',
                "invalid": u'格式不正确！'
            },
            "JXCG_SY": {
                "required": u'系数不能为空！',
                "invalid": u'格式不正确！'
            },
            "JXCG_SE": {
                "required": u'系数不能为空！',
                "invalid": u'格式不正确！'
            },
            "JXCG_XT": {
                "required": u'系数不能为空！',
                "invalid": u'格式不正确！'
            },
            "JXCG_XY": {
                "required": u'系数不能为空！',
                "invalid": u'格式不正确！'
            },
            "JXCG_XE": {
                "required": u'系数不能为空！',
                "invalid": u'格式不正确！'
            },
            "JC_TS": {
                "required": u'系数不能为空！',
                "invalid": u'格式不正确！'
            },
            "JC_YB": {
                "required": u'系数不能为空！',
                "invalid": u'格式不正确！'
            },
            "ZX_GJJ": {
                "required": u'系数不能为空！',
                "invalid": u'格式不正确！'
            },
            "ZX_SBJ": {
                "required": u'系数不能为空！',
                "invalid": u'格式不正确！'
            },
            "ZX_XJ": {
                "required": u'系数不能为空！',
                "invalid": u'格式不正确！'
            },
            "KC_GJJ": {
                "required": u'系数不能为空！',
                "invalid": u'格式不正确！'
            },
            "KC_SBJ": {
                "required": u'系数不能为空！',
                "invalid": u'格式不正确！'
            },
            "KC_XJ": {
                "required": u'系数不能为空！',
                "invalid": u'格式不正确！'
            },
            "MS_GJJ": {
                "required": u'系数不能为空！',
                "invalid": u'格式不正确！'
            },
            "MS_SBJ": {
                "required": u'系数不能为空！',
                "invalid": u'格式不正确！'
            },
            "MS_XJ": {
                "required": u'系数不能为空！',
                "invalid": u'格式不正确！'
            },
            "DC_GJJ": {
                "required": u'系数不能为空！',
                "invalid": u'格式不正确！'
            },
            "DC_SBJ": {
                "required": u'系数不能为空！',
                "invalid": u'格式不正确！'
            },
            "DC_XJ": {
                "required": u'系数不能为空！',
                "invalid": u'格式不正确！'
            },
            "GCSJ": {
                "required": u'系数不能为空！',
                "invalid": u'格式不正确！'
            },
            "QGXK_TD": {
                "required": u'系数不能为空！',
                "invalid": u'格式不正确！'
            },
            "QGXK_YD": {
                "required": u'系数不能为空！',
                "invalid": u'格式不正确！'
            },
            "QGXK_ED": {
                "required": u'系数不能为空！',
                "invalid": u'格式不正确！'
            },
            "SBJS_TD": {
                "required": u'系数不能为空！',
                "invalid": u'格式不正确！'
            },
            "SBJS_YD": {
                "required": u'系数不能为空！',
                "invalid": u'格式不正确！'
            },
            "SBJS_ED": {
                "required": u'系数不能为空！',
                "invalid": u'格式不正确！'
            },
            "SCI": {
                "required": u'系数不能为空！',
                "invalid": u'格式不正确！'
            },
            "HX": {
                "required": u'系数不能为空！',
                "invalid": u'格式不正确！'
            },
            "YB": {
                "required": u'系数不能为空！',
                "invalid": u'格式不正确！'
            }
        }


class RejectReasonForm(forms.Form):
    reject_reason = forms.CharField(
        required=True,
        max_length=300,
        label="驳回原因",
        widget=forms.Textarea(
            attrs={
                'placeholder': '请输入'
            }
        ),
        error_messages={
            'required': '原因不能为空',
            'max_length': '最多为300个字符',
        }
    )

