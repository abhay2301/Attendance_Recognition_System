import base64
import cv2
import numpy as np
import face_recognition
import pickle

from django.utils import timezone
from django.http import JsonResponse

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import models
from django.db.models import Count, Q
from django.views.decorators.csrf import csrf_exempt
import face_recognition
from .models import Course, Attendance, Enrollment
from users.models import CustomUser
from datetime import datetime, timedelta

import json

@login_required
def mark_attendance(request):
    """View to mark attendance using face recognition"""
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)

    courses = Course.objects.filter(is_active=True)

    # Today's attendance records
    today_records = Attendance.objects.filter(date=today).select_related('student', 'course')

    # Summary counts for today
    on_time_today = today_records.filter(status='present').exclude(time_in__gt='09:30').count()
    late_today = today_records.filter(Q(status='late') | Q(status='present', time_in__gt='09:30')).count()
    early_today = today_records.filter(status='present', time_in__lt='09:00').count()
    absent_today = today_records.filter(status='absent').count()

    total_students = CustomUser.objects.filter(user_type='student', is_active=True).count()
    clocked_in_ids = today_records.values_list('student_id', flat=True)
    no_clock_in_today = total_students - clocked_in_ids.count()

    # Yesterday's counts for comparison
    yesterday_records = Attendance.objects.filter(date=yesterday)
    on_time_yesterday = yesterday_records.filter(status='present').exclude(time_in__gt='09:30').count()
    late_yesterday = yesterday_records.filter(Q(status='late') | Q(status='present', time_in__gt='09:30')).count()
    early_yesterday = yesterday_records.filter(status='present', time_in__lt='09:00').count()
    absent_yesterday = yesterday_records.filter(status='absent').count()
    clocked_in_yesterday = yesterday_records.values_list('student_id', flat=True).count()
    no_clock_in_yesterday = total_students - clocked_in_yesterday

    # Students list for the modal
    students = CustomUser.objects.filter(user_type='student', is_active=True).order_by('first_name')

    context = {
        'title': 'Mark Attendance',
        'courses': courses,
        'today': today,
        'current_time': datetime.now().time(),
        'attendance_records': today_records,
        'students': students,
        # Summary
        'on_time_count': on_time_today,
        'late_count': late_today,
        'early_count': early_today,
        'absent_count': absent_today,
        'no_clock_in_count': no_clock_in_today,
        # Comparison deltas
        'on_time_delta': on_time_today - on_time_yesterday,
        'late_delta': late_today - late_yesterday,
        'early_delta': early_today - early_yesterday,
        'absent_delta': absent_today - absent_yesterday,
        'no_clock_in_delta': no_clock_in_today - no_clock_in_yesterday,
    }
    return render(request, 'Attendance/mark_Attendance.html', context)

@login_required
def view_attendance(request):
    """View to see attendance records"""
    context = {
        'title': 'View Attendance',
        'attendance_records': Attendance.objects.filter(student=request.user) if Attendance.objects.exists() else [],
        'absent_students': []
    }
    return render(request, 'Attendance/view_attendance.html', context)

@login_required
def attendance_history(request):
    """Detailed attendance history"""
    context = {
        'title': 'Attendance History',
        'attendance_records': Attendance.objects.filter(student=request.user) if Attendance.objects.exists() else []
    }
    return render(request, 'Attendance/attendance_history.html', context)

@login_required
def course_list(request):
    """List all courses"""
    context = {
        'title': 'Courses',
        'courses': Course.objects.all() if Course.objects.exists() else []
    }
    return render(request, 'courses/course_list.html', context)

