from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, StudentProfile, TeacherProfile, Department
from django.utils.html import format_html

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'full_name', 'email', 'user_type', 'student_id', 'employee_id', 'is_face_registered', 'is_active', 'is_staff')
    list_filter = ('user_type', 'is_staff', 'is_superuser', 'is_active', 'department')
    search_fields = ('username', 'email', 'student_id', 'employee_id', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': (
            'first_name', 'last_name', 'email', 'user_type',
            'profile_picture', 'gender', 'date_of_birth', 'phone'
        )}),
        ('Address Information', {'fields': (
            'address', 'city', 'state', 'country', 'pincode'
        )}),
        ('Academic/Professional Info', {'fields': (
            'student_id', 'employee_id', 'department', 'semester',
            'designation', 'qualification', 'experience', 'specialization',
            'year_of_admission', 'year_of_passing'
        )}),
        ('Face Recognition', {'fields': (
            'face_encoding', 'is_face_registered', 'registration_date'
        )}),
        ('Emergency Contact', {'fields': (
            'emergency_contact', 'emergency_contact_name', 'blood_group'
        )}),
        ('Permissions', {'fields': (
            'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'
        )}),
        ('Important Dates', {'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')}),
    )
    
    readonly_fields = ('last_login', 'date_joined', 'created_at', 'updated_at', 'face_encoding')
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'user_type', 'password1', 'password2'),
        }),
    )
    
    def profile_picture_preview(self, obj):
        if obj.profile_picture:
            return format_html('<img src="{}" width="50" height="50" style="border-radius:50%;" />', obj.profile_picture.url)
        return "No Image"
    profile_picture_preview.short_description = 'Profile Picture'

class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('roll_number', 'student_name', 'batch', 'current_semester', 'attendance_percentage', 'cgpa')
    list_filter = ('batch', 'current_semester', 'is_hosteller', 'scholarship')
    search_fields = ('roll_number', 'user__username', 'user__first_name', 'user__last_name', 'registration_number')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Student Information', {'fields': (
            'user', 'user_full_name', 'roll_number', 'registration_number', 'batch', 'section', 'current_semester'
        )}),
        ('Parent/Guardian Information', {'fields': (
            'father_name', 'mother_name', 'guardian_name', 'guardian_relation', 'guardian_contact'
        )}),
        ('Academic Performance', {'fields': (
            'cgpa', 'attendance_percentage', 'backlog_count'
        )}),
        ('Documents', {'fields': (
            'aadhar_card', 'pan_card'
        )}),
        ('Status', {'fields': (
            'is_hosteller', 'scholarship', 'scholarship_details'
        )}),
        ('Timestamps', {'fields': (
            'created_at', 'updated_at'
        )}),
    )
    
    # def student_name(self, obj):
    #     return obj.user.get_full_name()
    
    def student_name(self, obj):
        return obj.user.get_full_name() or obj.user.username

    student_name.short_description = "Student Name"
    
    def user_full_name(self, obj):
        return obj.user.get_full_name()
    user_full_name.short_description = 'Student Name'

class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ('employee_code', 'user_full_name', 'department', 'designation', 'total_experience', 'is_hod')
    list_filter = ('department', 'designation', 'is_hod', 'is_class_coordinator', 'is_active')
    search_fields = ('employee_code', 'user__username', 'user__first_name', 'user__last_name')
    readonly_fields = ('created_at', 'updated_at', 'experience_years')
    
    fieldsets = (
        ('Basic Information', {'fields': (
            'user', 'employee_code', 'department', 'designation'
        )}),
        ('Academic Qualifications', {'fields': (
            'highest_qualification', 'qualification_details', 'specialization'
        )}),
        ('Professional Experience', {'fields': (
            'total_experience', 'previous_institution', 'joining_date', 'experience_years'
        )}),
        ('Contact Information', {'fields': (
            'office_phone', 'extension', 'office_location'
        )}),
        ('Administrative Details', {'fields': (
            'is_hod', 'hod_department', 'is_class_coordinator', 'coordinator_class'
        )}),
        ('Documents', {'fields': (
            'aadhar_card', 'pan_card', 'bank_account', 'ifsc_code'
        )}),
        ('Status', {'fields': (
            'is_active', 'leave_balance'
        )}),
        ('Timestamps', {'fields': (
            'created_at', 'updated_at'
        )}),
    )
    
    def user_full_name(self, obj):
        return obj.user.get_full_name()
    user_full_name.short_description = 'Teacher Name'

class DepartmentAdmin(admin.ModelAdmin):

    list_display = (
        'code',
        'name',
        'hod',
        'total_students',
        'total_teachers'
    )

    list_filter = (
        'established_date',
    )

    search_fields = (
        'name',
        'code',
        'hod__username'
    )

    # Only timestamps should be read-only
    readonly_fields = (
        'created_at',
        'updated_at'
    )

    fieldsets = (
        (
            'Basic Information',
            {
                'fields': (
                    'name',
                    'code',
                    'description',
                    'established_date'
                )
            }
        ),

        (
            'Head of Department',
            {
                'fields': (
                    'hod',
                )
            }
        ),

        (
            'Statistics',
            {
                'fields': (
                    'total_students',
                    'total_teachers'
                )
            }
        ),

        (
            'Contact Information',
            {
                'fields': (
                    'office_phone',
                    'email',
                    'location'
                )
            }
        ),

        (
            'Timestamps',
            {
                'fields': (
                    'created_at',
                    'updated_at'
                )
            }
        ),
    )

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(StudentProfile, StudentProfileAdmin)
admin.site.register(TeacherProfile, TeacherProfileAdmin)
admin.site.register(Department, DepartmentAdmin)