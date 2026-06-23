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
    face_images = FaceImage.objects.filter(person=person).order_by('-created_at')
    
    # Get recognition logs
    recognition_logs = RecognitionLog.objects.filter(person=person).order_by('-timestamp')[:10]
    
    # Get attendance records
    attendance_records = Attendance.objects.filter(student=request.user).order_by('-date')[:10]
    
    context = {
        'face_images': face_images,
        'recognition_logs': recognition_logs,
        'attendance_records': attendance_records,
    }
    return render(request, 'users/profile.html', context)

@login_required
def dashboard(request):
    recent_attendance = Attendance.objects.filter(
        student=request.user
    ).order_by('-date', '-time_in')[:5]

    upcoming_courses = Course.objects.all()[:3]

    today = date.today()

    # Today's classes
    today_day = datetime.now().strftime("%A")

    today_classes = CourseSchedule.objects.filter(
        day=today_day
    ).select_related(
        'course',
        'course__teacher'
    ).order_by('start_time')

    total_students = CustomUser.objects.filter(
        user_type='student'
    ).count()

    present_students = Attendance.objects.filter(
        date=today,
        status='present'
    ).values('student').distinct().count()

    present_percentage = 0
    absent_percentage = 0

    if total_students > 0:
        present_percentage = round(
            (present_students / total_students) * 100, 2
        )

        absent_students = total_students - present_students
        absent_percentage = round(
            absent_students / total_students * 100, 2
        )
    else:
        absent_students = 0

    context = {
        'title': 'Dashboard',
        'recent_attendance': recent_attendance,
        'upcoming_courses': upcoming_courses,
        'today_classes': today_classes,
        'present_students': present_students,
        'present_percentage': present_percentage,
        'total_students': total_students,
        'absent_students': absent_students,
        'absent_percentage': absent_percentage
    }

    return render(request, 'users/dashboard.html', context)

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