# 🤖 Face Recognition & Biometric Attendance System

<div align="center">

![Django](https://img.shields.io/badge/Django-5.2.12-092E20?style=for-the-badge&logo=django&logoColor=green)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-4.10.0-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)
![dlib](https://img.shields.io/badge/AI%2FBiometrics-dlib%20%7C%20ResNet34-FF6F00?style=for-the-badge)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)
![Status](https://img.shields.io/badge/Status-Production%20Ready-4caf50?style=for-the-badge)

*An advanced, real-time AI-powered biometric facial recognition attendance and course management platform built with Django, OpenCV, and deep neural network face encodings.*

---

</div>

## 🌟 Executive Summary

The **Face Recognition Attendance System** is an enterprise-grade web application designed to eliminate manual attendance tracking in educational institutions and organizations. Utilizing state-of-the-art **128-dimensional facial embeddings** (via `dlib` and `face_recognition`), the platform enables **touchless, automated student identification and attendance logging directly from any web browser**.

The system features a **role-based multi-user architecture** (Teachers, Students, and Administrators), comprehensive course management, real-time attendance rate calculation, interactive dashboards, and customizable daily/historical reporting with PDF/CSV export capabilities—all wrapped in a modern **Glassmorphism UI design system**.

---

## ✨ Key Features

### 👁️ AI-Powered Biometric Recognition
- **Deep Learning Face Encodings**: Leverages `dlib`'s ResNet-34 deep neural network model (`99.38%` accuracy on the Labeled Faces in the Wild benchmark) to extract unique 128-D facial feature vectors upon user registration.
- **Real-Time WebRTC Auto-Scan**: Streams live camera frames directly from the browser to the backend REST API for instant face localization, alignment, and matching.
- **Zero-Touch Automatic Enrollment Verification**: Automatically detects the student's face, cross-references active course schedules, confirms student enrollment, and records attendance instantly without requiring manual student selection.
- **Biometric Security Status**: Live visual indicators across the dashboard indicating whether a user's biometric model is registered and verified.

### 👥 Role-Based Access Control (RBAC)
- **Teachers / Faculty**:
  - Register facial biometrics and manage student enrollments.
  - Create and configure courses (Course Code, Semester, Schedule, Room, Credits).
  - Launch live automatic attendance scanning sessions (`Auto-Detect Mode`).
  - Access analytics, attendance rate progress charts, and daily attendance logs.
- **Students**:
  - Register personal facial biometrics safely via browser webcam.
  - Browse available course catalogs and one-click enroll.
  - View individual attendance history and real-time attendance percentage per course.
- **Administrators**:
  - Full access to the Django Admin portal for system-wide configuration, user management, and data audit trails.

### 🎨 Modern Glassmorphism Design System
- **Curated `:root` Design Tokens**: Built on a unified palette of vibrant gradients (`--primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%)`, `--sidebar-gradient`, etc.).
- **Sticky Ergonomic Layouts**: Frosted-glass navigation bar with `backdrop-filter: blur(12px)` and anchored sticky sidebars that scroll independently of main content tables.
- **Micro-Animations & Toasts**: Smooth entrance animations (`@keyframes fadeInSlideUp`), custom scrollbars, and auto-dismissing toast notifications (`5-second auto-close`).

### 📊 Advanced Analytics & Reporting
- **Interactive Daily Reports**: Filter attendance logs by date, course, or status (`Present`, `Late`, `Absent`).
- **Live Progress Tracking**: Visual status badges and percentage progress bars displaying real-time attendance statistics per course.
- **Data Export**: One-click export to **PDF** and tabular formats for institutional records.

---

## 🏗️ System Architecture & Technology Stack

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           FRONTEND LAYER                                │
│   HTML5 / Jinja2 Templates  •  Vanilla CSS3 / Glassmorphism  •  WebRTC   │
│                 Bootstrap 5.3  •  Fetch API  •  jQuery                  │
└────────────────────────────────────▲────────────────────────────────────┘
                                     │  JSON REST / HTTP POST (Frames)
┌────────────────────────────────────▼────────────────────────────────────┘
│                         DJANGO BACKEND CORE                             │
│       • `users`: Custom User Model & Authentication (RBAC)             │
│       • `face_app`: Biometric Face Encodings & Real-Time Match Engine  │
│       • `attendance`: Course Management & Attendance Logs              │
│       • `reports`: Daily Analytics & PDF/CSV Export Engine              │
└────────────────────────────────────▲────────────────────────────────────┘
                                     │  SQL Queries & Encodings
┌────────────────────────────────────▼────────────────────────────────────┘
│                          AI & DATABASE LAYER                            │
│     dlib ResNet-34  •  OpenCV Headless  •  NumPy  •  SQLite / PostgreSQL│
└─────────────────────────────────────────────────────────────────────────┘
```

| Component | Technology / Library | Purpose |
| :--- | :--- | :--- |
| **Backend Framework** | Django `5.2.12` | MVC/MVT architecture, ORM, authentication, and REST endpoints |
| **Biometric Engine** | `face_recognition` `1.3.0` (`dlib`) | 128-dimensional facial feature vector extraction and Euclidean distance comparison |
| **Computer Vision** | `opencv-python-headless` `4.10.0` | Frame decoding, image pre-processing, and color-space conversions |
| **Numerical Array Math** | `numpy` `2.2.6` | Vector matrix operations for encoding distance threshold calculations |
| **Frontend UI/UX** | Bootstrap `5.3`, FontAwesome `6.4` | Responsive grid, icons, modals, and interactive UI components |
| **Static & Media Serving** | WhiteNoise `6.6.0`, Pillow `12.1.1` | Static file optimization and image processing (`CORS headers` enabled) |
| **Cloud Deployment** | Vercel (`build.sh`, `vercel.json`) | Serverless deployment support with production WSGI configuration |

---

## 📁 Project Structure

```text
Recognition_System/
│
├── attendance_system/                 # Main Django Workspace Root
│   ├── manage.py                      # Django CLI utility
│   ├── requirements.txt               # Pinned Python package dependencies
│   ├── db.sqlite3                     # Local development database
│   ├── vercel.json / build.sh         # Deployment configuration files
│   │
│   ├── attendance_system/             # Django Core Settings & URL Dispatcher
│   │   ├── settings.py                # App settings, DB config, installed apps
│   │   ├── urls.py                    # Root URL routing
│   │   └── wsgi.py                    # WSGI gateway for production servers
│   │
│   ├── users/                         # User & Authentication App
│   │   ├── models.py                  # Custom User model (`is_face_registered`, `user_type`)
│   │   ├── views.py                   # Login, Registration, Profile management
│   │   └── forms.py                   # Crispy forms for authentication
│   │
│   ├── face_app/                      # AI Biometrics & Face Recognition App
│   │   ├── models.py                  # `FaceEncoding` model storing 128-D numpy vectors
│   │   ├── views.py                   # `register_face_api`, `mark_attendance_api` (Auto-Scan)
│   │   └── urls.py                    # Biometric endpoints
│   │
│   ├── attendance/                    # Courses & Attendance App
│   │   ├── models.py                  # `Course`, `Enrollment`, `Attendance` models
│   │   ├── views.py                   # Course listing, enrollment, and attendance records
│   │   └── urls.py                    # Course management URLs
│   │
│   ├── reports/                       # Analytics & Reporting App
│   │   ├── views.py                   # Daily/Historical reports, PDF export
│   │   └── urls.py                    # Report endpoints
│   │
│   ├── templates/                     # Global HTML Layouts & Views
│   │   ├── base.html                  # Master Glassmorphism layout (Navbar, Sticky Sidebar)
│   │   ├── dashboard.html             # Role-specific summary dashboard
│   │   ├── Attendance/                # `mark_Attendance.html`, `view_Attendance.html`
│   │   ├── courses/                   # `course_list.html`, `course_detail.html`
│   │   ├── face_recognition/          # `register_face.html` (Webcam Capture UI)
│   │   └── reports/                   # `daily_report.html`
│   │
│   ├── static/                        # Custom CSS, JS utilities, and assets
│   └── media/                         # Uploaded user profile avatars & face captures
│
└── README.md                          # Project Documentation
```

---

## 🚀 Installation & Setup Guide

### 1. Prerequisites
Ensure you have the following installed on your system before proceeding:
- **Python** `3.10` or higher (`python --version`)
- **CMake & C++ Build Tools** (Required to compile `dlib` on Windows/Linux):
  - *Windows*: Install [Visual Studio Community](https://visualstudio.microsoft.com/) with **"Desktop development with C++"** workload selected.
  - *Linux (Ubuntu/Debian)*: `sudo apt-get update && sudo apt-get install build-essential cmake libopenblas-dev liblapack-dev libx11-dev libgtk-3-dev`
  - *macOS*: `brew install cmake`

### 2. Clone & Setup Virtual Environment
```bash
# Navigate to project directory
cd d:\MAJOR_PROJECT\Recognition_System\attendance_system

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows (PowerShell):
..\venv\Scripts\Activate.ps1
# Windows (Command Prompt):
..\venv\Scripts\activate.bat
# Linux / macOS:
source ../venv/bin/activate
```

### 3. Install Python Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Apply Database Migrations
Initialize the local SQLite/PostgreSQL database tables:
```bash
python manage.py makemigrations users face_app attendance reports
python manage.py migrate
```

### 5. Create Superuser (Admin)
```bash
python manage.py createsuperuser
# Follow prompt instructions to set up admin username, email, and password
```

### 6. Launch Development Server
```bash
python manage.py runserver
```
Open your web browser and navigate to: **`http://127.0.0.1:8000/`**

---

## 📖 Step-by-Step Usage Workflow

### Step 1: Register Account & Face Biometrics
1. Log into the system using your credentials or create a new account.
2. Navigate to **`Register Face`** from the left navigation sidebar.
3. Allow browser camera permissions. Center your face inside the visual scanning ring and click **`Capture & Register Face`**.
4. The system will extract your unique 128-D embedding and store it securely (`Face Status: Registered ✔`).

### Step 2: Course Setup & Enrollment
1. **For Teachers**: Go to **`Courses`** $\rightarrow$ **`Add New Course`**. Enter course code, name, credits, room, and schedule.
2. **For Students**: Go to **`Courses`**, browse the active course catalog, and click **`Enroll`** (`Status: Enrolled`).

### Step 3: Automated Biometric Attendance Scanning
1. As a Teacher, open **`Mark Attendance`** (`/attendance/mark/`).
2. Select **`Start Auto-Scan`**. The system initiates continuous real-time frame capturing via WebRTC.
3. As students step in front of the camera:
   - The AI detects the face and matches the 128-D vector against registered templates.
   - Cross-references the student's enrollments against current active courses.
   - Instantly marks attendance (`Present / Late / Absent`) with a real-time status feedback toast popup.

### Step 4: Monitor & Export Reports
1. Navigate to **`View Attendance`** or **`Reports`** from the sidebar.
2. Filter attendance records by course, date range, or student name.
3. Click **`Export PDF`** to generate official attendance logs for record-keeping.

---

## 🔌 API Endpoints Reference

| Endpoint URL | Method | Auth Required | Description |
| :--- | :--- | :--- | :--- |
| `/face/api/register/` | `POST` | Yes (`Teacher/Student`) | Receives base64 webcam image, extracts 128-D face encoding vector, and saves to database. |
| `/attendance/mark/api/` | `POST` | Yes (`Teacher`) | **Auto-Scan API**: Receives live camera frame, identifies student face, checks course enrollment, and marks attendance. |
| `/attendance/add_course_api/` | `POST` | Yes (`Teacher/Admin`) | Asynchronous JSON endpoint to create new courses with custom schedules and credit metrics. |
| `/reports/daily/` | `GET` / `POST` | Yes (`All Roles`) | Renders live statistical summary cards and filterable daily attendance records. |

---

## 🛠️ Troubleshooting & Known Issues

1. **`dlib` Installation Failure on Windows**:
   - *Cause*: Missing C++ build tools or CMake.
   - *Fix*: Ensure CMake (`cmake --version`) is added to your Windows `PATH` and Visual Studio C++ build tools are installed before running `pip install dlib==19.24.6`.

2. **Webcam Camera Access Denied (`NotAllowedError`)**:
   - *Cause*: Modern browsers restrict webcam access (`navigator.mediaDevices.getUserMedia`) to secure contexts (`HTTPS` or `http://127.0.0.1` / `http://localhost`).
   - *Fix*: Always access the local server via `http://127.0.0.1:8000/` instead of your local LAN IP (`http://192.168.x.x:8000/`) unless SSL certificates/CORS headers are set up.

3. **Static/Media Files Not Loading**:
   - *Fix*: Ensure `MEDIA_URL = '/media/'` and `STATIC_URL = '/static/'` are configured correctly in `settings.py`, and run `python manage.py collectstatic` when deploying to production environments.

---

<div align="center">
  <p>Built for the <strong>Major Project: AI Biometric Recognition Systems</strong>.</p>
  <p>Version 1.0.0 • &copy; 2026 All Rights Reserved.</p>
</div>
