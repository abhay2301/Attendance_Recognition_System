from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from datetime import datetime

@login_required
def reports_dashboard(request):
    """Reports dashboard"""
    context = {
        'title': 'Reports Dashboard'
    }
    return render(request, 'reports/reports_dashboard.html', context)

@login_required
def daily_report(request):
    """Daily attendance report"""
    context = {
        'title': 'Daily Report',
        'selected_date': datetime.now().strftime('%Y-%m-%d')
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