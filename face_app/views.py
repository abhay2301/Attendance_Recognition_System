import json
import base64
import cv2
import numpy as np
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET, require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
import threading
import time
from datetime import datetime
import os
import face_recognition

from face_app.models import FaceImage


from users.forms import FaceImageUploadForm
from .models import Person
from .utils import face_system
from .camera import get_camera, release_all_cameras
from users.models import CustomUser, StudentProfile
from attendance.models import Attendance, Course


@login_required
def register_face_view(request):
    """Teacher registers student faces"""

    if request.user.user_type != "teacher":
        messages.error(
            request,
            "Only teachers can register student faces."
        )
        return redirect("dashboard")

    students = StudentProfile.objects.select_related(
        "user"
    ).filter(
        user__user_type="student"
    ).order_by("roll_number")

    print("Students Found:", students.count())   # Debug

    context = {
        "title": "Register Face",
        "user": request.user,
        "students": students,
    }

    return render(
        request,
        "face_registration/register_face.html",
        context
    )

@login_required
def mark_attendance_view(request):
    courses = Course.objects.filter(is_active=True)

    students = StudentProfile.objects.select_related(
        'user'
    ).all().order_by('roll_number')

    context = {
        'title': 'Mark Attendance',
        'courses': courses,
        'students': students,
        'user': request.user
    }

    return render(
        request,
        'Attendance/mark_Attendance.html',
        context
    )

@login_required
def view_attendance_view(request):
    """View attendance records"""
    if request.user.user_type == 'student':
        attendance_records = Attendance.objects.filter(
            student=request.user
        ).order_by('-date', '-time_in')[:50]
    else:
        attendance_records = Attendance.objects.all().order_by('-date', '-time_in')[:100]
    
    context = {
        'title': 'View Attendance',
        'attendance_records': attendance_records
    }
    return render(request, 'face_app/view_attendance.html', context)

# @csrf_exempt
# @require_POST
# @login_required
# def capture_faces_for_registration(request):
#     """Capture multiple faces for registration"""
#     try:
#         data = json.loads(request.body)
#         images_base64 = data.get('images', [])
        
#         if not images_base64:
#             return JsonResponse({'success': False, 'error': 'No images provided'})
        
#         images = []
#         for img_base64 in images_base64:
#             # Convert base64 to numpy array
#             img_data = base64.b64decode(img_base64.split(',')[1])
#             np_arr = np.frombuffer(img_data, np.uint8)
#             img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            
#             if img is not None:
#                 images.append(img)
        
#         if len(images) < 3:
#             return JsonResponse({
#                 'success': False, 
#                 'error': f'Need at least 3 images. Got {len(images)}'
#             })
        
#         # Register face
#         success = face_system.register_face(request.user, images)
        
#         if success:
#             return JsonResponse({
#                 'success': True,
#                 'message': 'Face registration successful!'
#             })
#         else:
#             return JsonResponse({
#                 'success': False,
#                 'error': 'Failed to register face. Please try again.'
#             })
            
#     except Exception as e:
#         return JsonResponse({
#             'success': False,
#             'error': str(e)
#         })

