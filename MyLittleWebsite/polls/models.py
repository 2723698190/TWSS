# -*- coding:utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    stuff_card = models.IntegerField(unique=True, verbose_name='教职工号')
    sex = models.IntegerField(choices=(
        (1, '男'), (2, '女'), (3, '保密')
    ), default=3, verbose_name='用户性别')
    birth = models.DateField(verbose_name="出生日期", default="2017-5-2")
    school = models.CharField(max_length=50, verbose_name="毕业院校", default="郑州大学")
    major = models.CharField(max_length=50, verbose_name="用户专业", default="生态学")
    title = models.IntegerField(choices=(
        (1, '助教'), (2, '讲师'), (3, '副教授'), (4, '教授')
    ), default=4, verbose_name='用户职称')
    authority = models.IntegerField(choices=(
        (1, '教师'), (2, '教务员'), (3, '系负责人')
    ), default=1, verbose_name='用户权限')
    department = models.IntegerField(choices=(
        (1, '生物技术'), (2, '生物信息'), (3, '生物工程'), (4, '其他')
    ), default=1, verbose_name='用户部门')
    phone = models.IntegerField(verbose_name='用户电话', default=1888)

    def __str__(self):
        return self.user.first_name


# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance)
#
#
# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance,created, **kwargs):
#     instance.profile.save()


class Class(models.Model):
    class_card = models.IntegerField(primary_key=True, verbose_name="班级编号")
    grade = models.IntegerField(null=False, blank=False, default=2015, verbose_name="年级")
    class_name = models.CharField(null=False, blank=False, unique=True, max_length=20, default='提高一班', verbose_name="班名")
    # 班级所属专业，不是必要字段，完全可以删除
    class_major = models.IntegerField(null=False, blank=False, choices=(
        (1, '生物技术'), (2, '生物工程'), (3, '生物信息'), (4, '生命科学类')
    ), default=1, verbose_name="专业")
    total = models.IntegerField(null=False, blank=False, default='34', verbose_name="人数" )

    class Meta:
        db_table = 'Class'

    def __str__(self):
        return self.class_name


class Course(models.Model):
    Course_card = models.IntegerField(primary_key=True, verbose_name="课程编号")
    course_name = models.CharField(max_length=20, default='分子生物学', unique=True,verbose_name="课程名")
    course_property = models.IntegerField(choices=(
        (1, '理论课程'), (2, '专业课实验'), (3, '计算机上机实验'), (4, '开放实验'),
        (5, '市内认识实习'), (6, '外地认识,市内生产实习'), (7, '外地生产,毕业实习/设计'),
    ), default=1, verbose_name="课程类型")
    hours = models.IntegerField(default=40,verbose_name="学时")
    days = models.IntegerField(default=7, verbose_name="实习天数")

    class Meta:
        db_table = 'Course'

    def __str__(self):
        return self.course_name


