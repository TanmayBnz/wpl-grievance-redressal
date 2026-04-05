from django.contrib import admin
from .models import Profile, Complaint, ComplaintHistory, Grievance


class ComplaintHistoryInline(admin.TabularInline):
    model = ComplaintHistory
    extra = 0
    readonly_fields = ('changed_by', 'old_status', 'new_status', 'remarks', 'timestamp')
    can_delete = False


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'collegename', 'Branch', 'type_user', 'contactnumber')
    list_filter = ('type_user', 'collegename', 'Branch')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email')


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('complaint_id', 'user', 'Subject', 'Type_of_complaint', 'department', 'Time', 'status')
    list_filter = ('status', 'Type_of_complaint', 'department')
    search_fields = ('Subject', 'Description', 'user__username')
    readonly_fields = ('Time', 'updated_at')
    inlines = [ComplaintHistoryInline]


@admin.register(ComplaintHistory)
class ComplaintHistoryAdmin(admin.ModelAdmin):
    list_display = ('complaint', 'changed_by', 'old_status', 'new_status', 'timestamp')
    list_filter = ('new_status',)
    readonly_fields = ('timestamp',)


@admin.register(Grievance)
class GrievanceAdmin(admin.ModelAdmin):
    list_display = ('guser',)
