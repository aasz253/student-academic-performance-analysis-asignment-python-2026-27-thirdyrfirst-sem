/* SAPAS Version 3 - Student Academic Performance Analysis JavaScript */

let unitsChartInstance = null;
let comparisonChartInstance = null;
let currentStudentSummary = null;

document.addEventListener('DOMContentLoaded', function() {
    initApp();
});

function initApp() {
    setupAuthListeners();
    checkExistingSession();
}

/**
 * Check if student session is already active in sessionStorage
 */
function checkExistingSession() {
    try {
        const stored = sessionStorage.getItem('sapas_student_session');
        if (stored) {
            const student = JSON.parse(stored);
            if (student && student.registration_number) {
                fetchStudentData(student.registration_number);
                return;
            }
        }
    } catch (e) {
        console.error('Error reading session:', e);
    }
    showLandingView();
}

/**
 * Configure login and navigation event handlers
 */
function setupAuthListeners() {
    const loginForm = document.getElementById('student-login-form');
    const logoutBtn = document.getElementById('btn-logout');
    const demoPills = document.querySelectorAll('.demo-pill');
    const printReportBtn = document.getElementById('btn-print-report');
    const refreshBtn = document.getElementById('btn-refresh-data');
    const closeReportBtn = document.getElementById('btn-close-report');
    const closeReportFooter = document.getElementById('btn-close-report-footer');

    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const identifier = document.getElementById('student-identifier').value.trim();
            if (!identifier) return;
            await performLogin(identifier);
        });
    }

    if (logoutBtn) {
        logoutBtn.addEventListener('click', function() {
            sessionStorage.removeItem('sapas_student_session');
            currentStudentSummary = null;
            showLandingView();
        });
    }

    demoPills.forEach(pill => {
        pill.addEventListener('click', function() {
            const ident = this.getAttribute('data-ident');
            if (ident) {
                const input = document.getElementById('student-identifier');
                if (input) input.value = ident;
                performLogin(ident);
            }
        });
    });

    if (printReportBtn) {
        printReportBtn.addEventListener('click', openReportModal);
    }

    if (refreshBtn) {
        refreshBtn.addEventListener('click', function() {
            if (currentStudentSummary && currentStudentSummary.student) {
                fetchStudentData(currentStudentSummary.student.registration_number);
            }
        });
    }

    if (closeReportBtn) {
        closeReportBtn.addEventListener('click', closeReportModal);
    }
    if (closeReportFooter) {
        closeReportFooter.addEventListener('click', closeReportModal);
    }
}

/**
 * Perform login request to /api/login
 */
async function performLogin(identifier) {
    const errorBox = document.getElementById('login-error');
    const btnSubmit = document.getElementById('btn-signin');
    if (errorBox) {
        errorBox.style.display = 'none';
        errorBox.textContent = '';
    }
    if (btnSubmit) {
        btnSubmit.disabled = true;
        btnSubmit.textContent = 'Verifying credentials...';
    }

    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ registration_number: identifier })
        });

        const data = await response.json();

        if (response.ok && data.success && data.summary) {
            // Save session
            sessionStorage.setItem('sapas_student_session', JSON.stringify(data.student));
            currentStudentSummary = data.summary;
            renderStudentDashboard(data.summary);
            showDashboardView();
        } else {
            showLoginError(data.error || 'Student registration number not found. Please verify and try again.');
        }
    } catch (err) {
        console.error('Login error:', err);
        showLoginError('Network error connecting to the academic portal. Please ensure the server is active.');
    } finally {
        if (btnSubmit) {
            btnSubmit.disabled = false;
            btnSubmit.textContent = 'Access Academic Dashboard →';
        }
    }
}

function showLoginError(msg) {
    const errorBox = document.getElementById('login-error');
    if (errorBox) {
        errorBox.textContent = msg;
        errorBox.style.display = 'block';
    }
}

/**
 * Fetch fresh student summary data
 */
async function fetchStudentData(regNo) {
    try {
        const response = await fetch(`/api/student-summary?registration=${encodeURIComponent(regNo)}`);
        if (response.ok) {
            const summary = await response.json();
            currentStudentSummary = summary;
            renderStudentDashboard(summary);
            showDashboardView();
        } else {
            // If failed to fetch, fall back to landing
            sessionStorage.removeItem('sapas_student_session');
            showLandingView();
        }
    } catch (e) {
        console.error('Fetch student data failed:', e);
        showLandingView();
    }
}