class WorkloadCoefficent(models.Model):
    L_L_less_four_zero = models.DecimalField(default=1.00,verbose_name="40人及以下",max_digits=4,decimal_places=2)
    L_L_less_eight_five = models.DecimalField(default=1.60,verbose_name="41-85人",max_digits=4,decimal_places=2)
    L_L_less_one_two_five = models.DecimalField(default=2.30,verbose_name="86-125人",max_digits=4,decimal_places=2)
    L_L_less_two_zero_zero = models.DecimalField(default=3.00,verbose_name="126-200人",max_digits=4,decimal_places=2)
    L_L_more_two_zero_zero = models.DecimalField(default=3.60,verbose_name="201人及以上",max_digits=4,decimal_places=2)
    SY_Z_Y = models.DecimalField(default=0.045,verbose_name="专业课实验",max_digits=4,decimal_places=3)
    SY_S_J = models.DecimalField(default=0.020,verbose_name="计算机上机实验",max_digits=4,decimal_places=3)
    SY_K_F = models.DecimalField(default=0.065,verbose_name="开放实验",max_digits=4,decimal_places=3)
    SX_S_Q_R_S = models.DecimalField(default=0.05,verbose_name="市内认识实习",max_digits=4,decimal_places=2)
    SX_W_D_R_S = models.DecimalField(default=0.07,verbose_name="外地认识、市内生产",max_digits=4,decimal_places=2)
    SX_W_D_S_C = models.DecimalField(default=0.09,verbose_name="外地生产、毕业实习、论文、设计",max_digits=4,decimal_places=2)
    # 教学成果
    JYLW_HX = models.IntegerField(default=100,verbose_name="教研论文核心期刊")
    JYLW_YB = models.IntegerField(default=30,verbose_name="教研论文一般")

    JGXM_GJJ = models.IntegerField(default=2000,verbose_name="教改项目国家级")
    JGXM_SBJ = models.IntegerField(default=800,verbose_name="教改项目省部级")
    JGXM_XJ = models.IntegerField(default=50,verbose_name="教改项目校级")

    JXCG_GT = models.IntegerField(default=20000,verbose_name="国家级特等")
    JXCG_GY = models.IntegerField(default=10000,verbose_name="国家级一等")
    JXCG_GE = models.IntegerField(default=5000,verbose_name="国家级二等")

    JXCG_ST = models.IntegerField(default=3000,verbose_name="省部级特等")
    JXCG_SY = models.IntegerField(default=2000,verbose_name="省部级一等")
    JXCG_SE = models.IntegerField(default=1000,verbose_name="省部级二等")

    JXCG_XT = models.IntegerField(default=300,verbose_name="校级特等")
    JXCG_XY = models.IntegerField(default=160,verbose_name="校级一等")
    JXCG_XE = models.IntegerField(default=50,verbose_name="校级二等")

    JC_TS = models.IntegerField(default=1500,verbose_name="统编、规划、等优秀教材")
    JC_YB = models.IntegerField(default=500,verbose_name="其他正式出版教材")
    # 教学工程
    ZX_GJJ = models.IntegerField(default=10000,verbose_name="专业国家级")
    ZX_SBJ = models.IntegerField(default=5000,verbose_name="专业省部级")
    ZX_XJ = models.IntegerField(default=1000,verbose_name="专业校级")

    KC_GJJ = models.IntegerField(default=10000,verbose_name="课程国家级")
    KC_SBJ = models.IntegerField(default=2000,verbose_name="课程省部级")
    KC_XJ = models.IntegerField(default=400,verbose_name="课程校级")

    MS_GJJ = models.IntegerField(default=5000,verbose_name="名师国家级")
    MS_SBJ = models.IntegerField(default=1000,verbose_name="名师省部级")
    MS_XJ = models.IntegerField(default=200,verbose_name="名师校级")

    DC_GJJ = models.IntegerField(default=300,verbose_name="大创国家级")
    DC_SBJ = models.IntegerField(default=160,verbose_name="大创省部级")
    DC_XJ = models.IntegerField(default=50,verbose_name="大创校级")

    GCSJ = models.IntegerField(default=10000,verbose_name="工程实践教育")
    # 指导竞赛
    QGXK_TD = models.IntegerField(default=1000,verbose_name="全国性大学生学科竞赛特等")
    QGXK_YD = models.IntegerField(default=600,verbose_name="全国性大学生学科竞赛一等")
    QGXK_ED = models.IntegerField(default=400,verbose_name="全国性大学生学科竞赛二等")

    SBJS_TD = models.IntegerField(default=300,verbose_name="省部级大学生竞赛特等")
    SBJS_YD = models.IntegerField(default=200,verbose_name="省部级大学生竞赛一等")
    SBJS_ED = models.IntegerField(default=100,verbose_name="省部级大学生竞赛二等")
    # 指导论文
    SCI = models.IntegerField(default=600,verbose_name="SCI")
    HX = models.IntegerField(default=130,verbose_name="核心")
    YB = models.IntegerField(default=40,verbose_name="一般")

    def __str__(self):
        return str(self.YB)


class ClassSchedule(models.Model):
    year = models.PositiveSmallIntegerField(verbose_name="年度", default=2017)
    term = models.PositiveSmallIntegerField(
        verbose_name="学期",
        choices=(
            (1, "春期"), (2, "秋期")
        ),
        default=1,
    )
    place = models.CharField(null=True, blank=True, max_length=30, verbose_name="地点", default="未填写")
    # teacher_id = models.ForeignKey(User, to_field="username", related_name="from_teacher")
    teacher_id = models.ForeignKey(Profile, on_delete=models.CASCADE, null= True, related_name="from_teacher")
    class_id = models.ForeignKey(Class, on_delete=models.CASCADE, null=True, related_name="from_class")
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, related_name="from_course")
    state = models.PositiveSmallIntegerField(verbose_name="状态", choices=(
        (0, "待教务员审核"), (1, "待教师确认"), (2, "已确认/已审核"), (3, "驳回待修改")
    ), default=1)
    rejectReason = models.TextField(blank=True, null=True, default="未填写")
    workload = models.FloatField(blank=True, null=True, verbose_name="工作量", default=0)

    class Meta:
        unique_together = ('year', 'term', 'teacher_id', 'class_id', 'course_id')

    def __str__(self):
        return str(self.year)