@login_required
def course_detail(request, course_id):
    """View course details"""
    course = get_object_or_404(Course, id=course_id)
    
    # Check if user is enrolled
    is_enrolled = False
    if request.user.user_type == 'student':
        is_enrolled = Enrollment.objects.filter(
            student=request.user,
            course=course,
            is_active=True
        ).exists()
    
    # Get attendance records for this course
    if request.user.user_type == 'student':
        attendance_records = Attendance.objects.filter(
            course=course,
            student=request.user
        ).order_by('-date')
    else:
        attendance_records = Attendance.objects.filter(
            course=course
        ).order_by('-date', 'student__username')[:50]
    
    # Calculate attendance statistics
    total_classes = Attendance.objects.filter(course=course).values('date').distinct().count()
    
    attended_classes = 0
    attendance_rate = 0
    
    if request.user.user_type == 'student':
        attended_classes = Attendance.objects.filter(
            course=course,
            student=request.user,
            status='present'
        ).count()
        attendance_rate = round((attended_classes / total_classes * 100) if total_classes > 0 else 0, 1)
    
    # Get enrolled students count
    enrolled_students = Enrollment.objects.filter(
        course=course,
        is_active=True
    ).count()
    
    context = {
        'title': course.course_name,
        'course': course,
        'is_enrolled': is_enrolled,
        'attendance_records': attendance_records,
        'total_classes': total_classes,
        'attended_classes': attended_classes,
        'attendance_rate': attendance_rate,
        'enrolled_students': enrolled_students,
    }
    return render(request, 'courses/course_detail.html', context)

@login_required
def enroll_course(request, course_id):
    """Enroll in a course"""
    if request.user.user_type != 'student':
        messages.error(request, 'Only students can enroll in courses.')
        return redirect('course_list')
    
    course = get_object_or_404(Course, id=course_id)
    
    # Check if already enrolled
    existing_enrollment = Enrollment.objects.filter(
        student=request.user,
        course=course
    ).first()
    
    if existing_enrollment:
        if existing_enrollment.is_active:
            messages.info(request, f'You are already enrolled in {course.course_name}.')
        else:
            existing_enrollment.is_active = True
            existing_enrollment.save()
            messages.success(request, f'Successfully re-enrolled in {course.course_name}!')
    else:
        Enrollment.objects.create(
            student=request.user,
            course=course,
            is_active=True
        )
        messages.success(request, f'Successfully enrolled in {course.course_name}!')
    
    return redirect('attendance:course_detail', course_id=course_id)

@login_required
def daily_report(request):
    """Daily attendance report"""
    context = {
        'title': 'Daily Report',
        'selected_date': datetime.now().strftime('%Y-%m-%d'),
        'daily_records': Attendance.objects.filter(date=datetime.now().date()) if Attendance.objects.exists() else [],
        'absent_students': []
    }
    return render(request, 'reports/daily_report.html', context)

@login_required
def monthly_report(request):
    """Monthly attendance report"""
    context = {
        'title': 'Monthly Report',
        'selected_month': datetime.now().strftime('%Y-%m')
    }
    return render(request, 'reports/monthly_report.html', context)

@login_required
def student_report(request):
    """Student-specific report"""
    context = {
        'title': 'Student Report',
        'student': request.user
    }
    return render(request, 'reports/student_report.html', context)

