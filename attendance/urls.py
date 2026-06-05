from django.urls import path
from . import views

app_name = 'attendance'  # This is important for namespacing

urlpatterns = [
    # Main attendance URLs
    path('mark/', views.mark_attendance, name='mark_Attendance'),
    path('view/', views.view_attendance, name='view_Attendance'),
    path('history/', views.attendance_history, name='attendance_history'),
    
    # Course URLs
    path('courses/', views.course_list, name='course_list'),
    path('courses/<int:course_id>/', views.course_detail, name='course_detail'),
    path('courses/<int:course_id>/enroll/', views.enroll_course, name='enroll_course'),
    path('attendance/add-course/', views.add_course_api, name='add_course_api'),
    
    # Report URLs
    # path('reports/', views.reports, name='reports'),
    path('reports/daily/', views.daily_report, name='daily_report'),
    path('reports/monthly/', views.monthly_report, name='monthly_report'),
    # API endpoints
    path('api/records/', views.attendance_api, name='attendance_api'),
    path('api/save/', views.save_attendance_api, name='save_attendance_api'),
]