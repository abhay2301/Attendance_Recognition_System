from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
import uuid

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    )
    
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    )
    
    # Basic Information
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='student')
    student_id = models.CharField(max_length=20, unique=True, blank=True, null=True, verbose_name="Student ID")
    employee_id = models.CharField(max_length=20, unique=True, blank=True, null=True, verbose_name="Employee ID")
    
    # Personal Information
    phone = models.CharField(max_length=15, blank=True, verbose_name="Phone Number")
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    date_of_birth = models.DateField(null=True, blank=True, verbose_name="Date of Birth")
    address = models.TextField(blank=True, verbose_name="Address")
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True, default="India")
    pincode = models.CharField(max_length=10, blank=True)
    
    # Academic Information
    department = models.CharField(max_length=100, blank=True, verbose_name="Department")
    semester = models.IntegerField(null=True, blank=True, verbose_name="Semester")
    year_of_admission = models.IntegerField(null=True, blank=True, verbose_name="Year of Admission")
    year_of_passing = models.IntegerField(null=True, blank=True, verbose_name="Year of Passing")
    
    # Professional Information (for teachers)
    designation = models.CharField(max_length=100, blank=True, verbose_name="Designation")
    qualification = models.CharField(max_length=200, blank=True, verbose_name="Qualification")
    experience = models.IntegerField(null=True, blank=True, verbose_name="Experience (years)")
    specialization = models.CharField(max_length=200, blank=True, verbose_name="Specialization")
    
    # Profile & Face Recognition
    profile_picture = models.ImageField(
        upload_to='profile_pics/', 
        blank=True, 
        null=True,
        verbose_name="Profile Picture"
    )
    face_encoding = models.BinaryField(blank=True, null=True, verbose_name="Face Encoding")
    is_face_registered = models.BooleanField(default=False, verbose_name="Face Registered")
    registration_date = models.DateTimeField(null=True, blank=True, verbose_name="Face Registration Date")
    
    # Status & Timestamps
    is_active = models.BooleanField(default=True, verbose_name="Active")
    is_verified = models.BooleanField(default=False, verbose_name="Verified")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")
    
    # Additional fields
    blood_group = models.CharField(max_length=5, blank=True, verbose_name="Blood Group")
    emergency_contact = models.CharField(max_length=15, blank=True, verbose_name="Emergency Contact")
    emergency_contact_name = models.CharField(max_length=100, blank=True, verbose_name="Emergency Contact Name")
    
    class Meta:
        ordering = ['-date_joined']
        verbose_name = "User"
        verbose_name_plural = "Users"
    
    def __str__(self):
        if self.user_type == 'student' and self.student_id:
            return f"{self.student_id} - {self.get_full_name() or self.username}"
        elif self.user_type == 'teacher' and self.employee_id:
            return f"{self.employee_id} - {self.get_full_name() or self.username}"
        else:
            return f"{self.username} ({self.get_user_type_display()})"
    
    @property
    def full_name(self):
        """Return full name of the user"""
        return self.get_full_name() or self.username
    
    @property
    def is_student(self):
        return self.user_type == 'student'
    
    @property
    def is_teacher(self):
        return self.user_type == 'teacher'
    
    @property
    def is_admin_user(self):
        return self.user_type == 'admin' or self.is_staff
    
    def save(self, *args, **kwargs):
        # Auto-generate student_id if not provided and user is student
        if self.user_type == 'student' and not self.student_id:
            # Generate student ID like: STU-2024-001
            from django.db.models import Count
            year = self.date_joined.year
            last_student = CustomUser.objects.filter(
                user_type='student', 
                date_joined__year=year
            ).count()
            self.student_id = f"STU-{year}-{last_student + 1:03d}"
        
        # Auto-generate employee_id if not provided and user is teacher
        elif self.user_type == 'teacher' and not self.employee_id:
            # Generate employee ID like: EMP-2024-001
            from django.db.models import Count
            year = self.date_joined.year
            last_teacher = CustomUser.objects.filter(
                user_type='teacher', 
                date_joined__year=year
            ).count()
            self.employee_id = f"EMP-{year}-{last_teacher + 1:03d}"
        
        super().save(*args, **kwargs)
        