class TeachAchievement(models.Model):
    year = models.PositiveSmallIntegerField(verbose_name="年度", default=2017)
    type = models.IntegerField(choices=(
        (1, '教研论文'), (2, '教改项目结项'), (3, '教学成果'), (4, '教材')
    ), default=1, verbose_name="成果类型")
    achievement = models.CharField(max_length=30, default='未记录', verbose_name="成果名称")
    level = models.IntegerField(choices=(
        (1,'核心期刊'),(2,'一般期刊')
    ), default=1, verbose_name="获奖等级")
    level1 = models.IntegerField(choices=(
        (1, "国家级"), (2, "省部级"), (3, "校级")
    ), default=3, verbose_name="获奖类型")
    level2 = models.IntegerField(choices=(
        (1, "特等"), (2, "一等"), (3, "二等"),
    ), default=3, verbose_name="获奖等级")
    level3 = models.IntegerField(choices=(
        (1, '全国统编教材'), (2, '国家级规划教材'), (3, '全国教学专业指导委员会制定教材'), (4,'全国优秀教材'), (5,'其他正式出版教材')
    ), default=6, verbose_name="获奖等级")
    teacher_id = models.ForeignKey(User, on_delete=models.CASCADE)
    state = models.IntegerField(choices=(
        (0, '初审未通过'), (1, '复审未通过'), (2, '未审核'), (3, '初审通过'), (4, '复审通过'),
    ), default=2, verbose_name="审核状态")
    rejectReason = models.TextField(blank=True, null=True, default="未填写", verbose_name="拒绝原因")
    time = models.DateField(default="2017-5-2", verbose_name="鉴定/获奖时间")
    file = models.FileField(upload_to='./upload/', verbose_name="上传材料", blank=True, null=True)
    workload = models.FloatField(blank=True, null=True, verbose_name="工作量", default=0)

    class Meta:
        db_table = 'TeachAchievement'

    def __str__(self):
        return str(self.achievement)


class TeachObject(models.Model):
    year = models.PositiveSmallIntegerField(verbose_name="年度", default=2017)
    type = models.IntegerField(choices=(
        (1, '专业、团队及实验中心类'), (2, '课程类'), (3, '工程实践教育类'), (4, '教学名师'), (5, '大学生创新创业训练')
    ), default=1, verbose_name="成果类型")
    object = models.CharField(max_length=20, default='未记录', verbose_name="成果名称")
    level = models.IntegerField(choices=(
        (1, '国家级'), (2, '省部级'), (3, '校级')
    ), default=1, verbose_name="获奖等级")
    teacher_id = models.ForeignKey(User, on_delete=models.CASCADE)
    state = models.IntegerField(choices=(
        (0, '初审未通过'), (1, '复审未通过'), (2, '未审核'), (3, '初审通过'), (4, '复审通过'),
    ), default=2, verbose_name="审核状态")
    rejectReason = models.TextField(blank=True, null=True, default="未填写", verbose_name="拒绝原因")
    time = models.DateField(default="2017-5-2", verbose_name="鉴定/获奖时间")
    file = models.FileField(upload_to='./untitled2/upload/', verbose_name="上传材料", blank=True, null=True)
    workload = models.FloatField(blank=True, null=True, verbose_name="工作量", default=0)

    class Meta:
        db_table = 'TeachObject'

    def __str__(self):
        return self.object


