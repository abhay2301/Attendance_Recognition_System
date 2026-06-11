from django.urls import path
from . import views
from attendance.views import register_face_from_attendance

app_name = 'face_app'

urlpatterns = [
    path('register/', views.register_face_view, name='register_face'),
    path('capture/', views.capture_faces_for_registration, name='face_capture'),
    path('verify/', views.mark_attendance_view, name='face_verification'),
    path('test-camera/', views.camera_stream, name='camera_test'),
    path('mark-attendance/', views.mark_attendance_api, name='mark_attendance_api'),
    path('upload-face/', views.upload_face, name='upload_face'),
    path('face/delete/<int:face_id>/', views.delete_face, name='delete_face'),
    path('register-face-attendance/', register_face_from_attendance, name='register_face_from_attendance'),
    
]