class StudentProfile(models.Model):
    """Additional details for students"""

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='students'
    )

    # Academic Details
    user_full_name = models.CharField(max_length=100, verbose_name="Student Name")

    roll_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Roll Number"
    )

    registration_number = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Registration Number"
    )

    batch = models.CharField(
        max_length=10,
        verbose_name="Batch (e.g., 2024-2028)"
    )

    section = models.CharField(
        max_length=10,
        blank=True,
        verbose_name="Section"
    )

    current_semester = models.IntegerField(
        default=1,
        verbose_name="Current Semester"
    )

    # Parent Information
    father_name = models.CharField(max_length=100, blank=True)
    mother_name = models.CharField(max_length=100, blank=True)

    guardian_name = models.CharField(max_length=100, blank=True)
    guardian_relation = models.CharField(max_length=50, blank=True)

    guardian_contact = models.CharField(
        max_length=15,
        blank=True,
        verbose_name="Guardian Contact"
    )

    # Academic Performance
    cgpa = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True
    )

    attendance_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.0
    )

    backlog_count = models.IntegerField(default=0)

    # Documents
    aadhar_card = models.CharField(max_length=12, blank=True)
    pan_card = models.CharField(max_length=10, blank=True)

    # Status
    is_hosteller = models.BooleanField(default=False)

    scholarship = models.BooleanField(default=False)
    scholarship_details = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Student Profile"
        verbose_name_plural = "Student Profiles"

    def __str__(self):
        return f"{self.roll_number} - {self.user.get_full_name() or self.user.username}"

class TeacherProfile(models.Model):
    """Additional details for teachers"""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='teacher_profile')
    
    # Professional Details
    user_full_name = models.CharField(max_length=100, blank=True, verbose_name="Employee Name")
    employee_code = models.CharField(max_length=20, unique=True, verbose_name="Employee Code")
    department = models.CharField(max_length=100, verbose_name="Department")
    designation = models.CharField(max_length=100, verbose_name="Designation")
    
    # Academic Qualifications
    highest_qualification = models.CharField(max_length=100, verbose_name="Highest Qualification")
    qualification_details = models.TextField(blank=True, verbose_name="Qualification Details")
    specialization = models.CharField(max_length=200, verbose_name="Specialization")
    
    # Professional Experience
    total_experience = models.IntegerField(verbose_name="Total Experience (Years)")
    previous_institution = models.CharField(max_length=200, blank=True, verbose_name="Previous Institution")
    joining_date = models.DateField(verbose_name="Joining Date")
    
    # Contact Information
    office_phone = models.CharField(max_length=15, blank=True, verbose_name="Office Phone")
    extension = models.CharField(max_length=10, blank=True, verbose_name="Extension")
    office_location = models.CharField(max_length=100, blank=True, verbose_name="Office Location")
    
    # Administrative Details
    is_hod = models.BooleanField(default=False, verbose_name="Head of Department")
    hod_department = models.CharField(max_length=100, blank=True, verbose_name="HOD Department")
    is_class_coordinator = models.BooleanField(default=False, verbose_name="Class Coordinator")
    coordinator_class = models.CharField(max_length=50, blank=True, verbose_name="Coordinator Class")
    
    # Documents
    aadhar_card = models.CharField(max_length=12, blank=True, verbose_name="Aadhar Card Number")
    pan_card = models.CharField(max_length=10, blank=True, verbose_name="PAN Card Number")
    bank_account = models.CharField(max_length=20, blank=True, verbose_name="Bank Account Number")
    ifsc_code = models.CharField(max_length=11, blank=True, verbose_name="IFSC Code")
    
    # Status
    is_active = models.BooleanField(default=True, verbose_name="Active")
    leave_balance = models.IntegerField(default=30, verbose_name="Leave Balance (Days)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Teacher Profile"
        verbose_name_plural = "Teacher Profiles"
    
    def __str__(self):
        return f"{self.employee_code} - {self.user.get_full_name() or self.user.username}"
    
    @property
    def experience_years(self):
        from datetime import date
        if self.joining_date:
            today = date.today()
            experience = today.year - self.joining_date.year
            if today.month < self.joining_date.month or (today.month == self.joining_date.month and today.day < self.joining_date.day):
                experience -= 1
            return experience
        return self.total_experience

class Department(models.Model):
    """Department model for organizing students and teachers"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Department Name")
    code = models.CharField(max_length=10, unique=True, verbose_name="Department Code")
    hod = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        limit_choices_to={'user_type': 'teacher'},
        related_name='department_hod',
        verbose_name="Head of Department"
    )
    description = models.TextField(blank=True, verbose_name="Description")
    established_date = models.DateField(null=True, blank=True, verbose_name="Established Date")
    total_students = models.IntegerField(default=0, verbose_name="Total Students")
    total_teachers = models.IntegerField(default=0, verbose_name="Total Teachers")
    
    # Contact Information
    office_phone = models.CharField(max_length=15, blank=True, verbose_name="Office Phone")
    email = models.EmailField(blank=True, verbose_name="Department Email")
    location = models.CharField(max_length=200, blank=True, verbose_name="Location")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = "Department"
        verbose_name_plural = "Departments"
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    def update_counts(self):
        """Update student and teacher counts"""
        self.total_students = self.student_set.count()
        self.total_teachers = self.teacher_set.count()
        self.save()