class Competition(models.Model):
    year = models.PositiveSmallIntegerField(verbose_name="年度", default=2017)
    competition = models.CharField(max_length=20, default='未记录', verbose_name="参赛项目名称")
    type = models.IntegerField(choices=(
        (1, '全国性大学生学科竞赛'),(2,'省部级大学生竞赛')
    ), default=1, verbose_name="类型")
    level = models.IntegerField(choices=(
        (1, '特等奖'), (2, '一等奖'), (3, '二等奖')
    ), default=1, verbose_name="获奖等级")
    teacher_id = models.ForeignKey(User, on_delete=models.CASCADE)
    state = models.IntegerField(choices=(
        (0, '初审未通过'), (1, '复审未通过'), (2, '未审核'), (3, '初审通过'), (4, '复审通过'),
    ), default=2, verbose_name="审核状态")
    rejectReason = models.TextField(blank=True, null=True, default="未填写", verbose_name="拒绝原因")
    time = models.DateField(default="2017-5-2", verbose_name="鉴定/获奖时间")
    file = models.FileField(upload_to='./untitled2/upload/', verbose_name="上传材料", blank=True, null=True)
    workload = models.FloatField(blank=True, null=True, verbose_name="工作量", default=0)

    class Meta:
        db_table = 'Competition'

    def __str__(self):
        return str(self.type) + ' ' + str(self.competition)


class GuidePaper(models.Model):
    year = models.PositiveSmallIntegerField(verbose_name="年度", default=2017)
    Paper = models.CharField(max_length=20, default='未记录', verbose_name="成果名称")
    type = models.CharField(max_length=20, default='指导实习论文', verbose_name="成果类型")
    level = models.IntegerField(choices=(
        (1, 'SCI'), (2, '核心期刊'), (3, "一般")
    ), default=1, verbose_name="获奖等级")
    teacher_id = models.ForeignKey(User, on_delete=models.CASCADE)
    state = models.IntegerField(choices=(
        (0, '初审未通过'), (1, '复审未通过'), (2, '未审核'), (3, '初审通过'), (4, '复审通过'),
    ), default=2, verbose_name="审核状态")
    stuclas = models.CharField(max_length=30, verbose_name="学生班级")
    stuname = models.CharField(max_length=30, verbose_name="学生姓名")
    rejectReason = models.TextField(blank=True, null=True, default="未填写", verbose_name="拒绝原因")
    time = models.DateField(default="2017-5-2", verbose_name="鉴定/获奖时间")
    file = models.FileField(upload_to='./untitled2/upload/', verbose_name="上传材料", blank=True, null=True)
    workload = models.FloatField(blank=True, null=True, verbose_name="工作量", default=0)

    class Meta:
        db_table = 'Paper'

    def __str__(self):
        return self.Paper


# 工作量详细信息表
class WorkloadInfomation(models.Model):
    year = models.PositiveSmallIntegerField(verbose_name="年度", default=2017)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    theroy = models.FloatField(blank=True, null=True, verbose_name="理论课工作量", default=0)
    experiment = models.FloatField(blank=True, null=True, verbose_name="实验课工作量", default=0)
    intermship = models.FloatField(blank=True, null=True, verbose_name="实习课工作量", default=0)
    achievement = models.FloatField(blank=True, null=True, verbose_name="教学成果工作量", default=0)
    object = models.FloatField(blank=True, null=True, verbose_name="教学工程工作量", default=0)
    competition = models.FloatField(blank=True, null=True, verbose_name="竞赛指导", default=0)
    paper = models.FloatField(blank=True, null=True, verbose_name="论文指导", default=0)
    teaching_workload = models.FloatField(blank=True, null=True, verbose_name="教学工作量", default=0)
    searching_workload = models.FloatField(blank=True, null=True, verbose_name="教研工作量", default=0)
    total = models.FloatField(blank=True, null=True, verbose_name="总工作量", default=0)

    def __str__(self):
        return self.teacher.first_name


# 文件上传验证
class Myfile(models.Model):
    filepath = models.FileField(upload_to='./upload', verbose_name="上传文件路径")

    def __str__(self):
        return self.filepath


class Year(models.Model):
    year = models.PositiveSmallIntegerField(blank=False, null=False, default=2017, verbose_name="学年")


class PageItemTotal(models.Model):
    page_item_total = models.PositiveSmallIntegerField(blank=False, name=False, default=5, verbose_name='每页条数')


class Deadline(models.Model):
    start_time = models.DateField(blank=True, null=True, verbose_name="起始日期")
    end_time = models.DateField(blank=True, null=True, verbose_name="截止日期")
    name = models.CharField(blank=True, null=True, max_length=20, verbose_name="时间")

