from django.db import models
from users.models import CustomUser, Department

class Course(models.Model):
    """Course model"""
    COURSE_TYPE_CHOICES = (
        ('core', 'Core'),
        ('elective', 'Elective'),
        ('lab', 'Lab'),
        ('project', 'Project'),
        ('seminar', 'Seminar'),
    )
    
    # DAY_CHOICES = (
    #     ('Monday', 'Monday'),
    #     ('Tuesday', 'Tuesday'),
    #     ('Wednesday', 'Wednesday'),
    #     ('Thursday', 'Thursday'),
    #     ('Friday', 'Friday'),
    #     ('Saturday', 'Saturday'),
    # )
    
    
    course_code = models.CharField(max_length=50, unique=True, verbose_name="Course Code")
    course_name = models.CharField(max_length=200, verbose_name="Course Name")
    course_type = models.CharField(max_length=20, choices=COURSE_TYPE_CHOICES, default='core')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses',blank=True, null=True)
    semester = models.IntegerField(verbose_name="Semester")
    credits = models.IntegerField(default=3, verbose_name="Credits")
    
    # Teaching Details
    teacher = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        limit_choices_to={'user_type': 'teacher'},
        related_name='courses_taught',
        verbose_name="Course Teacher"
    )
    co_teacher = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        limit_choices_to={'user_type': 'teacher'},
        related_name='courses_co_taught',
        verbose_name="Co-Teacher"
    )
    # Schedule Details
    
   
    
    # day = models.CharField(
    #     max_length=20,
    #     choices=DAY_CHOICES,
    #     blank=True,
    #     null=True
    # )

    # start_time = models.TimeField(
    #     blank=True,
    #     null=True
    # )

    # end_time = models.TimeField(
    #     blank=True,
    #     null=True
    # )

    # room = models.CharField(max_length=50)

    # created_at = models.DateTimeField(auto_now_add=True)
    
    # Schedule Details
    schedule = models.CharField(max_length=100, verbose_name="Schedule (e.g., Mon-Wed-Fri 10:00-11:30)")
    room = models.CharField(max_length=50, verbose_name="Room Number")
    start_date = models.DateField(verbose_name="Start Date",null=True, blank=True)
    end_date = models.DateField(verbose_name="End Date",null=True, blank=True)
    
    # Course Details
    description = models.TextField(blank=True, verbose_name="Course Description")
    objectives = models.TextField(blank=True, verbose_name="Course Objectives")
    prerequisites = models.CharField(max_length=200, blank=True, verbose_name="Prerequisites")
    total_hours = models.IntegerField(default=45, verbose_name="Total Hours")
    
    # Status
    is_active = models.BooleanField(default=True, verbose_name="Active")
    max_strength = models.IntegerField(default=60, verbose_name="Maximum Strength")
    current_strength = models.IntegerField(default=0, verbose_name="Current Strength")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['course_code']
        verbose_name = "Course"
        verbose_name_plural = "Courses"
    
    def __str__(self):
        return f"{self.course_code} - {self.course_name}"
    
    def save(self, *args, **kwargs):
        # Auto-generate course code if not provided
        if not self.course_code:
            dept_code = self.department.code if self.department else 'GEN'
            self.course_code = f"{dept_code}{self.semester:02d}{Course.objects.filter(department=self.department, semester=self.semester).count() + 1:03d}"
        super().save(*args, **kwargs)
    
    @property
    def attendance_percentage(self):
        """Calculate overall attendance percentage for this course"""
        from django.db.models import Avg
        avg_attendance = Attendance.objects.filter(
            course=self,
            status='present'
        ).aggregate(Avg('confidence_score'))['confidence_score__avg']
        return avg_attendance or 0

class Enrollment(models.Model):
    """Student enrollment in courses"""
    student = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        limit_choices_to={'user_type': 'student'},
        related_name='enrollments'
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrollment_date = models.DateField(auto_now_add=True, verbose_name="Enrollment Date")
    enrollment_type = models.CharField(
        max_length=20, 
        choices=[('regular', 'Regular'), ('audit', 'Audit'), ('credit', 'Credit')],
        default='regular'
    )
    grade = models.CharField(max_length=2, blank=True, verbose_name="Grade")
    marks = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Marks")
    is_active = models.BooleanField(default=True, verbose_name="Active")
    
    class Meta:
        unique_together = ['student', 'course']
        ordering = ['-enrollment_date']
        verbose_name = "Enrollment"
        verbose_name_plural = "Enrollments"
    
    def __str__(self):
        return f"{self.student.student_id} - {self.course.course_code}"

