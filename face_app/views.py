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
from users.models import CustomUser
from attendance.models import Attendance, Course


@login_required
def register_face_view(request):
    """Face registration page"""
    if request.user.is_face_registered:
        messages.info(request, "Your face is already registered!")
        return redirect('dashboard')
    
    context = {
        'title': 'Register Face',
        'user': request.user
    }
    return render(request, 'face_registration/register_face.html', context)

@login_required
def mark_attendance_view(request):
    """Mark attendance page"""
    courses = Course.objects.filter(is_active=True)
    students = CustomUser.objects.filter(
    user_type='student'
    )
    context = {
        'title': 'Mark Attendance',
        'courses': courses,
        'students': students,
        'user': request.user
    }
    return render(request, 'face_recognition/mark_attendance.html', context)

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

@csrf_exempt
@require_POST
@login_required
def capture_faces_for_registration(request):
    """Capture multiple faces for registration"""
    try:
        data = json.loads(request.body)
        images_base64 = data.get('images', [])
        
        if not images_base64:
            return JsonResponse({'success': False, 'error': 'No images provided'})
        
        images = []
        for img_base64 in images_base64:
            # Convert base64 to numpy array
            img_data = base64.b64decode(img_base64.split(',')[1])
            np_arr = np.frombuffer(img_data, np.uint8)
            img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            
            if img is not None:
                images.append(img)
        
        if len(images) < 3:
            return JsonResponse({
                'success': False, 
                'error': f'Need at least 3 images. Got {len(images)}'
            })
        
        # Register face
        success = face_system.register_face(request.user, images)
        
        if success:
            return JsonResponse({
                'success': True,
                'message': 'Face registration successful!'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Failed to register face. Please try again.'
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@csrf_exempt
@require_POST
@login_required
def mark_attendance_api(request):
    """API to mark attendance"""
    try:
        data = json.loads(request.body)
        image_base64 = data.get('image', '')
        course_id = data.get('course_id', '')
        
        if not image_base64:
            return JsonResponse({'success': False, 'error': 'No image provided'})
        
        if not course_id:
            return JsonResponse({'success': False, 'error': 'No course selected'})
        
        # Convert base64 to numpy array
        img_data = base64.b64decode(image_base64.split(',')[1])
        np_arr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        
        if img is None:
            return JsonResponse({'success': False, 'error': 'Invalid image'})
        
        # Recognize face
        recognition_result = face_system.recognize_face(img)
        
        if not recognition_result:
            return JsonResponse({
                'success': False,
                'error': 'No face recognized. Please try again.'
            })
        
        # Check confidence
        if recognition_result['confidence'] < 60:  # 60% confidence threshold
            return JsonResponse({
                'success': False,
                'error': f'Low confidence ({recognition_result["confidence"]}%). Please try again.'
            })
        
        # Get user
        user = CustomUser.objects.get(id=recognition_result['user_id'])
        course = get_object_or_404(Course, id=course_id)
        
        # Check if attendance already marked today
        today = datetime.now().date()
        existing_attendance = Attendance.objects.filter(
            student=user,
            course=course,
            date=today
        ).first()
        
        if existing_attendance:
            # Update time out
            existing_attendance.time_out = datetime.now().time()
            existing_attendance.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Attendance updated for {user.get_full_name()}',
                'user_name': user.get_full_name(),
                'student_id': user.student_id,
                'confidence': recognition_result['confidence'],
                'action': 'time_out'
            })
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
            img_filename = f'attendance_{user.id}_{int(time.time())}.jpg'
            img_path = os.path.join(settings.MEDIA_ROOT, 'attendance_images', img_filename)
            os.makedirs(os.path.dirname(img_path), exist_ok=True)
            cv2.imwrite(img_path, img)
            attendance.face_image = f'attendance_images/{img_filename}'
            attendance.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Attendance marked for {user.get_full_name()}',
                'user_name': user.get_full_name(),
                'student_id': user.student_id,
                'confidence': recognition_result['confidence'],
                'action': 'time_in'
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