/**
 * Switch views
 */
function showLandingView() {
    const landing = document.getElementById('landing-section');
    const dashboard = document.getElementById('dashboard-section');
    const navGuest = document.getElementById('nav-guest');
    const navUser = document.getElementById('nav-user');
    const errorBox = document.getElementById('login-error');

    if (landing) landing.style.display = 'block';
    if (dashboard) dashboard.style.display = 'none';
    if (navGuest) navGuest.style.display = 'flex';
    if (navUser) navUser.style.display = 'none';
    if (errorBox) errorBox.style.display = 'none';

    // Clear charts
    if (unitsChartInstance) {
        unitsChartInstance.destroy();
        unitsChartInstance = null;
    }
    if (comparisonChartInstance) {
        comparisonChartInstance.destroy();
        comparisonChartInstance = null;
    }
}

function showDashboardView() {
    const landing = document.getElementById('landing-section');
    const dashboard = document.getElementById('dashboard-section');
    const navGuest = document.getElementById('nav-guest');
    const navUser = document.getElementById('nav-user');

    if (landing) landing.style.display = 'none';
    if (dashboard) dashboard.style.display = 'block';
    if (navGuest) navGuest.style.display = 'none';
    if (navUser) navUser.style.display = 'flex';

    window.scrollTo({ top: 0, behavior: 'smooth' });
}

/**
 * Render all student metrics, charts, and table
 */
function renderStudentDashboard(summary) {
    if (!summary || !summary.student) return;

    const student = summary.student;
    const perf = summary.performance || {};
    const units = summary.units || [];
    const classAvg = summary.class_average || 0;

    // 1. Header & Welcome Area
    const navName = document.getElementById('nav-student-name');
    const navReg = document.getElementById('nav-student-reg');
    const dashName = document.getElementById('dash-student-name');
    const dashReg = document.getElementById('dash-student-reg');
    const dashYear = document.getElementById('dash-student-year');

    if (navName) navName.textContent = student.name;
    if (navReg) navReg.textContent = `(${student.registration_number})`;
    if (dashName) dashName.textContent = student.name;
    if (dashReg) dashReg.textContent = student.registration_number;
    if (dashYear) dashYear.textContent = student.academic_year || '2024/2025';

    // 2. KPI Cards
    const kpiAvg = document.getElementById('kpi-average');
    const kpiTotal = document.getElementById('kpi-total-marks');
    const kpiGrade = document.getElementById('kpi-grade');
    const kpiGradeRemarks = document.getElementById('kpi-grade-remarks');
    const kpiClassification = document.getElementById('kpi-classification');
    const kpiPassed = document.getElementById('kpi-units-passed');
    const kpiFailed = document.getElementById('kpi-units-failed');

    if (kpiAvg) kpiAvg.textContent = `${perf.average_marks || 0}%`;
    if (kpiTotal) kpiTotal.textContent = `Total Marks: ${perf.total_marks || 0}`;
    if (kpiGrade) kpiGrade.textContent = `Grade ${perf.overall_grade || 'N/A'}`;
    if (kpiGradeRemarks) kpiGradeRemarks.textContent = getGradeRemarksText(perf.overall_grade);
    if (kpiClassification) kpiClassification.textContent = perf.performance_classification || 'Pending';
    if (kpiPassed) kpiPassed.textContent = `${perf.units_passed || 0} Units Passed`;
    if (kpiFailed) kpiFailed.textContent = `${perf.units_failed || 0} Failed Units`;

    // 3. Populate Marks Records Table
    const tbody = document.getElementById('student-marks-tbody');
    if (tbody) {
        if (units.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: #64748b; padding: 2rem;">No examination records entered for this student yet.</td></tr>`;
        } else {
            let rowsHtml = '';
            units.forEach(u => {
                const gradeBadgeClass = `badge-${(u.grade || 'e').toLowerCase()}`;
                const statusBadgeClass = u.status === 'Passed' ? 'badge-pass' : 'badge-fail';
                rowsHtml += `
                    <tr>
                        <td><strong>${escapeHtml(u.unit_code)}</strong></td>
                        <td>${escapeHtml(u.unit_name)}</td>
                        <td><strong>${u.marks}</strong> / 100</td>
                        <td><span class="badge ${gradeBadgeClass}">Grade ${escapeHtml(u.grade)}</span></td>
                        <td>${escapeHtml(u.remarks)}</td>
                        <td><span class="badge ${statusBadgeClass}">${escapeHtml(u.status)}</span></td>
                    </tr>
                `;
            });
            tbody.innerHTML = rowsHtml;
        }
    }

    // 4. Render Subject Breakdown Chart
    renderUnitsChart(units);

    // 5. Render Comparison Chart (Student vs Class Average)
    renderComparisonChart(perf.average_marks || 0, classAvg);
}