@csrf_exempt
@require_POST
@login_required
def mark_attendance_api(request):
    """API to mark attendance"""
    try:
        data = json.loads(request.body)
        
        if request.user.user_type != 'teacher':
            return JsonResponse({
                'success': False,
                'error': 'Only teachers can mark attendance.'
            })
        
        image_base64 = data.get('image', '')
        course_id = data.get('course_id', '')
        
        if not image_base64:
            return JsonResponse({'success': False, 'error': 'No image provided'})
        
        # course_id can be optional (auto-detect from student's enrollments)
        # if not course_id:
        #     return JsonResponse({'success': False, 'error': 'No course selected'})
        
        # Convert base64 to numpy array
        img_data = base64.b64decode(image_base64.split(',')[1])
        np_arr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        
        if img is None:
            return JsonResponse({'success': False, 'error': 'Invalid image'})
        
        # Reload latest registered faces
        face_system.load_known_faces()
        
        # Recognize face
        recognition_result = face_system.recognize_face(img)
        
        print("Recognition Result:", recognition_result)
        
        if not recognition_result:
            return JsonResponse({
                'success': False,
                'error': 'No face recognized. Please try again.'
            })
        
        # Check confidence
        if recognition_result['confidence'] < 50:  # 50% confidence threshold
            return JsonResponse({
                'success': False,
                'error': f'Low confidence ({recognition_result["confidence"]}%). Please try again.'
            })
        
        # Get user
        user = CustomUser.objects.get(id=recognition_result['user_id'])
        
        # Only students can be recognized
        if user.user_type != 'student':
            return JsonResponse({
                'success': False,
                'error': 'Only student faces can mark attendance.'
            })

        # Face must be registered
        if not user.is_face_registered:
            return JsonResponse({
                'success': False,
                'error': 'Student face is not registered.'
            })

        # Face encoding must exist
        if not user.face_encoding:
            return JsonResponse({
                'success': False,
                'error': 'Face encoding not found.'
            })
        
        from attendance.models import Enrollment
        from django.db.models import Q

        display_name = user.get_full_name()
        if not display_name and hasattr(user, 'students') and user.students.exists():
            display_name = user.students.first().user_full_name
        if not display_name:
            display_name = user.username

        courses_to_mark = []
        if course_id:
            course = get_object_or_404(Course, id=course_id)
            # Verify student is enrolled in this course
            is_enrolled = Enrollment.objects.filter(student=user, course=course, is_active=True, course__is_active=True).exists()
            if not is_enrolled:
                return JsonResponse({
                    'success': False,
                    'error': f'Recognized student {display_name} ({user.student_id or user.username}) is NOT enrolled in {course.course_code}. Attendance cannot be marked.'
                })
            courses_to_mark = [course]
        else:
            # Automatically detect active enrolled courses for this student
            enrollments = Enrollment.objects.filter(student=user, is_active=True, course__is_active=True).select_related('course', 'course__teacher', 'course__co_teacher')
            
            # If a teacher is marking, prefer courses taught by this teacher, but fallback if needed
            if request.user.user_type == 'teacher':
                teacher_enrollments = enrollments.filter(Q(course__teacher=request.user) | Q(course__co_teacher=request.user))
                if teacher_enrollments.exists():
                    enrollments = teacher_enrollments
            
            if not enrollments.exists():
                return JsonResponse({
                    'success': False,
                    'error': f'Recognized student {display_name} ({user.student_id or user.username}) is not enrolled in any active courses.'
                })
            
            courses_to_mark = [e.course for e in enrollments]
        
        today = datetime.now().date()
        marked_courses = []
        any_marked = False
        latest_action = 'time_in'

        for course in courses_to_mark:
            existing_attendance = Attendance.objects.filter(
                student=user,
                course=course,
                date=today
            ).first()
            
            if existing_attendance:
                # Update time out
                existing_attendance.time_out = datetime.now().time()
                existing_attendance.save()
                marked_courses.append(f'{course.course_code}')
                latest_action = 'time_out'
            else:
                # Create new attendance record
                attendance = Attendance.objects.create(
                    student=user,
                    course=course,
                    date=today,
                    time_in=datetime.now().time(),
                    marked_by=request.user,
                    confidence_score=recognition_result['confidence'],
                    status='present'
                )
                
                # Save face image
                img_filename = f'attendance_{user.id}_{int(time.time())}_{course.id}.jpg'
                img_path = os.path.join(settings.MEDIA_ROOT, 'attendance_images', img_filename)
                os.makedirs(os.path.dirname(img_path), exist_ok=True)
                cv2.imwrite(img_path, img)
                attendance.face_image = f'attendance_images/{img_filename}'
                attendance.save()
                
                marked_courses.append(f'{course.course_code}')
                any_marked = True
                latest_action = 'time_in'

        courses_str = ", ".join(marked_courses)
        if any_marked:
            msg = f'Attendance automatically marked for {display_name} ({user.student_id or user.username}) in enrolled course(s): {courses_str}'
        else:
            msg = f'Attendance updated (Time Out) for {display_name} ({user.student_id or user.username}) in enrolled course(s): {courses_str}'

        return JsonResponse({
            'success': True,
            'message': msg,
            'user_name': display_name,
            'student_id': user.student_id or user.username,
            'confidence': recognition_result['confidence'],
            'action': latest_action,
            'courses': marked_courses
        })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@require_GET