class Attendance(models.Model):
    STATUS_CHOICES = (
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('half_day', 'Half Day'),
        ('leave', 'Leave'),
        ('od', 'On Duty'),
    )
    
    # Student and Course
    student = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        limit_choices_to={'user_type': 'student'},
        related_name='attendances',
        verbose_name="Student"
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='attendances')
    
    # Date and Time
    date = models.DateField(verbose_name="Date")
    time_in = models.TimeField(verbose_name="Check-in Time")
    time_out = models.TimeField(null=True, blank=True, verbose_name="Check-out Time")
    duration = models.DurationField(null=True, blank=True, verbose_name="Duration")
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='present')
    reason = models.TextField(blank=True, verbose_name="Reason for Absence/Late")
    is_verified = models.BooleanField(default=False, verbose_name="Verified")
    
    # Face Recognition Details
    face_image = models.ImageField(upload_to='attendance_images/', blank=True, null=True, verbose_name="Face Image")
    confidence_score = models.FloatField(null=True, blank=True, verbose_name="Confidence Score")
    face_match_duration = models.FloatField(null=True, blank=True, verbose_name="Face Match Duration (ms)")
    
    # Device and Location
    device_id = models.CharField(max_length=100, blank=True, verbose_name="Device ID")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP Address")
    location = models.CharField(max_length=200, blank=True, verbose_name="Location")
    
    # Marked By
    marked_by = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='marked_attendances',
        verbose_name="Marked By"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['student', 'course', 'date']
        ordering = ['-date', '-time_in']
        indexes = [
            models.Index(fields=['student', 'date']),
            models.Index(fields=['course', 'date']),
            models.Index(fields=['status', 'date']),
        ]
        verbose_name = "Attendance"
        verbose_name_plural = "Attendance Records"
    
    def __str__(self):
        return f"{self.student.username} - {self.course.course_code} - {self.date} - {self.status}"
    
    def save(self, *args, **kwargs):
        # Calculate duration if time_out is provided
        if self.time_out and self.time_in:
            from datetime import datetime, date
            dt_in = datetime.combine(date.today(), self.time_in)
            dt_out = datetime.combine(date.today(), self.time_out)
            self.duration = dt_out - dt_in
        
        super().save(*args, **kwargs)
    
    @property
    def attendance_percentage(self):
        """Calculate attendance percentage for this student in this course"""
        total_classes = Attendance.objects.filter(
            student=self.student, 
            course=self.course
        ).count()
        present_classes = Attendance.objects.filter(
            student=self.student, 
            course=self.course,
            status='present'
        ).count()
        
        if total_classes > 0:
            return (present_classes / total_classes) * 100
        return 0

class AttendanceLog(models.Model):
    """Log for attendance marking attempts"""
    ACTION_CHOICES = (
        ('attempt', 'Attempt'),
        ('success', 'Success'),
        ('failure', 'Failure'),
        ('retry', 'Retry'),
    )
    
    student = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        limit_choices_to={'user_type': 'student'},
        null=True, 
        blank=True
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    confidence_score = models.FloatField(null=True, blank=True)
    image_path = models.CharField(max_length=500, blank=True)
    device_id = models.CharField(max_length=100, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Attendance Log"
        verbose_name_plural = "Attendance Logs"
    
    def __str__(self):
        return f"{self.student.username if self.student else 'Unknown'} - {self.action} - {self.timestamp}"
    


class CourseSchedule(models.Model):

    DAY_CHOICES = (
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='schedules'
    )

    day = models.CharField(
        max_length=20,
        choices=DAY_CHOICES
    )

    start_time = models.TimeField()

    end_time = models.TimeField()

    room = models.CharField(
        max_length=50,
        blank=True
    )

    def __str__(self):
        return f"{self.course.course_code} - {self.day}"