function getGradeRemarksText(grade) {
    switch (grade) {
        case 'A': return 'Excellent Standing';
        case 'B': return 'Very Good Standing';
        case 'C': return 'Good Standing';
        case 'D': return 'Pass Standing';
        case 'E': return 'Remediation Required';
        default: return 'No Grades Recorded';
    }
}

/**
 * Render Bar Chart of student's marks per academic unit
 */
function renderUnitsChart(units) {
    const canvas = document.getElementById('studentUnitsChart');
    if (!canvas || typeof Chart === 'undefined') return;

    if (unitsChartInstance) {
        unitsChartInstance.destroy();
    }

    const labels = units.map(u => u.unit_name || u.unit_code);
    const dataVals = units.map(u => u.marks);
    const bgColors = dataVals.map(val => {
        if (val >= 70) return 'rgba(16, 185, 129, 0.75)'; // green
        if (val >= 60) return 'rgba(59, 130, 246, 0.75)'; // blue
        if (val >= 50) return 'rgba(245, 158, 11, 0.75)'; // amber
        if (val >= 40) return 'rgba(234, 88, 12, 0.75)';  // orange
        return 'rgba(239, 68, 68, 0.75)';                 // red
    });

    const ctx = canvas.getContext('2d');
    unitsChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels.length ? labels : ['No units'],
            datasets: [{
                label: 'Score (/100)',
                data: dataVals.length ? dataVals : [0],
                backgroundColor: bgColors,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: { color: '#64748b' },
                    grid: { color: '#e2e8f0' }
                },
                x: {
                    ticks: { color: '#64748b' },
                    grid: { display: false }
                }
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Marks: ${context.parsed.y} / 100`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Render Student Average vs Class Average Comparison Chart
 */
function renderComparisonChart(studentAvg, classAvg) {
    const canvas = document.getElementById('studentComparisonChart');
    if (!canvas || typeof Chart === 'undefined') return;

    if (comparisonChartInstance) {
        comparisonChartInstance.destroy();
    }

    const ctx = canvas.getContext('2d');
    comparisonChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Your Average', 'Class Average'],
            datasets: [{
                label: 'Average Score (%)',
                data: [studentAvg, classAvg],
                backgroundColor: [
                    'rgba(30, 58, 138, 0.85)', // navy
                    'rgba(148, 163, 184, 0.75)' // slate
                ],
                borderColor: [
                    '#1e3a8a',
                    '#94a3b8'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: { color: '#64748b' },
                    grid: { color: '#e2e8f0' }
                },
                x: {
                    ticks: { color: '#64748b' },
                    grid: { display: false }
                }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}

/**
 * Official Report Modal generator
 */
function openReportModal() {
    if (!currentStudentSummary || !currentStudentSummary.student) return;

    const modal = document.getElementById('report-modal');
    const body = document.getElementById('report-modal-body');
    if (!modal || !body) return;

    const s = currentStudentSummary.student;
    const p = currentStudentSummary.performance || {};
    const units = currentStudentSummary.units || [];
    const dateStr = new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });

    let unitsTableHtml = '';
    units.forEach(u => {
        unitsTableHtml += `
            <tr style="border-bottom: 1px solid #e2e8f0;">
                <td style="padding: 8px 12px; font-weight: 600;">${escapeHtml(u.unit_code)}</td>
                <td style="padding: 8px 12px;">${escapeHtml(u.unit_name)}</td>
                <td style="padding: 8px 12px; text-align: center;">${u.marks}</td>
                <td style="padding: 8px 12px; text-align: center; font-weight: 700;">${escapeHtml(u.grade)}</td>
                <td style="padding: 8px 12px;">${escapeHtml(u.remarks)}</td>
            </tr>
        `;
    });

    body.innerHTML = `
        <div style="font-family: inherit; color: #1e293b;">
            <div style="text-align: center; margin-bottom: 1.5rem; border-bottom: 2px solid #1e3a8a; padding-bottom: 1rem;">
                <h2 style="margin: 0; color: #1e3a8a; font-size: 1.4rem;">OFFICIAL ACADEMIC TRANSCRIPT & PERFORMANCE REPORT</h2>
                <p style="margin: 4px 0 0 0; color: #64748b; font-size: 0.9rem;">Student Academic Performance Analysis System (SAPAS)</p>
                <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 0.8rem;">Date Generated: ${dateStr}</p>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; background: #f8fafc; padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem; font-size: 0.9rem;">
                <div>
                    <p style="margin: 3px 0;"><strong>Student Name:</strong> ${escapeHtml(s.name)}</p>
                    <p style="margin: 3px 0;"><strong>Registration Number:</strong> ${escapeHtml(s.registration_number)}</p>
                </div>
                <div>
                    <p style="margin: 3px 0;"><strong>Academic Year:</strong> ${escapeHtml(s.academic_year || '2024/2025')}</p>
                    <p style="margin: 3px 0;"><strong>Degree Standing:</strong> <span style="color: #047857; font-weight: 700;">${escapeHtml(p.performance_classification || 'Pending')}</span></p>
                </div>
            </div>

            <table style="width: 100%; border-collapse: collapse; margin-bottom: 1.5rem; font-size: 0.9rem;">
                <thead>
                    <tr style="background: #1e3a8a; color: white;">
                        <th style="padding: 8px 12px; text-align: left;">Code</th>
                        <th style="padding: 8px 12px; text-align: left;">Academic Unit Title</th>
                        <th style="padding: 8px 12px; text-align: center;">Marks</th>
                        <th style="padding: 8px 12px; text-align: center;">Grade</th>
                        <th style="padding: 8px 12px; text-align: left;">Remarks</th>
                    </tr>
                </thead>
                <tbody>
                    ${unitsTableHtml}
                </tbody>
            </table>

            <div style="background: #f1f5f9; padding: 1rem; border-radius: 8px; display: flex; justify-content: space-around; text-align: center;">
                <div>
                    <div style="font-size: 0.8rem; color: #64748b; font-weight: 600;">TOTAL MARKS</div>
                    <div style="font-size: 1.3rem; font-weight: 800; color: #1e3a8a;">${p.total_marks || 0}</div>
                </div>
                <div>
                    <div style="font-size: 0.8rem; color: #64748b; font-weight: 600;">OVERALL AVERAGE</div>
                    <div style="font-size: 1.3rem; font-weight: 800; color: #1e3a8a;">${p.average_marks || 0}%</div>
                </div>
                <div>
                    <div style="font-size: 0.8rem; color: #64748b; font-weight: 600;">OVERALL GRADE</div>
                    <div style="font-size: 1.3rem; font-weight: 800; color: #047857;">${escapeHtml(p.overall_grade || 'N/A')}</div>
                </div>
                <div>
                    <div style="font-size: 0.8rem; color: #64748b; font-weight: 600;">UNITS PASSED</div>
                    <div style="font-size: 1.3rem; font-weight: 800; color: #1e3a8a;">${p.units_passed || 0} / ${(p.units_passed || 0) + (p.units_failed || 0)}</div>
                </div>
            </div>

            <div style="margin-top: 2rem; display: flex; justify-content: space-between; font-size: 0.85rem; color: #64748b;">
                <div>
                    <p>Verified by SAPAS System Controller</p>
                    <p style="margin-top: 2rem; border-top: 1px dashed #cbd5e1; width: 200px;">Authorized Signature</p>
                </div>
                <div style="text-align: right;">
                    <p>Academic Registrar Seal</p>
                    <p style="margin-top: 2rem; border-top: 1px dashed #cbd5e1; width: 200px; margin-left: auto;">Official Stamp</p>
                </div>
            </div>
        </div>
    `;

    modal.style.display = 'block';
}

function closeReportModal() {
    const modal = document.getElementById('report-modal');
    if (modal) modal.style.display = 'none';
}

function escapeHtml(text) {
    if (text === null || text === undefined) return '';
    return String(text)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}
