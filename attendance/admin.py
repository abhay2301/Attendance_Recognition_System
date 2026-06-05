from django.contrib import admin
from .models import Course, Enrollment, Attendance, AttendanceLog
from django.utils.html import format_html
from datetime import date

# admin.site.register(Course)

class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    extra = 1
    readonly_fields = ('enrollment_date',)
    raw_id_fields = ('student',)

class AttendanceInline(admin.TabularInline):
    model = Attendance
    extra = 0
    readonly_fields = ('created_at',)
    raw_id_fields = ('student',)
    can_delete = False
    max_num = 10

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_code', 'course_name', 'department', 'semester', 'teacher', 'current_strength', 'is_active')
    list_filter = ('course_type', 'semester', 'department', 'is_active', 'start_date')
    search_fields = ('course_code', 'course_name', 'teacher__username', 'department__name')
    list_editable = ('is_active',)
    readonly_fields = ('created_at', 'updated_at', 'current_strength', 'attendance_percentage')
    inlines = [EnrollmentInline]
    
    fieldsets = (
        ('Basic Information', {'fields': (
            'course_code', 'course_name', 'course_type', 'department', 'semester', 'credits'
        )}),
        ('Teaching Staff', {'fields': (
            'teacher', 'co_teacher'
        )}),
        ('Schedule', {'fields': (
            'schedule', 'room', 'start_date', 'end_date', 'total_hours'
        )}),
        ('Course Details', {'fields': (
            'description', 'objectives', 'prerequisites'
        )}),
        ('Status', {'fields': (
            'is_active', 'max_strength', 'current_strength'
        )}),
        ('Statistics', {'fields': (
            'attendance_percentage',
        )}),
        ('Timestamps', {'fields': (
            'created_at', 'updated_at'
        )}),
    )

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrollment_date', 'enrollment_type', 'grade', 'is_active')
    list_filter = ('enrollment_type', 'is_active', 'enrollment_date')
    search_fields = ('student__username', 'student__student_id', 'course__course_code')
    list_editable = ('grade', 'is_active')
    readonly_fields = ('enrollment_date',)
    
    fieldsets = (
        ('Enrollment Details', {'fields': (
            'student', 'course', 'enrollment_type'
        )}),
        ('Results', {'fields': (
            'grade', 'marks'
        )}),
        ('Status', {'fields': (
            'is_active',
        )}),
        ('Timestamps', {'fields': (
            'enrollment_date',
        )}),
    )

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'date', 'status', 'time_in', 'confidence_score', 'is_verified')
    list_filter = ('status', 'date', 'course', 'is_verified')
    search_fields = ('student__username', 'student__student_id', 'course__course_code')
    list_editable = ('status', 'is_verified')
    readonly_fields = ('created_at', 'updated_at', 'duration', 'attendance_percentage')
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Attendance Details', {'fields': (
            'student', 'course', 'date', 'time_in', 'time_out', 'duration'
        )}),
        ('Status', {'fields': (
            'status', 'reason', 'is_verified'
        )}),
        ('Face Recognition', {'fields': (
            'face_image', 'confidence_score', 'face_match_duration'
        )}),
        ('Device Information', {'fields': (
            'device_id', 'ip_address', 'location'
        )}),
        ('Marked By', {'fields': (
            'marked_by',
        )}),
        ('Statistics', {'fields': (
            'attendance_percentage',
        )}),
        ('Timestamps', {'fields': (
            'created_at', 'updated_at'
        )}),
    )
    
    def face_image_preview(self, obj):
        if obj.face_image:
            return format_html('<img src="{}" width="100" height="100" style="border-radius:5px;" />', obj.face_image.url)
        return "No Image"
    face_image_preview.short_description = 'Face Image'
    
    actions = ['mark_as_present', 'mark_as_absent', 'export_attendance']
    
    def mark_as_present(self, request, queryset):
        updated = queryset.update(status='present', is_verified=True)
        self.message_user(request, f"{updated} attendance records marked as present.")
    mark_as_present.short_description = "Mark selected as present"
    
    def mark_as_absent(self, request, queryset):
        updated = queryset.update(status='absent', is_verified=True)
        self.message_user(request, f"{updated} attendance records marked as absent.")
    mark_as_absent.short_description = "Mark selected as absent"
    
    def export_attendance(self, request, queryset):
        # This would export to CSV/Excel
        self.message_user(request, "Export functionality would be implemented here.")
    export_attendance.short_description = "Export selected attendance"

@admin.register(AttendanceLog)
class AttendanceLogAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'action', 'confidence_score', 'timestamp', 'ip_address')
    list_filter = ('action', 'timestamp', 'course')
    search_fields = ('student__username', 'course__course_code', 'ip_address')
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Log Details', {'fields': (
            'student', 'course', 'action'
        )}),
        ('Technical Details', {'fields': (
            'confidence_score', 'image_path', 'device_id', 'ip_address'
        )}),
        ('Error Information', {'fields': (
            'error_message',
        )}),
        ('Timestamp', {'fields': (
            'timestamp',
        )}),
    )