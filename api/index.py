import sys
import os

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vercel_wsgi import handler
from attendance_system.wsgi import application

app = handler(application)
