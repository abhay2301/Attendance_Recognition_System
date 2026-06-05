// Mobile sidebar toggle
document.addEventListener('DOMContentLoaded', function() {
    // Mobile sidebar toggle
    const sidebarToggle = document.createElement('button');
    sidebarToggle.className = 'btn btn-primary d-md-none position-fixed';
    sidebarToggle.style.cssText = 'top: 10px; left: 10px; z-index: 1001;';
    sidebarToggle.innerHTML = '<i class="fas fa-bars"></i>';
    document.body.appendChild(sidebarToggle);
    
    sidebarToggle.addEventListener('click', function() {
        document.querySelector('.sidebar').classList.toggle('show');
    });
    
    // Auto-hide sidebar on mobile when clicking outside
    document.addEventListener('click', function(e) {
        if (window.innerWidth < 768 && 
            !e.target.closest('.sidebar') && 
            !e.target.closest('.sidebar-toggle')) {
            document.querySelector('.sidebar').classList.remove('show');
        }
    });
    
    // Real-time clock update
    function updateClock() {
        const now = new Date();
        const clockElement = document.getElementById('live-clock');
        if (clockElement) {
            clockElement.textContent = now.toLocaleTimeString();
        }
    }
    
    setInterval(updateClock, 1000);
    updateClock();
    
    // Auto-refresh attendance status every 30 seconds
    setInterval(function() {
        if (window.location.pathname.includes('dashboard')) {
            fetch('/api/attendance/stats/')
                .then(response => response.json())
                .then(data => {
                    // Update stats on dashboard
                    console.log('Refreshed attendance stats:', data);
                });
        }
    }, 30000);
});