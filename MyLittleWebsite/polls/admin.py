from django.contrib import admin
from polls.models import *
#
class ClassScheduleAdmin(admin.ModelAdmin):
    list_display = ('teacher_id','class_id','course_id')

class CompetitionAdmin(admin.ModelAdmin):
    list_display = ('competition','type','teacher_id')


class TeachAchievementAdmin(admin.ModelAdmin):
    list_display = ('achievement','type','teacher_id')

class TeachObjectAdmin(admin.ModelAdmin):
    list_display = ('object','type','teacher_id')

class GuidPaperAdmin(admin.ModelAdmin):
    list_display = ('Paper','type','teacher_id')



admin.site.register(Class)
admin.site.register(WorkloadCoefficent)
admin.site.register(Year)
admin.site.register(Course)
admin.site.register(ClassSchedule,ClassScheduleAdmin)
admin.site.register(TeachAchievement,TeachAchievementAdmin)
admin.site.register(TeachObject,TeachObjectAdmin)
admin.site.register(Competition,CompetitionAdmin)
admin.site.register(GuidePaper, GuidPaperAdmin)
admin.site.register(Profile)
admin.site.register(Myfile)