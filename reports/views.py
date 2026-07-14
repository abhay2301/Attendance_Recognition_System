from datetime import datetime


from django.contrib.auth.decorators import login_required

from django.db.models import Q, Sum

from django.shortcuts import render

from django.utils import timezone

from attendance.models import Attendance, Course, Enrollment
from users.models import Department, CustomUser


@login_required
def reports_dashboard(request):
    context = {
        'title': 'Reports Dashboard'
    }

    return render(
        request,
        'reports/reports_dashboard.html',
        context
    )


@login_required
def daily_report(request):
    # ---------------------------------------
    # Selected date
    # ---------------------------------------

    date_string = request.GET.get('date')

    if date_string:
        try:
            selected_date = datetime.strptime(
                date_string,
                '%Y-%m-%d'
            ).date()

        except ValueError:
            selected_date = timezone.localdate()

    else:
        selected_date = timezone.localdate()


    # ---------------------------------------
    # Attendance records
    # ---------------------------------------

    daily_records = Attendance.objects.filter(
        date=selected_date
    ).select_related(
        'student',
        'course',
        'course__department'
    )


    # ---------------------------------------
    # Teacher
    # ---------------------------------------

    if request.user.user_type == 'teacher':

        teacher_courses = Course.objects.filter(
            Q(teacher=request.user) |
            Q(co_teacher=request.user)
        ).distinct()


        daily_records = daily_records.filter(
            course__in=teacher_courses
        )


        total_students = Enrollment.objects.filter(
            course__in=teacher_courses,
            is_active=True
        ).values('student_id').distinct().count()


    # ---------------------------------------
    # Admin
    # ---------------------------------------

    elif request.user.is_admin_user:

        total_students = CustomUser.objects.filter(
            user_type='student',
            is_active=True
        ).count()


    # ---------------------------------------
    # Student
    # ---------------------------------------

    else:

        daily_records = daily_records.filter(
            student=request.user
        )

        total_students = 1


    # ---------------------------------------
    # Unique student statistics
    # ---------------------------------------

    present_count = daily_records.filter(
        status='present'
    ).values(
        'student_id'
    ).distinct().count()


    late_count = daily_records.filter(
        status='late'
    ).values(
        'student_id'
    ).distinct().count()


    attended_count = daily_records.filter(
        status__in=[
            'present',
            'late'
        ]
    ).values(
        'student_id'
    ).distinct().count()


    absent_count = max(
        total_students - attended_count,
        0
    )


    attendance_percentage = (
        round(
            (
                attended_count /
                total_students
            ) * 100,
            1
        )
        if total_students > 0
        else 0
    )


    # ---------------------------------------
    # Absent students
    # ---------------------------------------

    attended_student_ids = daily_records.filter(
        status__in=['present', 'late']
    ).values_list('student_id', flat=True)

    if request.user.is_admin_user:
        absent_students = Enrollment.objects.filter(
            is_active=True
        ).exclude(
            student_id__in=attended_student_ids
        ).select_related('student', 'course')[:50]
    elif request.user.user_type == 'teacher':
        absent_students = Enrollment.objects.filter(
            course__in=teacher_courses,
            is_active=True
        ).exclude(
            student_id__in=attended_student_ids
        ).select_related('student', 'course')[:50]
    else:
        absent_students = []


    # ---------------------------------------
    # Debug
    # ---------------------------------------

    print("\n========== REPORT DEBUG ==========")

    print(
        "VIEW FILE:",
        __file__
    )

    print(
        "User:",
        request.user.username
    )

    print(
        "User Type:",
        request.user.user_type
    )

    print(
        "Selected Date:",
        selected_date
    )

    print(
        "Attendance rows:",
        daily_records.count()
    )

    print(
        "Statuses:",
        list(
            daily_records.values_list(
                'status',
                flat=True
            )
        )
    )

    print(
        "Total Students:",
        total_students
    )

    print(
        "Present:",
        present_count
    )

    print(
        "Absent:",
        absent_count
    )

    print(
        "Late:",
        late_count
    )

    print(
        "Percentage:",
        attendance_percentage
    )

    print("==================================\n")


    # ---------------------------------------
    # Context
    # ---------------------------------------

    context = {

        'title':
            'Daily Report',

        'selected_date':
            selected_date,

        'daily_records':
            daily_records,

        'total_students':
            total_students,

        'present_count':
            present_count,

        'absent_count':
            absent_count,

        'late_count':
            late_count,

        'attendance_percentage':
            attendance_percentage,

        'absent_students':
            absent_students,
    }


    return render(
        request,
        'reports/daily_report.html',
        context
    )

@login_required
def monthly_report(request):

    context = {
        'title': 'Monthly Report',
        'selected_month': datetime.now().strftime('%Y-%m')
    }

    return render(
        request,
        'reports/monthly_report.html',
        context
    )


@login_required
def student_report(request):

    context = {
        'title': 'Student Report',
        'student': request.user
    }

    return render(
        request,
        'reports/student_report.html',
        context
    )