@login_required
def attendance_api(request):
    """API to fetch attendance records with filters"""
    course_id = request.GET.get('course_id', '')
    date_str = request.GET.get('date', '')
    search = request.GET.get('search', '')

    records = Attendance.objects.select_related('student', 'course')

    if date_str:
        try:
            filter_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            filter_date = datetime.now().date()
    else:
        filter_date = datetime.now().date()

    records = records.filter(date=filter_date)

    if course_id:
        records = records.filter(course_id=course_id)

    if search:
        records = records.filter(
            Q(student__first_name__icontains=search) |
            Q(student__last_name__icontains=search) |
            Q(student__student_id__icontains=search) |
            Q(student__username__icontains=search)
        )

    data = []
    for record in records:
        duration_str = ''
        if record.duration:
            total_seconds = int(record.duration.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            duration_str = f'{hours}h {minutes}m'

        data.append({
            'id': record.id,
            'student_name': record.student.get_full_name() or record.student.username,
            'student_id': record.student.student_id or '-',
            'time_in': record.time_in.strftime('%I:%M %p') if record.time_in else '-',
            'time_out': record.time_out.strftime('%I:%M %p') if record.time_out else '-',
            'duration': duration_str or '-',
            'course': record.course.course_code,
            'status': record.status,
            'confidence': f'{record.confidence_score:.1f}%' if record.confidence_score else '-',
            'confidence_value': record.confidence_score or 0,
        })

    return JsonResponse({'success': True, 'records': data})

@login_required
def save_attendance_api(request):
    """API to manually save an attendance record"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'})

    try:
        data = json.loads(request.body)
        student_id = data.get('student_id')
        course_id = data.get('course_id')
        date_str = data.get('date')
        time_in_str = data.get('time_in')
        time_out_str = data.get('time_out')
        status = data.get('status', 'present')
        confidence = data.get('confidence')
        notes = data.get('notes', '')

        if not all([student_id, course_id, date_str, time_in_str]):
            return JsonResponse({'success': False, 'error': 'Missing required fields'})

        student = get_object_or_404(CustomUser, id=student_id)
        course = get_object_or_404(Course, id=course_id)
        att_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        att_time_in = datetime.strptime(time_in_str, '%H:%M').time()
        att_time_out = datetime.strptime(time_out_str, '%H:%M').time() if time_out_str else None

        # Check for existing record
        existing = Attendance.objects.filter(student=student, course=course, date=att_date).first()
        if existing:
            return JsonResponse({'success': False, 'error': 'Attendance already exists for this student, course, and date'})

        Attendance.objects.create(
            student=student,
            course=course,
            date=att_date,
            time_in=att_time_in,
            time_out=att_time_out,
            status=status,
            confidence_score=float(confidence) if confidence else None,
            reason=notes,
            marked_by=request.user,
        )

        return JsonResponse({'success': True, 'message': 'Attendance saved successfully'})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
    
@csrf_exempt
def add_course_api(request):
    if request.method == "POST":
        data = json.loads(request.body)

        Course.objects.create(
            course_code=data['course_code'],
            course_name=data['course_name'],
            description=data.get('description', ''),
            credits=data['credits'],
            schedule=data.get('schedule', ''),
            room=data.get('room', ''),
            semester=data['semester'],
            # start_date=data['start_date'],
            # end_date=data.get('end_date'),
            teacher=request.user
        )

        return JsonResponse({
            "success": True
        })
        
       
@csrf_exempt
@login_required
def register_face_from_attendance(request):

    if request.method != "POST":
        return JsonResponse({
            "success": False,
            "error": "POST request required"
        })

    try:

        data = json.loads(request.body)

        student_id = data.get("user_id")
        image_data = data.get("image")

        student = CustomUser.objects.get(
            id=student_id,
            user_type='student'
        )

        # Decode Base64 Image
        image_bytes = base64.b64decode(
            image_data.split(',')[1]
        )

        np_arr = np.frombuffer(
            image_bytes,
            np.uint8
        )

        img = cv2.imdecode(
            np_arr,
            cv2.IMREAD_COLOR
        )

        rgb = cv2.cvtColor(
            img,
            cv2.COLOR_BGR2RGB
        )

        encodings = face_recognition.face_encodings(rgb)

        if len(encodings) == 0:
            return JsonResponse({
                "success": False,
                "error": "No face detected"
            })

        encoding = encodings[0]

        student.face_encoding = pickle.dumps(encoding)

        student.is_face_registered = True

        student.registration_date = timezone.now()

        student.save()

        return JsonResponse({
            "success": True,
            "message": f"{student.get_full_name()} face registered successfully"
        })

    except Exception as e:

        return JsonResponse({
            "success": False,
            "error": str(e)
        })