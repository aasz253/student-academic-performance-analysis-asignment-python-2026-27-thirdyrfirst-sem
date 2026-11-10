/* SAPAS Version 3 - JavaScript */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize charts
    initGradeChart();
    initUnitChart();
    
    // Update statistics from data attributes
    updateStats();
    
    // Setup menu navigation
    setupNav();
});

function initGradeChart() {
    // Grade distribution data - would normally come from Flask backend
    const ctx = document.getElementById('gradeChart').getContext('2d');
    
    // Sample data - in production, fetch from API
    const gradeData = {
        labels: ['A', 'B', 'C', 'D', 'E'],
        datasets: [{
            label: 'Grade Distribution',
            data: [8, 12, 10, 5, 3],
            backgroundColor: [
                'rgba(46, 204, 113, 0.7)',
                'rgba(52, 152, 219, 0.7)',
                'rgba(241, 196, 15, 0.7)',
                'rgba(192, 57, 43, 0.7)',
                'rgba(149, 165, 190, 0.7)'
            ],
            borderColor: [
                'rgba(46, 204, 113, 1)',
                'rgba(52, 152, 219, 1)',
                'rgba(241, 196, 15, 1)',
                'rgba(192, 57, 43, 1)',
                'rgba(149, 165, 190, 1)'
            ],
            borderWidth: 1
        }]
    };
    
    const gradeChart = new Chart(ctx, {
        type: 'bar',
        data: gradeData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    enabled: true
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: var(--text-light)
                    },
                    grid: {
                        color: var(--border-color)
                    }
                },
                x: {
                    ticks: {
                        color: var(--text-light)
                    },
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

function initUnitChart() {
    const ctx = document.getElementById('unitChart').getContext('2d');
    
    // Sample unit performance data
    const unitData = {
        labels: ['Mathematics I', 'Physics I', 'Chemistry'],
        datasets: [{
            label: 'Average Marks',
            data: [72.5, 65.3, 58.8],
            backgroundColor: [
                'rgba(46, 204, 113, 0.5)',
                'rgba(52, 152, 219, 0.5)',
                'rgba(241, 196, 15, 0.5)'
            ],
            borderColor: [
                'rgba(46, 204, 113, 1)',
                'rgba(52, 152, 219, 1)',
                'rgba(241, 196, 15, 1)'
            ],
            borderWidth: 1
        }]
    };
    
    const unitChart = new Chart(ctx, {
        type: 'bar',
        data: unitData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    enabled: true
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        color: var(--text-light)
                    },
                    grid: {
                        color: var(--border-color)
                    }
                },
                x: {
                    ticks: {
                        color: var(--text-light)
                    },
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

function updateStats() {
    // Read data from data attributes set by Flask backend
    const totalStudents = document.getElementById('total-students');
    const totalUnits = document.getElementById('total-units');
    const classAvg = document.getElementById('class-avg');
    const passRate = document.getElementById('pass-rate');
    
    // These would be populated by the Flask template
    // For now, leave as loading state
    if (totalStudents.dataset.count) {
        totalStudents.textContent = totalStudents.dataset.count;
    }
    if (totalUnits.dataset.count) {
        totalUnits.textContent = totalUnits.dataset.dataset.count;
    }
    if (classAvg.dataset.avg) {
        classAvg.textContent = classAvg.dataset.avg;
    }
    if (passRate.dataset.rate) {
        passRate.textContent = passRate.dataset.rate + '%';
    }
}

function setupNav() {
    const navLinks = document.querySelectorAll('.action-buttons a, .btn');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // In a real app, this would navigate to different pages
            // For now, just show which section was clicked
            const target = this.getAttribute('href').replace('/', '');
            showSection(target);
        });
    });
}

function showSection(section) {
    // Hide all sections, show selected one
    const sections = {
        students: 'Student Management',
        units: 'Unit Management', 
        marks: 'Marks Entry',
        reports: 'Reports'
    };
    
    alert(`Navigating to: ${sections[section] || section}`);
    // In Version 2+, this would use AJAX or SPA routing
}