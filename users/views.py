from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login
from .forms import StudentRegisterForm, UserRegisterForm, UserUpdateForm, ProfileUpdateForm, UserLoginForm, FaceImageUploadForm
from attendance.models import Attendance, Course
from face_app.models import Person, FaceImage, RecognitionLog
from datetime import date, datetime
from attendance.models import Attendance, CourseSchedule
from users.models import CustomUser

def home(request):
    """Landing page for non-authenticated users"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'home.html')

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Account created for {user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def profile(request):
    # Get or create Person for the user
    try:
        person = Person.objects.get(email=request.user.email)
    except Person.DoesNotExist:
        person = Person.objects.create(
            name=request.user.get_full_name() or request.user.username,
            email=request.user.email,
            created_by=request.user
        )
    
    # Get face images
    face_images = FaceImage.objects.filter(person_id=person).order_by('-created_at')
    
    # Get recognition logs
    recognition_logs = RecognitionLog.objects.filter(person_id=person).order_by('-timestamp')[:10]
    
    # Get attendance records
    attendance_records = Attendance.objects.filter(student=request.user).order_by('-date')[:10]
    
    context = {
        'face_images': face_images,
        'recognition_logs': recognition_logs,
        'attendance_records': attendance_records,
    }
    return render(request, 'users/profile.html', context)

from datetime import date
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone

@login_required
def dashboard(request):

    today = timezone.localdate()
    today_day = today.strftime("%A")
    current_time = timezone.localtime().time()

    recent_attendance = Attendance.objects.filter(
        student=request.user
    ).order_by('-date', '-time_in')[:5]

    # -------------------------------
    # ADMIN DASHBOARD
    # -------------------------------
    if request.user.user_type == "admin":

        today_classes = CourseSchedule.objects.filter(
            day=today_day
        ).select_related(
            "course",
            "course__teacher"
        ).order_by("start_time")

        total_students = CustomUser.objects.filter(
            user_type="student"
        ).count()

        present_students = Attendance.objects.filter(
            date=today,
            status="present"
        ).values("student").distinct().count()

        absent_students = total_students - present_students

        present_percentage = round(
            (present_students / total_students) * 100, 2
        ) if total_students else 0

        absent_percentage = round(
            (absent_students / total_students) * 100, 2
        ) if total_students else 0

    # -------------------------------
    # TEACHER DASHBOARD
    # -------------------------------
    elif request.user.user_type == "teacher":

        today_classes = CourseSchedule.objects.filter(
            day=today_day,
            course__teacher=request.user
        ).select_related(
            "course"
        ).order_by("start_time")

        teacher_students = Enrollment.objects.filter(
            course__teacher=request.user,
            is_active=True
        ).values("student").distinct()

        total_students = teacher_students.count()

        present_students = Attendance.objects.filter(
            course__teacher=request.user,
            date=today,
            status="present"
        ).values("student").distinct().count()

        absent_students = total_students - present_students

        present_percentage = round(
            (present_students / total_students) * 100, 2
        ) if total_students else 0

        absent_percentage = round(
            (absent_students / total_students) * 100, 2
        ) if total_students else 0

    # -------------------------------
    # STUDENT DASHBOARD
    # -------------------------------
    else:

        today_classes = CourseSchedule.objects.filter(
            day=today_day,
            course__enrollments__student=request.user,
            course__enrollments__is_active=True
        ).select_related(
            "course",
            "course__teacher"
        ).distinct().order_by("start_time")

        total_students = Attendance.objects.filter(
            student=request.user
        ).count()

        present_students = Attendance.objects.filter(
            student=request.user,
            status="present"
        ).count()

        absent_students = total_students - present_students

        present_percentage = round(
            (present_students / total_students) * 100, 2
        ) if total_students else 0

        absent_percentage = round(
            (absent_students / total_students) * 100, 2
        ) if total_students else 0

    # -------------------------------
    # Class Status
    # -------------------------------
    for schedule in today_classes:

        if current_time < schedule.start_time:
            schedule.status = "Upcoming"

        elif schedule.start_time <= current_time <= schedule.end_time:
            schedule.status = "Ongoing"

        else:
            schedule.status = "Completed"

    context = {
        "title": "Dashboard",
        "recent_attendance": recent_attendance,
        "today_classes": today_classes,
        "present_students": present_students,
        "present_percentage": present_percentage,
        "absent_students": absent_students,
        "absent_percentage": absent_percentage,
        "total_students": total_students,
    }

    return render(
        request,
        "users/dashboard.html",
        context,
    )

def student_register(request):

    if request.method == 'POST':

        form = StudentRegisterForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.user_type = "student"
            user.set_password(form.cleaned_data['password'])
            user.save()

            messages.success(request,"Student registered successfully")
            return redirect('login')

    else:
        form = StudentRegisterForm()

    return render(request,'users/student_register.html',{'form':form})


def LoginView(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(
                request,
                username=username,
                password=password
            )

            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                form.add_error(None, "Invalid username or password")
    else:
        form = UserLoginForm()

    return render(request, 'users/login.html', {'form': form})