def camera_stream(request):
    """Camera streaming endpoint"""
    camera_id = int(request.GET.get('camera_id', 0))
    camera = get_camera(camera_id)
    
    if not camera.is_opened():
        if not camera.start():
            return JsonResponse({'error': 'Camera not available'})
    
    def generate_frames():
        while True:
            frame = camera.get_latest_frame()
            if frame is not None:
                # Convert to JPEG
                _, buffer = cv2.imencode('.jpg', frame)
                frame_bytes = buffer.tobytes()
                
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            time.sleep(0.033)  # ~30 FPS
    
    return StreamingHttpResponse(
        generate_frames(), 
        content_type='multipart/x-mixed-replace; boundary=frame'
    )

@csrf_exempt
@require_POST
def check_face_api(request):
    """API to check if face exists in image"""
    try:
        data = json.loads(request.body)
        image_base64 = data.get('image', '')
        
        if not image_base64:
            return JsonResponse({'success': False, 'error': 'No image provided'})
        
        # Convert base64 to numpy array
        img_data = base64.b64decode(image_base64.split(',')[1])
        np_arr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        
        # Detect faces
        faces = face_system.detect_faces(img)
        
        if faces:
            return JsonResponse({
                'success': True,
                'face_count': len(faces),
                'message': f'Found {len(faces)} face(s)'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'No face detected'
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@login_required
def test_camera_view(request):
    """Test camera functionality"""
    context = {
        'title': 'Test Camera',
        'available_cameras': get_camera(0).list_cameras()
    }
    return render(request, 'face_recognition/test_camera.html', context)

@csrf_exempt
@require_POST
def get_attendance_stats(request):
    """Get attendance statistics"""
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        
        if user_id:
            user = get_object_or_404(CustomUser, id=user_id)
            attendance_records = Attendance.objects.filter(student=user)
        else:
            attendance_records = Attendance.objects.all()
        
        # Calculate statistics
        total_records = attendance_records.count()
        present_count = attendance_records.filter(status='present').count()
        absent_count = attendance_records.filter(status='absent').count()
        
        stats = {
            'total': total_records,
            'present': present_count,
            'absent': absent_count,
            'attendance_rate': round((present_count / total_records * 100) if total_records > 0 else 0, 2)
        }
        
        return JsonResponse({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

def cleanup():
    """Cleanup function"""
    release_all_cameras()

# Register cleanup on exit
import atexit
atexit.register(cleanup)


def home(request):
    return render(request, 'face_app/base.html')

def face_register(request):
    return render(request, 'face_app/register_face.html')


@login_required
def upload_face(request):
    """Upload face image view"""
    if request.method == 'POST':
        form = FaceImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Get or create Person for the user
            person, created = Person.objects.get_or_create(
                email=request.user.email,
                defaults={
                    'name': request.user.get_full_name() or request.user.username,
                    'created_by': request.user
                }
            )
            
            face_image = form.save(commit=False)
            face_image.person = person
            
            # Generate face encoding
            try:
                image = face_recognition.load_image_file(face_image.image)
                face_encodings = face_recognition.face_encodings(image)
                
                if len(face_encodings) == 0:
                    messages.error(request, 'No face detected in the image. Please upload a clear face image.')
                    return render(request, 'face_app/upload_face.html', {'form': form})
                
                if len(face_encodings) > 1:
                    messages.warning(request, 'Multiple faces detected. Using the first face.')
                
                # Store encoding as JSON
                face_image.encoding = face_encodings[0].tolist()
                face_image.save()
                
                messages.success(request, 'Face image uploaded successfully!')
                return redirect('profile')
                
            except Exception as e:
                messages.error(request, f'Error processing image: {str(e)}')
                return render(request, 'face_app/upload_face.html', {'form': form})
    else:
        form = FaceImageUploadForm()
    
    return render(request, 'face_app/upload_face.html', {'form': form})

@login_required
@require_http_methods(["DELETE"])
def delete_face(request, face_id):
    """Delete face image"""
    face_image = get_object_or_404(FaceImage, id=face_id)
    
    # Check if the face belongs to the user
    if face_image.person.email != request.user.email:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    face_image.delete()
    return JsonResponse({'success': True})