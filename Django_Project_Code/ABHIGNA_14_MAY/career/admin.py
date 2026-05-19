from django.contrib import admin
from .models import Skill, JobRole, UserProfile, Project

admin.site.register(Skill)
admin.site.register(JobRole)
admin.site.register(UserProfile)
admin.site.register(Project)