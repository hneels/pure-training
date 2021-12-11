"""Models registered on Django Admin site"""
from django.contrib import admin
from .models import User, Exercise, Routine, Setgroup, Set, Session


class SetInline(admin.TabularInline):
    model = Set

class SetgroupAdmin(admin.ModelAdmin):
    inlines = [
        SetInline
    ]

class SetgroupInline(admin.TabularInline):
    model = Setgroup

class SessionAdmin(admin.ModelAdmin):
    inlines = [
        SetgroupInline,
    ]

admin.site.register(User)
admin.site.register(Exercise)
admin.site.register(Routine)
admin.site.register(Setgroup, SetgroupAdmin)
admin.site.register(Set)
admin.site.register(Session, SessionAdmin)
