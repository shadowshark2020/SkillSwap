from django.contrib import admin
from .models import (
    Skill, Category, ClassRequest, ChatRoom, Message, 
    Report, Block, SupportTicket, Notification, 
    MissionTemplate, UserMission
)

@admin.register(ClassRequest)
class ClassRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'skill', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('student__email', 'skill__title')


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('reporter', 'reported_user', 'reason', 'created_at')
    search_fields = ('reporter__email', 'reported_user__email', 'reason')


@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ('blocker', 'blocked', 'created_at')


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'subject', 'status', 'created_at', 'admin_response')
    list_display_links = ('id', 'subject')  
    list_filter = ('status',)
    search_fields = ('user__email', 'subject', 'message')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'sender', 'message', 'is_read', 'created_at')
    list_filter = ('is_read',)


@admin.register(MissionTemplate)
class MissionTemplateAdmin(admin.ModelAdmin):
    list_display = ('title', 'mission_type', 'target_role', 'target_count', 'reward_amount', 'action_key')
    list_filter = ('mission_type', 'target_role')
    search_fields = ('title', 'action_key', 'description')


@admin.register(UserMission)
class UserMissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'template', 'progress', 'is_completed', 'is_claimed', 'assigned_date')
    list_filter = ('is_completed', 'is_claimed', 'assigned_date')
    search_fields = ('user__email', 'template__title')
    
admin.site.register(Category)
admin.site.register(Skill)